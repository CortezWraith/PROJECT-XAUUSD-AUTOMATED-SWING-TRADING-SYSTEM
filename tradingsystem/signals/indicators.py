"""Causal indicator library.

Every function uses only information available at the close of bar ``t`` for
the value stored at ``t``. Channel functions that must exclude the current bar
say so explicitly (``shift=1``). There is a unit test that recomputes every
indicator on truncated history and checks the last value is unchanged.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(x: pd.Series, n: int) -> pd.Series:
    return x.rolling(n, min_periods=n).mean()


def ema(x: pd.Series, n: int) -> pd.Series:
    return x.ewm(span=n, adjust=False, min_periods=n).mean()


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev = close.shift(1)
    tr = pd.concat([high - low, (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1)
    tr.iloc[0] = high.iloc[0] - low.iloc[0]
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, n: int) -> pd.Series:
    """Average true range, simple rolling mean (finite memory => exact live/backtest parity)."""
    return true_range(high, low, close).rolling(n, min_periods=n).mean()


def donchian_high(high: pd.Series, n: int, shift: int = 1) -> pd.Series:
    """Highest high of the ``n`` bars *before* the current one (shift=1 excludes current bar)."""
    return high.rolling(n, min_periods=n).max().shift(shift)


def donchian_low(low: pd.Series, n: int, shift: int = 1) -> pd.Series:
    return low.rolling(n, min_periods=n).min().shift(shift)


def rsi(close: pd.Series, n: int) -> pd.Series:
    """RSI with simple-average gains/losses (Cutler's RSI): finite memory, no seed dependence."""
    d = close.diff()
    up = d.clip(lower=0).rolling(n, min_periods=n).mean()
    dn = (-d.clip(upper=0)).rolling(n, min_periods=n).mean()
    rs = up / dn.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    out = out.where(dn > 0, 100.0)
    out = out.where(up > 0, out.where(dn == 0, 0.0))
    return out.where(d.rolling(n, min_periods=n).count() == n)


def zscore(x: pd.Series, n: int) -> pd.Series:
    m = x.rolling(n, min_periods=n).mean()
    s = x.rolling(n, min_periods=n).std(ddof=0)
    return (x - m) / s.replace(0, np.nan)


def log_returns(close: pd.Series) -> pd.Series:
    return np.log(close).diff()


def realized_vol(close: pd.Series, n: int) -> pd.Series:
    return log_returns(close).rolling(n, min_periods=n).std(ddof=0)


def efficiency_ratio(close: pd.Series, n: int) -> pd.Series:
    """Kaufman efficiency ratio: |net change| / sum |changes| over n bars (0 = noise, 1 = straight line)."""
    net = (close - close.shift(n)).abs()
    path = close.diff().abs().rolling(n, min_periods=n).sum()
    return net / path.replace(0, np.nan)


def rolling_percentile_rank(x: pd.Series, n: int) -> pd.Series:
    """Percentile (0..1) of the current value within the trailing n values (inclusive)."""
    def _rank(a: np.ndarray) -> float:
        return (a[:-1] < a[-1]).mean() if len(a) > 1 else np.nan
    return x.rolling(n, min_periods=n).apply(_rank, raw=True)


def bollinger_bandwidth(close: pd.Series, n: int, k: float = 2.0) -> pd.Series:
    m = close.rolling(n, min_periods=n).mean()
    s = close.rolling(n, min_periods=n).std(ddof=0)
    return (2 * k * s) / m
