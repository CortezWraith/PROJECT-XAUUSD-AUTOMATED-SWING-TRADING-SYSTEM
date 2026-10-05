import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingsystem.brokers.base import Quote  # noqa: E402
from tradingsystem.brokers.simulated import SimBroker  # noqa: E402
from tradingsystem.core.types import EntryType, Order, OrderPurpose, Side, Signal, SignalAction  # noqa: E402
from tradingsystem.costs.model import CostModel, RateCurve  # noqa: E402
from tradingsystem.data.bars import add_mid, resample_bidask  # noqa: E402
from tradingsystem.data.instrument import XAUUSD, server_to_utc, utc_to_server  # noqa: E402
from tradingsystem.execution.engine import ExecutionEngine  # noqa: E402
from tradingsystem.portfolio.ledger import TradeLedger  # noqa: E402
from tradingsystem.portfolio.manager import PortfolioManager  # noqa: E402
from tradingsystem.risk.manager import RiskConfig, RiskManager  # noqa: E402
from tradingsystem.signals import indicators as ind  # noqa: E402


def bar(b, s=0.2, h=None, l=None, o=None):
    o = b if o is None else o
    h = max(o, b) if h is None else h
    l = min(o, b) if l is None else l
    return (o, h, l, b, o + s, h + s, l + s, b + s)


def order(side=Side.LONG, vol=1.0, sl=None, tp=None, et=EntryType.MARKET, price=None, cid="c1"):
    return Order(client_order_id=cid, strategy_id="s", symbol="XAUUSD", side=side, volume=vol,
                 purpose=OrderPurpose.ENTRY, entry_type=et, price=price, stop_loss=sl, take_profit=tp, risk_amount=100)


ZERO_SLIP = CostModel(slippage_bps_market=0.0, slippage_bps_stop=0.0, swap_enabled=False)


def test_market_order_fills_next_open_at_ask():
    b = SimBroker(cost=ZERO_SLIP)
    t = pd.Timestamp("2020-01-06 10:00")
    b.process_bar(t, *bar(2000))
    b.submit(order(sl=1990))
    assert not b.open_positions()          # not filled on the signal bar
    b.process_bar(t + pd.Timedelta(hours=1), *bar(2001, o=2000.5))
    p = b.open_positions()[0]
    assert p.entry_price == pytest.approx(2000.5 + 0.2)


def test_stop_loss_gap_fills_at_open_and_sl_before_tp():
    b = SimBroker(cost=ZERO_SLIP)
    t = pd.Timestamp("2020-01-06 10:00")
    b.process_bar(t, *bar(2000))
    b.submit(order(sl=1990, tp=2010))
    b.process_bar(t + pd.Timedelta(hours=1), *bar(2000))
    # bar gaps below the stop and also touches the target: stop assumed first, filled at the open
    b.process_bar(t + pd.Timedelta(hours=2), *bar(1995, o=1985, h=2015, l=1980))
    tr = b.poll_events().closed_trades[0]
    assert tr.exit_reason == "stop_loss"
    assert tr.exit_price == pytest.approx(1985)


def test_stop_entry_gap_and_same_bar_stop():
    b = SimBroker(cost=ZERO_SLIP)
    t = pd.Timestamp("2020-01-06 10:00")
    b.process_bar(t, *bar(2000))
    b.submit(order(et=EntryType.STOP, price=2005, sl=1999))
    b.process_bar(t + pd.Timedelta(hours=1), *bar(2003, o=2001, h=2008, l=1998))
    ev = b.poll_events()
    # triggered at 2005 (ask) and stopped in the same bar (conservative)
    assert len(ev.closed_trades) == 1
    assert ev.closed_trades[0].entry_price == pytest.approx(2005)


def test_frictionless_gross_equals_net_and_costs_add_up():
    for cm in (CostModel(multiplier=0.0, swap_enabled=False), CostModel(swap_enabled=False)):
        b = SimBroker(cost=cm)
        t = pd.Timestamp("2020-01-06 10:00")
        b.process_bar(t, *bar(2000))
        b.submit(order())
        b.process_bar(t + pd.Timedelta(hours=1), *bar(2004))
        pid = b.open_positions()[0].position_id
        b.close_position(pid, "x")
        b.process_bar(t + pd.Timedelta(hours=2), *bar(2010))
        tr = b.poll_events().closed_trades[0]
        assert tr.pnl_gross - tr.spread_cost - tr.slippage_cost - tr.commission + tr.swap == pytest.approx(tr.pnl_net)
        if cm.multiplier == 0:
            assert tr.pnl_net == pytest.approx(tr.pnl_gross)


def test_triple_swap_on_wednesday_rollover():
    cm = CostModel(swap_markup_annual=0.0, slippage_bps_market=0, multiplier=1.0)
    b = SimBroker(cost=cm, rates=RateCurve(default=0.036))
    t = pd.Timestamp("2020-01-08 22:00")   # Wednesday (server time)
    b.process_bar(t, *bar(2000, s=0.0))
    b.submit(order(vol=1.0))
    b.process_bar(t + pd.Timedelta(hours=1), *bar(2000, s=0.0))
    b.process_bar(t + pd.Timedelta(hours=3), *bar(2000, s=0.0))  # Thursday 01:00 -> rollover
    p = b.open_positions()[0]
    assert p.swap == pytest.approx(-100 * 2000 * 0.036 / 360 * 3)


def test_spread_guard_defers_market_orders():
    b = SimBroker(cost=ZERO_SLIP, max_fill_spread_bps=4.0)
    t = pd.Timestamp("2020-01-06 00:00")
    b.process_bar(t, *bar(2000))
    b.submit(order())
    b.process_bar(t + pd.Timedelta(hours=1), *bar(2000, s=2.0))   # 10 bps spread -> deferred
    assert not b.open_positions()
    b.process_bar(t + pd.Timedelta(hours=2), *bar(2000, s=0.2))
    assert b.open_positions()


def test_indicators_are_causal():
    rng = np.random.default_rng(0)
    c = pd.Series(2000 + rng.normal(0, 3, 600).cumsum())
    h, l = c + rng.uniform(0, 3, 600), c - rng.uniform(0, 3, 600)
    funcs = [lambda c, h, l: ind.atr(h, l, c, 14), lambda c, h, l: ind.donchian_high(h, 20),
             lambda c, h, l: ind.rsi(c, 2), lambda c, h, l: ind.zscore(c, 48),
             lambda c, h, l: ind.efficiency_ratio(c, 48), lambda c, h, l: ind.sma(c, 200),
             lambda c, h, l: ind.rolling_percentile_rank(ind.bollinger_bandwidth(c, 20), 120)]
    for f in funcs:
        full = f(c, h, l)
        for n in (300, 450, 599):
            part = f(c[:n], h[:n], l[:n])
            a, b_ = full.iloc[n - 1], part.iloc[-1]
            assert (np.isnan(a) and np.isnan(b_)) or a == pytest.approx(b_)


def test_risk_sizing_rounds_down_and_respects_caps():
    rm = RiskManager(RiskConfig(risk_per_trade=0.005, max_open_risk=0.015))
    rm.on_time(pd.Timestamp("2020-01-06"), 100_000)
    q = Quote("XAUUSD", 2000.0, 2000.3, pd.Timestamp("2020-01-06"))
    sig = Signal("s", "XAUUSD", pd.Timestamp("2020-01-06"), SignalAction.ENTER, side=Side.LONG, stop_price=1980.3)
    d = rm.size_entry(sig, q, XAUUSD, 100_000, 0.0, 0.0, "c")
    # 500 USD / (20 USD * 100 oz) = 0.25 lots
    assert d.approved and d.order.volume == pytest.approx(0.25)
    d2 = rm.size_entry(sig, q, XAUUSD, 100_000, 1400.0, 0.0, "c2")
    assert not d2.approved and "open risk" in d2.reason
    rm.on_time(pd.Timestamp("2020-01-06 12:00"), 97_500)
    assert rm.entry_blockers("s", 97_500) == "daily loss limit"


def test_sizing_base_is_month_start_equity():
    rm = RiskManager(RiskConfig())
    rm.on_time(pd.Timestamp("2020-01-02"), 100_000)
    rm.on_time(pd.Timestamp("2020-01-20"), 150_000)
    assert rm.state.sizing_equity == 100_000
    rm.on_time(pd.Timestamp("2020-02-03"), 150_000)
    assert rm.state.sizing_equity == 150_000


def test_duplicate_signal_never_sends_two_orders():
    b = SimBroker(cost=ZERO_SLIP)
    t = pd.Timestamp("2020-01-06 10:00")
    b.process_bar(t, *bar(2000))
    led = TradeLedger()
    rm = RiskManager(RiskConfig())
    rm.on_time(t, 100_000)
    pm = PortfolioManager(b, led, rm)
    ex = ExecutionEngine(b, rm, pm, led)
    sig = Signal("s", "XAUUSD", t, SignalAction.ENTER, side=Side.LONG, stop_price=1980)
    ex.handle(sig, "H1")
    ex.handle(sig, "H1")
    assert len(led.orders) == 1


def test_duplicate_protection_survives_restart(tmp_path):
    path = str(tmp_path / "ledger.jsonl")
    t = pd.Timestamp("2020-01-06 10:00")
    sig = Signal("s", "XAUUSD", t, SignalAction.ENTER, side=Side.LONG, stop_price=1980)
    for _ in range(2):  # second loop = process restart with a fresh broker
        b = SimBroker(cost=ZERO_SLIP)
        b.process_bar(t, *bar(2000))
        led = TradeLedger(path)
        rm = RiskManager(RiskConfig())
        rm.on_time(t, 100_000)
        ex = ExecutionEngine(b, rm, PortfolioManager(b, led, rm), led)
        ex.handle(sig, "H1")
    assert len(led.orders) == 0      # nothing new sent after restart


def test_server_time_roundtrip_and_daily_bar_alignment():
    utc = pd.date_range("2021-03-01", "2021-03-20", freq="1h")
    srv = utc_to_server(utc)
    back = server_to_utc(srv)
    assert (back == utc).mean() > 0.99
    # 17:00 New York (EST, UTC-5) = 22:00 UTC = server midnight
    assert utc_to_server(pd.DatetimeIndex([pd.Timestamp("2021-01-04 22:00")]))[0] == pd.Timestamp("2021-01-05 00:00")


def test_resample_bidask_drops_weekend_and_aggregates():
    idx = pd.date_range("2021-01-04 01:00", periods=48, freq="1h")
    df = pd.DataFrame({c: np.arange(48, dtype=float) for c in
                       ["open_bid", "high_bid", "low_bid", "close_bid", "open_ask", "high_ask", "low_ask", "close_ask"]}, index=idx)
    d1 = resample_bidask(df, "D1")
    assert list(d1.index) == [pd.Timestamp("2021-01-04"), pd.Timestamp("2021-01-05"), pd.Timestamp("2021-01-06")]
    assert d1.iloc[0]["open_bid"] == 0 and d1.iloc[0]["close_bid"] == 22
