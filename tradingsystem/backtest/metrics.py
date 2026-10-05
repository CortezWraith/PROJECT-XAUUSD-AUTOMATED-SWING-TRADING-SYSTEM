"""Performance metrics computed from a BacktestResult (trades + equity curve)."""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def daily_returns(equity: pd.Series) -> pd.Series:
    d = equity.groupby(equity.index.normalize()).last()
    return d.pct_change().dropna()


def max_drawdown(equity: pd.Series) -> tuple[float, pd.Timedelta]:
    """Max drawdown (fraction, positive number) and longest time under water."""
    if equity.empty:
        return 0.0, pd.Timedelta(0)
    peak = equity.cummax()
    dd = equity / peak - 1.0
    mdd = float(-dd.min())
    under = dd < 0
    longest = pd.Timedelta(0)
    start = None
    for ts, u in under.items():
        if u and start is None:
            start = ts
        elif not u and start is not None:
            longest = max(longest, ts - start)
            start = None
    if start is not None:
        longest = max(longest, equity.index[-1] - start)
    return mdd, longest


def longest_losing_streak(pnl: pd.Series) -> int:
    best = cur = 0
    for x in pnl:
        cur = cur + 1 if x <= 0 else 0
        best = max(best, cur)
    return best


def sharpe(r: pd.Series) -> float:
    if len(r) < 2 or r.std(ddof=1) == 0:
        return float("nan")
    return float(r.mean() / r.std(ddof=1) * math.sqrt(TRADING_DAYS))


def sortino(r: pd.Series) -> float:
    if len(r) < 2:
        return float("nan")
    dn = r[r < 0]
    dd = math.sqrt((dn ** 2).sum() / len(r)) if len(dn) else 0.0
    return float(r.mean() / dd * math.sqrt(TRADING_DAYS)) if dd > 0 else float("nan")


def trade_stats(tr: pd.DataFrame, initial: float, years: float) -> dict:
    if tr is None or tr.empty:
        return {"trades": 0}
    pnl = tr["pnl_net"]
    wins = pnl[pnl > 0]
    losses = pnl[pnl <= 0]
    gp, gl = wins.sum(), -losses.sum()
    hold_h = (pd.to_datetime(tr["exit_time"]) - pd.to_datetime(tr["entry_time"])).dt.total_seconds() / 3600
    r = tr["r"].replace([np.inf, -np.inf], np.nan).dropna()
    out = {
        "trades": int(len(tr)),
        "trades_per_year": len(tr) / years if years > 0 else float("nan"),
        "win_rate": float((pnl > 0).mean()),
        "avg_win": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss": float(losses.mean()) if len(losses) else 0.0,
        "avg_win_r": float(r[r > 0].mean()) if (r > 0).any() else 0.0,
        "avg_loss_r": float(r[r <= 0].mean()) if (r <= 0).any() else 0.0,
        "expectancy": float(pnl.mean()),
        "expectancy_r": float(r.mean()) if len(r) else float("nan"),
        "expectancy_r_t": float(r.mean() / (r.std(ddof=1) / math.sqrt(len(r)))) if len(r) > 2 and r.std(ddof=1) > 0 else float("nan"),
        "profit_factor": float(gp / gl) if gl > 0 else float("inf"),
        "avg_hold_hours": float(hold_h.mean()),
        "median_hold_hours": float(hold_h.median()),
        "longest_losing_streak": longest_losing_streak(pnl),
        "net_pnl": float(pnl.sum()),
        "gross_pnl": float(tr["pnl_gross"].sum()),
        "cost_spread": float(tr["spread_cost"].sum()),
        "cost_slippage": float(tr["slippage_cost"].sum()),
        "cost_commission": float(tr["commission"].sum()),
        "swap": float(tr["swap"].sum()),
        "long_trades": int((tr["side"] == 1).sum()),
        "short_trades": int((tr["side"] == -1).sum()),
        "long_pnl": float(pnl[tr["side"] == 1].sum()),
        "short_pnl": float(pnl[tr["side"] == -1].sum()),
        "long_expectancy_r": float(tr.loc[tr["side"] == 1, "r"].mean()) if (tr["side"] == 1).any() else float("nan"),
        "short_expectancy_r": float(tr.loc[tr["side"] == -1, "r"].mean()) if (tr["side"] == -1).any() else float("nan"),
    }
    out["net_return_pct_initial"] = out["net_pnl"] / initial * 100
    return out


def summarize(res, label: Optional[str] = None) -> dict:
    eq = res.equity
    years = max((res.end - res.start).total_seconds() / (365.25 * 86400), 1e-9)
    r = daily_returns(eq)
    mdd, under = max_drawdown(eq)
    final = float(eq.iloc[-1]) if len(eq) else res.initial
    cagr = (final / res.initial) ** (1 / years) - 1 if final > 0 else -1.0
    out = {"label": label, "start": str(res.start.date()), "end": str(res.end.date()), "years": round(years, 2),
           "cagr": cagr, "sharpe": sharpe(r), "sortino": sortino(r), "max_dd": mdd,
           "calmar": cagr / mdd if mdd > 0 else float("nan"), "longest_underwater_days": under.days,
           "exposure": float((res.exposure != 0).mean()) if len(res.exposure) else 0.0,
           "final_equity": final}
    out.update(trade_stats(res.trades, res.initial, years))
    return out


def yearly_table(res) -> pd.DataFrame:
    tr = res.trades
    if tr.empty:
        return pd.DataFrame()
    eq = res.equity
    y_eq = eq.groupby(eq.index.year).last()
    y_ret = y_eq.pct_change()
    y_ret.iloc[0] = y_eq.iloc[0] / res.initial - 1
    t = tr.copy()
    t["year"] = pd.to_datetime(t["exit_time"]).dt.year
    g = t.groupby("year")
    df = pd.DataFrame({
        "return": y_ret,
        "trades": g.size(),
        "win_rate": g["pnl_net"].apply(lambda x: (x > 0).mean()),
        "exp_r": g["r"].mean(),
        "pf": g["pnl_net"].apply(lambda x: x[x > 0].sum() / -x[x <= 0].sum() if (x <= 0).any() and x[x <= 0].sum() < 0 else np.inf),
        "long_pnl": g.apply(lambda x: x.loc[x["side"] == 1, "pnl_net"].sum()),
        "short_pnl": g.apply(lambda x: x.loc[x["side"] == -1, "pnl_net"].sum()),
    })
    return df
