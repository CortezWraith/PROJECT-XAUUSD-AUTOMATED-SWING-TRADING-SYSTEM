"""Step 3: cross-strategy complementarity and the combined portfolio (DEV+OOS, holdout untouched).

Usage: python research/s03_portfolio.py C3 C2 C8b   (keys of the final candidates)
"""
from __future__ import annotations

import json
import math
import os
import pickle
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DEV, OOS, RESULTS, bars_for, fmt_table, macro, run  # noqa: E402
from registry import SPECS, make  # noqa: E402
from stats import regime_frame  # noqa: E402

from tradingsystem.backtest.metrics import daily_returns, summarize, yearly_table  # noqa: E402
from tradingsystem.risk.manager import RiskConfig  # noqa: E402

FULL = (DEV[0], OOS[1])
CACHE = os.path.join(RESULTS, "cache")


def position_series(trades: pd.DataFrame, index: pd.DatetimeIndex) -> pd.Series:
    """+1 / -1 / 0 per hourly timestamp from trade entry/exit times."""
    pos = pd.Series(0.0, index=index)
    for _, t in trades.iterrows():
        m = (index >= pd.Timestamp(t["entry_time"])) & (index < pd.Timestamp(t["exit_time"]))
        pos[m] = t["side"]
    return pos


def drawdown(d: pd.Series) -> pd.Series:
    eq = (1 + d).cumprod()
    return eq / eq.cummax() - 1


def main(keys: list[str]) -> dict:
    data = {}
    for k in keys:
        with open(os.path.join(CACHE, f"{k}_full.pkl"), "rb") as f:
            data[k] = pickle.load(f)
    names = {k: SPECS[k]["name"] for k in keys}
    out: dict = {"keys": keys}
    md = ["# Cross-strategy complementarity (DEV+OOS 2010-2023)\n"]

    # daily return correlation
    D = pd.DataFrame({k: data[k]["daily"] for k in keys}).fillna(0.0)
    corr = D.corr()
    out["daily_corr"] = corr.round(3).to_dict()
    md.append("## Daily return correlation\n" + corr.round(2).to_markdown() if hasattr(corr, "to_markdown") else str(corr.round(2)))

    # positions on an hourly grid
    idx = bars_for("H1").loc[FULL[0]:FULL[1]].index
    P = pd.DataFrame({k: position_series(data[k]["trades"], idx) for k in keys})
    rows = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            both = (P[a] != 0) & (P[b] != 0)
            same = both & (np.sign(P[a]) == np.sign(P[b]))
            opp = both & (np.sign(P[a]) != np.sign(P[b]))
            in_a = (P[a] != 0).mean()
            in_b = (P[b] != 0).mean()
            ddA, ddB = drawdown(D[a]), drawdown(D[b])
            deepA, deepB = ddA < ddA.quantile(0.2), ddB < ddB.quantile(0.2)
            rows.append({"pair": f"{a} / {b}", "corr_daily": float(corr.loc[a, b]),
                         "time_in_market_a": in_a, "time_in_market_b": in_b,
                         "overlap_share_of_time": float(both.mean()),
                         "overlap_expected_if_indep": float(in_a * in_b),
                         "same_direction_share_of_overlap": float(same.sum() / max(both.sum(), 1)),
                         "opposite_direction_share_of_overlap": float(opp.sum() / max(both.sum(), 1)),
                         "drawdown_corr": float(ddA.corr(ddB)),
                         "joint_deep_dd_share": float((deepA & deepB).mean()),
                         "joint_deep_dd_if_indep": float(deepA.mean() * deepB.mean())})
    out["pairs"] = rows
    md.append("## Pairwise overlap\n" + fmt_table(rows, list(rows[0].keys())))
    net = P.sum(axis=1)
    out["net_direction"] = {"all_long_share": float((P > 0).all(axis=1).mean()), "all_short_share": float((P < 0).all(axis=1).mean()),
                            "any_position_share": float((P != 0).any(axis=1).mean()),
                            "max_simultaneous_same_direction": int(max((P > 0).sum(axis=1).max(), (P < 0).sum(axis=1).max()))}
    md.append("## Simultaneous directional exposure\n" + json.dumps(out["net_direction"], indent=1))

    # regime overlap: expectancy per regime per strategy
    reg = regime_frame(bars_for("D1"), macro())
    rr = []
    for k in keys:
        t = data[k]["trades"].copy()
        t["day"] = pd.to_datetime(t["entry_time"]).dt.normalize()
        t = t.join(reg, on="day")
        for col in ("trend", "vol", "usd", "rates", "crisis"):
            for lab, g in t.groupby(col):
                rr.append({"strategy": k, "regime": col, "state": lab, "trades": len(g), "exp_r": g["r"].mean()})
    R = pd.DataFrame(rr).pivot_table(index=["regime", "state"], columns="strategy", values="exp_r")
    out["regime_exp_r"] = R.round(3).reset_index().to_dict("records")
    md.append("## Regime overlap (expectancy in R by regime)\n" + fmt_table(R.reset_index().to_dict("records"), ["regime", "state"] + keys))

    # combined portfolio through the full engine with production risk limits
    strategies = [make(k) for k in keys]
    # one risk budget for one economic bet: weights 1/n so that the family risks ~0.5% when all agree
    w = {make(k).strategy_id: 1.0 / len(keys) for k in keys}
    rc = RiskConfig(strategy_risk_weights=w)          # production limits ON (incl. 15% DD kill switch)
    res = run(strategies, *FULL, risk=rc)
    s = summarize(res, f"portfolio, weights 1/{len(keys)}, limits ON")
    res_full = run(strategies, *FULL, risk=RiskConfig())
    s_full = summarize(res_full, "portfolio, 0.5% each, limits ON")
    res_off = run(strategies, *FULL)
    s_off = summarize(res_off, "portfolio, 0.5% each, limits OFF")
    out["portfolio_full_weights"] = s_full
    out["portfolio_full_weights_meta"] = res_full.meta
    out["portfolio"] = s
    out["portfolio_no_limits"] = s_off
    out["portfolio_meta"] = res.meta
    dec = res.decisions
    rej = dec[~dec["approved"]]["reason"].str.replace(r"spread .* too wide", "spread too wide", regex=True).value_counts().to_dict() if len(dec) else {}
    out["risk_rejections"] = rej
    md.append("## Combined portfolio\n" + fmt_table([s, s_full, s_off], ["label", "trades", "expectancy_r", "profit_factor", "sharpe", "sortino", "cagr", "max_dd", "calmar", "exposure", "longest_underwater_days"])
              + f"\nrisk-manager rejections (weighted run): {rej}\nmeta (weighted run): {res.meta}\nmeta (0.5% each, limits ON): {res_full.meta}\n")
    yt = yearly_table(res)
    md.append("### Portfolio by year\n" + fmt_table(yt.reset_index().rename(columns={"index": "year"}).to_dict("records"), ["year", "return", "trades", "win_rate", "exp_r", "pf"]))
    with open(os.path.join(RESULTS, "s03_portfolio.md"), "w") as f:
        f.write("\n\n".join(md))
    with open(os.path.join(RESULTS, "s03_portfolio.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    with open(os.path.join(CACHE, "portfolio_full.pkl"), "wb") as f:
        pickle.dump({"equity": res.equity, "trades": res.trades}, f)
    print("\n\n".join(md)[:6000])
    return out


if __name__ == "__main__":
    main(sys.argv[1:] or ["C3", "C2", "C8b"])
