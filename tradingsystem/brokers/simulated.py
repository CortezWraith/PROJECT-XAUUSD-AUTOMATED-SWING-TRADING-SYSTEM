"""Simulated broker used for backtests and paper trading.

Execution conventions (conservative by construction):

* Signals are produced on bar close; MARKET orders fill at the *next* bar's
  open (ask for buys, bid for sells) plus slippage. ``delay_bars`` adds extra
  bars of latency for the entry-delay robustness test.
* STOP entries fill when the bar trades through the level, at
  ``max(level, open)`` for buys (gaps fill at the worse price) plus stop slippage.
* Protective stops behave like broker-side stops: triggered on bid (longs) or
  ask (shorts), filled at the worse of stop and open, plus stop slippage.
* If a stop-loss and take-profit are both inside one bar, the stop is assumed
  to have been hit first. A position opened inside a bar can be stopped out in
  the same bar.
* Swap is charged at every server-midnight rollover (17:00 New York), triple
  on the configured weekday.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from tradingsystem.brokers.base import AccountInfo, BrokerAdapter, BrokerEvents, OrderResult, Quote
from tradingsystem.core.types import EntryType, Fill, Order, OrderPurpose, OrderStatus, Position, Side, Trade
from tradingsystem.costs.model import CostModel, RateCurve
from tradingsystem.data.instrument import InstrumentSpec, XAUUSD


@dataclass
class _Bar:
    ts: pd.Timestamp
    ob: float
    hb: float
    lb: float
    cb: float
    oa: float
    ha: float
    la: float
    ca: float


@dataclass
class _PosState:
    pos: Position
    entry_mid: float
    tags: dict


class SimBroker(BrokerAdapter):
    name = "sim"

    def __init__(self, initial_balance: float = 100_000.0, cost: Optional[CostModel] = None,
                 rates: Optional[RateCurve] = None, spec: InstrumentSpec = XAUUSD,
                 delay_bars: int = 0, fill_market_immediately: bool = False,
                 max_fill_spread_bps: float = 4.0, max_deferrals: int = 3) -> None:
        self.balance = initial_balance
        self.cost = cost or CostModel()
        self.rates = rates or RateCurve()
        self.spec = spec
        self.delay_bars = delay_bars
        self.fill_market_immediately = fill_market_immediately   # paper trading on live quotes
        # spread guard (same policy as live execution): market orders are deferred bar by bar
        # while the quoted spread is abnormally wide (e.g. right after the daily re-open)
        self.max_fill_spread_bps = max_fill_spread_bps
        self.max_deferrals = max_deferrals
        self._deferrals: dict[str, int] = {}
        self._positions: dict[str, _PosState] = {}
        self._pending: dict[str, Order] = {}
        self._market_queue: list[tuple[int, Order]] = []
        self._bar_no = 0
        self._last: Optional[_Bar] = None
        self._events = BrokerEvents()
        self._ids = itertools.count(1)
        self.connected = True

    # ------------------------------------------------------------------ adapter API
    def connect(self) -> bool:
        self.connected = True
        return True

    def is_connected(self) -> bool:
        return self.connected

    def server_time(self) -> pd.Timestamp:
        return self._last.ts if self._last else pd.Timestamp(0)

    def account(self) -> AccountInfo:
        eq = self.balance + self.unrealized()
        return AccountInfo(balance=self.balance, equity=eq, margin_free=eq)

    def instrument(self, symbol: str) -> InstrumentSpec:
        return self.spec

    def quote(self, symbol: str) -> Optional[Quote]:
        if self._last is None:
            return None
        b, a = self.cost.effective_quotes(self._last.cb, self._last.ca)
        return Quote(symbol, b, a, self._last.ts)

    def submit(self, order: Order) -> OrderResult:
        if order.volume < self.spec.min_lot - 1e-12:
            order.status = OrderStatus.REJECTED
            return OrderResult(False, order.client_order_id, reason="volume below min lot")
        order.status = OrderStatus.SUBMITTED
        if order.entry_type is EntryType.STOP:
            self._pending[order.client_order_id] = order
            return OrderResult(True, order.client_order_id, broker_order_id=order.client_order_id)
        if self.fill_market_immediately and self._last is not None:
            fill = self._fill_market(order, self._last, at_close=True)
            return OrderResult(True, order.client_order_id, fills=[fill] if fill else [])
        self._market_queue.append((self._bar_no + self.delay_bars, order))
        return OrderResult(True, order.client_order_id, broker_order_id=order.client_order_id)

    def cancel(self, client_order_id: str) -> bool:
        o = self._pending.pop(client_order_id, None)
        if o is not None:
            o.status = OrderStatus.CANCELLED
            return True
        before = len(self._market_queue)
        self._market_queue = [(n, o) for n, o in self._market_queue if o.client_order_id != client_order_id]
        return len(self._market_queue) != before

    def modify_stops(self, position_id: str, stop_loss: Optional[float], take_profit: Optional[float]) -> bool:
        st = self._positions.get(position_id)
        if st is None:
            return False
        st.pos.stop_loss = stop_loss
        st.pos.take_profit = take_profit
        return True

    def close_position(self, position_id: str, client_order_id: str) -> OrderResult:
        st = self._positions.get(position_id)
        if st is None:
            return OrderResult(False, client_order_id, reason="unknown position")
        o = Order(client_order_id=client_order_id, strategy_id=st.pos.strategy_id, symbol=st.pos.symbol,
                  side=st.pos.side.opposite, volume=st.pos.volume, purpose=OrderPurpose.EXIT,
                  position_id=position_id)
        return self.submit(o)

    def open_positions(self, symbol: Optional[str] = None) -> list[Position]:
        return [s.pos for s in self._positions.values() if symbol is None or s.pos.symbol == symbol]

    def pending_orders(self, symbol: Optional[str] = None) -> list[Order]:
        out = list(self._pending.values()) + [o for _, o in self._market_queue]
        return [o for o in out if symbol is None or o.symbol == symbol]

    def poll_events(self) -> BrokerEvents:
        ev, self._events = self._events, BrokerEvents()
        return ev

    # ------------------------------------------------------------------ simulation
    def unrealized(self) -> float:
        if self._last is None:
            return 0.0
        b, a = self.cost.effective_quotes(self._last.cb, self._last.ca)
        return sum(s.pos.unrealized(b, a, self.spec.contract_size) for s in self._positions.values())

    def process_quote(self, ts: pd.Timestamp, bid: float, ask: float) -> None:
        """Paper trading: treat a live quote as a degenerate bar."""
        self.process_bar(ts, bid, bid, bid, bid, ask, ask, ask, ask)

    def process_bar(self, ts: pd.Timestamp, ob: float, hb: float, lb: float, cb: float,
                    oa: float, ha: float, la: float, ca: float) -> None:
        bar = _Bar(ts, ob, hb, lb, cb, oa, ha, la, ca)
        if self._last is not None and ts.normalize() != self._last.ts.normalize():
            self._rollover(self._last)
        self._bar_no += 1
        # 1) queued market orders at the open
        due = [(n, o) for n, o in self._market_queue if n < self._bar_no]
        self._market_queue = [(n, o) for n, o in self._market_queue if n >= self._bar_no]
        for n, o in due:
            raw_bps = (bar.oa - bar.ob) / bar.ob * 1e4 if bar.ob > 0 else 0.0
            k = self._deferrals.get(o.client_order_id, 0)
            if raw_bps > self.max_fill_spread_bps and k < self.max_deferrals:
                self._deferrals[o.client_order_id] = k + 1
                self._market_queue.append((self._bar_no, o))
                continue
            self._deferrals.pop(o.client_order_id, None)
            self._fill_market(o, bar, at_close=False)
        # 2) resting stop entries
        for cid in list(self._pending):
            o = self._pending[cid]
            if o.expires is not None and ts >= o.expires:
                o.status = OrderStatus.EXPIRED
                del self._pending[cid]
                self._events.cancelled.append(cid)
                continue
            self._try_stop_entry(o, bar)
        # OCO: a filled entry cancels the strategy's other resting entries
        if self._pending:
            held = {st.pos.strategy_id for st in self._positions.values()}
            for cid in [c for c, o in self._pending.items() if o.strategy_id in held]:
                self._pending.pop(cid).status = OrderStatus.CANCELLED
                self._events.cancelled.append(cid)
        # 3) protective stops / targets
        for pid in list(self._positions):
            self._check_exits(pid, bar)
        # 4) excursions
        mb = 0.5 * (bar.hb + bar.ha)
        ml = 0.5 * (bar.lb + bar.la)
        for st in self._positions.values():
            p = st.pos
            if p.side is Side.LONG:
                p.mfe = max(p.mfe, mb - p.entry_price)
                p.mae = max(p.mae, p.entry_price - ml)
            else:
                p.mfe = max(p.mfe, p.entry_price - ml)
                p.mae = max(p.mae, mb - p.entry_price)
        self._last = bar

    # ------------------------------------------------------------------ internals
    def _eff(self, bid: float, ask: float) -> tuple[float, float]:
        return self.cost.effective_quotes(bid, ask)

    def _open_position(self, o: Order, price: float, mid: float, ts: pd.Timestamp, slip: float, is_stop: bool) -> Fill:
        cs = self.spec.contract_size
        commission = self.cost.commission(o.volume)
        pid = f"P{next(self._ids)}"
        pos = Position(position_id=pid, strategy_id=o.strategy_id, symbol=o.symbol, side=o.side, volume=o.volume,
                       entry_price=price, entry_time=ts, stop_loss=o.stop_loss, take_profit=o.take_profit,
                       initial_stop=o.stop_loss, risk_amount=o.risk_amount, commission=commission,
                       spread_cost=abs(price - mid) * o.volume * cs - slip * o.volume * cs,
                       slippage_cost=slip * o.volume * cs, max_exit_time=o.max_exit_time)
        self.balance -= commission
        self._positions[pid] = _PosState(pos=pos, entry_mid=mid, tags={"entry_type": o.entry_type.value})
        o.status = OrderStatus.FILLED
        o.filled_volume = o.volume
        f = Fill(o.client_order_id, o.strategy_id, o.symbol, o.side, o.volume, price, ts, OrderPurpose.ENTRY,
                 commission=commission, slippage_cost=slip * o.volume * cs,
                 spread_cost=pos.spread_cost, position_id=pid)
        self._events.fills.append(f)
        return f

    def _close_position(self, pid: str, price: float, mid: float, ts: pd.Timestamp, slip: float, reason: str,
                        cid: str) -> Fill:
        st = self._positions.pop(pid)
        p = st.pos
        cs = self.spec.contract_size
        commission = self.cost.commission(p.volume)
        self.balance -= commission
        price_pnl = (price - p.entry_price) * int(p.side) * p.volume * cs
        self.balance += price_pnl
        exit_spread = abs(price - mid) * p.volume * cs - slip * p.volume * cs
        spread_cost = p.spread_cost + exit_spread
        slippage_cost = p.slippage_cost + slip * p.volume * cs
        commission_total = p.commission + commission
        gross = (mid - st.entry_mid) * int(p.side) * p.volume * cs
        net = price_pnl - commission_total + p.swap
        tr = Trade(position_id=pid, strategy_id=p.strategy_id, symbol=p.symbol, side=p.side, volume=p.volume,
                   entry_time=p.entry_time, entry_price=p.entry_price, exit_time=ts, exit_price=price,
                   exit_reason=reason, pnl_gross=gross, spread_cost=spread_cost, slippage_cost=slippage_cost,
                   commission=commission_total, swap=p.swap, pnl_net=net, risk_amount=p.risk_amount,
                   initial_stop=p.initial_stop, bars_held=p.bars_held, mae=p.mae, mfe=p.mfe, tags=st.tags)
        f = Fill(cid, p.strategy_id, p.symbol, p.side.opposite, p.volume, price, ts, OrderPurpose.EXIT,
                 commission=commission, slippage_cost=slip * p.volume * cs, spread_cost=exit_spread,
                 position_id=pid)
        self._events.fills.append(f)
        self._events.closed_trades.append(tr)
        return f

    def _fill_market(self, o: Order, bar: _Bar, at_close: bool) -> Optional[Fill]:
        b, a = self._eff(bar.cb, bar.ca) if at_close else self._eff(bar.ob, bar.oa)
        mid = 0.5 * (b + a)
        if o.purpose is OrderPurpose.EXIT:
            st = self._positions.get(o.position_id or "")
            if st is None:
                o.status = OrderStatus.CANCELLED
                return None
            # closing a long sells at bid, closing a short buys at ask
            ref = b if st.pos.side is Side.LONG else a
            slip = self.cost.slippage(ref, is_stop=False)
            price = ref - slip if st.pos.side is Side.LONG else ref + slip
            o.status = OrderStatus.FILLED
            return self._close_position(st.pos.position_id, price, mid, bar.ts, slip, "signal_exit", o.client_order_id)
        ref = a if o.side is Side.LONG else b
        slip = self.cost.slippage(ref, is_stop=False)
        price = ref + slip if o.side is Side.LONG else ref - slip
        # a protective stop that is already through the market would be rejected by a real broker
        if o.stop_loss is not None and ((o.side is Side.LONG and o.stop_loss >= b) or (o.side is Side.SHORT and o.stop_loss <= a)):
            o.status = OrderStatus.REJECTED
            o.reject_reason = "stop through market at fill"
            self._events.cancelled.append(o.client_order_id)
            return None
        return self._open_position(o, price, mid, bar.ts, slip, is_stop=False)

    def _try_stop_entry(self, o: Order, bar: _Bar) -> None:
        lvl = o.price
        if o.side is Side.LONG:
            _, a_open = self._eff(bar.ob, bar.oa)
            _, a_high = self._eff(bar.hb, bar.ha)
            if a_high < lvl:
                return
            ref = max(lvl, a_open)
            slip = self.cost.slippage(ref, is_stop=True)
            price = ref + slip
        else:
            b_open, _ = self._eff(bar.ob, bar.oa)
            b_low, _ = self._eff(bar.lb, bar.la)
            if b_low > lvl:
                return
            ref = min(lvl, b_open)
            slip = self.cost.slippage(ref, is_stop=True)
            price = ref - slip
        del self._pending[o.client_order_id]
        # mid at the trigger: quoted price minus half the effective spread
        hs = 0.5 * (bar.oa - bar.ob) * self.cost.multiplier
        mid = ref - hs if o.side is Side.LONG else ref + hs
        self._open_position(o, price, mid, bar.ts, slip, is_stop=True)

    def _check_exits(self, pid: str, bar: _Bar) -> None:
        st = self._positions[pid]
        p = st.pos
        b_open, a_open = self._eff(bar.ob, bar.oa)
        b_low, a_low = self._eff(bar.lb, bar.la)
        b_high, a_high = self._eff(bar.hb, bar.ha)
        hs = 0.5 * (bar.oa - bar.ob) * self.cost.multiplier
        cid = f"{pid}-x"
        if p.side is Side.LONG:
            if p.stop_loss is not None and b_low <= p.stop_loss:
                ref = min(p.stop_loss, b_open)
                slip = self.cost.slippage(ref, is_stop=True)
                self._close_position(pid, ref - slip, ref + hs, bar.ts, slip, "stop_loss", cid)
            elif p.take_profit is not None and b_high >= p.take_profit:
                ref = max(p.take_profit, b_open)
                self._close_position(pid, ref, ref + hs, bar.ts, 0.0, "take_profit", cid)
        else:
            if p.stop_loss is not None and a_high >= p.stop_loss:
                ref = max(p.stop_loss, a_open)
                slip = self.cost.slippage(ref, is_stop=True)
                self._close_position(pid, ref + slip, ref - hs, bar.ts, slip, "stop_loss", cid)
            elif p.take_profit is not None and a_low <= p.take_profit:
                ref = min(p.take_profit, a_open)
                self._close_position(pid, ref, ref - hs, bar.ts, 0.0, "take_profit", cid)

    def _rollover(self, last: _Bar) -> None:
        if not self._positions:
            return
        rate = self.rates.rate(last.ts.normalize() - pd.Timedelta(days=1))
        wd = last.ts.weekday()
        mid = 0.5 * (last.cb + last.ca)
        for st in self._positions.values():
            p = st.pos
            sw = self.cost.nightly_swap(p.side, p.volume, mid, rate, wd)
            p.swap += sw
            self.balance += sw
