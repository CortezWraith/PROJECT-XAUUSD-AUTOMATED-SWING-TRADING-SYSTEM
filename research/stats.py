"""Statistical tools: bootstrap, deflated Sharpe ratio, PBO (CSCV), regimes."""
from __future__ import annotations

import itertools
import math

import numpy as np
import pandas as pd
from scipy import stats as st


# ----------------------------------------------------------------------------- bootstrap
def _longest_run(B: np.ndarray) -> np.ndarray:
    """Longest run of True per row of a boolean matrix."""
    c = np.cumsum(B, axis=1)
    reset = np.maximum.accumulate(np.where(~B, c, 0), axis=1)
    return (c - reset).max(axis=1)


def trade_bootstrap(r: np.ndarray, years: float, risk: float = 0.005, n: int = 10_000, seed: int = 7,
                    chunk: int = 500) -> dict:
    """Resample trade R-multiples with replacement; equity compounds by (1 + risk*R) per trade."""
    rng = np.random.default_rng(seed)
    r = np.asarray(r, float)
    k = len(r)
    acc = {"cagr": [], "expectancy_r": [], "pf": [], "max_dd": [], "losing_streak": [], "recovery_trades": []}
    done = 0
    while done < n:
        m = min(chunk, n - done)
        S = r[rng.integers(0, k, (m, k))]
        eq = np.cumprod(1 + risk * S, axis=1)
        peak = np.maximum.accumulate(eq, axis=1)
        dd = 1 - eq / peak
        acc["cagr"].append(eq[:, -1] ** (1 / years) - 1)
        acc["expectancy_r"].append(S.mean(1))
        gp = np.where(S > 0, S, 0).sum(1)
        gl = -np.where(S <= 0, S, 0).sum(1)
        acc["pf"].append(np.where(gl > 0, gp / np.where(gl > 0, gl, 1), np.nan))
        acc["max_dd"].append(dd.max(1))
        acc["losing_streak"].append(_longest_run(S <= 0))
        acc["recovery_trades"].append(_longest_run(dd > 0))
        done += m
    res = {}
    for key, v in acc.items():
        a = np.concatenate(v).astype(float)
        res[key] = {"p05": float(np.nanpercentile(a, 5)), "p50": float(np.nanpercentile(a, 50)),
                    "p95": float(np.nanpercentile(a, 95))}
    res["prob_expectancy_positive"] = float((np.concatenate(acc["expectancy_r"]) > 0).mean())
    return res


def block_bootstrap_daily(ret: pd.Series, block: int = 20, n: int = 5_000, seed: int = 11) -> dict:
    rng = np.random.default_rng(seed)
    x = ret.values
    T = len(x)
    nb = int(math.ceil(T / block))
    sh, cg, md = [], [], []
    years = T / 252
    for _ in range(n):
        starts = rng.integers(0, T - block, nb)
        s = np.concatenate([x[i:i + block] for i in starts])[:T]
        sd = s.std(ddof=1)
        sh.append(s.mean() / sd * math.sqrt(252) if sd > 0 else np.nan)
        eq = np.cumprod(1 + s)
        cg.append(eq[-1] ** (1 / years) - 1)
        md.append((1 - eq / np.maximum.accumulate(eq)).max())
    q = lambda a: {"p05": float(np.nanpercentile(a, 5)), "p50": float(np.nanpercentile(a, 50)), "p95": float(np.nanpercentile(a, 95))}
    return {"sharpe": q(sh), "cagr": q(cg), "max_dd": q(md), "prob_sharpe_positive": float((np.asarray(sh) > 0).mean())}


# ----------------------------------------------------------------------------- deflated Sharpe
def deflated_sharpe(ret: pd.Series, n_trials: int, sr_var_trials: float) -> dict:
    """Bailey & Lopez de Prado (2014). Sharpe ratios per observation (daily, not annualised)."""
    x = ret.dropna().values
    T = len(x)
    sr = x.mean() / x.std(ddof=1)
    g3 = st.skew(x)
    g4 = st.kurtosis(x, fisher=False)
    emc = 0.5772156649
    sr0 = math.sqrt(max(sr_var_trials, 1e-12)) * ((1 - emc) * st.norm.ppf(1 - 1 / n_trials) + emc * st.norm.ppf(1 - 1 / (n_trials * math.e)))
    denom = math.sqrt(max(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2, 1e-12))
    dsr = st.norm.cdf((sr - sr0) * math.sqrt(T - 1) / denom)
    psr = st.norm.cdf((sr - 0) * math.sqrt(T - 1) / denom)
    return {"sr_daily": float(sr), "sr_annual": float(sr * math.sqrt(252)), "sr0_annual": float(sr0 * math.sqrt(252)),
            "psr_vs_zero": float(psr), "dsr": float(dsr), "n_trials": n_trials, "T": T}


# ----------------------------------------------------------------------------- PBO
def pbo_cscv(M: pd.DataFrame, S: int | None = None) -> dict:
    """Probability of backtest overfitting via combinatorially symmetric cross-validation.

    M: rows = periods (e.g. years), columns = configurations, values = period returns.
    """
    X = M.values
    T, N = X.shape
    S = S or T - (T % 2)
    X = X[:S]
    idx = list(range(S))
    logits = []
    for comb in itertools.combinations(idx, S // 2):
        tr = list(comb)
        te = [i for i in idx if i not in comb]
        is_perf = X[tr].mean(0) / (X[tr].std(0, ddof=1) + 1e-12)
        oos_perf = X[te].mean(0) / (X[te].std(0, ddof=1) + 1e-12)
        best = int(np.argmax(is_perf))
        rank = (oos_perf < oos_perf[best]).sum() / (N - 1) if N > 1 else 0.5
        rank = min(max(rank, 1e-6), 1 - 1e-6)
        logits.append(math.log(rank / (1 - rank)))
    logits = np.asarray(logits)
    return {"pbo": float((logits <= 0).mean()), "n_splits": len(logits), "median_logit": float(np.median(logits))}


# ----------------------------------------------------------------------------- regimes
def regime_frame(d1: pd.DataFrame, macro: pd.DataFrame) -> pd.DataFrame:
    """Ex-ante regime labels per server date, using information up to the previous day only."""
    c = 0.5 * (d1["close_bid"] + d1["close_ask"])
    r = np.log(c).diff()
    vol20 = r.rolling(20).std()
    tstat = np.log(c).diff(60).abs() / (r.rolling(60).std() * math.sqrt(60))
    f = pd.DataFrame(index=d1.index)
    f["trend"] = np.where(tstat > 1.0, "trending", "ranging")
    f["vol"] = np.where(vol20 > vol20.rolling(252, min_periods=120).median(), "high vol", "low vol")
    f.loc[tstat.isna(), "trend"] = np.nan
    f.loc[vol20.rolling(252, min_periods=120).median().isna(), "vol"] = np.nan
    f = f.shift(1)          # known at the start of the day
    m = macro.copy()
    m.index = m.index + pd.Timedelta(days=1)    # publication lag
    m = m.reindex(f.index, method="ffill")
    usd_chg = np.log(macro["usd_index"].dropna()).diff(60)
    usd_chg.index = usd_chg.index + pd.Timedelta(days=1)
    y_chg = macro["ust_10y"].dropna().diff(60)
    y_chg.index = y_chg.index + pd.Timedelta(days=1)
    f["usd"] = np.where(usd_chg.reindex(f.index, method="ffill") > 0, "strong USD", "weak USD")
    f["rates"] = np.where(y_chg.reindex(f.index, method="ffill") > 0, "rising yields", "falling yields")
    f["crisis"] = np.where(m["vix"] > 25, "crisis (VIX>25)", "normal")
    return f
