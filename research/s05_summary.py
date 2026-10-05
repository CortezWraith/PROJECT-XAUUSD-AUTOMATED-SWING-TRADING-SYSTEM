"""Step 5: pooled 2004-2026 statistics and figures for the report (no decisions are made here)."""
from __future__ import annotations

import json
import math
import os
import pickle
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DEV, HOLDOUT, OOS, PRE_SAMPLE, RESULTS, bars_for, fmt_table, run, stitched  # noqa: E402
from registry import SPECS, make  # noqa: E402

from tradingsystem.backtest.metrics import daily_returns  # noqa: E402

FIG = os.path.join(RESULTS, "figures")
os.makedirs(FIG, exist_ok=True)
CACHE = os.path.join(RESULTS, "cache")
SEGS = [("PRE 2004-09", PRE_SAMPLE, "stitched"), ("DEV 2010-18", DEV, "stitched"), ("OOS 2019-23", OOS, "stitched"), ("HOLDOUT 2024-26", HOLDOUT, "A")]
COLORS = {"C3": "#2a6fdb", "C2": "#d9822b", "C5": "#3a9d5d", "C9": "#8e6bbf", "C8b": "#888888"}


def pooled(keys):
    rows, curves = [], {}
    for k in keys:
        trs, ds = [], []
        for lab, (a, b), src in SEGS:
            res = run([make(k)], a, b, source=src)
            t = res.trades.copy()
            t["segment"] = lab
            trs.append(t)
            ds.append(daily_returns(res.equity))
        T = pd.concat(trs)
        D = pd.concat(ds).sort_index()
        D = D[~D.index.duplicated()]
        curves[k] = (1 + D).cumprod()
        r = T["r"].dropna()
        seg_exp = T.groupby("segment")["r"].mean()
        rows.append({"strategy": SPECS[k]["name"], "trades": len(r), "exp_r": r.mean(),
                     "t_stat": r.mean() / (r.std(ddof=1) / math.sqrt(len(r))),
                     "pf": T.loc[T.pnl_net > 0, "pnl_net"].sum() / -T.loc[T.pnl_net <= 0, "pnl_net"].sum(),
                     "sharpe": D.mean() / D.std() * math.sqrt(252),
                     "positive_segments": int((seg_exp > 0).sum()),
                     **{f"exp_{s.split()[0]}": seg_exp.get(s, np.nan) for s, _, _ in SEGS},
                     "long_exp_r": T.loc[T.side == 1, "r"].mean(), "short_exp_r": T.loc[T.side == -1, "r"].mean()})
    return rows, curves


def fig_equity(curves):
    fig, ax = plt.subplots(figsize=(11, 5))
    for k, c in curves.items():
        ax.plot(c.index, c.values, label=SPECS[k]["name"], color=COLORS.get(k), lw=1.4)
    for (lab, (a, b), _), shade in zip(SEGS, ["#f3f3f3", "#ffffff", "#eef4ff", "#fff3e6"]):
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=shade, zorder=0)
        ax.text(pd.Timestamp(a) + pd.Timedelta(days=60), 0.97, lab, fontsize=8, va="top", color="#555",
                transform=ax.get_xaxis_transform())
    ax.axhline(1, color="#999", lw=0.8)
    ax.set_title("Equity (0.5% risk per trade, baseline costs) - PRE / DEV / OOS / HOLDOUT")
    ax.set_ylabel("equity multiple")
    ax.legend(loc="lower left", fontsize=8, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "equity_segments.png"), dpi=120)
    plt.close(fig)


def fig_gold():
    d1 = stitched("D1")
    c = 0.5 * (d1.close_bid + d1.close_ask)
    fig, ax = plt.subplots(figsize=(11, 3))
    ax.plot(c.index, c.values, color="#b8860b", lw=1.2)
    ax.set_yscale("log")
    ax.set_title("XAUUSD daily close (log scale), research series B -> A")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "xauusd.png"), dpi=120)
    plt.close(fig)


def fig_session_profile():
    h = stitched("H1")
    r = np.log(h.open_bid).diff().shift(-1)
    df = pd.DataFrame({"r": r, "hour": h.index.hour})
    fig, ax = plt.subplots(figsize=(11, 3.5))
    for (lab, (a, b)), col in zip([("2004-2009", ("2004-07-01", "2010-01-01")), ("DEV 2010-2018", DEV), ("OOS 2019-2023", OOS)],
                                  ["#999999", "#2a6fdb", "#d9822b"]):
        m = df[(df.index >= a) & (df.index < b)].groupby("hour")["r"].mean() * 1e4
        ax.plot(m.index, m.cumsum().values, marker="o", ms=3, label=lab, color=col)
    ax.axvspan(2, 9, color="#e8f5e9", zorder=0)
    ax.axvspan(9, 15, color="#fdecea", zorder=0)
    ax.set_xlabel("server hour (NY+7); green = Asian long leg, red = London short leg of C8b")
    ax.set_ylabel("cumulative mean bid return, bp")
    ax.set_title("Intraday profile of XAUUSD (bid, open-to-open hourly returns)")
    ax.legend(frameon=False, fontsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "session_profile.png"), dpi=120)
    plt.close(fig)


def fig_grid(key, x, y, z="expectancy_r"):
    g = pd.read_csv(os.path.join(RESULTS, f"grid_{key}.csv"))
    if "oat" in g:
        g = g[g["oat"].isna()]
    piv = g.groupby([y, x])[z].median().unstack()
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(piv.values, cmap="RdYlGn", vmin=-0.2, vmax=0.2, origin="lower")
    ax.set_xticks(range(len(piv.columns)), [str(v) for v in piv.columns])
    ax.set_yticks(range(len(piv.index)), [str(v) for v in piv.index])
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            ax.text(j, i, f"{piv.values[i, j]:.2f}", ha="center", va="center", fontsize=7)
    ax.set_title(f"{SPECS[key]['name']}: median {z} (DEV+OOS)", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"grid_{key}.png"), dpi=120)
    plt.close(fig)


def main():
    rows, curves = pooled(["C3", "C2", "C5", "C9", "C8b"])
    cols = ["strategy", "trades", "exp_r", "t_stat", "pf", "sharpe", "positive_segments", "exp_PRE", "exp_DEV", "exp_OOS", "exp_HOLDOUT", "long_exp_r", "short_exp_r"]
    md = "# Pooled 2004-07 .. 2026-08 (PRE + DEV + OOS + HOLDOUT), baseline costs\n\n" + fmt_table(rows, cols)
    with open(os.path.join(RESULTS, "s05_pooled.md"), "w") as f:
        f.write(md)
    with open(os.path.join(RESULTS, "s05_pooled.json"), "w") as f:
        json.dump(rows, f, indent=2, default=str)
    print(md)
    fig_equity({k: v for k, v in curves.items() if k in ("C3", "C2", "C5", "C8b")})
    fig_gold()
    fig_session_profile()
    fig_grid("C3", "slow", "fast")
    fig_grid("C2", "exit_n", "entry_n")
    fig_grid("C5", "squeeze_pct", "bb_n")


if __name__ == "__main__":
    main()
