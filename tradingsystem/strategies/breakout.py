"""Volatility / range-expansion breakout candidates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import pandas as pd

from tradingsystem.core.types import EntryType, Side, SignalAction
from tradingsystem.signals import indicators as ind
from tradingsystem.strategies.base import PositionView, Strategy


class VolatilityBreakout(Strategy):
    """Daily range-expansion breakout (Williams / ORB family).

    After each daily close place a two-sided OCO bracket valid for the next day:
    buy stop at close + k*ATR, sell stop at close - k*ATR. Protective stop at
    ``stop_atr`` ATR from the entry level; exit at the close of the ``hold_days``-th
    daily bar after entry.
    """

    strategy_id = "volbreak_d1"
    timeframe = "D1"

    @dataclass(frozen=True)
    class Params:
        k: float = 0.5
        atr_n: int = 14
        stop_atr: float = 1.0
        hold_days: int = 2
        allow_long: bool = True
        allow_short: bool = True

    @property
    def warmup_bars(self) -> int:
        return self.params.atr_n + 2

    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        f = pd.DataFrame(index=bars.index)
        f["close"] = bars["close"]
        f["atr"] = ind.atr(bars["high"], bars["low"], bars["close"], self.params.atr_n)
        return f

    def on_bar(self, ts, row: Any, pos: Optional[PositionView]):
        p = self.params
        if np.isnan(row.atr):
            return []
        if pos is not None:
            if pos.bars_held >= p.hold_days:
                return [self._sig(ts, SignalAction.EXIT, side=pos.side, reason="time exit")]
            return []
        out = []
        if p.allow_long:
            lvl = row.close + p.k * row.atr
            out.append(self._sig(ts, SignalAction.ENTER, side=Side.LONG, entry_type=EntryType.STOP, entry_price=lvl,
                                 stop_price=lvl - p.stop_atr * row.atr, valid_bars=1, reason="range expansion up"))
        if p.allow_short:
            lvl = row.close - p.k * row.atr
            out.append(self._sig(ts, SignalAction.ENTER, side=Side.SHORT, entry_type=EntryType.STOP, entry_price=lvl,
                                 stop_price=lvl + p.stop_atr * row.atr, valid_bars=1, reason="range expansion down"))
        return out


class SqueezeBreakout(Strategy):
    """Momentum after consolidation on H4: a Bollinger-bandwidth squeeze (bandwidth in the
    lowest ``squeeze_pct`` of the trailing ``rank_n`` bars, within the last ``lookback`` bars)
    followed by a close outside the band. Stop: ``stop_atr`` ATR; exit when the close crosses
    the middle band or after ``max_hold`` bars."""

    strategy_id = "squeeze_h4"
    timeframe = "H4"

    @dataclass(frozen=True)
    class Params:
        bb_n: int = 20
        bb_k: float = 2.0
        rank_n: int = 120
        squeeze_pct: float = 0.2
        lookback: int = 5
        atr_n: int = 20
        stop_atr: float = 2.0
        max_hold: int = 30
        allow_long: bool = True
        allow_short: bool = True

    @property
    def warmup_bars(self) -> int:
        return self.params.rank_n + self.params.bb_n + self.params.lookback

    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        c = bars["close"]
        f = pd.DataFrame(index=bars.index)
        f["close"] = c
        mid = ind.sma(c, p.bb_n)
        sd = c.rolling(p.bb_n, min_periods=p.bb_n).std(ddof=0)
        f["mid"] = mid
        f["upper"] = mid + p.bb_k * sd
        f["lower"] = mid - p.bb_k * sd
        bw = ind.bollinger_bandwidth(c, p.bb_n, p.bb_k)
        rank = ind.rolling_percentile_rank(bw, p.rank_n)
        f["squeeze"] = (rank < p.squeeze_pct).astype(float).where(rank.notna()).rolling(p.lookback).max()
        f["atr"] = ind.atr(bars["high"], bars["low"], c, p.atr_n)
        return f

    def on_bar(self, ts, row: Any, pos: Optional[PositionView]):
        p = self.params
        if np.isnan(row.atr) or np.isnan(row.squeeze):
            return []
        if pos is None:
            if row.squeeze < 1:
                return []
            if p.allow_long and row.close > row.upper:
                return [self._sig(ts, SignalAction.ENTER, side=Side.LONG, stop_price=row.close - p.stop_atr * row.atr)]
            if p.allow_short and row.close < row.lower:
                return [self._sig(ts, SignalAction.ENTER, side=Side.SHORT, stop_price=row.close + p.stop_atr * row.atr)]
            return []
        if pos.bars_held >= p.max_hold or (pos.side is Side.LONG and row.close < row.mid) or \
                (pos.side is Side.SHORT and row.close > row.mid):
            return [self._sig(ts, SignalAction.EXIT, side=pos.side, reason="mid-band / time")]
        return []
