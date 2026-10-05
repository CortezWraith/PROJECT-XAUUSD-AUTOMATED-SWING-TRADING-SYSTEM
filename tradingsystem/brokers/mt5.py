"""MetaTrader 5 broker adapter and market-data source.

Requires the official ``MetaTrader5`` Python package (Windows, or Wine) and a
running MT5 terminal logged into the broker. The package is imported lazily so
the rest of the system (research, backtests, tests) runs anywhere.

Broker-reality handling
-----------------------
* contract size, min lot, lot step, max lot, tick size and stops level are
  read from ``symbol_info`` at connect time - never hard coded;
* filling mode is negotiated from the symbol's allowed modes (FOK/IOC/RETURN);
* retcodes are classified into success / retryable (requote, price changed,
  timeout, connection, too many requests) / hard reject;
* partial fills (IOC) are recorded at the actually filled volume;
* every order carries a magic number per strategy and the client order id in
  the comment; before sending an entry the adapter checks open positions and
  pending orders for the same id (duplicate protection that survives a lost
  local ledger);
* quotes older than ``max_quote_age_s`` are treated as stale;
* broker server time is mapped to the system's server-time convention
  (NY+7) with ``server_offset_hours`` (0 for GMT+2/+3 "New York close" brokers);
* ``ensure_connected`` re-initialises the terminal with exponential backoff;
  after a reconnect the engine reconciles positions from the broker.
"""
from __future__ import annotations

import hashlib
import logging
import time
from typing import Any, Optional

import numpy as np
import pandas as pd

from tradingsystem.brokers.base import AccountInfo, BrokerAdapter, BrokerEvents, OrderResult, Quote
from tradingsystem.core.types import EntryType, Fill, Order, OrderPurpose, OrderStatus, Position, Side, Trade
from tradingsystem.data.instrument import InstrumentSpec
from tradingsystem.data.market_data import MarketData

log = logging.getLogger("tradingsystem.mt5")

RETRYABLE = {10004, 10020, 10021, 10012, 10031, 10024}   # requote, price changed, price off, timeout, no connection, too many requests
SUCCESS = {10008, 10009, 10010}                          # placed, done, done partially
TF_MAP = {"M1": "TIMEFRAME_M1", "M5": "TIMEFRAME_M5", "M15": "TIMEFRAME_M15", "M30": "TIMEFRAME_M30",
          "H1": "TIMEFRAME_H1", "H2": "TIMEFRAME_H2", "H3": "TIMEFRAME_H3", "H4": "TIMEFRAME_H4",
          "H6": "TIMEFRAME_H6", "D1": "TIMEFRAME_D1"}


def magic_for(strategy_id: str, base: int = 770000) -> int:
    return base + int(hashlib.sha1(strategy_id.encode()).hexdigest(), 16) % 10000


def _mt5():
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on platform
        raise RuntimeError("MetaTrader5 package not available: pip install MetaTrader5 (Windows)") from exc
    return mt5


class MT5Broker(BrokerAdapter):
    name = "mt5"

    def __init__(self, login: Optional[int] = None, password: Optional[str] = None, server: Optional[str] = None,
                 terminal_path: Optional[str] = None, strategies: Optional[list[str]] = None,
                 server_offset_hours: int = 0, deviation_points: int = 30, max_quote_age_s: float = 30.0,
                 expect_demo: bool = True) -> None:
        self.login, self.password, self.server, self.path = login, password, server, terminal_path
        self.server_offset = pd.Timedelta(hours=server_offset_hours)
        self.deviation = deviation_points
        self.max_quote_age_s = max_quote_age_s
        self.expect_demo = expect_demo
        self.magic_to_strategy = {magic_for(s): s for s in (strategies or [])}
        self._specs: dict[str, InstrumentSpec] = {}
        self._filling: dict[str, int] = {}
        self._seen_deals: set[int] = set()
        self._last_deal_check = pd.Timestamp.utcnow() - pd.Timedelta(days=1)
        self.mt5 = None

    # ------------------------------------------------------------------ connection
    def connect(self) -> bool:
        mt5 = self.mt5 = _mt5()
        kw: dict[str, Any] = {}
        if self.path:
            kw["path"] = self.path
        if self.login:
            kw.update(login=int(self.login), password=self.password, server=self.server)
        if not mt5.initialize(**kw):
            log.error("MT5 initialize failed: %s", mt5.last_error())
            return False
        acc = mt5.account_info()
        if acc is None:
            return False
        is_demo = acc.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO
        if self.expect_demo and not is_demo:
            mt5.shutdown()
            raise RuntimeError("refusing to trade: account is REAL but configuration expects DEMO")
        return True

    def is_connected(self) -> bool:
        if self.mt5 is None:
            return False
        info = self.mt5.terminal_info()
        return bool(info and info.connected and self.mt5.account_info() is not None)

    def ensure_connected(self, max_attempts: int = 6) -> bool:
        delay = 1.0
        for _ in range(max_attempts):
            if self.is_connected():
                return True
            try:
                if self.mt5 is not None:
                    self.mt5.shutdown()
                if self.connect():
                    return True
            except RuntimeError:
                raise
            except Exception:  # pragma: no cover
                log.exception("reconnect failed")
            time.sleep(delay)
            delay = min(delay * 2, 60)
        return False

    def _to_server(self, epoch_s: float) -> pd.Timestamp:
        return pd.Timestamp(epoch_s, unit="s") + self.server_offset

    def server_time(self) -> pd.Timestamp:
        q = self.quote("XAUUSD")
        return q.time if q else pd.Timestamp.utcnow().tz_localize(None)

    # ------------------------------------------------------------------ info
    def account(self) -> AccountInfo:
        a = self.mt5.account_info()
        return AccountInfo(balance=a.balance, equity=a.equity, margin_free=a.margin_free, currency=a.currency,
                           leverage=float(a.leverage))

    def instrument(self, symbol: str) -> InstrumentSpec:
        if symbol not in self._specs:
            mt5 = self.mt5
            if not mt5.symbol_select(symbol, True):
                raise RuntimeError(f"symbol {symbol} not available")
            i = mt5.symbol_info(symbol)
            self._specs[symbol] = InstrumentSpec(symbol=symbol, contract_size=i.trade_contract_size, min_lot=i.volume_min,
                                                 lot_step=i.volume_step, max_lot=i.volume_max, tick_size=i.trade_tick_size or i.point,
                                                 stops_level_points=i.trade_stops_level,
                                                 swap_triple_weekday=(i.swap_rollover3days - 1) % 7)
            fm = i.filling_mode
            self._filling[symbol] = mt5.ORDER_FILLING_IOC if fm & 2 else (mt5.ORDER_FILLING_FOK if fm & 1 else mt5.ORDER_FILLING_RETURN)
        return self._specs[symbol]

    def quote(self, symbol: str) -> Optional[Quote]:
        t = self.mt5.symbol_info_tick(symbol)
        if t is None or t.bid <= 0:
            return None
        return Quote(symbol, t.bid, t.ask, self._to_server(t.time_msc / 1000.0))

    def quote_is_stale(self, q: Quote, now_utc: Optional[pd.Timestamp] = None) -> bool:
        # compare the tick age using the terminal's own clock to avoid local clock drift
        info = self.mt5.symbol_info(q.symbol)
        last = self._to_server(info.time) if info else q.time
        return (last - q.time).total_seconds() > self.max_quote_age_s

    # ------------------------------------------------------------------ orders
    def _already_sent(self, symbol: str, cid: str) -> bool:
        tag = f"XTS|{cid}"
        for p in self.mt5.positions_get(symbol=symbol) or ():
            if p.comment == tag:
                return True
        for o in self.mt5.orders_get(symbol=symbol) or ():
            if o.comment == tag:
                return True
        return False

    def _send(self, req: dict) -> Any:
        res = self.mt5.order_send(req)
        if res is None:
            return None
        return res

    def submit(self, order: Order) -> OrderResult:
        mt5 = self.mt5
        spec = self.instrument(order.symbol)
        if order.purpose is OrderPurpose.ENTRY and self._already_sent(order.symbol, order.client_order_id):
            return OrderResult(True, order.client_order_id, reason="already at broker (duplicate suppressed)")
        q = self.quote(order.symbol)
        if q is None:
            return OrderResult(False, order.client_order_id, retryable=True, reason="no quote")
        buy = order.side is Side.LONG
        req = {"symbol": order.symbol, "volume": float(order.volume), "magic": magic_for(order.strategy_id),
               "comment": f"XTS|{order.client_order_id}"[:31], "type_time": mt5.ORDER_TIME_GTC,
               "type_filling": self._filling.get(order.symbol, mt5.ORDER_FILLING_IOC), "deviation": self.deviation}
        if order.stop_loss:
            req["sl"] = spec.round_price(order.stop_loss)
        if order.take_profit:
            req["tp"] = spec.round_price(order.take_profit)
        if order.entry_type is EntryType.STOP:
            req.update(action=mt5.TRADE_ACTION_PENDING, type=mt5.ORDER_TYPE_BUY_STOP if buy else mt5.ORDER_TYPE_SELL_STOP,
                       price=spec.round_price(order.price))
            if order.expires is not None:
                req.update(type_time=mt5.ORDER_TIME_SPECIFIED,
                           expiration=int((order.expires - self.server_offset).timestamp()))
        else:
            req.update(action=mt5.TRADE_ACTION_DEAL, type=mt5.ORDER_TYPE_BUY if buy else mt5.ORDER_TYPE_SELL,
                       price=q.ask if buy else q.bid)
            if order.purpose is OrderPurpose.EXIT and order.position_id:
                req["position"] = int(order.position_id)
                req.pop("sl", None)
                req.pop("tp", None)
        res = self._send(req)
        if res is None:
            return OrderResult(False, order.client_order_id, retryable=True, reason=str(mt5.last_error()))
        if res.retcode == 10030:  # unsupported filling mode -> try the next one once
            for alt in (mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN, mt5.ORDER_FILLING_IOC):
                if alt != req["type_filling"]:
                    req["type_filling"] = alt
                    res = self._send(req)
                    if res is not None and res.retcode in SUCCESS:
                        self._filling[order.symbol] = alt
                        break
        if res.retcode not in SUCCESS:
            order.status = OrderStatus.REJECTED
            order.reject_reason = f"{res.retcode} {res.comment}"
            return OrderResult(False, order.client_order_id, retryable=res.retcode in RETRYABLE, reason=order.reject_reason)
        order.broker_order_id = str(res.order)
        fills = []
        if order.entry_type is EntryType.MARKET and res.volume > 0:
            order.filled_volume = res.volume
            order.status = OrderStatus.FILLED if res.volume >= order.volume - 1e-9 else OrderStatus.PARTIALLY_FILLED
            fills.append(Fill(order.client_order_id, order.strategy_id, order.symbol, order.side, res.volume, res.price,
                              self.server_time(), order.purpose, position_id=str(res.order)))
        else:
            order.status = OrderStatus.SUBMITTED
        return OrderResult(True, order.client_order_id, broker_order_id=str(res.order), fills=fills)

    def cancel(self, client_order_id: str) -> bool:
        tag = f"XTS|{client_order_id}"[:31]
        for o in self.mt5.orders_get() or ():
            if o.comment == tag:
                res = self._send({"action": self.mt5.TRADE_ACTION_REMOVE, "order": o.ticket})
                return bool(res and res.retcode in SUCCESS)
        return False

    def modify_stops(self, position_id: str, stop_loss: Optional[float], take_profit: Optional[float]) -> bool:
        p = self.mt5.positions_get(ticket=int(position_id))
        if not p:
            return False
        spec = self.instrument(p[0].symbol)
        req = {"action": self.mt5.TRADE_ACTION_SLTP, "position": int(position_id), "symbol": p[0].symbol,
               "sl": spec.round_price(stop_loss) if stop_loss else 0.0, "tp": spec.round_price(take_profit) if take_profit else 0.0}
        res = self._send(req)
        return bool(res and res.retcode in SUCCESS)

    def close_position(self, position_id: str, client_order_id: str) -> OrderResult:
        p = self.mt5.positions_get(ticket=int(position_id))
        if not p:
            return OrderResult(False, client_order_id, reason="position not found")
        p = p[0]
        sid = self.magic_to_strategy.get(p.magic, str(p.magic))
        side = Side.LONG if p.type == self.mt5.POSITION_TYPE_BUY else Side.SHORT
        o = Order(client_order_id=client_order_id, strategy_id=sid, symbol=p.symbol, side=side.opposite,
                  volume=p.volume, purpose=OrderPurpose.EXIT, position_id=str(p.ticket))
        return self.submit(o)

    # ------------------------------------------------------------------ state
    def open_positions(self, symbol: Optional[str] = None) -> list[Position]:
        out = []
        for p in (self.mt5.positions_get(symbol=symbol) if symbol else self.mt5.positions_get()) or ():
            if p.magic not in self.magic_to_strategy:
                continue   # never touch positions that this system did not open
            side = Side.LONG if p.type == self.mt5.POSITION_TYPE_BUY else Side.SHORT
            out.append(Position(position_id=str(p.ticket), strategy_id=self.magic_to_strategy[p.magic], symbol=p.symbol,
                                side=side, volume=p.volume, entry_price=p.price_open, entry_time=self._to_server(p.time),
                                stop_loss=p.sl or None, take_profit=p.tp or None, swap=p.swap,
                                risk_amount=abs(p.price_open - p.sl) * p.volume * self.instrument(p.symbol).contract_size if p.sl else 0.0))
        return out

    def pending_orders(self, symbol: Optional[str] = None) -> list[Order]:
        out = []
        for o in (self.mt5.orders_get(symbol=symbol) if symbol else self.mt5.orders_get()) or ():
            if o.magic not in self.magic_to_strategy:
                continue
            buy = o.type in (self.mt5.ORDER_TYPE_BUY_STOP, self.mt5.ORDER_TYPE_BUY_LIMIT)
            cid = o.comment.split("|", 1)[1] if o.comment.startswith("XTS|") else str(o.ticket)
            spec = self.instrument(o.symbol)
            risk = abs(o.price_open - o.sl) * o.volume_current * spec.contract_size if o.sl else 0.0
            out.append(Order(client_order_id=cid, strategy_id=self.magic_to_strategy[o.magic], symbol=o.symbol,
                             side=Side.LONG if buy else Side.SHORT, volume=o.volume_current, purpose=OrderPurpose.ENTRY,
                             entry_type=EntryType.STOP, price=o.price_open, stop_loss=o.sl or None,
                             broker_order_id=str(o.ticket), status=OrderStatus.SUBMITTED, risk_amount=risk))
        return out

    def poll_events(self) -> BrokerEvents:
        """Closed trades from the deal history since the last poll (SL/TP hits, manual closes, our exits)."""
        ev = BrokerEvents()
        now = pd.Timestamp.utcnow().tz_localize(None)
        deals = self.mt5.history_deals_get(self._last_deal_check.to_pydatetime(), (now + pd.Timedelta(days=1)).to_pydatetime()) or ()
        self._last_deal_check = now - pd.Timedelta(hours=1)
        for d in deals:
            if d.ticket in self._seen_deals or d.magic not in self.magic_to_strategy:
                continue
            self._seen_deals.add(d.ticket)
            if d.entry != self.mt5.DEAL_ENTRY_OUT:
                continue
            ins = [x for x in deals if x.position_id == d.position_id and x.entry == self.mt5.DEAL_ENTRY_IN]
            if not ins:
                continue
            i = ins[0]
            side = Side.LONG if i.type == self.mt5.DEAL_TYPE_BUY else Side.SHORT
            reason = {4: "stop_loss", 5: "take_profit"}.get(d.reason, "signal_exit")
            net = d.profit + d.swap + d.commission + i.commission
            ev.closed_trades.append(Trade(position_id=str(d.position_id), strategy_id=self.magic_to_strategy[d.magic],
                                          symbol=d.symbol, side=side, volume=d.volume, entry_time=self._to_server(i.time),
                                          entry_price=i.price, exit_time=self._to_server(d.time), exit_price=d.price,
                                          exit_reason=reason, pnl_gross=d.profit, spread_cost=0.0, slippage_cost=0.0,
                                          commission=-(d.commission + i.commission), swap=d.swap, pnl_net=net,
                                          risk_amount=0.0))
        return ev


class MT5MarketData(MarketData):
    """Closed bars and quotes from the MT5 terminal. MT5 bars are bid-based; ask OHLC is
    reconstructed from the bar's recorded spread (points)."""

    def __init__(self, broker: MT5Broker) -> None:
        self.broker = broker

    def now(self) -> pd.Timestamp:
        return self.broker.server_time()

    def quote(self, symbol: str) -> Optional[Quote]:
        return self.broker.quote(symbol)

    def bars(self, symbol: str, tf: str, count: int, now: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        mt5 = self.broker.mt5
        rates = mt5.copy_rates_from_pos(symbol, getattr(mt5, TF_MAP[tf]), 0, count + 1)
        if rates is None or len(rates) == 0:
            return pd.DataFrame()
        df = pd.DataFrame(rates)
        point = mt5.symbol_info(symbol).point
        idx = pd.to_datetime(df["time"], unit="s") + self.broker.server_offset
        spr = df["spread"].astype(float) * point
        out = pd.DataFrame({"open_bid": df["open"].values, "high_bid": df["high"].values, "low_bid": df["low"].values,
                            "close_bid": df["close"].values}, index=idx)
        for c in ("open", "high", "low", "close"):
            out[f"{c}_ask"] = out[f"{c}_bid"] + spr.values
        out["volume"] = df["tick_volume"].values
        from tradingsystem.data.bars import bars_closed_before
        out = bars_closed_before(out, now or self.now(), tf)
        return out.iloc[-count:]
