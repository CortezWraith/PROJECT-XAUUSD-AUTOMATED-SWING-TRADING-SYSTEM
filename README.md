# PROJECT XAUUSD – Automated Swing Trading System

Nezávislý výzkum a kvantitativní ověření swingových strategií pro XAUUSD + Python TradingSystem
připravený pro backtest, paper, demo a live (MetaTrader 5). Zadání: `Project XAUUSD.docx`.

**👉 Hlavní výstup: [REPORT.md](REPORT.md)** (24 kapitol dle zadání).

## Výsledek ve zkratce

* Testováno 10 rodin strategií (+1 data-driven revize) na XAUUSD 2004–2026 s reálným bid/ask,
  skluzem a swapy; předregistrovaný protokol, chronologické splity DEV / OOS / HOLDOUT.
* **Žádná strategie neprošla všemi předem stanovenými branami robustnosti.**
* Jediná konzistentně (slabě) kladná rodina: střednědobý trend na H4 – pořadí kandidátů
  **C3 EMA trend H4, C2 Donchian H4, C5 Squeeze H4** (všechno stejná sázka, důvěra LOW).
* Mean reversion, volatility breakout, denní TSMOM a session/čas-v-dni anomálie zamítnuty.
* Doporučení: pouze pozorovací **PAPER** fáze s jedním rizikovým rozpočtem pro celou rodinu.

## Struktura

```
tradingsystem/            produkční balíček (stejný kód pro backtest / paper / demo / live)
  core/types.py           Signal, Order, Fill, Position, Trade
  data/                   InstrumentSpec + serverový čas (NY+7), bid/ask bary, MarketData
  signals/indicators.py   kauzální indikátory (ATR, Donchian, EMA, RSI, z-score, ...)
  strategies/             Strategy rozhraní + kandidáti (trend, breakout, meanrev, session)
  risk/manager.py         sizing (riziko k ATR stopu, měsíční báze), limity, kill switch
  portfolio/              PortfolioManager, TradeLedger (JSONL audit trail)
  execution/engine.py     ExecutionEngine (idempotence, exit-and-reverse, retry, jen zpřísňování stopů)
  brokers/                BrokerAdapter, SimBroker (backtest/paper), MT5Broker + MT5MarketData
  costs/model.py          spread / skluz / komise / swap (3M T-bill ± přirážka), stres ×1,5 / ×2
  live/                   TradingEngine (orchestrace), LiveRunner (paper/demo/live driver)
  backtest/               replay driver a metriky
  monitoring/monitor.py   alerty, heartbeat, drift vs. výzkumná pásma
  cli.py, config.py       CLI a TOML konfigurace
research/                 výzkumná pipeline (PROTOCOL.md, DEV_SELECTION.md, frozen_spec.json, s01–s05)
  results/                všechny tabulky (md/json/csv) a grafy (figures/)
config/paper.toml         konfigurace PAPER fáze (zmrazená specifikace)
tests/                    14 testů (fills, swapy, kauzalita, sizing, idempotence, parita backtest/live)
```

## Instalace

```bash
pip install -r requirements.txt          # pandas, numpy, scipy, pyarrow, matplotlib, pytest
pip install MetaTrader5                  # jen pro paper/demo/live (Windows + MT5 terminál)
python -m pytest -q tests
```

## Reprodukce výzkumu

```bash
bash research/fetch_data.sh              # stáhne veřejná data do data/raw (necommitují se)
python research/prepare_data.py          # data/processed/*.parquet + data_quality.json
python research/scorecard.py             # literaturní scorecard
python research/s01_dev_screen.py        # DEV screen všech kandidátů
python research/s02_validate.py          # OOS, WF, perturbace, TF, zpoždění, náklady, režimy, bootstrap
python research/s03_portfolio.py C3 C2 C5  # korelace, překryvy, portfolio
python research/s04_holdout.py           # holdout 2024–2026 (spouštět jen se zmrazenou specifikací)
python research/s05_summary.py           # souhrn 2004–2026 + grafy
```

## Backtest a provoz

```bash
python -m tradingsystem.cli backtest --config config/paper.toml --start 2024-01-01 --end 2026-09-01 --source A
# MT5 přihlášení přes proměnné prostředí: MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, MT5_PATH
python -m tradingsystem.cli run --mode paper --config config/paper.toml
python -m tradingsystem.cli run --mode demo  --config config/paper.toml   # odmítne reálný účet
# live vyžaduje --i-understand-live a vyplněnou promotion bránu v konfiguraci (REPORT.md kap. 22)
```

Upozornění: výzkum, ne investiční doporučení. Žádná strategie neprošla branami pro nasazení kapitálu.
