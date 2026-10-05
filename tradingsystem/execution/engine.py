"""Execution engine: turns strategy signals into broker orders.

Responsibilities
* one position per strategy, no pyramiding, no averaging down;
* duplicate-order protection: the client order id is derived from the
  signal (strategy, bar time, action, side); ids already submitted (including
  those found in the persisted ledger after a restart) are never resent;
* stop management: protective stops may only be moved in the risk-reducing
  direction;
* bounded retries for transient broker errors (requote, price changed,
  timeout); hard rejections are logged and not retried;
* stale-quote and session guards in live trading.
"""
from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

from tradingsystem.brokers.base import BrokerAdapter, OrderResult, Quote
from tradingsystem.core.types import EntryType, OrderPurpose, Side, Signal, SignalAction
from tradingsystem.data.bars import tf_minutes
from tradingsystem.portfolio.ledger import TradeLedger
from tradingsystem.portfolio.manager import PortfolioManager
from tradingsystem.risk.manager import RiskManager

log = logging.getLogger("tradingsystem.execution")


class ExecutionEngine:
    def __init__(self, broker: BrokerAdapter, risk: RiskManager, portfolio: PortfolioManager,
                 ledger: TradeLedger, max_retries: int = 3, max_quote_age_s: Optional[float] = None) -> None:
        self.broker = broker
        self.risk = risk
        self.portfolio = portfolio
        self.ledger = ledger
        self.max_retries = max_retries
        self.max_quote_age_s = max_quote_age_s
        self.sent: set[str] = ledger.submitted_ids()

    # ------------------------------------------------------------------ public
    def handle(self, sig: Signal, timeframe: str, now: Optional[pd.Timestamp] = None) -> None:
        if sig.action is SignalAction.ENTER:
            self._enter(sig, timeframe, now)
        elif sig.action is SignalAction.EXIT:
            self._exit(sig)
        elif sig.action is SignalAction.UPDATE_STOP:
            self._update_stop(sig)
        elif sig.action is SignalAction.CANCEL_ENTRY:
            for o in self.broker.pending_orders(sig.symbol):
                if o.strategy_id == sig.strategy_id and o.purpose is OrderPurpose.ENTRY:
                    self.broker.cancel(o.client_order_id)

    def flatten_all(self, reason: str) -> None:
        for o in self.broker.pending_orders():
            self.broker.cancel(o.client_order_id)
        for p in self.portfolio.positions():
            cid = f"{p.position_id}-flat"
            if cid not in self.sent:
                self.sent.add(cid)
                self._with_retries(lambda: self.broker.close_position(p.position_id, cid))
                log.warning("flatten %s: %s", p.position_id, reason)

    # ------------------------------------------------------------------ internals
    def _quote_ok(self, q: Optional[Quote], now: Optional[pd.Timestamp]) -> Optional[str]:
        if q is None:
            return "no quote"
        if self.max_quote_age_s is not None and now is not None:
            if (now - q.time).total_seconds() > self.max_quote_age_s:
                return "stale quote"
        if q.bid <= 0 or q.ask <= q.bid:
            return "invalid quote"
        return None

    def _enter(self, sig: Signal, timeframe: str, now: Optional[pd.Timestamp]) -> None:
        cid = sig.signal_id
        if cid in self.sent:
            self.ledger.record_decision(sig.timestamp, sig.strategy_id, "ENTER", False, "duplicate signal id")
            return
        if self.portfolio.position_of(sig.strategy_id) is not None:
            self.ledger.record_decision(sig.timestamp, sig.strategy_id, "ENTER", False, "already in position")
            return
        # replace resting entries on the same side (two-sided OCO brackets keep the other side)
        for o in self.broker.pending_orders(sig.symbol):
            if o.strategy_id == sig.strategy_id and o.purpose is OrderPurpose.ENTRY and o.side == sig.side:
                self.broker.cancel(o.client_order_id)
        q = self.broker.quote(sig.symbol)
        bad = self._quote_ok(q, now)
        if bad:
            self.ledger.record_decision(sig.timestamp, sig.strategy_id, "ENTER", False, bad)
            return
        spec = self.broker.instrument(sig.symbol)
        equity = self.portfolio.equity()
        expires = None
        if sig.entry_type is EntryType.STOP:
            expires = sig.timestamp + pd.Timedelta(minutes=tf_minutes(timeframe) * (1 + sig.valid_bars))
        dec = self.risk.size_entry(sig, q, spec, equity, self.portfolio.open_risk(),
                                   self.portfolio.gross_notional(q.mid), cid, expires=expires)
        self.ledger.record_decision(sig.timestamp, sig.strategy_id, "ENTER", dec.approved, dec.reason or sig.reason)
        if not dec.approved:
            return
        self.sent.add(cid)
        self.ledger.record_order(dec.order)
        res = self._with_retries(lambda: self.broker.submit(dec.order))
        if not res.accepted:
            log.info("entry rejected %s: %s", cid, res.reason)

    def _exit(self, sig: Signal) -> None:
        p = self.portfolio.position_of(sig.strategy_id)
        if p is None:
            for o in self.broker.pending_orders(sig.symbol):
                if o.strategy_id == sig.strategy_id and o.purpose is OrderPurpose.ENTRY:
                    self.broker.cancel(o.client_order_id)
            return
        cid = sig.signal_id
        if cid in self.sent:
            return
        self.sent.add(cid)
        self.ledger.record_decision(sig.timestamp, sig.strategy_id, "EXIT", True, sig.reason)
        self._with_retries(lambda: self.broker.close_position(p.position_id, cid))

    def _update_stop(self, sig: Signal) -> None:
        p = self.portfolio.position_of(sig.strategy_id)
        if p is None or sig.stop_price is None:
            return
        new = self.broker.instrument(sig.symbol).round_price(sig.stop_price)
        old = p.stop_loss
        tighter = old is None or (p.side is Side.LONG and new > old) or (p.side is Side.SHORT and new < old)
        if not tighter:
            return
        q = self.broker.quote(sig.symbol)
        if q is not None and ((p.side is Side.LONG and new >= q.bid) or (p.side is Side.SHORT and new <= q.ask)):
            # stop would be through the market: exit instead of placing an invalid stop
            self._exit(sig)
            return
        self.broker.modify_stops(p.position_id, new, p.take_profit)

    def _with_retries(self, fn) -> OrderResult:
        res = fn()
        n = 0
        while not res.accepted and res.retryable and n < self.max_retries:
            n += 1
            res = fn()
        return res
