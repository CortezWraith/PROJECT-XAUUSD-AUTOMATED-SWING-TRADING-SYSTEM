"""Backtest driver and live driver must produce the same trades from the same bars.

Synthetic data is built with open[t] == close[t-1] (bid and ask), so a market order filled
at the live quote (close of the signal bar) gets the same price as the backtest fill at the
next bar's open. Any difference would therefore come from the orchestration code paths.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingsystem.backtest.runner import run_backtest  # noqa: E402
from tradingsystem.brokers.simulated import SimBroker  # noqa: E402
from tradingsystem.costs.model import CostModel  # noqa: E402
from tradingsystem.data.bars import resample_bidask  # noqa: E402
from tradingsystem.data.market_data import HistoricalMarketData  # noqa: E402
from tradingsystem.live.engine import TradingEngine  # noqa: E402
from tradingsystem.live.runner import LiveRunner  # noqa: E402
from tradingsystem.portfolio.ledger import TradeLedger  # noqa: E402
from tradingsystem.risk.manager import RiskConfig, RiskManager  # noqa: E402
from tradingsystem.strategies.session import AsiaLondonSession  # noqa: E402
from tradingsystem.strategies.trend import DonchianBreakout  # noqa: E402


def synthetic_h1(n_days=260, seed=3):
    rng = np.random.default_rng(seed)
    idx = []
    day = pd.Timestamp("2021-01-04")
    while len(idx) < n_days * 23:
        if day.weekday() < 5:
            idx.extend(day + pd.Timedelta(hours=h) for h in range(1, 24))
        day += pd.Timedelta(days=1)
    idx = pd.DatetimeIndex(idx)
    steps = rng.normal(0, 3.0, len(idx)) + 0.05 * np.sin(np.arange(len(idx)) / 400)
    close = 1800 + np.cumsum(steps)
    open_ = np.concatenate([[1800.0], close[:-1]])
    wig = np.abs(rng.normal(0, 2.0, len(idx)))
    high = np.maximum(open_, close) + wig
    low = np.minimum(open_, close) - wig
    sp = 0.3
    df = pd.DataFrame({"open_bid": open_, "high_bid": high, "low_bid": low, "close_bid": close}, index=idx)
    for c in ("open", "high", "low", "close"):
        df[f"{c}_ask"] = df[f"{c}_bid"] + sp
    df["volume"] = 1.0
    return df


def test_backtest_and_live_runner_produce_identical_trades():
    h1 = synthetic_h1()
    h4 = resample_bidask(h1, "H4")
    cost = CostModel(slippage_bps_market=0.0, slippage_bps_stop=0.0, swap_enabled=False)
    risk = RiskConfig(enforce_loss_limits=False, max_open_risk=1.0, max_gross_notional_x_equity=100, max_spread_bps=1e9)
    mk = lambda: [DonchianBreakout(entry_n=20, exit_n=10), AsiaLondonSession(daily_atr_days=5)]

    bt = run_backtest(mk(), h1, "H1", {"H4": h4}, cost=cost, risk_config=risk)

    broker = SimBroker(cost=cost, fill_market_immediately=True, max_fill_spread_bps=1e9)
    md = HistoricalMarketData({"H1": h1, "H4": h4})
    engine = TradingEngine(mk(), broker, RiskManager(risk), TradeLedger())
    runner = LiveRunner(engine, md, max_quote_age_s=1e9)
    runner.last_bar = {s.strategy_id: None for s in engine.strategies}   # act from the first bar on
    arr = h1[["open_bid", "high_bid", "low_bid", "close_bid", "open_ask", "high_ask", "low_ask", "close_ask"]].to_numpy()
    for i, ts in enumerate(h1.index):
        md.set_now(ts)                           # bar opens: deferred decisions act now
        runner.step()
        broker.process_bar(ts, *arr[i])          # intrabar stops, same as backtest
        close_t = ts + pd.Timedelta(hours=1)     # bar has closed; live sees the closing quote
        md.set_now(close_t)
        runner.step()
    live = engine.ledger.trades_frame()
    b = bt.trades.sort_values(["strategy_id", "entry_time"]).reset_index(drop=True)
    lv = live.sort_values(["strategy_id", "entry_time"]).reset_index(drop=True)
    assert len(b) > 20
    # the backtest may hold one more open position at the end; compare common trades
    n = min(len(b), len(lv))
    assert abs(len(b) - len(lv)) <= 2
    np.testing.assert_allclose(b["entry_price"].values[:n], lv["entry_price"].values[:n], rtol=0, atol=1e-6)
    np.testing.assert_allclose(b["exit_price"].values[:n], lv["exit_price"].values[:n], rtol=0, atol=1e-6)
    assert (b["side"].values[:n] == lv["side"].values[:n]).all()
    assert (pd.to_datetime(b["entry_time"]).values[:n] == pd.to_datetime(lv["entry_time"]).values[:n]).all()
