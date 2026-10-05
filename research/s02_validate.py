"""Step 2: full validation of the DEV-selected strategies (OOS 2019-2023 is evaluated here;
the 2024-2026 holdout is NOT touched by this script).

Usage: python research/s02_validate.py [C5 C9 C3 C2 C8b]
"""
from __future__ import annotations

import json
import math
import os
import pickle
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DEV, OOS, PRE_SAMPLE, RESULTS, bars_for, fmt_table, macro, run  # noqa: E402
from registry import SPECS, make  # noqa: E402
from stats import block_bootstrap_daily, deflated_sharpe, pbo_cscv, regime_frame, trade_bootstrap  # noqa: E402

from tradingsystem.backtest.metrics import daily_returns, summarize, yearly_table  # noqa: E402
from tradingsystem.costs.model import CostModel  # noqa: E402

FULL = (DEV[0], OOS[1])           # 2010-01-01 .. 2023-12-31
N_TRIALS = 60
CACHE = os.path.join(RESULTS, "cache")
os.makedirs(CACHE, exist_ok=True)

SUM_COLS = ["label", "trades", "trades_per_year", "win_rate", "avg_win_r", "avg_loss_r", "expectancy_r",
            "expectancy_r_t", "profit_factor", "sharpe", "sortino", "cagr", "max_dd", "calmar", "exposure",
            "avg_hold_hours", "longest_losing_streak", "longest_underwater_days"]


def _job(args):
    key, tf, overrides, start, end, source, cost_kw, delay, label = args
    s = make(key, tf=tf, **overrides)
    if key == "C8b" and tf:
        s.timeframe = tf
    cost = CostModel(**cost_kw) if cost_kw is not None else CostModel()
    res = run([s], start, end, source=source, cost=cost, delay_bars=delay)
    out = summarize(res, label)
    dr = daily_returns(res.equity)
    return label, out, dr, res.trades


def pmap(jobs, procs=4):
    with Pool(procs) as p:
        return p.map(_job, jobs, chunksize=1)


def gates(dev, oos, full15, perturb_pos_share, wf_total, max_year_share, boot_p) -> dict:
    g = {
        "1 DEV exp>0 & PF>1.10": dev.get("expectancy_r", -1) > 0 and dev.get("profit_factor", 0) > 1.10,
        "2 OOS exp>0, PF>1.05, Sharpe>0.3": oos.get("expectancy_r", -1) > 0 and oos.get("profit_factor", 0) > 1.05 and oos.get("sharpe", 0) > 0.3,
        "3 costs x1.5 exp>0 (DEV+OOS)": full15.get("expectancy_r", -1) > 0,
        "4 >=70% neighbours exp>0": perturb_pos_share >= 0.70,
        "5 walk-forward OOS > 0": None if wf_total is None else wf_total > 0,
        "6 no year > 50% of net profit": max_year_share <= 0.50,
        "7 bootstrap P(exp>0) >= 90%": boot_p >= 0.90,
    }
    g["ALL"] = all(v for v in g.values() if v is not None)
    return g


def validate(key: str) -> dict:
    spec = SPECS[key]
    name = spec["name"]
    t0 = time.time()
    out: dict = {"key": key, "name": name}
    md = [f"# {name}\n"]

    # ------------------------------------------------------------ A. baseline segments
    jobs = [(key, None, {}, *seg, "stitched", None, 0, lab) for lab, seg in
            (("PRE-SAMPLE 2004-09 (B)", PRE_SAMPLE), ("DEV 2010-18", DEV), ("OOS 2019-23", OOS), ("DEV+OOS 2010-23", FULL))]
    # B. long / short
    for side, kw in (("long", {"allow_short": False}), ("short", {"allow_long": False})):
        if key == "C8b":
            kw = {"allow_short": False} if side == "long" else {"allow_long": False}
        for lab, seg in (("DEV", DEV), ("OOS", OOS), ("DEV+OOS", FULL)):
            jobs.append((key, None, kw, *seg, "stitched", None, 0, f"{side} {lab}"))
    # C. costs
    cost_cases = {"gross (x0)": dict(multiplier=0.0, swap_enabled=False), "x1.0": {}, "x1.5": dict(multiplier=1.5),
                  "x2.0": dict(multiplier=2.0), "ECN scenario (x0.5 + 3.5 USD/lot/side)": dict(multiplier=0.5, commission_per_lot_side=7.0)}
    # note: commission is also scaled by the multiplier -> 7.0 * 0.5 = 3.5 USD per lot per side
    for lab, kw in cost_cases.items():
        jobs.append((key, None, {}, *FULL, "stitched", kw, 0, f"cost {lab} DEV+OOS"))
        jobs.append((key, None, {}, *OOS, "stitched", kw, 0, f"cost {lab} OOS"))
    # D. entry delay
    jobs.append((key, None, {}, *FULL, "stitched", None, 1, "delay +1 bar"))
    jobs.append((key, None, {}, *FULL, "stitched", dict(slippage_bps_market=0.9, slippage_bps_stop=3.0), 1, "delay +1 bar & slippage x3"))
    res_a = pmap(jobs)
    seg = {lab: s for lab, s, _, _ in res_a}
    trades_full = next(t for lab, _, _, t in res_a if lab == "DEV+OOS 2010-23")
    daily_full = next(d for lab, _, d, _ in res_a if lab == "DEV+OOS 2010-23")
    out["segments"] = seg
    md.append("## Segments (baseline costs)\n" + fmt_table([seg[k] for k in ("PRE-SAMPLE 2004-09 (B)", "DEV 2010-18", "OOS 2019-23", "DEV+OOS 2010-23")], SUM_COLS))
    md.append("## Long vs short\n" + fmt_table([seg[f"{sd} {lab}"] for sd in ("long", "short") for lab in ("DEV", "OOS", "DEV+OOS")],
                                              ["label", "trades", "win_rate", "expectancy_r", "expectancy_r_t", "profit_factor", "sharpe", "net_return_pct_initial"]))
    md.append("## Cost stress\n" + fmt_table([seg[f"cost {lab} {p}"] for lab in cost_cases for p in ("DEV+OOS", "OOS")],
                                            ["label", "trades", "expectancy_r", "profit_factor", "sharpe", "cagr", "max_dd", "gross_pnl", "net_pnl", "cost_spread", "cost_slippage", "cost_commission", "swap"]))
    md.append("## Entry delay\n" + fmt_table([seg["DEV+OOS 2010-23"], seg["delay +1 bar"], seg["delay +1 bar & slippage x3"]],
                                            ["label", "trades", "expectancy_r", "profit_factor", "sharpe", "cagr", "max_dd"]))

    # ------------------------------------------------------------ E. parameter perturbation (+ PBO)
    gjobs = [(key, None, g, *FULL, "stitched", None, 0, json.dumps(g)) for g in spec["grid"]]
    for p, vals in spec["oat"].items():
        for v in vals:
            gjobs.append((key, None, {p: v}, *FULL, "stitched", None, 0, json.dumps({p: v, "oat": True})))
    res_g = pmap(gjobs)
    grid_rows = []
    yearly = {}
    for lab, s, d, tr in res_g:
        cfg = json.loads(lab)
        row = dict(cfg)
        row.update({k: s.get(k) for k in ("trades", "expectancy_r", "profit_factor", "sharpe", "cagr", "max_dd")})
        grid_rows.append(row)
        if not cfg.get("oat"):
            yearly[lab] = d.groupby(d.index.year).apply(lambda x: (1 + x).prod() - 1)
    gdf = pd.DataFrame(grid_rows)
    main = gdf[gdf.get("oat").isna()] if "oat" in gdf else gdf
    pos_share = float((main["expectancy_r"] > 0).mean())
    M = pd.DataFrame(yearly).fillna(0.0)
    pbo = pbo_cscv(M) if M.shape[1] > 2 else {"pbo": float("nan")}
    out["perturbation"] = {"n": int(len(main)), "share_exp_positive": pos_share, "share_pf_gt_1": float((main["profit_factor"] > 1).mean()),
                           "sharpe_p10": float(main["sharpe"].quantile(0.1)), "sharpe_median": float(main["sharpe"].median()),
                           "sharpe_p90": float(main["sharpe"].quantile(0.9)), "pbo": pbo}
    gdf.to_csv(os.path.join(RESULTS, f"grid_{key}.csv"), index=False)
    md.append(f"## Parameter perturbation (DEV+OOS, {len(main)} grid points)\n"
              f"share with expectancy > 0: **{pos_share:.0%}**, share PF > 1: {out['perturbation']['share_pf_gt_1']:.0%}, "
              f"Sharpe p10/median/p90: {out['perturbation']['sharpe_p10']:.2f} / {out['perturbation']['sharpe_median']:.2f} / {out['perturbation']['sharpe_p90']:.2f}; "
              f"PBO (CSCV, yearly blocks): {pbo.get('pbo', float('nan')):.2f}\n")
    # marginal effect of each grid axis
    axes = [c for c in spec["grid"][0]] if spec["grid"] else []
    axes = sorted({k for g in spec["grid"] for k in g}, key=lambda k: list(spec["grid"][0]).index(k) if k in spec["grid"][0] else 99)
    for ax in axes:
        if ax not in main or main[ax].isna().all():
            continue
        m = main.groupby(ax)[["expectancy_r", "profit_factor", "sharpe"]].median().reset_index()
        md.append(f"Median by `{ax}`:\n" + fmt_table(m.to_dict("records"), [ax, "expectancy_r", "profit_factor", "sharpe"]))
    if spec["oat"]:
        o = gdf[gdf.get("oat") == True]  # noqa: E712
        md.append("One-at-a-time:\n" + fmt_table(o.to_dict("records"), [c for c in o.columns if c != "oat"]))

    # ------------------------------------------------------------ F. timeframe robustness
    tjobs = []
    for tf in spec["tfs"]:
        if key == "C8b":
            tjobs.append((key, tf, {}, "2016-09-01", OOS[1], "A", None, 0, f"{tf} (A 2016-09..2023)"))
            if tf == "M30":
                for off in (-30, 30):
                    tjobs.append((key, tf, {"offset_minutes": off}, "2016-09-01", OOS[1], "A", None, 0, f"M30 shift {off:+d} min (A)"))
        else:
            tjobs.append((key, tf, {}, *FULL, "stitched", None, 0, f"{tf}"))
    res_t = pmap(tjobs)
    out["timeframes"] = {lab: s for lab, s, _, _ in res_t}
    md.append("## Timeframe robustness (lookbacks scaled to equal clock time)\n" + fmt_table([s for _, s, _, _ in res_t],
              ["label", "trades", "expectancy_r", "expectancy_r_t", "profit_factor", "sharpe", "cagr", "max_dd", "avg_hold_hours"]))

    # ------------------------------------------------------------ G. walk-forward (3x3 grid, 4y train -> 1y test)
    wf_total = None
    if spec["wf"]:
        base = SPECS[key]["cls"].Params()
        def cfg_label(g):
            full = {k: getattr(base, k) for k in spec["grid"][0]}
            full.update(g)
            return json.dumps({k: full[k] for k in spec["grid"][0]})
        labels = [cfg_label(g) for g in spec["wf"]]
        daily = {lab: d for lab, _, d, _ in res_g if lab in labels}
        rows, pieces = [], []
        for test_year in range(2014, 2024):
            tr0, tr1 = pd.Timestamp(f"{test_year - 4}-01-01"), pd.Timestamp(f"{test_year}-01-01")
            best, best_sr = None, -np.inf
            for lab in labels:
                d = daily[lab]
                x = d[(d.index >= tr0) & (d.index < tr1)]
                sr = x.mean() / x.std() * math.sqrt(252) if x.std() > 0 else -np.inf
                if sr > best_sr:
                    best, best_sr = lab, sr
            d = daily[best]
            te = d[(d.index >= tr1) & (d.index < pd.Timestamp(f"{test_year + 1}-01-01"))]
            dflt = daily[cfg_label({})] if cfg_label({}) in daily else None
            te_def = dflt[(dflt.index >= tr1) & (dflt.index < pd.Timestamp(f"{test_year + 1}-01-01"))] if dflt is not None else None
            pieces.append(te)
            rows.append({"test_year": test_year, "chosen": best, "train_sharpe": best_sr,
                         "test_return": float((1 + te).prod() - 1),
                         "default_return": float((1 + te_def).prod() - 1) if te_def is not None else float("nan")})
        wf = pd.concat(pieces)
        wf_total = float((1 + wf).prod() - 1)
        wf_sr = float(wf.mean() / wf.std() * math.sqrt(252)) if wf.std() > 0 else float("nan")
        out["walk_forward"] = {"total_return": wf_total, "sharpe": wf_sr, "folds": rows,
                               "positive_folds": int(sum(r["test_return"] > 0 for r in rows))}
        md.append(f"## Walk-forward (4y train / 1y test, 2014-2023)\nconcatenated OOS return **{wf_total:.1%}**, Sharpe {wf_sr:.2f}, "
                  f"positive folds {out['walk_forward']['positive_folds']}/10\n" + fmt_table(rows, ["test_year", "chosen", "train_sharpe", "test_return", "default_return"]))

    # ------------------------------------------------------------ H. bootstrap
    years = (pd.Timestamp(FULL[1]) - pd.Timestamp(FULL[0])).days / 365.25
    r = trades_full["r"].dropna().values
    tb = trade_bootstrap(r, years, n=10_000 if len(r) < 2000 else 2_000)
    bb = block_bootstrap_daily(daily_full)
    out["bootstrap"] = {"trades": tb, "daily_block": bb}
    rows = [{"metric": k, **v} for k, v in tb.items() if isinstance(v, dict)]
    md.append(f"## Bootstrap (DEV+OOS)\nTrade bootstrap (risk 0.5%/trade): P(expectancy > 0) = **{tb['prob_expectancy_positive']:.1%}**\n"
              + fmt_table(rows, ["metric", "p05", "p50", "p95"])
              + f"\nBlock bootstrap of daily returns (20-day blocks): Sharpe p05/p50/p95 = {bb['sharpe']['p05']:.2f} / {bb['sharpe']['p50']:.2f} / {bb['sharpe']['p95']:.2f}; "
              f"CAGR {bb['cagr']['p05']:.2%} / {bb['cagr']['p50']:.2%} / {bb['cagr']['p95']:.2%}; MaxDD {bb['max_dd']['p05']:.1%} / {bb['max_dd']['p50']:.1%} / {bb['max_dd']['p95']:.1%}; "
              f"P(Sharpe>0) {bb['prob_sharpe_positive']:.1%}\n")

    # ------------------------------------------------------------ I. regimes
    reg = regime_frame(bars_for("D1"), macro())
    t = trades_full.copy()
    t["day"] = pd.to_datetime(t["entry_time"]).dt.normalize()
    t = t.join(reg, on="day")
    rrows = []
    for col in ("trend", "vol", "usd", "rates", "crisis"):
        for lab, g in t.groupby(col):
            d = daily_full[daily_full.index.isin(reg.index[reg[col] == lab])]
            rrows.append({"regime": col, "state": lab, "trades": len(g), "expectancy_r": g["r"].mean(),
                          "win_rate": (g["pnl_net"] > 0).mean(),
                          "pf": g.loc[g.pnl_net > 0, "pnl_net"].sum() / max(-g.loc[g.pnl_net <= 0, "pnl_net"].sum(), 1e-9),
                          "long_exp_r": g.loc[g.side == 1, "r"].mean(), "short_exp_r": g.loc[g.side == -1, "r"].mean(),
                          "daily_sharpe": d.mean() / d.std() * math.sqrt(252) if len(d) > 20 and d.std() > 0 else float("nan")})
    out["regimes"] = rrows
    md.append("## Regimes (ex-ante labels; DEV+OOS)\n" + fmt_table(rrows, ["regime", "state", "trades", "expectancy_r", "win_rate", "pf", "long_exp_r", "short_exp_r", "daily_sharpe"]))

    # ------------------------------------------------------------ J. sub-periods
    t = trades_full.copy()
    t["year"] = pd.to_datetime(t["exit_time"]).dt.year
    yr = t.groupby("year").agg(trades=("r", "size"), exp_r=("r", "mean"), net=("pnl_net", "sum"),
                               long_net=("pnl_net", lambda x: x[t.loc[x.index, "side"] == 1].sum()),
                               short_net=("pnl_net", lambda x: x[t.loc[x.index, "side"] == -1].sum())).reset_index()
    total = yr["net"].sum()
    max_share = float(yr["net"].max() / total) if total > 0 else float("inf")
    blocks = []
    for a, b in ((2010, 2012), (2013, 2015), (2016, 2018), (2019, 2021), (2022, 2023)):
        g = t[(t.year >= a) & (t.year <= b)]
        blocks.append({"block": f"{a}-{b}", "trades": len(g), "exp_r": g["r"].mean(), "net": g["pnl_net"].sum(),
                       "pf": g.loc[g.pnl_net > 0, "pnl_net"].sum() / max(-g.loc[g.pnl_net <= 0, "pnl_net"].sum(), 1e-9)})
    out["years"] = yr.to_dict("records")
    out["blocks"] = blocks
    out["max_year_share"] = max_share
    md.append(f"## Sub-periods\nlargest single-year share of total net profit: **{max_share:.0%}**\n"
              + fmt_table(yr.to_dict("records"), ["year", "trades", "exp_r", "net", "long_net", "short_net"])
              + "\n" + fmt_table(blocks, ["block", "trades", "exp_r", "pf", "net"]))

    # ------------------------------------------------------------ K. deflated Sharpe
    with open(os.path.join(RESULTS, "s01_dev_screen.json")) as f:
        screen = json.load(f)["baseline"]
    srs = [float(s["sharpe"]) / math.sqrt(252) for s in screen if s.get("sharpe") not in (None, "None") and not (isinstance(s["sharpe"], float) and math.isnan(s["sharpe"]))]
    var_sr = float(np.var(srs, ddof=1))
    oos_daily = daily_full[daily_full.index >= pd.Timestamp(OOS[0])]
    out["dsr_full"] = deflated_sharpe(daily_full, N_TRIALS, var_sr)
    out["dsr_oos"] = deflated_sharpe(oos_daily, N_TRIALS, var_sr)
    md.append(f"## Deflated Sharpe (N={N_TRIALS} trials, var of trial SR from DEV screen)\n"
              f"DEV+OOS: SR {out['dsr_full']['sr_annual']:.2f} vs. SR0 {out['dsr_full']['sr0_annual']:.2f} → PSR(>0) {out['dsr_full']['psr_vs_zero']:.2f}, **DSR {out['dsr_full']['dsr']:.2f}**; "
              f"OOS only: SR {out['dsr_oos']['sr_annual']:.2f}, PSR {out['dsr_oos']['psr_vs_zero']:.2f}, DSR {out['dsr_oos']['dsr']:.2f}\n")

    # ------------------------------------------------------------ L. gates
    g = gates(seg["DEV 2010-18"], seg["OOS 2019-23"], seg["cost x1.5 DEV+OOS"], pos_share, wf_total, max_share,
              tb["prob_expectancy_positive"])
    out["gates"] = g
    md.append("## Pre-registered gates\n" + "\n".join(f"- {'N/A' if v is None else ('PASS' if v else 'FAIL')} — {k}" for k, v in g.items()) + "\n")
    out["runtime_s"] = time.time() - t0

    with open(os.path.join(RESULTS, f"s02_{key}.md"), "w") as f:
        f.write("\n\n".join(md))
    with open(os.path.join(RESULTS, f"s02_{key}.json"), "w") as f:
        json.dump(out, f, indent=2, default=lambda x: None if isinstance(x, float) and math.isnan(x) else str(x))
    with open(os.path.join(CACHE, f"{key}_full.pkl"), "wb") as f:
        pickle.dump({"trades": trades_full, "daily": daily_full}, f)
    print(f"{key} done in {out['runtime_s']:.0f}s; gates: {g}")
    return out


if __name__ == "__main__":
    keys = sys.argv[1:] or ["C5", "C9", "C3", "C2", "C8b"]
    for k in keys:
        validate(k)
