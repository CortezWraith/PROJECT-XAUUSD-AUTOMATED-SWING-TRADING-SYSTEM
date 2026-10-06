"""Competitor's first experiment, implemented as specified (no tuning):
H1 close beyond the 20 previous completed bars' high/low -> entry at next quote;
stop 2x ATR(14); exit on opposite 10-bar breakout (close), after 8 hours, or at 16:00 New York;
one position, max 2 entries per day; risk 0.25 % per trade.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fmt_table, run  # noqa: E402

from tradingsystem.backtest.metrics import summarize, yearly_table  # noqa: E402
from tradingsystem.core.types import Side, SignalAction  # noqa: E402
from tradingsystem.costs.model import CostModel  # noqa: E402
from tradingsystem.risk.manager import RiskConfig  # noqa: E402
from tradingsystem.signals import indicators as ind  # noqa: E402
from tradingsystem.strategies.base import Strategy  # noqa: E402

NY_16_SERVER = 23   # 16:00 New York = 23:00 server time (NY+7)


class H1Breakout(Strategy):
    strategy_id = "h1_breakout"
    timeframe = "H1"

    @dataclass(frozen=True)
    class Params:
        entry_n: int = 20
        exit_n: int = 10
        atr_n: int = 14
        stop_atr: float = 2.0
        max_hold: int = 8
        max_entries_per_day: int = 2
        allow_long: bool = True
        allow_short: bool = True

    def __init__(self, **kw):
        super().__init__(**kw)
        self._day, self._n = None, 0

    @property
    def warmup_bars(self):
        return self.params.entry_n + self.params.atr_n + 2

    def features(self, bars):
        p = self.params
        f = pd.DataFrame(index=bars.index)
        f["close"] = bars["close"]
        f["hh"] = ind.donchian_high(bars["high"], p.entry_n)
        f["ll"] = ind.donchian_low(bars["low"], p.entry_n)
        f["xh"] = ind.donchian_high(bars["high"], p.exit_n)
        f["xl"] = ind.donchian_low(bars["low"], p.exit_n)
        f["atr"] = ind.atr(bars["high"], bars["low"], bars["close"], p.atr_n)
        nxt = bars.index + pd.Timedelta(hours=1)
        f["next_hour"] = nxt.hour
        f["day"] = nxt.normalize()
        return f

    def on_bar(self, ts, row, pos):
        p = self.params
        if np.isnan(row.atr) or np.isnan(row.hh) or np.isnan(row.xl):
            return []
        if pos is not None:
            if (pos.bars_held >= p.max_hold or row.next_hour == NY_16_SERVER
                    or (pos.side is Side.LONG and row.close < row.xl)
                    or (pos.side is Side.SHORT and row.close > row.xh)):
                return [self._sig(ts, SignalAction.EXIT, side=pos.side)]
            return []
        if row.day != self._day:
            self._day, self._n = row.day, 0
        if self._n >= p.max_entries_per_day or row.next_hour in (NY_16_SERVER, 0):
            return []   # no entry into the 16:00 NY exit or the daily break
        if p.allow_long and row.close > row.hh:
            self._n += 1
            return [self._sig(ts, SignalAction.ENTER, side=Side.LONG, stop_price=row.close - p.stop_atr * row.atr)]
        if p.allow_short and row.close < row.ll:
            self._n += 1
            return [self._sig(ts, SignalAction.ENTER, side=Side.SHORT, stop_price=row.close + p.stop_atr * row.atr)]
        return []


RISK = RiskConfig(risk_per_trade=0.0025, enforce_loss_limits=False, max_open_risk=1.0,
                  max_gross_notional_x_equity=50.0, max_spread_bps=1e9)
COLS = ["label", "trades", "trades_per_year", "win_rate", "expectancy_r", "expectancy_r_t", "profit_factor",
        "sharpe", "cagr", "max_dd", "avg_hold_hours", "long_expectancy_r", "short_expectancy_r"]

if __name__ == "__main__":
    rows, years = [], None
    for lab, (a, b), src, cost in [
        ("DEV/val 2015-2023, gross", ("2015-01-01", "2024-01-01"), "stitched", CostModel().frictionless()),
        ("DEV/val 2015-2023, costs x1", ("2015-01-01", "2024-01-01"), "stitched", CostModel()),
        ("DEV/val 2015-2023, costs x1.5", ("2015-01-01", "2024-01-01"), "stitched", CostModel(multiplier=1.5)),
        ("A only 2016-09..2023, costs x1", ("2016-09-01", "2024-01-01"), "A", CostModel()),
        ("TEST 2024-01..2026-08, gross", ("2024-01-01", "2026-09-01"), "A", CostModel().frictionless()),
        ("TEST 2024-01..2026-08, costs x1", ("2024-01-01", "2026-09-01"), "A", CostModel()),
        ("TEST 2024-01..2026-08, costs x1.5", ("2024-01-01", "2026-09-01"), "A", CostModel(multiplier=1.5)),
    ]:
        res = run([H1Breakout()], a, b, source=src, cost=cost, risk=RISK)
        rows.append(summarize(res, lab))
        if lab == "DEV/val 2015-2023, costs x1":
            years = yearly_table(res)
    out = ("# x01 – H1 breakout (návrh konkurenta, pravidla beze změn)\n\n" + fmt_table(rows, COLS)
           + "\n\n## Roky, DEV/val, náklady x1\n\n"
           + fmt_table(years.reset_index().rename(columns={"index": "year"}).to_dict("records"),
                       ["year", "return", "trades", "win_rate", "exp_r", "pf"]) + "\n")
    print(out)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "x01_h1_breakout.md"), "w") as f:
        f.write(out)
