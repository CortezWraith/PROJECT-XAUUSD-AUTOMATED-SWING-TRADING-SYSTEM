"""Command line entry point.

    python -m tradingsystem.cli backtest --config config/production.toml --start 2019-01-01 --end 2024-01-01
    python -m tradingsystem.cli run --mode paper --config config/production.toml
    python -m tradingsystem.cli run --mode demo  --config config/production.toml
    python -m tradingsystem.cli run --mode live  --config config/production.toml --i-understand-live
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys

import pandas as pd


def _setup_logging(path: str | None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if path:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        handlers.append(logging.FileHandler(path))
    logging.basicConfig(level=logging.INFO, handlers=handlers,
                        format='{"t":"%(asctime)s","lvl":"%(levelname)s","log":"%(name)s","msg":"%(message)s"}')


def cmd_backtest(args, cfg) -> None:
    from tradingsystem.backtest.metrics import summarize
    from tradingsystem.backtest.runner import run_backtest
    from tradingsystem.config import build_risk, build_strategies
    from tradingsystem.costs.model import CostModel, RateCurve
    proc = os.path.join(args.data, "processed")
    macro = pd.read_parquet(os.path.join(proc, "macro_daily.parquet"))
    strategies = build_strategies(cfg, macro=macro)
    base = pd.read_parquet(os.path.join(proc, f"{args.source}_H1.parquet"))
    tf_bars = {s.timeframe: pd.read_parquet(os.path.join(proc, f"{args.source}_{s.timeframe}.parquet"))
               for s in strategies if s.timeframe != "H1"}
    res = run_backtest(strategies, base, "H1", tf_bars, cost=CostModel(multiplier=args.cost_multiplier),
                       rates=RateCurve(macro["ust_3m"].ffill()), risk_config=build_risk(cfg),
                       initial=cfg.get("system", {}).get("initial_capital", 100_000.0), start=args.start, end=args.end)
    print(json.dumps(summarize(res, "portfolio"), indent=2, default=str))
    if args.trades_out:
        res.trades.to_csv(args.trades_out, index=False)


def cmd_run(args, cfg) -> None:
    from tradingsystem.config import build_broker, build_risk, build_strategies
    from tradingsystem.live.engine import TradingEngine
    from tradingsystem.live.runner import LiveRunner
    from tradingsystem.monitoring.monitor import Monitor
    from tradingsystem.portfolio.ledger import TradeLedger
    from tradingsystem.risk.manager import RiskManager
    if args.mode == "live":
        if not args.i_understand_live:
            sys.exit("live mode requires --i-understand-live")
        gate = cfg.get("promotion", {}).get("small_live_approved_on")
        if not gate:
            sys.exit("live mode requires [promotion] small_live_approved_on in the config (passed promotion gate)")
    sysc = cfg.get("system", {})
    strategies = build_strategies(cfg)
    if any(getattr(s, "macro", "absent") is None for s in strategies):
        sys.exit("a strategy needs macro data; provide a live macro feed before enabling it")
    from tradingsystem.brokers.mt5 import MT5Broker, MT5MarketData
    data_broker = MT5Broker(login=int(os.environ["MT5_LOGIN"]) if os.environ.get("MT5_LOGIN") else None,
                            password=os.environ.get("MT5_PASSWORD"), server=os.environ.get("MT5_SERVER"),
                            terminal_path=os.environ.get("MT5_PATH"), strategies=[s.strategy_id for s in strategies],
                            server_offset_hours=cfg.get("broker", {}).get("server_offset_hours", 0),
                            expect_demo=(args.mode != "live"))
    if not data_broker.connect():
        sys.exit("cannot connect to MetaTrader 5")
    broker = data_broker if args.mode in ("demo", "live") else build_broker(cfg, [s.strategy_id for s in strategies], "paper")
    ledger = TradeLedger(os.path.join(sysc.get("state_dir", "state"), f"ledger_{args.mode}.jsonl"))
    engine = TradingEngine(strategies, broker, RiskManager(build_risk(cfg)), ledger, Monitor(),
                           max_quote_age_s=sysc.get("max_quote_age_s", 30.0))
    LiveRunner(engine, MT5MarketData(data_broker), poll_seconds=sysc.get("poll_seconds", 5.0)).run_forever()


def main(argv=None) -> None:
    from tradingsystem.config import load_config
    p = argparse.ArgumentParser(prog="tradingsystem")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backtest")
    b.add_argument("--config", required=True)
    b.add_argument("--start", required=True)
    b.add_argument("--end", required=True)
    b.add_argument("--source", default="A", choices=["A", "B"])
    b.add_argument("--data", default="data")
    b.add_argument("--cost-multiplier", type=float, default=1.0)
    b.add_argument("--trades-out")
    r = sub.add_parser("run")
    r.add_argument("--config", required=True)
    r.add_argument("--mode", required=True, choices=["paper", "demo", "live"])
    r.add_argument("--i-understand-live", action="store_true")
    args = p.parse_args(argv)
    cfg = load_config(args.config)
    _setup_logging(cfg.get("system", {}).get("log_path"))
    {"backtest": cmd_backtest, "run": cmd_run}[args.cmd](args, cfg)


if __name__ == "__main__":
    main()
