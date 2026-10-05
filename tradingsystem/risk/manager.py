"""Risk manager: position sizing and pre-trade / portfolio limits.

Principles
----------
* Fixed-fractional risk to the protective stop. The stop distance is
  volatility-based (ATR multiples), so position size is automatically
  inverse to volatility.
* The sizing base is the account equity at the *start of the calendar month*.
  Risk therefore never ramps up after a winning streak inside the month and
  never ramps up after losses (no martingale, no loss recovery, no averaging
  down: a strategy can hold at most one position).
* Hard limits: total open risk, daily / weekly loss stops, strategy-level
  drawdown stop, portfolio-level drawdown kill switch, spread sanity check.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from tradingsystem.brokers.base import Quote
from tradingsystem.core.types import EntryType, Order, OrderPurpose, Side, Signal, SignalAction
from tradingsystem.data.instrument import InstrumentSpec


@dataclass
class RiskConfig:
    risk_per_trade: float = 0.005             # 0.5% of sizing equity per trade
    strategy_risk_weights: dict = field(default_factory=dict)  # optional per-strategy multipliers (<=1)
    max_open_risk: float = 0.015              # sum of open risk to stops, all XAUUSD positions
    max_gross_notional_x_equity: float = 3.0  # cap on |notional| / equity across positions
    max_daily_loss: float = 0.02              # block new entries for the rest of the server day
    max_weekly_loss: float = 0.04             # block new entries for the rest of the week
    strategy_dd_stop: float = 0.10            # disable strategy if its PnL drawdown > 10% of equity
    portfolio_dd_stop: float = 0.15           # flatten + halt if equity drawdown from peak > 15%
    max_spread_bps: float = 6.0               # defer entries when spread is abnormal
    min_stop_distance_bps: float = 5.0        # reject absurdly tight stops
    enforce_loss_limits: bool = True


@dataclass
class RiskDecision:
    approved: bool
    order: Optional[Order] = None
    reason: str = ""


@dataclass
class RiskState:
    month_key: Optional[tuple] = None
    sizing_equity: float = 0.0
    day_key: Optional[pd.Timestamp] = None
    day_start_equity: float = 0.0
    week_key: Optional[tuple] = None
    week_start_equity: float = 0.0
    peak_equity: float = 0.0
    halted: bool = False
    halt_reason: str = ""
    disabled_strategies: dict = field(default_factory=dict)
    strategy_pnl: dict = field(default_factory=dict)
    strategy_peak: dict = field(default_factory=dict)


class RiskManager:
    def __init__(self, config: Optional[RiskConfig] = None) -> None:
        self.cfg = config or RiskConfig()
        self.state = RiskState()

    # ------------------------------------------------------------------ state updates
    def on_time(self, ts: pd.Timestamp, equity: float) -> None:
        """Roll month/day/week anchors and check the portfolio kill switch."""
        st = self.state
        mk = (ts.year, ts.month)
        if st.month_key != mk:
            st.month_key = mk
            st.sizing_equity = equity
        dk = ts.normalize()
        if st.day_key != dk:
            st.day_key = dk
            st.day_start_equity = equity
        wk = tuple(ts.isocalendar())[:2]
        if st.week_key != wk:
            st.week_key = wk
            st.week_start_equity = equity
        st.peak_equity = max(st.peak_equity, equity)
        if self.cfg.enforce_loss_limits and st.peak_equity > 0 and not st.halted:
            if equity / st.peak_equity - 1.0 <= -self.cfg.portfolio_dd_stop:
                st.halted = True
                st.halt_reason = f"portfolio drawdown stop at {ts}"

    def on_trade_closed(self, strategy_id: str, pnl: float, equity: float) -> None:
        st = self.state
        st.strategy_pnl[strategy_id] = st.strategy_pnl.get(strategy_id, 0.0) + pnl
        st.strategy_peak[strategy_id] = max(st.strategy_peak.get(strategy_id, 0.0), st.strategy_pnl[strategy_id])
        dd = st.strategy_peak[strategy_id] - st.strategy_pnl[strategy_id]
        base = max(st.sizing_equity, 1e-9)
        if self.cfg.enforce_loss_limits and dd / base > self.cfg.strategy_dd_stop:
            st.disabled_strategies.setdefault(strategy_id, f"strategy drawdown {dd / base:.1%}")

    # ------------------------------------------------------------------ checks
    def entry_blockers(self, strategy_id: str, equity: float) -> Optional[str]:
        st, c = self.state, self.cfg
        if st.halted:
            return st.halt_reason or "halted"
        if strategy_id in st.disabled_strategies:
            return "strategy disabled: " + st.disabled_strategies[strategy_id]
        if c.enforce_loss_limits:
            if st.day_start_equity > 0 and equity / st.day_start_equity - 1 <= -c.max_daily_loss:
                return "daily loss limit"
            if st.week_start_equity > 0 and equity / st.week_start_equity - 1 <= -c.max_weekly_loss:
                return "weekly loss limit"
        return None

    def size_entry(self, signal: Signal, quote: Quote, spec: InstrumentSpec, equity: float,
                   open_risk: float, gross_notional: float, client_order_id: str,
                   expires: Optional[pd.Timestamp] = None) -> RiskDecision:
        assert signal.action is SignalAction.ENTER and signal.side is not None
        c = self.cfg
        why = self.entry_blockers(signal.strategy_id, equity)
        if why:
            return RiskDecision(False, reason=why)
        if signal.stop_price is None:
            return RiskDecision(False, reason="entry without protective stop")
        if quote.mid > 0 and quote.spread / quote.mid * 1e4 > c.max_spread_bps:
            return RiskDecision(False, reason=f"spread {quote.spread:.2f} too wide")
        if signal.entry_type is EntryType.STOP:
            ref = signal.entry_price
        else:
            ref = quote.ask if signal.side is Side.LONG else quote.bid
        dist = (ref - signal.stop_price) * int(signal.side)
        if dist <= 0 or dist / ref * 1e4 < c.min_stop_distance_bps:
            return RiskDecision(False, reason="invalid stop distance")
        weight = c.strategy_risk_weights.get(signal.strategy_id, 1.0)
        risk_amount = c.risk_per_trade * weight * (self.state.sizing_equity or equity)
        vol = spec.round_volume(risk_amount / (dist * spec.contract_size))
        if vol < spec.min_lot:
            return RiskDecision(False, reason="size below minimum lot")
        actual_risk = vol * spec.contract_size * dist
        if open_risk + actual_risk > c.max_open_risk * equity + 1e-9:
            return RiskDecision(False, reason="max open risk")
        if gross_notional + spec.notional(vol, ref) > c.max_gross_notional_x_equity * equity:
            return RiskDecision(False, reason="max gross notional")
        order = Order(client_order_id=client_order_id, strategy_id=signal.strategy_id, symbol=signal.symbol,
                      side=signal.side, volume=vol, purpose=OrderPurpose.ENTRY, entry_type=signal.entry_type,
                      price=signal.entry_price, stop_loss=spec.round_price(signal.stop_price),
                      take_profit=spec.round_price(signal.take_profit) if signal.take_profit else None,
                      created=signal.timestamp, expires=expires, risk_amount=actual_risk)
        return RiskDecision(True, order=order)
