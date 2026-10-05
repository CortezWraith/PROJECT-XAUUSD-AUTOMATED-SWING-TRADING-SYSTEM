"""Live driver for :class:`TradingEngine` (paper, demo and live modes).

* paper - quotes and bars from MT5 (any account), execution simulated by SimBroker
          with immediate fills at the live quote and the research cost model;
* demo  - MT5Broker on a demo account (``expect_demo=True`` refuses real accounts);
* live  - MT5Broker on a real account (requires an explicit ``--i-understand-live`` flag
          in the CLI and a passed promotion gate recorded in the config).

The loop polls; it never trades on a bar that has not closed, never acts on a
stale quote and reconnects with backoff. On start and after every reconnect
the portfolio is reconciled from the broker (the broker is the source of truth).
"""
from __future__ import annotations

import logging
import time
from typing import Optional, Sequence

import pandas as pd

from tradingsystem.brokers.base import BrokerAdapter
from tradingsystem.brokers.simulated import SimBroker
from tradingsystem.data.bars import add_mid, tf_minutes
from tradingsystem.data.instrument import TradingSession
from tradingsystem.data.market_data import MarketData
from tradingsystem.live.engine import TradingEngine
from tradingsystem.strategies.base import Strategy

log = logging.getLogger("tradingsystem.runner")


class LiveRunner:
    def __init__(self, engine: TradingEngine, market_data: MarketData, symbol: str = "XAUUSD",
                 poll_seconds: float = 5.0, history_bars: Optional[dict] = None,
                 session: Optional[TradingSession] = None, max_quote_age_s: float = 30.0,
                 max_entry_spread_bps: float = 4.0, max_defer_minutes: float = 180.0) -> None:
        self.engine = engine
        self.md = market_data
        self.symbol = symbol
        self.poll = poll_seconds
        self.session = session or TradingSession()
        self.max_quote_age_s = max_quote_age_s
        self.history = history_bars or {}
        # same policy as the simulator's spread guard: a closed bar is acted upon only while the
        # market is open and the spread is normal (deferred at most ``max_defer_minutes``)
        self.max_entry_spread_bps = max_entry_spread_bps
        self.max_defer = pd.Timedelta(minutes=max_defer_minutes)
        self.last_bar: dict[str, pd.Timestamp] = {}
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def _history_len(self, s: Strategy) -> int:
        return max(self.history.get(s.strategy_id, 0), 3 * s.warmup_bars, 300)

    def step(self) -> None:
        broker: BrokerAdapter = self.engine.broker
        if hasattr(broker, "ensure_connected") and not broker.ensure_connected():
            if self.engine.monitor:
                self.engine.monitor.alert("CONNECTION", "broker not connected")
            return
        q = self.md.quote(self.symbol)
        now = self.md.now()
        if q is None:
            return
        stale = (now - q.time).total_seconds() > self.max_quote_age_s and self.session.is_open(now)
        if stale and self.engine.monitor:
            self.engine.monitor.alert("STALE_QUOTE", f"last tick {q.time}, now {now}")
        if isinstance(broker, SimBroker) and not stale:
            broker.process_quote(q.time, q.bid, q.ask)
        self.engine.on_clock(now)
        if stale:
            return
        tradable = self.session.is_open(now) and (q.spread / q.mid * 1e4 <= self.max_entry_spread_bps)
        for s in self.engine.strategies:
            bars = self.md.bars(self.symbol, s.timeframe, self._history_len(s), now=now)
            if bars.empty:
                continue
            last = bars.index[-1]
            if self.last_bar.get(s.strategy_id) == last:
                continue
            first_run = s.strategy_id not in self.last_bar
            bar_close = last + pd.Timedelta(minutes=tf_minutes(s.timeframe))
            if not first_run and not tradable and now - bar_close < self.max_defer:
                continue   # wait for the session to open / the spread to normalise
            self.last_bar[s.strategy_id] = last
            if first_run:
                continue   # never act on a bar that closed before the process started
            feats = s.features(add_mid(bars))
            row = next(feats.iloc[[-1]].itertuples())
            self.engine.on_bar_closed(s, last, row, now=now)
        self.engine.mark(now)
        if self.engine.monitor:
            self.engine.monitor.heartbeat(now)

    def run_forever(self) -> None:
        log.info("runner started: %s", [s.strategy_id for s in self.engine.strategies])
        while not self._stop:
            try:
                self.step()
            except Exception:
                log.exception("runner step failed")
                if self.engine.monitor:
                    self.engine.monitor.alert("RUNNER_ERROR", "exception in step; see log")
            time.sleep(self.poll)
