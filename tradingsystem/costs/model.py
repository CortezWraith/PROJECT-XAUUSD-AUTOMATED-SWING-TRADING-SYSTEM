"""Transaction-cost model for XAUUSD CFDs / spot.

Components (all scaled by ``multiplier`` for cost stress tests, except the
interest-rate part of the swap, which is a market rate, not a broker cost):

* spread         - taken from the data (bid/ask) when available, otherwise a
                   modelled spread in basis points by server hour; the
                   multiplier widens bid/ask symmetrically around mid.
* slippage       - basis points of price, separately for market orders and
                   stop orders (stop orders slip more, and gaps are filled at
                   the first available price, never at the stop level).
* commission     - USD per lot per side.
* swap/financing - long pays (r + markup), short receives (r - markup) per
                   night, ACT/360, triple on the configured weekday. ``r`` is
                   the 3-month US T-bill rate (historical, daily), ``markup``
                   approximates the broker's spread on financing. Calibrated
                   to typical 2024-2025 retail XAUUSD swaps (e.g. long -60 /
                   short +19 points at ~USD 3300 with r ~4.3% => markup ~2.2%).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

import pandas as pd

from tradingsystem.core.types import Side


@dataclass(frozen=True)
class CostModel:
    multiplier: float = 1.0
    slippage_bps_market: float = 0.3
    slippage_bps_stop: float = 1.0
    commission_per_lot_side: float = 0.0
    swap_markup_annual: float = 0.0225
    swap_enabled: bool = True
    contract_size: float = 100.0
    triple_swap_weekday: int = 2
    # fallback modelled spread in bps of mid if bid/ask are not in the data
    fallback_spread_bps: float = 2.0

    def stressed(self, multiplier: float) -> "CostModel":
        return replace(self, multiplier=multiplier)

    def frictionless(self) -> "CostModel":
        return replace(self, multiplier=0.0, swap_enabled=False)

    # ------------------------------------------------------------------ prices
    def effective_quotes(self, bid: float, ask: float) -> tuple[float, float]:
        """Widen (or remove, multiplier 0) the quoted spread around mid."""
        mid = 0.5 * (bid + ask)
        half = 0.5 * (ask - bid) * self.multiplier
        return mid - half, mid + half

    def slippage(self, price: float, is_stop: bool) -> float:
        bps = self.slippage_bps_stop if is_stop else self.slippage_bps_market
        return price * bps * 1e-4 * self.multiplier

    def commission(self, volume: float) -> float:
        return abs(volume) * self.commission_per_lot_side * self.multiplier

    # ------------------------------------------------------------------ swap
    def nightly_swap(self, side: Side, volume: float, price: float, rate_annual: float, weekday: int) -> float:
        """Swap for one rollover (account currency, signed: negative = cost)."""
        if not self.swap_enabled:
            return 0.0
        nights = 3 if weekday == self.triple_swap_weekday else 1
        markup = self.swap_markup_annual * self.multiplier
        notional = volume * self.contract_size * price
        if side is Side.LONG:
            annual = -(rate_annual + markup)
        else:
            annual = rate_annual - markup
        return notional * annual / 360.0 * nights


class RateCurve:
    """Daily short rate lookup (decimal, e.g. 0.05). Forward-filled, never looks ahead."""

    def __init__(self, series: Optional[pd.Series] = None, default: float = 0.02):
        self.default = default
        if series is not None and len(series):
            s = series.dropna().sort_index()
            self._idx = s.index.values
            self._vals = s.values.astype(float)
        else:
            self._idx = None
            self._vals = None

    def rate(self, ts: pd.Timestamp) -> float:
        if self._idx is None:
            return self.default
        import numpy as np
        pos = np.searchsorted(self._idx, np.datetime64(ts), side="right") - 1
        if pos < 0:
            return self.default
        return float(self._vals[pos])
