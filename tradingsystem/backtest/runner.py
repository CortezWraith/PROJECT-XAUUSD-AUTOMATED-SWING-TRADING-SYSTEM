"""Historical replay driver for :class:`TradingEngine`.

The driver replays *base* bars (bid/ask, e.g. H1) into the SimBroker so that
stops are resolved at base-bar granularity, and calls each strategy whenever a
bar of the strategy's own timeframe has closed. Strategy features are computed
once on the full strategy-timeframe history (they are causal; see tests).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from tradingsystem.brokers.simulated import SimBroker
from tradingsystem.costs.model import CostModel, RateCurve
from tradingsystem.data.bars import add_mid, resample_bidask, tf_minutes
from tradingsystem.data.instrument import InstrumentSpec, XAUUSD
from tradingsystem.live.engine import TradingEngine
from tradingsystem.portfolio.ledger import TradeLedger
from tradingsystem.risk.manager import RiskConfig, RiskManager
from tradingsystem.strategies.base import Strategy


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity: pd.Series
    exposure: pd.Series
    decisions: pd.DataFrame
    initial: float
    start: pd.Timestamp
    end: pd.Timestamp
    meta: dict = field(default_factory=dict)


def _schedule(base_index: pd.DatetimeIndex, base_tf: str, tf_index: pd.DatetimeIndex, tf: str) -> dict[int, list[int]]:
    """Map base-bar position -> strategy bar positions that close at the end of that base bar."""
    base_close = (base_index + pd.Timedelta(minutes=tf_minutes(base_tf))).values
    tf_close = (tf_index + pd.Timedelta(minutes=tf_minutes(tf))).values
    pos = np.searchsorted(base_close, tf_close, side="right") - 1
    out: dict[int, list[int]] = {}
    for k, i in enumerate(pos):
        if i < 0:
            continue
        # the base bar must belong to the strategy bar (has data inside it)
        if base_index.values[i] < tf_index.values[k]:
            continue
        out.setdefault(int(i), []).append(k)
    return out


def run_backtest(strategies: Sequence[Strategy], base_bars: pd.DataFrame, base_tf: str = "H1",
                 tf_bars: Optional[dict[str, pd.DataFrame]] = None, cost: Optional[CostModel] = None,
                 rates: Optional[RateCurve] = None, risk_config: Optional[RiskConfig] = None,
                 initial: float = 100_000.0, delay_bars: int = 0, start: Optional[str] = None,
                 end: Optional[str] = None, spec: InstrumentSpec = XAUUSD,
                 features_cache: Optional[dict] = None) -> BacktestResult:
    """Run strategies over ``base_bars`` between ``start`` and ``end`` (server time).

    Warm-up data before ``start`` is used for indicators but no trading happens there.
    """
    cost = cost or CostModel()
    risk_cfg = risk_config or RiskConfig(enforce_loss_limits=False)
    tf_bars = dict(tf_bars or {})
    tf_bars.setdefault(base_tf, base_bars)
    broker = SimBroker(initial_balance=initial, cost=cost, rates=rates, spec=spec, delay_bars=delay_bars)
    engine = TradingEngine(strategies, broker, RiskManager(risk_cfg), TradeLedger())

    t0 = pd.Timestamp(start) if start else base_bars.index[0]
    t1 = pd.Timestamp(end) if end else base_bars.index[-1] + pd.Timedelta(days=1)
    base = base_bars[(base_bars.index >= t0) & (base_bars.index < t1)]

    plans = []
    for s in strategies:
        bars = tf_bars.get(s.timeframe)
        if bars is None:
            bars = resample_bidask(base_bars, s.timeframe)
            tf_bars[s.timeframe] = bars
        key = (id(bars), s.strategy_id, repr(s.describe()))
        feats = features_cache.get(key) if features_cache is not None else None
        if feats is None:
            feats = s.features(add_mid(bars))
            if features_cache is not None:
                features_cache[key] = feats
        f = feats[(feats.index >= t0) & (feats.index < t1)]
        rows = list(f.itertuples())
        sched = _schedule(base.index, base_tf, f.index, s.timeframe)
        plans.append((s, f.index, rows, sched))

    arr = base[["open_bid", "high_bid", "low_bid", "close_bid", "open_ask", "high_ask", "low_ask", "close_ask"]].to_numpy()
    idx = base.index
    for i in range(len(base)):
        ts = idx[i]
        broker.process_bar(ts, *arr[i])
        engine.on_clock(ts)
        for s, findex, rows, sched in plans:
            ks = sched.get(i)
            if ks:
                for k in ks:
                    engine.on_bar_closed(s, findex[k], rows[k])
        engine.mark(ts)

    # close anything still open at the last close (marked, not traded: report as open-at-end)
    trades = engine.ledger.trades_frame()
    eq = pd.Series([e for _, e in engine.portfolio.equity_curve], index=[t for t, _ in engine.portfolio.equity_curve], name="equity")
    ex = pd.Series([e for _, e in engine.portfolio.exposure_curve], index=[t for t, _ in engine.portfolio.exposure_curve], name="net_lots")
    dec = pd.DataFrame(engine.ledger.decisions)
    return BacktestResult(trades=trades, equity=eq, exposure=ex, decisions=dec, initial=initial,
                          start=idx[0] if len(idx) else t0, end=idx[-1] if len(idx) else t1,
                          meta={"halted": engine.risk.state.halted, "halt_reason": engine.risk.state.halt_reason,
                                "disabled": dict(engine.risk.state.disabled_strategies),
                                "open_positions_at_end": len(broker.open_positions())})
