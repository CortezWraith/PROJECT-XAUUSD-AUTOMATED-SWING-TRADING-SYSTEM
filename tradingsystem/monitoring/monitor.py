"""Monitoring: health checks, alerts and live-vs-backtest drift statistics.

The monitor never trades. It raises alerts (log + optional callback such as
e-mail / Telegram / pager) and keeps the numbers needed for promotion gates:
realised slippage and spread vs. the model, trade frequency vs. backtest,
rolling expectancy in R, drawdown vs. the bootstrap distribution.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
import pandas as pd

log = logging.getLogger("tradingsystem.monitor")


@dataclass
class DriftBands:
    """Expected ranges from research (e.g. 5th-95th percentile of bootstrap) per strategy."""

    trades_per_month: tuple[float, float] = (0.0, np.inf)
    expectancy_r: tuple[float, float] = (-np.inf, np.inf)
    max_drawdown: float = np.inf
    slippage_bps: float = np.inf


@dataclass
class Monitor:
    alert_callback: Optional[Callable[[str, str], None]] = None
    heartbeat_timeout_s: float = 180.0
    bands: dict = field(default_factory=dict)
    last_heartbeat: Optional[pd.Timestamp] = None
    alerts: list = field(default_factory=list)

    def alert(self, kind: str, message: str) -> None:
        self.alerts.append((pd.Timestamp.utcnow(), kind, message))
        log.warning("ALERT %s: %s", kind, message)
        if self.alert_callback:
            try:
                self.alert_callback(kind, message)
            except Exception:  # alerting must never break trading
                log.exception("alert callback failed")

    def heartbeat(self, now: pd.Timestamp) -> None:
        self.last_heartbeat = now

    def check_heartbeat(self, now: pd.Timestamp) -> None:
        if self.last_heartbeat is not None and (now - self.last_heartbeat).total_seconds() > self.heartbeat_timeout_s:
            self.alert("HEARTBEAT", f"no heartbeat for {(now - self.last_heartbeat).total_seconds():.0f}s")

    def on_mark(self, ts, portfolio, risk) -> None:
        if risk.state.disabled_strategies:
            for sid, why in risk.state.disabled_strategies.items():
                key = ("DISABLED", sid)
                if key not in {(a[1], a[2].split(':')[0]) for a in self.alerts}:
                    self.alert("DISABLED", f"{sid}: {why}")

    def drift_report(self, trades: pd.DataFrame, months: float) -> dict:
        """Compare realised live/paper statistics with research bands."""
        out = {}
        if trades.empty:
            return out
        for sid, g in trades.groupby("strategy_id"):
            b = self.bands.get(sid, DriftBands())
            tpm = len(g) / max(months, 1e-9)
            exp_r = float(g["r"].mean())
            slip_bps = float((g["slippage_cost"] / (g["volume"] * 100 * g["entry_price"]) * 1e4).mean())
            out[sid] = {
                "trades_per_month": tpm, "tpm_in_band": b.trades_per_month[0] <= tpm <= b.trades_per_month[1],
                "expectancy_r": exp_r, "exp_in_band": b.expectancy_r[0] <= exp_r <= b.expectancy_r[1],
                "slippage_bps": slip_bps, "slippage_ok": slip_bps <= b.slippage_bps,
            }
        return out
