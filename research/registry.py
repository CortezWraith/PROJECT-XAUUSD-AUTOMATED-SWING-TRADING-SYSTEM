"""Strategies under full validation, with their declared grids (see PROTOCOL.md / DEV_SELECTION.md)."""
from __future__ import annotations

import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import macro  # noqa: E402

from tradingsystem.strategies.breakout import SqueezeBreakout  # noqa: E402
from tradingsystem.strategies.session import AsiaLondonSession  # noqa: E402
from tradingsystem.strategies.trend import DonchianBreakout, EmaTrend, MacroFilteredDonchian  # noqa: E402

# bins per server day for each timeframe (bars anchored at server midnight)
BINS_PER_DAY = {"H1": 24, "H2": 12, "H3": 8, "H4": 6, "H6": 4, "D1": 1}


def _grid(**axes):
    keys = list(axes)
    return [dict(zip(keys, v)) for v in itertools.product(*axes.values())]


SPECS = {
    "C5": dict(name="C5 squeeze_h4", cls=SqueezeBreakout, tf="H4",
               scale=["bb_n", "rank_n", "lookback", "atr_n", "max_hold"],
               grid=_grid(bb_n=[15, 17, 20, 23, 25], squeeze_pct=[0.15, 0.175, 0.2, 0.225, 0.25], stop_atr=[1.5, 1.75, 2.0, 2.25, 2.5]),
               oat={"rank_n": [90, 105, 120, 135, 150], "max_hold": [22, 26, 30, 34, 38]},
               wf=_grid(bb_n=[15, 20, 25], squeeze_pct=[0.15, 0.2, 0.25]),
               tfs=["H2", "H3", "H4", "H6"]),
    "C9": dict(name="C9 donchian_usd_h4", cls=MacroFilteredDonchian, tf="H4", needs_macro=True,
               scale=["entry_n", "exit_n", "atr_n", "max_hold"],
               grid=_grid(entry_n=[41, 47, 55, 63, 69], exit_n=[15, 17, 20, 23, 25], stop_atr=[1.5, 1.75, 2.0, 2.25, 2.5]),
               oat={"usd_ma": [38, 44, 50, 56, 63]},
               wf=_grid(entry_n=[41, 55, 69], exit_n=[15, 20, 25]),
               tfs=["H2", "H3", "H4", "H6", "D1"]),
    "C3": dict(name="C3 ema_trend_h4", cls=EmaTrend, tf="H4",
               scale=["fast", "slow", "atr_n"],
               grid=_grid(fast=[15, 17, 20, 23, 25], slow=[75, 85, 100, 115, 125], stop_atr=[2.25, 2.625, 3.0, 3.375, 3.75]),
               oat={},
               wf=_grid(fast=[15, 20, 25], slow=[75, 100, 125]),
               tfs=["H2", "H3", "H4", "H6", "D1"]),
    "C2": dict(name="C2 donchian_h4 (reference)", cls=DonchianBreakout, tf="H4",
               scale=["entry_n", "exit_n", "atr_n", "max_hold"],
               grid=_grid(entry_n=[41, 47, 55, 63, 69], exit_n=[15, 17, 20, 23, 25], stop_atr=[1.5, 1.75, 2.0, 2.25, 2.5]),
               oat={},
               wf=_grid(entry_n=[41, 55, 69], exit_n=[15, 20, 25]),
               tfs=["H2", "H3", "H4", "H6", "D1"]),
    "C8b": dict(name="C8b session_asia_london_h1 (cost-conditional)", cls=AsiaLondonSession, tf="H1",
                scale=[],
                grid=_grid(long_entry_hour=[1, 2, 3], long_exit_hour=[8, 9, 10]) + _grid(short_entry_hour=[8, 9, 10], short_exit_hour=[14, 15, 16]),
                oat={"stop_atr": [0.75, 1.0, 1.25, 1.5]},
                wf=[],
                tfs=["M30", "H1"]),
}


def make(key: str, tf: str | None = None, **overrides):
    spec = SPECS[key]
    params = dict(overrides)
    base_tf = spec["tf"]
    if tf and tf != base_tf and spec["scale"]:
        f = BINS_PER_DAY[tf] / BINS_PER_DAY[base_tf]
        defaults = spec["cls"].Params()
        for p in spec["scale"]:
            v = params.get(p, getattr(defaults, p))
            params[p] = max(2, int(round(v * f)))
    kw = dict(params)
    if spec.get("needs_macro"):
        s = spec["cls"](macro=macro(), **kw)
    else:
        s = spec["cls"](**kw)
    if tf and tf != base_tf and key != "C8b":
        s.timeframe = tf
    return s
