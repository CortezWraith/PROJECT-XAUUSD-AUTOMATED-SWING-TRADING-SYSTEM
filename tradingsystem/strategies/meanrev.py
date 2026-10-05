"""Conditional mean-reversion candidates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import pandas as pd

from tradingsystem.core.types import Side, SignalAction
from tradingsystem.signals import indicators as ind
from tradingsystem.strategies.base import PositionView, Strategy


class TrendPullbackRSI(Strategy):
    """Short-term oversold pullback inside a long-term trend (Connors RSI(2) family).

    * long when close > SMA(trend_n) and RSI(rsi_n) < ``lo``; short mirror with ``hi``;
    * exit when the close crosses back over SMA(exit_n) (the short-term mean), or after
      ``max_hold`` bars; catastrophic stop ``stop_atr`` ATR.
    """

    strategy_id = "rsi2_pullback_d1"
    timeframe = "D1"

    @dataclass(frozen=True)
    class Params:
        trend_n: int = 200
        rsi_n: int = 2
        lo: float = 10.0
        hi: float = 90.0
        exit_n: int = 5
        atr_n: int = 20
        stop_atr: float = 3.0
        max_hold: int = 10
        allow_long: bool = True
        allow_short: bool = True

    @property
    def warmup_bars(self) -> int:
        return self.params.trend_n + 2

    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        c = bars["close"]
        f = pd.DataFrame(index=bars.index)
        f["close"] = c
        f["trend"] = ind.sma(c, p.trend_n)
        f["rsi"] = ind.rsi(c, p.rsi_n)
        f["exit_ma"] = ind.sma(c, p.exit_n)
        f["atr"] = ind.atr(bars["high"], bars["low"], c, p.atr_n)
        return f

    def on_bar(self, ts, row: Any, pos: Optional[PositionView]):
        p = self.params
        if np.isnan(row.trend) or np.isnan(row.rsi) or np.isnan(row.atr):
            return []
        if pos is None:
            if p.allow_long and row.close > row.trend and row.rsi < p.lo:
                return [self._sig(ts, SignalAction.ENTER, side=Side.LONG, stop_price=row.close - p.stop_atr * row.atr,
                                  max_hold_bars=p.max_hold, reason="oversold in uptrend")]
            if p.allow_short and row.close < row.trend and row.rsi > p.hi:
                return [self._sig(ts, SignalAction.ENTER, side=Side.SHORT, stop_price=row.close + p.stop_atr * row.atr,
                                  max_hold_bars=p.max_hold, reason="overbought in downtrend")]
            return []
        if pos.bars_held >= p.max_hold:
            return [self._sig(ts, SignalAction.EXIT, side=pos.side, reason="time exit")]
        if (pos.side is Side.LONG and row.close > row.exit_ma) or (pos.side is Side.SHORT and row.close < row.exit_ma):
            return [self._sig(ts, SignalAction.EXIT, side=pos.side, reason="reverted to short-term mean")]
        return []


class RangeZScoreReversion(Strategy):
    """Volatility/regime-conditioned mean reversion on H1: fade 2-sigma deviations from a
    2-day mean only when the market is range-bound (low efficiency ratio)."""

    strategy_id = "zscore_mr_h1"
    timeframe = "H1"

    @dataclass(frozen=True)
    class Params:
        n: int = 48
        z_entry: float = 2.0
        er_max: float = 0.3
        atr_n: int = 48
        stop_atr: float = 2.5
        max_hold: int = 24
        allow_long: bool = True
        allow_short: bool = True

    @property
    def warmup_bars(self) -> int:
        return self.params.n + 2

    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        c = bars["close"]
        f = pd.DataFrame(index=bars.index)
        f["close"] = c
        f["z"] = ind.zscore(c, p.n)
        f["er"] = ind.efficiency_ratio(c, p.n)
        f["atr"] = ind.atr(bars["high"], bars["low"], c, p.atr_n)
        return f

    def on_bar(self, ts, row: Any, pos: Optional[PositionView]):
        p = self.params
        if np.isnan(row.z) or np.isnan(row.er) or np.isnan(row.atr):
            return []
        if pos is None:
            if row.er > p.er_max:
                return []
            if p.allow_long and row.z < -p.z_entry:
                return [self._sig(ts, SignalAction.ENTER, side=Side.LONG, stop_price=row.close - p.stop_atr * row.atr)]
            if p.allow_short and row.z > p.z_entry:
                return [self._sig(ts, SignalAction.ENTER, side=Side.SHORT, stop_price=row.close + p.stop_atr * row.atr)]
            return []
        if pos.bars_held >= p.max_hold or (pos.side is Side.LONG and row.z >= 0) or (pos.side is Side.SHORT and row.z <= 0):
            return [self._sig(ts, SignalAction.EXIT, side=pos.side, reason="mean / time")]
        return []
