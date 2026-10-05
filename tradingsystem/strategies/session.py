"""Time-of-day (session) effect in gold.

Literature: Blose, Gondhalekar & Kort (2018, J. Economics & Finance) find
significantly positive *overnight* and negative *day-session* returns in COMEX
gold, the London fix and gold ETFs/miners (1985-2012), economically
significant after costs; practitioners/WGC observe gold rising in Asian hours
and falling in US hours. Hypothesised mechanism: Asian physical/retail demand
and Western day-session selling / price discovery.

Rules (fixed clock times, no fitted parameters; server time = New York + 7h):
* LONG leg  - buy at the open of server hour ``long_entry_hour`` (02 = 19:00 NY, after
  the daily re-open spread normalises), sell at the open of server hour
  ``long_exit_hour`` (15 = 08:00 NY, before the COMEX day session). No rollover,
  so no swap.
* SHORT leg - sell at server 15 (08:00 NY), cover at server 21 (14:00 NY, after the
  COMEX day session closes at 13:30 NY).
* catastrophic stop: ``stop_atr`` x daily ATR (computed from H1 bars, 24 h window).
Signals are emitted on the close of the H1 bar *before* the target hour, so the
market order fills at the target hour's open.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import pandas as pd

from tradingsystem.core.types import Side, SignalAction
from tradingsystem.signals import indicators as ind
from tradingsystem.strategies.base import PositionView, Strategy


class SessionDrift(Strategy):
    strategy_id = "session_drift_h1"
    timeframe = "H1"

    @dataclass(frozen=True)
    class Params:
        long_entry_hour: int = 2
        long_exit_hour: int = 15
        short_entry_hour: int = 15
        short_exit_hour: int = 21
        daily_atr_days: int = 20
        stop_atr: float = 1.0
        allow_long: bool = True
        allow_short: bool = True
        weekdays: tuple = (0, 1, 2, 3, 4)

    @property
    def warmup_bars(self) -> int:
        return 24 * self.params.daily_atr_days + 2

    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        f = pd.DataFrame(index=bars.index)
        f["close"] = bars["close"]
        # daily-range proxy from H1 bars: rolling 24-bar high-low, averaged over N days of bars
        rng = bars["high"].rolling(23, min_periods=20).max() - bars["low"].rolling(23, min_periods=20).min()
        f["datr"] = rng.rolling(23 * p.daily_atr_days, min_periods=23 * p.daily_atr_days // 2).mean()
        f["next_hour"] = ((bars.index + pd.Timedelta(hours=1)).hour).astype(int)
        f["next_wd"] = (bars.index + pd.Timedelta(hours=1)).weekday
        return f

    def on_bar(self, ts, row: Any, pos: Optional[PositionView]):
        p = self.params
        if np.isnan(row.datr):
            return []
        nh, wd = row.next_hour, row.next_wd
        out = []
        if pos is not None:
            ends = (pos.side is Side.LONG and nh == p.long_exit_hour) or \
                   (pos.side is Side.SHORT and nh == p.short_exit_hour) or pos.bars_held >= 20
            if not ends:
                return []
            out.append(self._sig(ts, SignalAction.EXIT, side=pos.side, reason="session end"))
        if wd not in p.weekdays:
            return out
        if p.allow_long and nh == p.long_entry_hour:
            out.append(self._sig(ts, SignalAction.ENTER, side=Side.LONG, stop_price=row.close - p.stop_atr * row.datr,
                                 reason="long session"))
        elif p.allow_short and nh == p.short_entry_hour:
            out.append(self._sig(ts, SignalAction.ENTER, side=Side.SHORT, stop_price=row.close + p.stop_atr * row.datr,
                                 reason="short session"))
        return out


class AsiaLondonSession(SessionDrift):
    """C8b - revision of C8 made on DEVELOPMENT data only (disclosed as data-driven).

    The pre-registered C8 window (long 19:00->08:00 NY) failed on DEV even before costs,
    because it mixed two opposite intraday regimes visible in the DEV hourly profile:
    gold rose during Asian hours (server 01-09 = 18:00-02:00 NY) and fell during the
    London session (server 09-15 = 02:00-08:00 NY) - the "London bias" described by
    practitioners and consistent with Asian physical demand vs. Western selling.

    * LONG leg : buy at server 02 (19:00 NY, after the re-open spread normalises),
      sell at server 09 (02:00 NY, before London opens).
    * SHORT leg: sell at server 09, cover at server 15 (08:00 NY, before the COMEX open).
    Exit-and-reverse at server 09 is handled by the execution engine (close first, then open).
    """

    strategy_id = "session_asia_london_h1"

    @dataclass(frozen=True)
    class Params(SessionDrift.Params):
        long_entry_hour: int = 2
        long_exit_hour: int = 9
        short_entry_hour: int = 9
        short_exit_hour: int = 15
