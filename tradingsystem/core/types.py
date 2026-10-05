"""Core domain types shared by every layer (research, backtest, paper, demo, live).

Strategy code only ever produces :class:`Signal` objects. Orders, fills and
positions are owned by the risk / execution / portfolio layers, so a strategy
can never submit a broker order directly.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional


class Side(IntEnum):
    LONG = 1
    SHORT = -1

    @property
    def opposite(self) -> "Side":
        return Side.SHORT if self is Side.LONG else Side.LONG


class SignalAction(str, Enum):
    ENTER = "ENTER"            # open a new position (strategy has none)
    EXIT = "EXIT"              # close the strategy's position at next opportunity
    UPDATE_STOP = "UPDATE_STOP"  # move protective stop (only in the risk-reducing direction)
    CANCEL_ENTRY = "CANCEL_ENTRY"  # cancel a resting entry order


class EntryType(str, Enum):
    MARKET = "MARKET"  # executed at the open of the next bar (live: immediately after bar close)
    STOP = "STOP"      # resting stop order at ``entry_price`` (breakout entries)


class OrderStatus(str, Enum):
    NEW = "NEW"
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class OrderPurpose(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


@dataclass(frozen=True)
class Signal:
    """Deterministic trading intent emitted by a strategy on a closed bar."""

    strategy_id: str
    symbol: str
    timestamp: datetime          # open time (server time) of the bar that produced the signal
    action: SignalAction
    side: Optional[Side] = None
    entry_type: EntryType = EntryType.MARKET
    entry_price: Optional[float] = None    # for STOP entries
    stop_price: Optional[float] = None     # protective stop (mandatory for ENTER)
    take_profit: Optional[float] = None
    valid_bars: int = 1                    # lifetime of a resting entry order, in strategy bars
    max_hold_bars: Optional[int] = None    # time stop, in strategy bars
    reason: str = ""

    @property
    def signal_id(self) -> str:
        """Stable id: identical inputs always produce the same id (duplicate-order protection)."""
        raw = f"{self.strategy_id}|{self.symbol}|{self.timestamp.isoformat()}|{self.action.value}|{int(self.side or 0)}"
        return hashlib.sha1(raw.encode()).hexdigest()[:16]


@dataclass
class Order:
    client_order_id: str
    strategy_id: str
    symbol: str
    side: Side                      # direction of the *trade* (BUY = LONG, SELL = SHORT)
    volume: float                   # lots
    purpose: OrderPurpose
    entry_type: EntryType = EntryType.MARKET
    price: Optional[float] = None   # stop level for STOP orders
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    created: Optional[datetime] = None
    expires: Optional[datetime] = None
    max_exit_time: Optional[datetime] = None
    position_id: Optional[str] = None   # for exits
    status: OrderStatus = OrderStatus.NEW
    filled_volume: float = 0.0
    broker_order_id: Optional[str] = None
    reject_reason: str = ""
    risk_amount: float = 0.0           # account-currency risk to the stop at submission


@dataclass
class Fill:
    client_order_id: str
    strategy_id: str
    symbol: str
    side: Side
    volume: float
    price: float
    timestamp: datetime
    purpose: OrderPurpose
    commission: float = 0.0
    slippage_cost: float = 0.0       # account currency, vs. the reference price
    spread_cost: float = 0.0         # account currency, half-spread paid vs. mid
    position_id: Optional[str] = None


@dataclass
class Position:
    position_id: str
    strategy_id: str
    symbol: str
    side: Side
    volume: float
    entry_price: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    max_exit_time: Optional[datetime] = None
    initial_stop: Optional[float] = None
    risk_amount: float = 0.0
    swap: float = 0.0
    commission: float = 0.0
    spread_cost: float = 0.0
    slippage_cost: float = 0.0
    bars_held: int = 0
    mae: float = 0.0   # max adverse excursion, price units
    mfe: float = 0.0   # max favourable excursion, price units

    def unrealized(self, bid: float, ask: float, contract_size: float) -> float:
        px = bid if self.side is Side.LONG else ask
        return (px - self.entry_price) * int(self.side) * self.volume * contract_size


@dataclass
class Trade:
    """A closed round trip, as recorded by the trade ledger."""

    position_id: str
    strategy_id: str
    symbol: str
    side: Side
    volume: float
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    exit_reason: str
    pnl_gross: float            # price PnL at mid prices (before spread/slippage/commission/swap)
    spread_cost: float
    slippage_cost: float
    commission: float
    swap: float
    pnl_net: float
    risk_amount: float
    initial_stop: Optional[float] = None
    bars_held: int = 0
    mae: float = 0.0
    mfe: float = 0.0
    tags: dict = field(default_factory=dict)

    @property
    def r_multiple(self) -> float:
        return self.pnl_net / self.risk_amount if self.risk_amount > 0 else float("nan")
