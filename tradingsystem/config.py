"""Configuration loading (TOML) and object factories. Credentials only from environment variables."""
from __future__ import annotations

import importlib
import os
import tomllib
from dataclasses import fields
from typing import Any

from tradingsystem.risk.manager import RiskConfig
from tradingsystem.strategies.base import Strategy


def load_config(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def build_strategies(cfg: dict, macro=None) -> list[Strategy]:
    out = []
    for s in cfg.get("strategies", []):
        if not s.get("enabled", True):
            continue
        mod, cls = s["class"].rsplit(".", 1)
        klass = getattr(importlib.import_module(mod), cls)
        params = dict(s.get("params", {}))
        if s.get("needs_macro"):
            out.append(klass(macro=macro, **params))
        else:
            out.append(klass(**params))
        if s.get("timeframe"):
            out[-1].timeframe = s["timeframe"]
    return out


def build_risk(cfg: dict) -> RiskConfig:
    r = dict(cfg.get("risk", {}))
    names = {f.name for f in fields(RiskConfig)}
    return RiskConfig(**{k: v for k, v in r.items() if k in names})


def build_broker(cfg: dict, strategy_ids: list[str], mode: str) -> Any:
    b = cfg.get("broker", {})
    if mode == "paper":
        from tradingsystem.brokers.simulated import SimBroker
        from tradingsystem.costs.model import CostModel
        return SimBroker(initial_balance=cfg.get("system", {}).get("initial_capital", 100_000.0),
                         cost=CostModel(), fill_market_immediately=True)
    from tradingsystem.brokers.mt5 import MT5Broker
    login = os.environ.get("MT5_LOGIN")
    return MT5Broker(login=int(login) if login else None, password=os.environ.get("MT5_PASSWORD"),
                     server=os.environ.get("MT5_SERVER"), terminal_path=os.environ.get("MT5_PATH"),
                     strategies=strategy_ids, server_offset_hours=b.get("server_offset_hours", 0),
                     deviation_points=b.get("deviation_points", 30), expect_demo=(mode == "demo"))
