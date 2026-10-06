# 17. Architektura Python TradingSystemu

## 17.1 Princip

Jeden balíček `tradingsystem/` slouží výzkumu, backtestu, paper, demo i live obchodování. Klíčové
zásady:

1. **Strategie nikdy nemluví s brokerem.** Vrací jen deterministické `Signal` objekty. Nezná
   equity, velikost pozice ani broker.
2. **Jedna orchestrační cesta** (`TradingEngine`) pro všechny režimy. Liší se jen *driver* (replay
   historie vs. živé dotazování) a *broker adapter* (simulátor vs. MetaTrader 5).
3. **Broker je zdroj pravdy o pozicích.** Po restartu nebo reconnectu se stav načte od brokera.
4. **Ochrana proti chybám provozu:** idempotentní příkazy, kontrola staré kotace, denní přestávky
   a spreadu, kill switch.

## 17.2 Vrstvy a tok dat

```
             +-------------------+
 MarketData  |  bary bid/ask,    |  data/market_data.py, brokers/mt5.py::MT5MarketData
 ----------> |  kotace           |
             +---------+---------+
                       v
             +-------------------+
 SIGNALS     | features()        |  signals/indicators.py (kauzální indikátory)
 STRATEGY    | on_bar() -> Signal|  strategies/*.py
             +---------+---------+
                       v
             +-------------------+
 RISK        | RiskManager       |  risk/manager.py: sizing, limity, kill switch
             +---------+---------+
                       v
             +-------------------+
 EXECUTION   | ExecutionEngine   |  execution/engine.py: idempotence, retry, exit-and-reverse
             +---------+---------+
                       v
             +-------------------+
 BROKER      | BrokerAdapter     |  brokers/simulated.py (backtest, paper), brokers/mt5.py (demo, live)
             +---------+---------+
                       v
             +-------------------+
 PORTFOLIO   | PortfolioManager  |  portfolio/manager.py: pozice, expozice, equity
 LOGGING     | TradeLedger       |  portfolio/ledger.py: JSONL audit (orders, fills, trades, decisions)
 MONITORING  | Monitor           |  monitoring/monitor.py: alerty, heartbeat, drift
             +-------------------+

 TradingEngine (live/engine.py) propojuje vrstvy; drivery: backtest/runner.py, live/runner.py
```

## 17.3 Moduly a třídy

| Modul | Třída / funkce | Odpovědnost |
|---|---|---|
| `core/types.py` | `Signal`, `Order`, `Fill`, `Position`, `Trade`, `Side`, `SignalAction`, `EntryType` | doménové typy; `Signal.signal_id` = hash (strategie, čas baru, akce, směr) pro idempotenci |
| `data/instrument.py` | `InstrumentSpec`, `TradingSession`, `utc_to_server`, `server_to_utc` | specifikace kontraktu (100 oz, 0,01 lotu, zaokrouhlení objemu dolů), serverový čas NY+7, denní přestávka 17–18 NY |
| `data/bars.py` | `resample_bidask`, `add_mid`, `bars_closed_before` | agregace bid/ask svíček ukotvených na serverovou půlnoc; strategie dostávají jen uzavřené bary |
| `data/market_data.py` | `MarketData`, `HistoricalMarketData` | rozhraní pro bary a kotace; replay zdroj pro testy |
| `signals/indicators.py` | `atr`, `ema`, `sma`, `donchian_high/low`, `rsi`, `zscore`, `efficiency_ratio`, … | kauzální indikátory; test ověřuje, že výpočet na zkrácené historii dává stejnou poslední hodnotu |
| `strategies/base.py` | `Strategy`, `PositionView` | rozhraní `features(bars)` (vektorově, kauzálně) a `on_bar(ts, row, position)` |
| `strategies/trend.py`, `breakout.py`, `meanrev.py`, `session.py` | C1–C9, C8b | pravidla kandidátů |
| `risk/manager.py` | `RiskConfig`, `RiskManager` | sizing k ATR stopu, limity, DD stopy, kill switch |
| `execution/engine.py` | `ExecutionEngine` | převod signálů na příkazy, duplicitní ochrana, jen zpřísňování stopů, retry, exit-and-reverse, OCO |
| `brokers/base.py` | `BrokerAdapter`, `Quote`, `AccountInfo`, `OrderResult` | rozhraní brokera |
| `brokers/simulated.py` | `SimBroker` | simulace na bid/ask: fill na open dalšího baru, stop-entry, SL/TP, gapy, swapy, spread guard |
| `brokers/mt5.py` | `MT5Broker`, `MT5MarketData` | MetaTrader 5: symbol_info, filling, retcody, magic, komentáře, reconnect |
| `costs/model.py` | `CostModel`, `RateCurve` | spread, skluz, komise, swap (3M T-bill ± přirážka), stres násobky |
| `portfolio/manager.py` | `PortfolioManager` | pozice podle strategie, otevřené riziko, hrubá expozice, equity křivka |
| `portfolio/ledger.py` | `TradeLedger` | append-only JSONL; po restartu rekonstruuje odeslaná ID příkazů |
| `live/engine.py` | `TradingEngine` | jediná orchestrační cesta pro všechny režimy |
| `live/runner.py` | `LiveRunner` | driver pro paper, demo a live |
| `backtest/runner.py`, `metrics.py` | `run_backtest`, `summarize` | historický replay a metriky |
| `monitoring/monitor.py` | `Monitor`, `DriftBands` | alerty, heartbeat, porovnání live statistik s výzkumnými pásmy |
| `config.py`, `cli.py` | `load_config`, `build_*`, `main` | TOML konfigurace (credentials jen z proměnných prostředí), CLI |

## 17.4 Rozhraní strategie a jak napsat novou

```
class MojeStrategie(Strategy):
    strategy_id = "moje_h4"
    timeframe = "H4"

    @dataclass(frozen=True)
    class Params:
        n: int = 50
        stop_atr: float = 2.0

    @property
    def warmup_bars(self):
        return self.params.n + 2

    def features(self, bars):          # bars: mid OHLC uzavřených barů
        f = pd.DataFrame(index=bars.index)
        f["close"] = bars["close"]
        f["ma"] = ind.sma(bars["close"], self.params.n)
        f["atr"] = ind.atr(bars["high"], bars["low"], bars["close"], 20)
        return f

    def on_bar(self, ts, row, pos):
        if pos is None and row.close > row.ma:
            return [self._sig(ts, SignalAction.ENTER, side=Side.LONG,
                              stop_price=row.close - self.params.stop_atr * row.atr)]
        if pos is not None and row.close < row.ma:
            return [self._sig(ts, SignalAction.EXIT, side=pos.side)]
        return []
```

Strategie musí každý vstup doplnit ochranným stopem, jinak ho risk manager odmítne. Velikost pozice
nikdy neurčuje strategie.

## 17.5 Sekvence při uzavření baru

1. Driver zjistí, že se uzavřel nový bar timeframu strategie. V backtestu podle rozvrhu barů,
   v live pomocí `MarketData.bars` a `bars_closed_before`.
2. Live: pokud je trh zavřený (denní přestávka, víkend), kotace je stará nebo spread > 4 bp,
   vyhodnocení se odloží (max. 3 h). Backtest totéž modeluje spread guardem simulátoru.
3. `Strategy.features()` se spočítá z uzavřených barů (live na klouzavém okně ≥ 3× warm-up)
   a `on_bar()` dostane poslední řádek a `PositionView`.
4. Každý `Signal` jde do `ExecutionEngine.handle`:
   - ENTER: kontrola duplicitního ID, existující pozice, kotace; `RiskManager.size_entry` spočítá
     objem a ověří limity; příkaz jde brokerovi s `client_order_id = signal_id`;
   - EXIT: uzavření pozice (pozice se označí „closing“, což umožní exit-and-reverse);
   - UPDATE_STOP: jen ve směru snížení rizika; stop přes trh se převede na exit.
5. Broker vrací fills a uzavřené obchody. `PortfolioManager.sync` je zapíše do ledgeru a risk
   manageru (strategický DD).
6. `RiskManager.on_time` posune denní, týdenní a měsíční kotvy a zkontroluje portfolio DD stop.
   Při překročení `flatten_all` zavře vše a systém se zastaví.

| Režim | Driver | Broker | Data | Plnění market příkazů |
|---|---|---|---|---|
| Backtest | `backtest/runner.py` | `SimBroker` | historické bid/ask bary | open dalšího baru + skluz |
| Paper | `live/runner.py` | `SimBroker(fill_market_immediately=True)` | živé MT5 kotace | aktuální kotace + skluz modelu |
| Demo | `live/runner.py` | `MT5Broker(expect_demo=True)` | MT5 | skutečné plnění brokera |
| Live | `live/runner.py` | `MT5Broker(expect_demo=False)` | MT5 | skutečné; vyžaduje `--i-understand-live` a vyplněnou promotion bránu |

**Test parity** (`tests/test_parity.py`): na syntetických datech, kde open baru = close předchozího,
dávají backtest a live driver 165 ze 165 identických obchodů (čas vstupu, cena vstupu i výstupu, směr).
Test tak zachytil i chybu, kdy live driver plnil během denní přestávky. Chyba byla opravena.

## 17.6 Broker realita

| Téma | Řešení |
|---|---|
| Contract size, min lot, lot step, max lot, tick | čteno z `symbol_info`; objem se zaokrouhluje **dolů**; pod minimem příkaz odmítnut |
| Margin, leverage | `InstrumentSpec.margin()`, `account_info()`; limit hrubé expozice 3× equity |
| Bid/ask | long na ask, short na bid; MT5 bary jsou bid, ask = bid + spread baru |
| Komise, swap | z historie dealů do ledgeru; ve výzkumu modelováno (`costs/model.py`) |
| Odmítnuté příkazy | retcody: úspěch 10008/10009/10010; opakovatelné 10004/10020/10021/10012/10031/10024 (max 3×); ostatní tvrdé odmítnutí |
| Nepodporovaný filling | retcode 10030 → zkusí FOK / RETURN / IOC |
| Částečná plnění | IOC; zapisuje se skutečný objem (`PARTIALLY_FILLED`) |
| Reconnect | `ensure_connected` s exponenciálním backoffem (1 → 60 s); po obnovení rekonciliace pozic |
| Duplicitní příkazy | deterministické ID + JSONL ledger + kontrola komentáře (prefix XTS + ID) u otevřených pozic a příkazů brokera |
| Cizí pozice | magic number per strategie; pozice bez známého magicu se ignorují |
| Staré kotace | > 30 s v otevřené seanci → žádné rozhodnutí + alert |
| Hranice seance | `TradingSession`: přestávka 17–18 NY, víkend; odklad vyhodnocení do otevření a normálního spreadu |
| Časová zóna serveru | `server_offset_hours` převádí čas brokera na NY+7 |
| Bezpečnost účtu | demo režim odmítne reálný účet; live vyžaduje explicitní příznak a vyplněnou bránu |

## 17.7 Risk manager

- **Sizing:** objem = (riziko na obchod × váha strategie × equity na začátku měsíce) / (|vstup − stop| × 100 oz),
  zaokrouhleno dolů na 0,01 lotu.
- **Limity (výchozí hodnoty):** riziko 0,5 % na obchod, max. otevřené riziko 1,5 % equity, hrubá
  expozice ≤ 3× equity, denní ztráta 2 %, týdenní 4 %, strategický DD stop 10 %, portfolio DD
  stop 15 %, max. spread 6 bp, min. vzdálenost stopu 5 bp.
- **Žádný martingale:** sizing nezávisí na posledních výsledcích, jen na měsíční equity bázi;
  jedna pozice na strategii; žádné průměrování.

## 17.8 Konfigurace a CLI

`config/paper.toml` (příloha D) obsahuje sekce `[system]` (symbol, kapitál, cesty, interval
dotazování, max. stáří kotace), `[broker]` (`server_offset_hours`, deviation), `[risk]` (všechny
limity a váhy 1/3), `[[strategies]]` (třída a parametry C3, C2, C5) a `[promotion]` (datum schválení
SMALL LIVE; prázdné = live zakázán). Přihlašovací údaje se čtou jen z proměnných prostředí
`MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`, `MT5_PATH`.

```
python -m tradingsystem.cli backtest --config config/paper.toml --start 2024-01-01 --end 2026-09-01 --source A
python -m tradingsystem.cli run --mode paper --config config/paper.toml
python -m tradingsystem.cli run --mode demo  --config config/paper.toml
python -m tradingsystem.cli run --mode live  --config config/paper.toml --i-understand-live
```

Příkaz `backtest` nad holdoutem reprodukuje výsledek portfolia z kapitoly 12 (218 obchodů, Sharpe 0,72).

## 17.9 Testy

14 testů (`python -m pytest -q tests`): plnění market příkazů na open dalšího baru, gap přes stop,
pořadí SL před TP, stop-entry se stopem v témže baru, rozklad gross/net nákladů, trojitý swap ve
středu, spread guard, kauzalita indikátorů, sizing a limity, měsíční báze sizingu, duplicitní signál,
duplicitní ochrana po restartu, převody časových zón, agregace barů a parita backtest vs. live.

## 17.10 Rozšiřitelnost a známá omezení kódu

- **Nový broker:** implementovat `BrokerAdapter` (a případně `MarketData`). Strategie, risk ani
  portfolio se nemění.
- **Nový instrument:** `InstrumentSpec` se načítá od brokera; cost model a session je třeba nastavit.
- **Nová strategie:** viz 17.4 a registrace v konfiguraci.
- **Omezení:** MT5 adaptér nebyl spuštěn proti skutečnému terminálu (sandbox bez Windows/MT5).
  U obchodů z historie MT5 se nedoplňuje `risk_amount`, takže R se tam musí spárovat z ledgeru.
  Strategie C9 potřebuje živý USD index, který zatím není implementovaný.

*Zdrojové soubory: tradingsystem/**/*.py, tests/test_core.py, tests/test_parity.py, config/paper.toml,
README.md.*
