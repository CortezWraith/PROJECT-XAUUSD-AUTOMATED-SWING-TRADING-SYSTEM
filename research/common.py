"""Shared research helpers: data loading, protocol dates, standard runs."""
from __future__ import annotations

import json
import os
import sys
from functools import lru_cache
from typing import Optional, Sequence

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tradingsystem.backtest.metrics import summarize  # noqa: E402
from tradingsystem.backtest.runner import BacktestResult, run_backtest  # noqa: E402
from tradingsystem.costs.model import CostModel, RateCurve  # noqa: E402
from tradingsystem.risk.manager import RiskConfig  # noqa: E402

PROC = os.path.join(ROOT, "data", "processed")
RESULTS = os.path.join(ROOT, "research", "results")
os.makedirs(RESULTS, exist_ok=True)

# ----------------------------------------------------------------------------- protocol
# Fixed BEFORE any strategy was run (see research/PROTOCOL.md).
PRE_SAMPLE = ("2004-07-01", "2010-01-01")     # dataset B only, never used for development
DEV = ("2010-01-01", "2019-01-01")            # development (B until 2016-08-31, A afterwards)
OOS = ("2019-01-01", "2024-01-01")            # out-of-sample (A, executable bid/ask)
HOLDOUT = ("2024-01-01", "2026-09-01")        # final untouched holdout (A)
SEAM = "2016-09-01"                           # B -> A switch in the stitched research series
WARMUP_DAYS = 400


@lru_cache(maxsize=None)
def load(source: str, tf: str) -> pd.DataFrame:
    return pd.read_parquet(os.path.join(PROC, f"{source}_{tf}.parquet"))


@lru_cache(maxsize=None)
def stitched(tf: str) -> pd.DataFrame:
    """B before SEAM, A from SEAM onwards. The source is kept in the ``source`` column."""
    a = load("A", tf)
    b = load("B", tf)
    cols = ["open_bid", "high_bid", "low_bid", "close_bid", "open_ask", "high_ask", "low_ask", "close_ask", "volume", "source"]
    b = b[b.index < SEAM][cols]
    a = a[a.index >= SEAM][cols]
    return pd.concat([b, a]).sort_index()


@lru_cache(maxsize=None)
def macro() -> pd.DataFrame:
    return pd.read_parquet(os.path.join(PROC, "macro_daily.parquet"))


@lru_cache(maxsize=None)
def rate_curve() -> RateCurve:
    return RateCurve(macro()["ust_3m"].ffill())


def bars_for(tf: str, source: str = "stitched") -> pd.DataFrame:
    if source == "stitched":
        return stitched(tf)
    return load(source, tf)


def window_with_warmup(df: pd.DataFrame, start: str, end: str, warmup_days: int = WARMUP_DAYS) -> pd.DataFrame:
    s = pd.Timestamp(start) - pd.Timedelta(days=warmup_days)
    return df[(df.index >= s) & (df.index < pd.Timestamp(end))]


_FEATURE_CACHE: dict = {}


def run(strategies: Sequence, start: str, end: str, source: str = "stitched", base_tf: Optional[str] = None,
        cost: Optional[CostModel] = None, risk: Optional[RiskConfig] = None, delay_bars: int = 0,
        initial: float = 100_000.0) -> BacktestResult:
    tfs = {s.timeframe for s in strategies}
    if base_tf is None:
        base_tf = "M30" if "M30" in tfs else "H1"
    base = window_with_warmup(bars_for(base_tf, source), start, end)
    tf_bars = {tf: window_with_warmup(bars_for(tf, source), start, end) for tf in tfs if tf != base_tf}
    risk = risk or RiskConfig(enforce_loss_limits=False, max_open_risk=1.0, max_gross_notional_x_equity=50.0,
                              max_spread_bps=1e9)
    return run_backtest(strategies, base, base_tf=base_tf, tf_bars=tf_bars, cost=cost or CostModel(),
                        rates=rate_curve(), risk_config=risk, initial=initial, delay_bars=delay_bars,
                        start=start, end=end, features_cache=_FEATURE_CACHE)


def fmt_table(rows: list[dict], cols: list[str], floatfmt: str = "{:.3f}") -> str:
    head = "| " + " | ".join(cols) + " |\n|" + "|".join(["---"] * len(cols)) + "|\n"
    body = ""
    for r in rows:
        vals = []
        for c in cols:
            v = r.get(c, "")
            if isinstance(v, (float, np.floating)):
                vals.append("—" if np.isnan(v) else floatfmt.format(v))
            else:
                vals.append(str(v))
        body += "| " + " | ".join(vals) + " |\n"
    return head + body


def save_json(name: str, obj) -> None:
    with open(os.path.join(RESULTS, name), "w") as f:
        json.dump(obj, f, indent=2, default=lambda x: None if isinstance(x, float) and np.isnan(x) else str(x))
