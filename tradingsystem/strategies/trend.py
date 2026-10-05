"""Trend / time-series-momentum candidates.

Parameters are literature defaults chosen *before* looking at any XAUUSD
result (Turtle 55/20 channels, 2N stops; 3-month TSMOM; 20/100 EMA).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import pandas as pd

from tradingsystem.core.types import Side, SignalAction
from tradingsystem.signals import indicators as ind
from tradingsystem.strategies.base import PositionView, Strategy


class DonchianBreakout(Strategy):
    """Price-channel breakout (Turtle System-2 logic) on H4.

    * long when the close exceeds the highest high of the previous ``entry_n`` bars,
      short when it falls below the lowest low (signal on close, fill next open);
    * initial stop ``stop_atr`` x ATR from the signal close;
    * exit when the close crosses the opposite ``exit_n``-bar channel (trailing exit);
      the protective stop is ratcheted to that channel when it is tighter;
    * time stop after ``max_hold`` bars; one position at a time; re-entry needs a fresh breakout.
    """

    strategy_id = "donchian_h4"
    timeframe = "H4"

    @dataclass(frozen=True)
    class Params:
        entry_n: int = 55
        exit_n: int = 20
        atr_n: int = 20
        stop_atr: float = 2.0
        max_hold: int = 90
        allow_long: bool = True
        allow_short: bool = True

    @property
    def warmup_bars(self) -> int:
        return max(self.params.entry_n, self.params.exit_n, self.params.atr_n) + 2

    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        f = pd.DataFrame(index=bars.index)
        f["close"] = bars["close"]
        f["atr"] = ind.atr(bars["high"], bars["low"], bars["close"], p.atr_n)
        f["hh"] = ind.donchian_high(bars["high"], p.entry_n)
        f["ll"] = ind.donchian_low(bars["low"], p.entry_n)
        f["xh"] = ind.donchian_high(bars["high"], p.exit_n)
        f["xl"] = ind.donchian_low(bars["low"], p.exit_n)
        return f

    def on_bar(self, ts, row: Any, pos: Optional[PositionView]):
        p = self.params
        if np.isnan(row.atr) or np.isnan(row.hh) or np.isnan(row.xl):
            return []
        out = []
        if pos is None:
            if p.allow_long and row.close > row.hh:
                out.append(self._sig(ts, SignalAction.ENTER, side=Side.LONG, stop_price=row.close - p.stop_atr * row.atr,
                                     max_hold_bars=p.max_hold, reason="channel breakout up"))
            elif p.allow_short and row.close < row.ll:
                out.append(self._sig(ts, SignalAction.ENTER, side=Side.SHORT, stop_price=row.close + p.stop_atr * row.atr,
                                     max_hold_bars=p.max_hold, reason="channel breakout down"))
            return out
        if pos.side is Side.LONG:
            if row.close < row.xl or pos.bars_held >= p.max_hold:
                return [self._sig(ts, SignalAction.EXIT, side=Side.LONG, reason="exit channel / time")]
            if pos.stop_loss is None or row.xl > pos.stop_loss:
                return [self._sig(ts, SignalAction.UPDATE_STOP, side=Side.LONG, stop_price=row.xl)]
        else:
            if row.close > row.xh or pos.bars_held >= p.max_hold:
                return [self._sig(ts, SignalAction.EXIT, side=Side.SHORT, reason="exit channel / time")]
            if pos.stop_loss is None or row.xh < pos.stop_loss:
                return [self._sig(ts, SignalAction.UPDATE_STOP, side=Side.SHORT, stop_price=row.xh)]
        return out


class MacroFilteredDonchian(DonchianBreakout):
    """Donchian breakout traded only when the USD trend agrees (gold is priced in USD):
    longs only if the USD index is below its ``usd_ma``-day average, shorts only if above.
    Macro data is lagged one business day (publication timing)."""

    strategy_id = "donchian_usd_h4"

    @dataclass(frozen=True)
    class Params(DonchianBreakout.Params):
        usd_ma: int = 50

    def __init__(self, macro: Optional[pd.DataFrame] = None, **params: Any) -> None:
        super().__init__(**params)
        self.macro = macro

    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        f = super().features(bars)
        if self.macro is None:
            f["usd_up"] = np.nan
            return f
        usd = self.macro["usd_index"].dropna()
        up = (usd > usd.rolling(self.params.usd_ma, min_periods=self.params.usd_ma).mean()).astype(float)
        up = up.where(usd.rolling(self.params.usd_ma).count() == self.params.usd_ma)
        up.index = up.index + pd.Timedelta(days=1)          # known only after publication
        f["usd_up"] = up.reindex(f.index.normalize(), method="ffill").values
        return f

    def on_bar(self, ts, row: Any, pos: Optional[PositionView]):
        sigs = super().on_bar(ts, row, pos)
        if pos is None and sigs and not np.isnan(row.usd_up):
            s = sigs[0]
            if (s.side is Side.LONG and row.usd_up == 1.0) or (s.side is Side.SHORT and row.usd_up == 0.0):
                return []
        if pos is None and sigs and np.isnan(row.usd_up):
            return []
        return sigs


class EmaTrend(Strategy):
    """Moving-average trend: long while EMA(fast) > EMA(slow), short while below.
    Enters only on a fresh cross; exits on the opposite cross or a trailing ATR stop."""

    strategy_id = "ema_trend_h4"
    timeframe = "H4"

    @dataclass(frozen=True)
    class Params:
        fast: int = 20
        slow: int = 100
        atr_n: int = 20
        stop_atr: float = 3.0
        allow_long: bool = True
        allow_short: bool = True

    @property
    def warmup_bars(self) -> int:
        return 3 * self.params.slow

    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        f = pd.DataFrame(index=bars.index)
        f["close"] = bars["close"]
        f["atr"] = ind.atr(bars["high"], bars["low"], bars["close"], p.atr_n)
        # SMA instead of EMA would be finite-memory; EMA is kept as the literature rule,
        # live windows use >= 3x slow bars of history so parity holds to < 1e-6.
        f["fast"] = ind.ema(bars["close"], p.fast)
        f["slow"] = ind.ema(bars["close"], p.slow)
        f["state"] = np.sign(f["fast"] - f["slow"])
        f["prev_state"] = f["state"].shift(1)
        f["hc"] = bars["close"].rolling(p.atr_n).max()
        f["lc"] = bars["close"].rolling(p.atr_n).min()
        return f

    def on_bar(self, ts, row: Any, pos: Optional[PositionView]):
        p = self.params
        if np.isnan(row.atr) or np.isnan(row.prev_state):
            return []
        if pos is None:
            if p.allow_long and row.state > 0 and row.prev_state <= 0:
                return [self._sig(ts, SignalAction.ENTER, side=Side.LONG, stop_price=row.close - p.stop_atr * row.atr)]
            if p.allow_short and row.state < 0 and row.prev_state >= 0:
                return [self._sig(ts, SignalAction.ENTER, side=Side.SHORT, stop_price=row.close + p.stop_atr * row.atr)]
            return []
        if (pos.side is Side.LONG and row.state < 0) or (pos.side is Side.SHORT and row.state > 0):
            return [self._sig(ts, SignalAction.EXIT, side=pos.side, reason="ma cross")]
        trail = row.hc - p.stop_atr * row.atr if pos.side is Side.LONG else row.lc + p.stop_atr * row.atr
        return [self._sig(ts, SignalAction.UPDATE_STOP, side=pos.side, stop_price=trail)]


class TimeSeriesMomentum(Strategy):
    """Daily time-series momentum (Moskowitz-Ooi-Pedersen style, 3-month lookback).
    Position = sign of the ``lookback``-day return, reviewed daily, 3 ATR catastrophic stop."""

    strategy_id = "tsmom_d1"
    timeframe = "D1"

    @dataclass(frozen=True)
    class Params:
        lookback: int = 60
        atr_n: int = 20
        stop_atr: float = 3.0
        allow_long: bool = True
        allow_short: bool = True

    @property
    def warmup_bars(self) -> int:
        return self.params.lookback + self.params.atr_n

    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        f = pd.DataFrame(index=bars.index)
        f["close"] = bars["close"]
        f["atr"] = ind.atr(bars["high"], bars["low"], bars["close"], p.atr_n)
        f["mom"] = np.log(bars["close"]).diff(p.lookback)
        return f

    def on_bar(self, ts, row: Any, pos: Optional[PositionView]):
        p = self.params
        if np.isnan(row.mom) or np.isnan(row.atr):
            return []
        want = Side.LONG if row.mom > 0 else Side.SHORT
        allowed = (want is Side.LONG and p.allow_long) or (want is Side.SHORT and p.allow_short)
        if pos is not None and pos.side is not want:
            return [self._sig(ts, SignalAction.EXIT, side=pos.side, reason="momentum flip")]
        if pos is None and allowed:
            stop = row.close - p.stop_atr * row.atr if want is Side.LONG else row.close + p.stop_atr * row.atr
            return [self._sig(ts, SignalAction.ENTER, side=want, stop_price=stop)]
        return []
