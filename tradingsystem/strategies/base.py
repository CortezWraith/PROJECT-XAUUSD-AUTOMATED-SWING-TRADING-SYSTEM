"""Strategy interface.

A strategy is a pure, deterministic function of closed bars and its own
position state. It has two methods:

* ``features(bars)``  vectorised, *causal* feature computation on mid prices.
  The backtester calls it once on the full history; the live runner calls it
  on a rolling window and uses the last row. A parity test guarantees both give
  the same last row.
* ``on_bar(ts, row, position)``  decision logic for one closed bar, returning
  a list of :class:`~tradingsystem.core.types.Signal`.

Strategies never size positions, never see account equity and never talk to a
broker. That is what makes the same code usable in backtest, paper, demo and
live execution.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Optional

import pandas as pd

from tradingsystem.core.types import Side, Signal, SignalAction


@dataclass(frozen=True)
class PositionView:
    """Read-only snapshot of a strategy's open position (or pending entry) given to on_bar."""

    side: Side
    entry_price: float
    entry_time: pd.Timestamp
    bars_held: int
    stop_loss: Optional[float]
    initial_stop: Optional[float]
    take_profit: Optional[float] = None


class Strategy(ABC):
    #: unique id; also used as MT5 magic-number seed and in client order ids
    strategy_id: str = "base"
    timeframe: str = "H1"
    symbol: str = "XAUUSD"

    def __init__(self, **params: Any) -> None:
        self.params = self.Params(**params) if hasattr(self, "Params") else None

    # ------------------------------------------------------------------ interface
    @property
    @abstractmethod
    def warmup_bars(self) -> int:
        """Number of closed bars required before the first valid signal."""

    @abstractmethod
    def features(self, bars: pd.DataFrame) -> pd.DataFrame:
        """Causal features; index identical to ``bars``."""

    @abstractmethod
    def on_bar(self, ts: pd.Timestamp, row: Any, position: Optional[PositionView]) -> list[Signal]:
        """Decide on the close of bar ``ts``. ``row`` is a feature-row namedtuple."""

    # ------------------------------------------------------------------ helpers
    def describe(self) -> dict:
        return {"strategy_id": self.strategy_id, "timeframe": self.timeframe,
                "params": asdict(self.params) if self.params is not None else {}}

    def _sig(self, ts: pd.Timestamp, action: SignalAction, **kw: Any) -> Signal:
        return Signal(strategy_id=self.strategy_id, symbol=self.symbol, timestamp=ts, action=action, **kw)
