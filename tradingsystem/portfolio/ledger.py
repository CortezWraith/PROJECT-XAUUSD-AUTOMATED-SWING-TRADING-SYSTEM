"""Append-only trade ledger (orders, fills, closed trades, risk decisions).

In live/demo/paper mode every record is also written as one JSON line, so the
ledger survives restarts and is the audit trail for reconciliation.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Optional

import pandas as pd

from tradingsystem.core.types import Fill, Order, Trade


def _jsonable(x: Any) -> Any:
    if is_dataclass(x):
        x = asdict(x)
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, Enum):
        return x.value if not isinstance(x.value, int) else int(x.value)
    if isinstance(x, pd.Timestamp):
        return x.isoformat()
    if hasattr(x, "isoformat"):
        return x.isoformat()
    return x


class TradeLedger:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path
        self.orders: list[Order] = []
        self.fills: list[Fill] = []
        self.trades: list[Trade] = []
        self.decisions: list[dict] = []
        if path:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def _write(self, kind: str, obj: Any) -> None:
        if not self.path:
            return
        with open(self.path, "a") as f:
            f.write(json.dumps({"kind": kind, "data": _jsonable(obj)}) + "\n")

    def record_order(self, o: Order) -> None:
        self.orders.append(o)
        self._write("order", o)

    def record_fill(self, f: Fill) -> None:
        self.fills.append(f)
        self._write("fill", f)

    def record_trade(self, t: Trade) -> None:
        self.trades.append(t)
        self._write("trade", t)

    def record_decision(self, ts: pd.Timestamp, strategy_id: str, action: str, approved: bool, reason: str) -> None:
        d = {"ts": ts, "strategy_id": strategy_id, "action": action, "approved": approved, "reason": reason}
        self.decisions.append(d)
        self._write("decision", d)

    def submitted_ids(self) -> set[str]:
        """Client order ids already sent (rebuilt from the JSONL file after a restart)."""
        ids = {o.client_order_id for o in self.orders}
        if self.path and os.path.exists(self.path):
            with open(self.path) as f:
                for line in f:
                    rec = json.loads(line)
                    if rec.get("kind") == "order":
                        ids.add(rec["data"]["client_order_id"])
        return ids

    def trades_frame(self) -> pd.DataFrame:
        if not self.trades:
            return pd.DataFrame()
        rows = []
        for t in self.trades:
            d = asdict(t)
            d["side"] = int(t.side)
            d["r"] = t.r_multiple
            tags = d.pop("tags") or {}
            d.update({f"tag_{k}": v for k, v in tags.items()})
            rows.append(d)
        return pd.DataFrame(rows)
