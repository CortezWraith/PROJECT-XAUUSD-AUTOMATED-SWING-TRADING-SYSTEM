"""Step 4: the final holdout 2024-01-01 .. 2026-08-31, run ONCE with the frozen spec.

Nothing in tradingsystem/ or research/registry.py may change after this script has been run.
"""
from __future__ import annotations

import json
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HOLDOUT, RESULTS, fmt_table, run  # noqa: E402
from registry import SPECS, make  # noqa: E402

from tradingsystem.backtest.metrics import daily_returns, summarize, yearly_table  # noqa: E402
from tradingsystem.costs.model import CostModel  # noqa: E402
from tradingsystem.risk.manager import RiskConfig  # noqa: E402

COLS = ["label", "trades", "trades_per_year", "win_rate", "expectancy_r", "expectancy_r_t", "profit_factor", "sharpe",
        "cagr", "max_dd", "avg_hold_hours", "long_expectancy_r", "short_expectancy_r", "gross_pnl", "net_pnl"]


def main() -> None:
    with open(os.path.join(RESULTS, "..", "frozen_spec.json")) as f:
        frozen = json.load(f)
    rows, out = [], {}
    for k in ("C3", "C2", "C5", "C9", "C8b"):
        for lab, kw, cost in (("baseline", {}, CostModel()), ("x1.5", {}, CostModel(multiplier=1.5)),
                              ("x2.0", {}, CostModel(multiplier=2.0)),
                              ("long-only", {"allow_short": False}, CostModel()),
                              ("short-only", {"allow_long": False}, CostModel())):
            s = make(k, **kw)
            cur = json.loads(json.dumps(s.describe()["params"], default=str))
            ref = frozen["strategies"][k]["params"]
            assert all(cur[kk] == vv for kk, vv in ref.items() if kk not in ("allow_long", "allow_short")), k
            res = run([s], *HOLDOUT, source="A", cost=cost)
            r = summarize(res, f"{SPECS[k]['name']} — {lab}")
            rows.append(r)
            out[f"{k} {lab}"] = r
            if lab == "baseline":
                with open(os.path.join(RESULTS, "cache", f"{k}_holdout.pkl"), "wb") as f:
                    pickle.dump({"trades": res.trades, "daily": daily_returns(res.equity)}, f)
    p = frozen["portfolio"]
    strategies = [make(k) for k in ("C3", "C2", "C5")]
    rc = RiskConfig(risk_per_trade=p["risk_per_trade"], strategy_risk_weights=p["strategy_risk_weights"],
                    max_open_risk=p["max_open_risk"], max_daily_loss=p["max_daily_loss"], max_weekly_loss=p["max_weekly_loss"],
                    strategy_dd_stop=p["strategy_dd_stop"], portfolio_dd_stop=p["portfolio_dd_stop"])
    res = run(strategies, *HOLDOUT, source="A", risk=rc)
    pr = summarize(res, "PORTFOLIO C3+C2+C5 (weights 1/3, limits ON)")
    rows.append(pr)
    out["portfolio"] = pr
    out["portfolio_meta"] = res.meta
    yt = yearly_table(res)
    md = "# FINAL HOLDOUT 2024-01-01 .. 2026-08-31 (dataset A, run once with the frozen spec)\n\n" + fmt_table(rows, COLS)
    md += "\n\n## Portfolio by year\n" + fmt_table(yt.reset_index().rename(columns={"index": "year"}).to_dict("records"),
                                                   ["year", "return", "trades", "win_rate", "exp_r", "pf", "long_pnl", "short_pnl"])
    md += f"\n\nportfolio meta: {res.meta}\n"
    with open(os.path.join(RESULTS, "s04_holdout.md"), "w") as f:
        f.write(md)
    with open(os.path.join(RESULTS, "s04_holdout.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(md)


if __name__ == "__main__":
    main()
