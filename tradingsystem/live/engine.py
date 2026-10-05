"""TradingEngine: the single orchestration path used by backtest, paper, demo and live.

    MarketData -> Strategy.features/on_bar -> Signal -> RiskManager -> ExecutionEngine
               -> BrokerAdapter -> fills/positions -> PortfolioManager/TradeLedger -> Monitor

Only the *driver* differs between modes: the backtest driver replays
historical bars into a :class:`SimBroker`; the live driver polls MT5 for newly
closed bars and quotes. Strategy, risk, execution and portfolio code is
identical.
"""
from __future__ import annotations

import logging
from typing import Any, Optional, Sequence

import pandas as pd

from tradingsystem.brokers.base import BrokerAdapter
from tradingsystem.execution.engine import ExecutionEngine
from tradingsystem.monitoring.monitor import Monitor
from tradingsystem.portfolio.ledger import TradeLedger
from tradingsystem.portfolio.manager import PortfolioManager
from tradingsystem.risk.manager import RiskManager
from tradingsystem.strategies.base import Strategy

log = logging.getLogger("tradingsystem.engine")


class TradingEngine:
    def __init__(self, strategies: Sequence[Strategy], broker: BrokerAdapter, risk: RiskManager,
                 ledger: Optional[TradeLedger] = None, monitor: Optional[Monitor] = None,
                 symbol: str = "XAUUSD", max_quote_age_s: Optional[float] = None) -> None:
        self.strategies = list(strategies)
        self.broker = broker
        self.risk = risk
        self.ledger = ledger or TradeLedger()
        self.portfolio = PortfolioManager(broker, self.ledger, risk, symbol)
        self.execution = ExecutionEngine(broker, risk, self.portfolio, self.ledger, max_quote_age_s=max_quote_age_s)
        self.monitor = monitor
        self._halt_handled = False

    def on_clock(self, ts: pd.Timestamp) -> None:
        """Called after the broker state advanced (backtest: after each base bar; live: each poll)."""
        self.portfolio.sync()
        eq = self.portfolio.equity()
        self.risk.on_time(ts, eq)
        if self.risk.state.halted and not self._halt_handled:
            self._halt_handled = True
            self.execution.flatten_all(self.risk.state.halt_reason)
            self.portfolio.sync()
            if self.monitor:
                self.monitor.alert("HALT", self.risk.state.halt_reason)

    def on_bar_closed(self, strategy: Strategy, bar_ts: pd.Timestamp, row: Any,
                      now: Optional[pd.Timestamp] = None) -> None:
        """Run one strategy on one closed bar (``bar_ts`` = open time of that bar)."""
        self.portfolio.on_strategy_bar(strategy.strategy_id)
        view = self.portfolio.position_view(strategy.strategy_id)
        try:
            signals = strategy.on_bar(bar_ts, row, view)
        except Exception as exc:  # a strategy bug must never take the engine down
            log.exception("strategy %s failed on %s", strategy.strategy_id, bar_ts)
            if self.monitor:
                self.monitor.alert("STRATEGY_ERROR", f"{strategy.strategy_id}: {exc}")
            return
        for s in signals:
            self.execution.handle(s, strategy.timeframe, now=now)
        self.portfolio.sync()

    def mark(self, ts: pd.Timestamp) -> None:
        self.portfolio.mark(ts)
        if self.monitor:
            self.monitor.on_mark(ts, self.portfolio, self.risk)
