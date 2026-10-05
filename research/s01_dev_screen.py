"""Step 1: development-period screen of the full candidate universe (2010-2018 only).

Also: cross-source consistency check (dataset A vs B) on the DEV overlap 2016-09..2018-12.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DEV, RESULTS, fmt_table, macro, run, save_json  # noqa: E402

from tradingsystem.backtest.metrics import summarize  # noqa: E402
from tradingsystem.costs.model import CostModel  # noqa: E402
from tradingsystem.strategies.breakout import SqueezeBreakout, VolatilityBreakout  # noqa: E402
from tradingsystem.strategies.meanrev import RangeZScoreReversion, TrendPullbackRSI  # noqa: E402
from tradingsystem.strategies.session import AsiaLondonSession, SessionDrift  # noqa: E402
from tradingsystem.strategies.trend import DonchianBreakout, EmaTrend, MacroFilteredDonchian, TimeSeriesMomentum  # noqa: E402


def candidates():
    return {
        "C1 tsmom_d1": lambda **k: TimeSeriesMomentum(**k),
        "C2 donchian_h4 *": lambda **k: DonchianBreakout(**k),
        "C3 ema_trend_h4": lambda **k: EmaTrend(**k),
        "C4 volbreak_d1": lambda **k: VolatilityBreakout(**k),
        "C5 squeeze_h4": lambda **k: SqueezeBreakout(**k),
        "C6 rsi2_pullback_d1 *": lambda **k: TrendPullbackRSI(**k),
        "C7 zscore_mr_h1": lambda **k: RangeZScoreReversion(**k),
        "C8 session_drift_h1 *": lambda **k: SessionDrift(**k),
        "C9 donchian_usd_h4": lambda **k: MacroFilteredDonchian(macro=macro(), **k),
        # added after the first DEV screen (data-driven revision of C8, see session.py)
        "C8b session_asia_london_h1 (DEV-derived)": lambda **k: AsiaLondonSession(**k),
    }


COLS = ["label", "trades", "trades_per_year", "win_rate", "expectancy_r", "expectancy_r_t", "profit_factor",
        "sharpe", "cagr", "max_dd", "avg_hold_hours", "long_expectancy_r", "short_expectancy_r", "gross_r", "net_pnl", "gross_pnl"]


def main() -> None:
    rows, frictionless, sides, xsrc = [], [], [], []
    for name, mk in candidates().items():
        t = time.time()
        res = run([mk()], *DEV)
        s = summarize(res, name)
        g = run([mk()], *DEV, cost=CostModel().frictionless())
        sg = summarize(g, name)
        s["gross_r"] = sg.get("expectancy_r", float("nan"))
        rows.append(s)
        frictionless.append(sg)
        for side, kw in (("long-only", {"allow_short": False}), ("short-only", {"allow_long": False})):
            r2 = summarize(run([mk(**kw)], *DEV), f"{name} {side}")
            sides.append(r2)
        # cross-source check on the DEV overlap (no OOS data touched)
        for src in ("A", "B"):
            xsrc.append(summarize(run([mk()], "2016-09-01", "2019-01-01", source=src), f"{name} [{src}]"))
        print(f"{name}: {s['trades']} trades, expR={s.get('expectancy_r', float('nan')):.3f}, PF={s.get('profit_factor', float('nan')):.2f} ({time.time() - t:.0f}s)")

    md = "## DEV screen 2010-01-01 .. 2018-12-31 (baseline costs; * = pre-selected)\n\n" + fmt_table(rows, COLS)
    md += "\n\n## Long-only / short-only (DEV, baseline costs)\n\n" + fmt_table(sides, ["label", "trades", "win_rate", "expectancy_r", "expectancy_r_t", "profit_factor", "sharpe", "net_pnl"])
    md += "\n\n## Cross-source consistency, 2016-09 .. 2018-12 (A = Dukascopy bid/ask, B = MT4 bid + modelled ask)\n\n" + fmt_table(xsrc, ["label", "trades", "win_rate", "expectancy_r", "profit_factor", "net_pnl"])
    with open(os.path.join(RESULTS, "s01_dev_screen.md"), "w") as f:
        f.write(md)
    save_json("s01_dev_screen.json", {"baseline": rows, "frictionless": frictionless, "sides": sides, "cross_source": xsrc})
    print(md)


if __name__ == "__main__":
    main()
