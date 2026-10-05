"""Broker adapter interface.

The rest of the system talks to brokers only through this interface, so the
MetaTrader 5 adapter can later be swapped for another broker (cTrader, FIX,
Interactive Brokers, ...) or another instrument without touching strategies,
risk or portfolio code.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from tradingsystem.core.types import Fill, Order, Position, Trade
from tradingsystem.data.instrument import InstrumentSpec


@dataclass
class Quote:
    symbol: str
    bid: float
    ask: float
    time: pd.Timestamp          # server time of the last tick

    @property
    def mid(self) -> float:
        return 0.5 * (self.bid + self.ask)

    @property
    def spread(self) -> float:
        return self.ask - self.bid


@dataclass
class AccountInfo:
    balance: float
    equity: float
    margin_free: float
    currency: str = "USD"
    leverage: float = 100.0


@dataclass
class OrderResult:
    accepted: bool
    client_order_id: str
    broker_order_id: Optional[str] = None
    fills: list[Fill] = field(default_factory=list)
    retryable: bool = False
    reason: str = ""


@dataclass
class BrokerEvents:
    """Things that happened at the broker since the last poll (SL/TP hits, pending fills, swaps)."""

    fills: list[Fill] = field(default_factory=list)
    closed_trades: list[Trade] = field(default_factory=list)
    cancelled: list[str] = field(default_factory=list)


class BrokerAdapter(ABC):
    name: str = "abstract"

    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    def server_time(self) -> pd.Timestamp: ...

    @abstractmethod
    def account(self) -> AccountInfo: ...

    @abstractmethod
    def instrument(self, symbol: str) -> InstrumentSpec: ...

    @abstractmethod
    def quote(self, symbol: str) -> Optional[Quote]: ...

    @abstractmethod
    def submit(self, order: Order) -> OrderResult: ...

    @abstractmethod
    def cancel(self, client_order_id: str) -> bool: ...

    @abstractmethod
    def modify_stops(self, position_id: str, stop_loss: Optional[float], take_profit: Optional[float]) -> bool: ...

    @abstractmethod
    def close_position(self, position_id: str, client_order_id: str) -> OrderResult: ...

    @abstractmethod
    def open_positions(self, symbol: Optional[str] = None) -> list[Position]: ...

    @abstractmethod
    def pending_orders(self, symbol: Optional[str] = None) -> list[Order]: ...

    @abstractmethod
    def poll_events(self) -> BrokerEvents: ...
