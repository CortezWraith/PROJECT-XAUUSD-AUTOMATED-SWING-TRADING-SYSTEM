# 16. Doporučení pro další zpracování

Tato kapitola převádí závěry do konkrétních pracovních balíčků. Každý má vstupy, výstupy a
akceptační kritéria. Pořadí balíčků je závazné: další balíček má smysl až po splnění předchozího.

## 16.1 Balíček 1 – Re-validace na datech vlastního brokera

- **Proč:** všechna čísla stojí na datech Dukascopy a MT4 mirroru. Spready, swapy, časová zóna
  serveru a kotace vlastního brokera se mohou lišit. Například broker v datech B přepíná letní čas
  podle evropského kalendáře (kapitola 3).
- **Vstupy:** export M1 nebo H1 historie XAUUSD z MT5 terminálu brokera (co nejdelší), specifikace
  symbolu (`symbol_info`: contract size, min lot, lot step, swap long/short, triple swap den,
  stops level), historie realizovaných spreadů.
- **Postup:** převést export do formátu `data/processed` (bid/ask OHLC, serverový čas NY+7), ověřit
  posun časové zóny korelací s datovou sadou A, změřit medián spreadu podle hodiny, nastavit
  `CostModel` (spread, swapová přirážka podle skutečných swapů) a zopakovat backtest C3, C2, C5 a
  portfolia na překryvu s A (2016–2026) bez jakékoli změny pravidel.
- **Akceptační kritéria:** znaménko expectancy DEV+OOS i holdoutu shodné s výzkumem u všech tří;
  rozdíl exp. R ≤ 0,05 R; realizovaný průměrný spread ≤ 1,5× model; žádný posun časové zóny > 0 h
  po korekci.
- **Náročnost:** 1–2 týdny.

## 16.2 Balíček 2 – Integrační testy MT5 na demo účtu

Checklist (vše musí projít, `tradingsystem/brokers/mt5.py`):

1. `symbol_info` vrací očekávané hodnoty a `InstrumentSpec` je naplněna z brokera (ne natvrdo).
2. Filling mode: IOC, FOK nebo RETURN je správně vyjednán; retcode 10030 vede k fallbacku.
3. Market příkaz s SL, modifikace SL (jen zpřísnění), uzavření pozice, pending stop s expirací.
4. Částečné plnění se zapíše skutečným objemem.
5. Retcody: opakovatelné (10004, 10020, 10021, 10012, 10031, 10024) se zopakují max. 3×, ostatní ne.
6. Reconnect: odpojení terminálu → `ensure_connected` s backoffem → po obnovení rekonciliace pozic.
7. Restart procesu uprostřed obchodu: žádný duplicitní příkaz (ledger JSONL + komentář `XTS|id`).
8. Stará kotace: žádné rozhodnutí, alert.
9. Denní přestávka a víkend: vyhodnocení se odloží do otevření trhu a normálního spreadu.
10. Magic number: systém nikdy nesáhne na cizí pozici.
11. `expect_demo=True` odmítne reálný účet.

- **Náročnost:** 1–2 týdny.

## 16.3 Balíček 3 – PAPER fáze (pozorovací)

- **Konfigurace:** `config/paper.toml` (příloha D): C3, C2, C5, riziko 0,5 % na obchod celkem
  (1/3 na strategii), max. otevřené riziko 1,5 %, denní/týdenní limit 2 %/4 %, strategický DD stop
  10 %, portfolio DD stop 15 %. Spuštění: `python -m tradingsystem.cli run --mode paper --config config/paper.toml`.
- **Délka:** minimálně 3 měsíce a 30 signálů za rodinu.
- **Očekávaná pásma** (z DEV+OOS, k porovnání s realitou):

| Ukazatel | C3 | C2 | C5 | Portfolio |
|---|---|---|---|---|
| Obchody za měsíc (průměr) | 1,5 | 2,2 | 3,0 | 6,6 |
| Exp. R na obchod – bootstrap p05 / p50 / p95 | −0,044 / 0,058 / 0,172 | −0,086 / 0,080 / 0,257 | −0,060 / 0,038 / 0,139 | — |
| Nejdelší série ztrát – p50 / p95 | 11 / 17 | 13 / 20 | 12 / 18 | — |
| Max DD (portfolio, bloky 20 dní) – p50 / p90 / p95 | — | — | — | 8,3 % / 13,1 % / 14,9 % |
| Win rate (DEV+OOS) | 34,8 % | 31,4 % | 35,3 % | 33,7 % |

- **Měřit:** realizovaný spread a skluz proti modelu, swapy, frekvenci signálů proti pásmu, paritu
  signálů s offline replay stejných barů (cíl ≥ 99 %), latenci a chyby.
- **Eskalace:** chyba rekonciliace nebo duplicitní příkaz → okamžité zastavení a oprava; náklady
  > 2× model → zastavení a re-validace (balíček 1).

## 16.4 Balíček 4 – Rozhodovací strom po paper fázi

1. **Implementace selhala** (parita < 99 %, chyby rekonciliace, náklady > 1,5× model): opravit
   a paper fázi zopakovat.
2. **Implementace v pořádku, výsledky v bootstrap pásmu:** postoupit na DEMO (kapitola 18).
3. **Implementace v pořádku, výsledky pod p05** (expectancy, série ztrát nebo DD): nepostupovat;
   zkontrolovat režim trhu (krize, vysoká volatilita jsou známé režimy selhání) a pokračovat v paper
   fázi dalších 3 měsíců. Při opakování strategii odložit.
4. **Výsledky nad p95:** nic neměnit, nezvyšovat riziko. Jde pravděpodobně o příznivý režim, ne o důkaz.

## 16.5 Balíček 5 – Hledání nezávislého zdroje edge

Současná trojice je jedna sázka na trend. Skutečnou diverzifikaci by přinesla strategie s jiným
mechanismem. Kandidátní hypotézy pro **nový předregistrovaný výzkumný cyklus** (stejný protokol:
apriorní pravidla, DEV/OOS/holdout, brány):

- volatilita a opce: GVZ (implikovaná volatilita zlata), variance risk premium;
- pozicování: CFTC COT (managed money), extrémy pozicování jako kontrariánský signál;
- toky: změny držby zlatých ETF (GLD, IAU), čisté nákupy centrálních bank;
- intermarket: zlato vs. stříbro, AUD, těžaři (GDX), reálné výnosy (TIPS), až budou data k dispozici;
- sezónnost s větším vzorkem: přes více kovů a trhů, aby bylo obchodů dost;
- C9 (USD filtr) jako samostatně předregistrovaná varianta trendu;
- strojové učení pouze jako nadstavba nad robustní baseline s walk-forward validací bez úniku dat.

**Šablona předregistrace** (pro každou hypotézu před prvním během):

```
Hypotéza a mechanismus (proč by edge měl existovat):
Literatura / důkazy:
Přesná pravidla a parametry (apriorní):
Data, splity (DEV / OOS / holdout), nákladový model:
Brány přijetí (číselné):
Perturbační mřížka a timeframy:
Co by hypotézu vyvrátilo:
Datum a commit:
```

## 16.6 Co nedělat

- Neladit parametry ani filtry na OOS nebo holdout (například kratší stop u C5 či jiný timeframe).
- Nevypínat long nebo short stranu podle historické asymetrie. Holdout ukázal, že se otáčí.
- Nezvyšovat riziko po ziscích, nepoužívat martingale, nedohánět ztráty, neprůměrovat do ztrátové pozice.
- Nesčítat rizika tří strategií, jako by byly nezávislé (jsou jedna sázka).
- Nepřidávat další trendové varianty jako „diverzifikaci“.
- Neinterpretovat dobrý paper výsledek za 3 měsíce jako důkaz edge.
- Nenasazovat reálný kapitál před splněním bran v kapitole 18.

## 16.7 Předávací checklist pro vývojáře a kvanta

| Co | Kde |
|---|---|
| Závěry a odůvodnění | tento dokument, `REPORT.md` |
| Přesné parametry k použití | `config/paper.toml`, `research/frozen_spec.json` |
| Kód strategií | `tradingsystem/strategies/trend.py` (C3 `EmaTrend`, C2 `DonchianBreakout`), `breakout.py` (C5 `SqueezeBreakout`) |
| Risk, exekuce, broker | `tradingsystem/risk/`, `execution/`, `brokers/` |
| Reprodukce výzkumu | `research/fetch_data.sh`, `prepare_data.py`, `s01`–`s05` (příloha F) |
| Testy | `python -m pytest -q tests` (14 testů včetně parity backtest/live) |
| Výsledky | `research/results/*.md`, `*.json`, `figures/` |
| Protokol a rozhodnutí | `research/PROTOCOL.md`, `DEV_SELECTION.md` (přílohy A, B) |

## 16.8 Otevřené otázky

1. Jak velké jsou skutečné náklady (spread, swap, skluz) u zvoleného brokera?
2. Přežije trendová rodina na datech brokera se stejným znaménkem?
3. Je strategický DD stop 10 % správně kalibrovaný vůči skutečné volatilitě obchodování?
4. Existuje dostupný a stabilní zdroj dat pro nezávislý edge (GVZ, COT, ETF toky)?
5. Jak se zachová ensemble v režimu krize, který v datech znamenal nejhorší výsledky?

*Zdrojové soubory: config/paper.toml, research/results/s02_C3.json, s02_C2.json, s02_C5.json
(trades_per_year, win_rate, bootstrap), s03_portfolio.json, tradingsystem/brokers/mt5.py,
tradingsystem/cli.py.*
