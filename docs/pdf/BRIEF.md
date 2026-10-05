# Brief pro autory kapitol PDF dokumentu „XAUUSD – výzkum swing strategií“

Repo root: `/home/user/PROJECT-XAUUSD-AUTOMATED-SWING-TRADING-SYSTEM` (dále „root“).
Cílem je **podrobné PDF v češtině**, které obsahuje všechny informace, výstupy, vysvětlení,
objasnění a odůvodnění, které strategie jsou nejlepší a proč – pro další zpracování (navazující
vývoj, paper/demo trading, další výzkum). Čtenář je kvant / trader / vývojář, který u výzkumu nebyl.
Dokument musí obstát samostatně: kdo ho přečte, má pochopit co, jak, proč a s jakou jistotou.

## 1. Shrnutí projektu (fakta, která už platí – neměnit)

* Zadání: `Project XAUUSD.docx` (text lze vytáhnout přes python zipfile z `word/document.xml`).
  Úkol: nezávisle najít 3 nejrobustnější systematické swing strategie pro XAUUSD (H1/H4/D1, držení
  4 h – 10 dní), ověřit je kvantitativně (OOS, walk-forward, perturbace, timeframe, zpoždění,
  bootstrap, režimy, subperiody, long/short, náklady ×1,5/×2), navrhnout Python architekturu
  (MT5), risk framework, promotion gates. „Neříkej mi, co chci slyšet.“
* Hlavní dosavadní výstup: `REPORT.md` (24 kapitol). PDF ho má **rozšířit** (víc vysvětlení,
  všechny tabulky, interpretace), ne jen zopakovat.
* Data: A = Dukascopy-format M1 bid/ask 2016-09..2026-09 (UTC); B = MT4 broker H1 bid 2004-06..2025-06
  (server NY+7, ask syntetizován modelovým spreadem z A); makro VIX, USD index (DXY váhy, Fed H.10),
  US Treasury 3M/2Y/10Y. Detaily `research/results/data_quality.json`, `research/prepare_data.py`.
  Zdroje dat jsou GitHub mirrory, protože síť sandboxu blokovala Dukascopy/FRED/Yahoo.
* Serverový čas = New York + 7 h; D1 svíčka = 17:00–17:00 NY; H4 bary 00,04,…,20 serverového času.
* Splity: PRE-SAMPLE 2004-07..2009-12 (B), DEV 2010-01..2018-12, OOS 2019-01..2023-12,
  HOLDOUT 2024-01..2026-08 (A). Výzkumná řada = B do 2016-08-31, A od 2016-09-01.
* Protokol předregistrován (`research/PROTOCOL.md`, commit 6a151db) **před** prvním během strategií.
  DEV rozhodnutí (`research/DEV_SELECTION.md`, commit 41ce7b8) **před** OOS. Specifikace a pořadí
  zmrazeny (`research/frozen_spec.json`, commit cfe78c3) **před** holdoutem. Holdout spuštěn jednou (commit 87cd6b6).
* Kandidáti: C1 TSMOM D1, C2 Donchian H4, C3 EMA trend H4, C4 volatility breakout D1, C5 squeeze H4,
  C6 RSI(2) pullback D1, C7 z-score MR H1, C8 session drift H1, C9 USD-filtrovaný Donchian H4,
  C10 podzimní sezónnost (netestováno – 2 obchody/rok), C11 ML (vyloučeno), C8b = data-driven
  revize C8 (Asie long 02→09, Londýn short 09→15 serverového času).
* Předregistrovaný výběr: C2, C8, C6. Na DEV: C6 a C8 záporné už před náklady → zamítnuty; C2 těsně
  neprošla PF bránou (1,094). Bránu 1 prošly C3, C5, C9 (vše momentum) → plná validace C5, C9, C3
  + transparentně C2 a C8b.
* **Výsledek: žádná strategie neprošla všemi 7 předregistrovanými branami.** Jediná konzistentně
  slabě kladná rodina je trend/momentum na H4. Zmrazené pořadí pro další zkoumání:
  **#1 C3 EMA trend H4, #2 C2 Donchian H4, #3 C5 Squeeze H4** – jedna podkladová sázka, důvěra LOW.
  C9 vyřazena (korelace 0,79 s C2, potřeba živého USD indexu, OOS ≈ 0, WF −0,2 %).
  C8b zamítnuta (funguje jen před náklady, slábne od 2016). Doporučení: pouze pozorovací PAPER fáze
  s jedním rizikovým rozpočtem pro celou trendovou rodinu (váhy 1/3, 0,5 % na obchod celkem).
* Holdout 2024–26 kladný pro všechny trendové varianty (portfolio Sharpe 0,72), ale jen díky long
  straně v historickém býčím trhu zlata; short strana ztrácela. Asymetrie směrů je režimová.
* Kód: balíček `tradingsystem/` (data → signály → strategie → risk → exekuce → portfolio → broker
  adapter SimBroker/MT5 → ledger → monitoring), 14 testů v `tests/`, konfigurace `config/paper.toml`,
  CLI `tradingsystem/cli.py`.

## 2. Mapa zdrojových souborů (zdroj pravdy pro čísla)

| Soubor | Obsah |
|---|---|
| `research/results/data_quality.json` | kvalita dat A/B/makro |
| `research/results/scorecard.md/.json` | literaturní scorecard |
| `research/results/s01_dev_screen.md/.json` | DEV screen 10 kandidátů (baseline, frictionless, long/short, cross-source A vs B) |
| `research/results/s02_<K>.md/.json` (K ∈ C3, C2, C5, C9, C8b) | plná validace: segmenty, long/short, náklady, zpoždění, perturbace (+PBO), timeframe, walk-forward, bootstrap, režimy, roky, bloky, DSR, brány |
| `research/results/grid_<K>.csv` | všechny body perturbační mřížky |
| `research/results/dsr_within_grid.json` | deflated Sharpe s variancí v rámci mřížky |
| `research/results/s03_portfolio.md/.json` | komplementarita C3/C2/C5 + portfolio (3 varianty rizika) |
| `research/results/s03_portfolio_C2_C3_C5_C9.md/.json` | totéž pro 4 strategie včetně C9 (korelace C2/C9) |
| `research/results/s04_holdout.md/.json` | holdout 2024–2026 |
| `research/results/s05_pooled.md/.json` | souhrn 2004–2026 přes 4 segmenty |
| `research/results/figures/*.png` | grafy: `equity_segments.png`, `xauusd.png`, `session_profile.png`, `grid_C2.png`, `grid_C3.png`, `grid_C5.png` |
| `research/PROTOCOL.md`, `research/DEV_SELECTION.md`, `research/frozen_spec.json` | protokol a rozhodnutí |
| `research/*.py`, `tradingsystem/**/*.py`, `tests/*.py`, `config/paper.toml` | kód |
| `data/processed/*.parquet` | zpracovaná data (A_<TF>, B_<TF>, macro_daily) pro případné dopočty |

Pomocné moduly pro dopočty: `research/common.py` (funkce `run`, `stitched`, `load`, `macro`),
`research/registry.py` (`make(key)`), `research/stats.py`. Dopočty spouštěj z rootu
(`python3 - <<'EOF' ... sys.path.insert(0,'research') ...`). Jeden backtest trvá ~1–5 s.
Nikdy neměň soubory mimo své přidělené kapitoly; nespouštěj s01–s05 skripty (přepsaly by výsledky);
žádné git operace.

## 3. Pravidla přesnosti

1. Každé číslo musí pocházet ze zdrojového souboru nebo z vlastního ověřitelného dopočtu z dat.
   Nic neodhaduj, nezaokrouhluj „od oka“, nevymýšlej. `REPORT.md` je shrnutí – při rozporu platí
   raw výsledkové soubory.
2. Rozlišuj **empirický důkaz [E]**, **ekonomické zdůvodnění [R]**, **expertní inferenci [I]**,
   **nepodložený předpoklad [U]**, kde to dává smysl.
3. Žádné přikrašlování. Pokud výsledek nic neprokazuje, napiš to. Konzistentně s kapitolou výsledků.
4. Na konci každé kapitoly uveď odstavec `*Zdrojové soubory: ...*`.

## 4. Formát (Markdown podmnožina, kterou umí build skript)

* Soubor začíná nadpisem kapitoly `# N. Název` (přesně jedna `#` na soubor). Podkapitoly `## N.M Název`,
  dále `###`. Nepoužívej `####` a hlubší.
* Odstavce, **tučně**, *kurzíva*, `kód`, odrážky `-`/`*`, číslované seznamy, citace `>` (vykreslí se jako
  zvýrazněný box – používej pro klíčové závěry: `> **Závěr:** …`).
* Tabulky: GitHub pipe tabulky s řádkem `|---|`; každý řádek stejný počet sloupců; **nikdy znak `|`
  uvnitř buňky** (ani v kódu); max. ~12 sloupců (širší rozděl na dvě tabulky). Před i za tabulkou prázdný řádek.
* Obrázky: `![Popisek](research/results/figures/soubor.png)` – cesta relativní k rootu, samostatný odstavec.
* Kód / ASCII diagramy: ohraničené bloky ``` ``` ```.
* Čísla česky: desetinná čárka (0,061), procenta „7,4 %“, tisíce mezerou nebo bez („14 437“).
  Datum ISO (2024-01-01). R = násobek rizika obchodu.
* Žádné HTML, žádné emoji (✅❌ nahraď „ANO“ / „NE“), žádné poznámky pod čarou.
* Styl: věcná, srozumitelná čeština; odborné termíny anglicky jen tam, kde jsou běžné (Sharpe, drawdown,
  walk-forward, holdout…), při prvním výskytu vysvětlit. U každé tabulky 1–3 věty „jak číst“ a
  „co z toho plyne“.
