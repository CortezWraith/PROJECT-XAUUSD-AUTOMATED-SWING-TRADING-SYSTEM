"""Portfolio manager: the system's view of positions, exposure and equity.

The broker is the source of truth for open positions (in live trading after a
reconnect the portfolio is rebuilt from the broker, never from memory). The
portfolio manager adds strategy attribution, bar counting, exposure numbers
for the risk manager and the equity curve.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

from tradingsystem.brokers.base import BrokerAdapter
from tradingsystem.core.types import EntryType, Order, OrderPurpose, Position, Side
from tradingsystem.portfolio.ledger import TradeLedger
from tradingsystem.risk.manager import RiskManager
from tradingsystem.strategies.base import PositionView


class PortfolioManager:
    def __init__(self, broker: BrokerAdapter, ledger: TradeLedger, risk: RiskManager, symbol: str = "XAUUSD") -> None:
        self.broker = broker
        self.ledger = ledger
        self.risk = risk
        self.symbol = symbol
        self.spec = broker.instrument(symbol)
        self.bars_held: dict[str, int] = {}
        self.equity_curve: list[tuple[pd.Timestamp, float]] = []
        self.exposure_curve: list[tuple[pd.Timestamp, float]] = []

    # ------------------------------------------------------------------ queries
    def positions(self) -> list[Position]:
        return self.broker.open_positions(self.symbol)

    def position_of(self, strategy_id: str) -> Optional[Position]:
        for p in self.positions():
            if p.strategy_id == strategy_id:
                return p
        return None

    def pending_entry_of(self, strategy_id: str) -> Optional[Order]:
        for o in self.broker.pending_orders(self.symbol):
            if o.strategy_id == strategy_id and o.purpose is OrderPurpose.ENTRY:
                return o
        return None

    def position_view(self, strategy_id: str) -> Optional[PositionView]:
        p = self.position_of(strategy_id)
        if p is None:
            return None
        return PositionView(side=p.side, entry_price=p.entry_price, entry_time=p.entry_time,
                            bars_held=self.bars_held.get(p.position_id, 0), stop_loss=p.stop_loss,
                            initial_stop=p.initial_stop, take_profit=p.take_profit)

    def open_risk(self) -> float:
        cs = self.spec.contract_size
        total = 0.0
        for p in self.positions():
            if p.stop_loss is None:
                total += p.risk_amount
                continue
            total += max(0.0, (p.entry_price - p.stop_loss) * int(p.side)) * p.volume * cs
        for o in self.broker.pending_orders(self.symbol):
            if o.purpose is OrderPurpose.ENTRY:
                total += o.risk_amount
        return total

    def gross_notional(self, price: float) -> float:
        return sum(self.spec.notional(p.volume, price) for p in self.positions())

    def net_lots(self) -> float:
        return sum(int(p.side) * p.volume for p in self.positions())

    def equity(self) -> float:
        return self.broker.account().equity

    # ------------------------------------------------------------------ updates
    def on_strategy_bar(self, strategy_id: str) -> None:
        for p in self.positions():
            if p.strategy_id == strategy_id:
                self.bars_held[p.position_id] = self.bars_held.get(p.position_id, 0) + 1
                p.bars_held = self.bars_held[p.position_id]

    def sync(self) -> None:
        ev = self.broker.poll_events()
        for f in ev.fills:
            self.ledger.record_fill(f)
        for t in ev.closed_trades:
            t.bars_held = self.bars_held.pop(t.position_id, t.bars_held)
            self.ledger.record_trade(t)
            self.risk.on_trade_closed(t.strategy_id, t.pnl_net, self.equity())

    def mark(self, ts: pd.Timestamp) -> None:
        eq = self.equity()
        self.equity_curve.append((ts, eq))
        self.exposure_curve.append((ts, self.net_lots()))
