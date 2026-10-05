# 4. Metodika, protokol a simulace

Tato kapitola vysvětluje, **jak** výzkum probíhal a **proč** je postaven právě takto. U strategií se
slabým edge rozhoduje metodika víc než samotná čísla. Správně provedený test, který nic nenajde, má
větší hodnotu než přeladěný backtest se Sharpe 2. Kapitola popisuje chronologii a předregistraci,
brány přijetí, nákladový model, konvence simulátoru, sizing, výpočet metrik, statistické nástroje,
testy kódu a úplný seznam odchylek od předregistrovaného plánu.

## 4.1 Chronologie výzkumu a proč na pořadí záleží

### Commity v gitu

| Commit | Čas (UTC, 2026-10-05) | Obsah | Co v tu chvíli ještě nikdo neviděl |
|---|---|---|---|
| cf149e0, 32925d8 | 14:19, 14:21 | založení repozitáře, nahrání zadání `Project XAUUSD.docx` | žádná data ani kód |
| **6a151db** | 14:57 | **předregistrace:** `research/PROTOCOL.md`, scorecard, datová pipeline, celý engine `tradingsystem/`, 13 testů, `data_quality.json` | žádný výsledek strategie na XAUUSD (kromě smoke testu, odchylka 1) |
| **41ce7b8** | 15:05 | DEV screening 10 variant (`s01_dev_screen`), **rozhodnutí po DEV** (`research/DEV_SELECTION.md`), oprava dvou chyb enginu, revize C8b | žádný běh na OOS 2019–2023 |
| **cfe78c3** | 15:28 | plná validace (`s02_*`: OOS, walk-forward, perturbace, timeframe, zpoždění, náklady, režimy, bootstrap), portfolio C3+C2+C5 (`s03_portfolio`), `research/stats.py`, MT5 adaptér, live runner, test parity, **zmrazení specifikace a pořadí** (`research/frozen_spec.json`) | žádný běh na holdoutu 2024–2026 |
| **87cd6b6** | 15:42 | **holdout spuštěn jednou** (`s04_holdout`), souhrn 2004–2026 (`s05_pooled`), grafy, `dsr_within_grid.json`, `REPORT.md`, `config/paper.toml` | — |
| **91dbb12** | 15:42 | oprava vykreslení jedné tabulky v `REPORT.md` | — |
| a697f2f | 16:01 | rozpracovaná PDF dokumentace, výstup komplementarity se čtyřmi strategiemi (C2, C3, C5, C9) | — |

Jak číst tabulku: tučně jsou commity, které vymezují fáze výzkumu. Sloupec vpravo říká, jaké
informace v okamžiku zápisu rozhodnutí ještě neexistovaly. Co z toho plyne: v gitu je doložitelné, že
pravidla a parametry byly zapsány před prvním výsledkem, výběr po DEV před OOS a pořadí před holdoutem.
Všechny commity jsou z jednoho dne, rozhoduje ale jejich pořadí, ne délka intervalů.

### Proč na pořadí záleží

Hlavní nebezpečí kvantitativního výzkumu není chyba ve výpočtu, ale **ladění podle výsledků**. Výzkumník
má mnoho drobných rozhodnutí (který timeframe, jaký stop, které období, který filtr, kterou strategii
reportovat) a každé, které udělá po zhlédnutí výsledků, zvyšuje šanci najít náhodný vzor (tzv. „zahrada
rozvětvených cest“). Po stovkách takových rozhodnutí vypadá skvěle i strategie bez edge. Chronologické
zmrazování tento problém omezuje ve třech krocích:

1. **Předregistrace (6a151db) před prvním během:** parametry všech kandidátů jsou literaturní defaulty
   (Turtle 55/20, EMA 20/100, RSI(2)…), mřížky pro perturbaci, nákladový model a brány jsou pevné.
   Na DEV datech se tak testuje hypotéza, místo aby se hledala.
2. **Rozhodnutí po DEV (41ce7b8) před OOS:** co postupuje do validace, se určilo jen z DEV. OOS
   2019–2023 tak zůstává skutečně nevidět a jeho výsledek je poctivým odhadem degradace.
3. **Zmrazení před holdoutem (cfe78c3):** pořadí C3 > C2 > C5, parametry a portfolio váhy jsou zapsané
   v `frozen_spec.json`. Skript holdoutu (`research/s04_holdout.py`) před během kontroluje, že parametry
   strategií přesně odpovídají zmrazené specifikaci (příkaz `assert`). Holdout tak nelze „trochu doladit“.

Co chronologie **nedokazuje** [U]: (a) že mimo commity neproběhly jiné běhy (jeden smoke test je
přiznán, odchylka 1); (b) že výzkumník neměl předběžné znalosti. Autor zná obecný vývoj ceny zlata do
roku 2026 včetně býčího trhu 2024–2026, takže preference trendové rodiny mohla být ovlivněna hindsight
biasem. Zmrazení chrání pravidla a parametry, ne volbu rodiny strategií (kapitola 14 a 19).

### Výzkumná pipeline

| Skript | Krok | Hlavní výstupy | Commit |
|---|---|---|---|
| `research/fetch_data.sh` | stažení surových dat z GitHub mirrorů | `data/raw/` | 6a151db |
| `research/prepare_data.py` | časové zóny, bary, syntetický ask B, makro, kvalita | `data/processed/*.parquet`, `data_quality.json` | 6a151db |
| `research/scorecard.py` | literaturní scorecard 11 kandidátů | `scorecard.md/.json` | 6a151db |
| `research/s01_dev_screen.py` | DEV screening, long/short, hrubě, A vs. B | `s01_dev_screen.md/.json` | 41ce7b8 |
| `research/s02_validate.py` | plná validace C5, C9, C3, C2, C8b | `s02_<K>.md/.json`, `grid_<K>.csv` | cfe78c3 |
| `research/s03_portfolio.py` | komplementarita a portfolio | `s03_portfolio.md/.json` | cfe78c3 (verze se 4 strategiemi a697f2f) |
| `research/s04_holdout.py` | holdout 2024–2026, jednou | `s04_holdout.md/.json` | 87cd6b6 |
| `research/s05_summary.py` | souhrn 2004–2026, grafy | `s05_pooled.md/.json`, `figures/*.png` | 87cd6b6 |

Jak číst tabulku: skripty se spouštějí v tomto pořadí. Každý zapisuje jen do `research/results/`.
Co z toho plyne: kdo chce výsledky reprodukovat, spustí skripty ve stejném pořadí (příloha F). Kdo
chce testovat novou hypotézu, **nesmí** znovu spouštět `s04_holdout.py` s jinou specifikací, protože
holdout je spotřebovaný (kapitola 16).

## 4.2 Obsah předregistrace

`research/PROTOCOL.md` (doslovně v příloze A) stanovil před prvním během:

- **Data a jejich role:** A, B, C, makro; modelový spread B jen z 2016-09 – 2018-12; spojení B → A
  k 2016-09-01; serverový čas NY+7.
- **Chronologické segmenty:** PRE-SAMPLE, DEV, OOS, HOLDOUT s pravidly (DEV jediné místo rozhodování,
  OOS bez ladění, holdout jednou).
- **Výběr pro plné testování:** C2 (trend), C8 (session), C6 (mean reversion). Ostatní kandidáti tvoří
  kontrolní skupinu se stejnými náklady. Náhrada vybrané strategie kontrolní je povolena jen tehdy,
  když vybraná selže na DEV branách, a musí být označena (zvyšuje počet testů pro deflated Sharpe).
- **Nákladový model:** spread z dat, skluz 0,3 / 1,0 bp, komise 0 (citlivost 3,5 USD/lot/strana), swap
  z 3M T-bill ± 2,25 %, spread guard 4 bp / max. 3 bary, stres ×1,5 a ×2.
- **Testy robustnosti:** přesné perturbační mřížky (C2, C8, C6), timeframe testy, zpoždění vstupu,
  walk-forward 4 + 1 rok, bootstrap (10 000 a 5 000 opakování, bloky 20 dní), režimy s ex-ante
  definicemi, subperiody po letech a blocích, long a short zvlášť.
- **Osm bran přijetí** (kapitola 4.3) a **pravidlo pro směr:** směr, který samostatně neprojde
  branami 1–2, se označí jako bez edge a v produkci se vypne.

## 4.3 Osm bran přijetí a proč existují

| Brána | Podmínka | Proč existuje | Co chrání |
|---|---|---|---|
| 1 | DEV: expectancy > 0 a PF > 1,10 při baseline nákladech | minimální důkaz, že efekt po nákladech vůbec existuje. Rezerva 10 % v PF, protože DEV je optimistický (vybíralo se na něm) a náklady jsou nejisté | před strategiemi „na hraně nuly“, které OOS téměř jistě nepřežijí |
| 2 | OOS 2019–2023: expectancy > 0, PF > 1,05, Sharpe > 0,3 | efekt musí přetrvat na datech, která výzkum neviděl. Mírnější PF počítá s běžnou degradací, Sharpe > 0,3 vyjadřuje ekonomickou relevanci (pod 0,3 se provozní riziko a práce nevyplatí) [I] | před přeučením na DEV a před strategiemi, které fungovaly jen v jednom období |
| 3 | náklady ×1,5: expectancy DEV+OOS > 0 | skutečné náklady brokera jsou nejisté (syntetický ask B, jiný broker, swapová přirážka). Strategie musí mít rezervu | před „papírovým“ edge, který zmizí u horšího brokera |
| 4 | ≥ 70 % kombinací perturbační mřížky má expectancy > 0 | skutečný efekt nesmí záviset na přesné hodnotě parametru | před parameter miningem a osamocenými špičkami |
| 5 | spojený walk-forward výsledek > 0 | realistický proces pravidelné rekalibrace musí také vydělávat | před jednorázově šťastnou volbou parametrů |
| 6 | žádný kalendářní rok nepřinese > 50 % celkového čistého zisku | strategie, jejíž zisk pochází z jednoho roku, je sázka na opakování toho roku | před „jedním výjimečným obdobím“ (bod 11G a 13 zadání) |
| 7 | trade bootstrap: P(expectancy > 0) ≥ 90 % | statistická jistota, že kladný průměr není náhoda výběru obchodů. 90 % jednostranně odpovídá zhruba t ≈ 1,28, tedy relativně mírné laťce | před malými vzorky a šumem |
| 8 | holdout se jen reportuje, záporný výsledek snižuje důvěru, ale nemění pravidla | kdyby se pravidla po holdoutu měnila, holdout by se stal dalším DEV a ztratil by hodnotu | před laděním na posledních datech |

Jak číst tabulku: strategie je „robustní kandidát“ jen při splnění bran 1–7 současně. Co z toho plyne:
brány se navzájem doplňují. Brány 1–2 ověřují existenci efektu, 3 jeho ekonomickou rezervu, 4–5
nezávislost na parametrech, 6 nezávislost na období a 7 statistickou jistotu. Žádná testovaná
strategie neprošla všemi sedmi (kapitola 10 a 15). Nejčastěji selhávaly brány 2 (OOS Sharpe), 6
(koncentrace zisku) a 7 (bootstrap), tedy právě ty, které měří stabilitu v čase a statistickou jistotu.
Brány 3–5 trendové strategie splnily.

## 4.4 Nákladový model

Implementace: `tradingsystem/costs/model.py` (`CostModel`, `RateCurve`). Všechny brokerské složky se
pro stresové testy násobí faktorem m (baseline m = 1). Tržní sazba r se nenásobí.

### Spread

```
efektivní bid = mid − 0,5 × (ask − bid) × m
efektivní ask = mid + 0,5 × (ask − bid) × m,     mid = (bid + ask) / 2
```

Spread se bere přímo z dat: A má reálný bid/ask v každé minutě, B má ask syntetizovaný z mediánu spreadu
A podle serverové hodiny (kapitola 3.3). Long nakupuje na asku a prodává na bidu, short obráceně. Hrubý
PnL se počítá z mid, takže náklad spreadu = polovina spreadu na vstupu + polovina na výstupu.

### Skluz

```
skluz = cena × bp × 10⁻⁴ × m,    bp = 0,3 (market příkaz), 1,0 (stop příkaz, včetně stop-lossu)
long market vstup = ask_open + skluz;   long stop-loss výstup = min(stop, bid_open) − skluz
```

Stop příkazy mají vyšší skluz, protože se plní v okamžiku rychlého pohybu proti pozici. Gap přes stop
se navíc plní na horší ceně open, ne na úrovni stopu.

### Komise

`komise = objem (loty) × c × m` za každou stranu. Baseline c = 0 (spread-only účet, Dukascopy spread
~1,9 bp už obsahuje přirážku brokera). ECN scénář: c = 3,5 USD/lot/stranu (v kódu c = 7,0 s m = 0,5).

### Swap (noční financování)

```
notional = objem × 100 oz × mid (poslední bar před rollover)
long:  swap = −(r + 2,25 % × m) / 360 × notional × noci
short: swap = +(r − 2,25 % × m) / 360 × notional × noci
noci = 3 při rolloveru ze středy na čtvrtek, jinak 1
r = 3M US T-bill k předchozímu dni (RateCurve, dopředné doplnění)
```

Swap se účtuje při každé změně serverového dne (17:00 New York), trojitý ve středu (pokrývá víkend).
Konvence ACT/360 odpovídá peněžnímu trhu USD. **Kalibrace přirážky 2,25 %:** při ceně 3 300 USD
a r = 4,3 % dává model pro 1 lot −60,04 USD (long) a +18,79 USD (short) za noc. To odpovídá typickým
retailovým swapům 2024–2025 „long −60 / short +19 bodů“ (specifikace RoboForex, kapitola 5). Jeden bod
je 0,01 USD × 100 oz = 1 USD na lot. Pro roky před 2024 je přirážka předpoklad [U].

**Numerický příklad:** 1 lot při ceně 2 000 USD (notional 200 000 USD) a r = 5 %:

| Případ | Long za noc | Long středa (×3) | Long týden (7 nocí) | Short za noc | Short středa (×3) | Short týden |
|---|---|---|---|---|---|---|
| r = 5 %, baseline | −40,28 USD | −120,83 USD | −281,94 USD | +15,28 USD | +45,83 USD | +106,94 USD |
| r = 0 %, baseline | −12,50 USD | −37,50 USD | −87,50 USD | −12,50 USD | −37,50 USD | −87,50 USD |
| r = 5 %, stres ×1,5 | −46,53 USD | — | — | +9,03 USD | — | — |
| r = 5 %, stres ×2 | −52,78 USD | — | — | +2,78 USD | — | — |

Jak číst tabulku: výpočet podle vzorce výše (dopočet). Long: −(0,05 + 0,0225) / 360 × 200 000 =
−40,28 USD; short: +(0,05 − 0,0225) / 360 × 200 000 = +15,28 USD. Týden obsahuje 5 rolloverů, z toho
jeden trojitý, tedy 7 nocí. Co z toho plyne: při vysokých sazbách long platí a short dostává, při
nulových sazbách platí obě strany přirážku.

**Co to znamená v R:** typická pozice s rizikem 500 USD a stopem 20 USD má 0,25 lotu (notional 50 000
USD při 2 000 USD). Týdenní držení longu při r = 5 % stojí 70,49 USD = **−0,141 R**, short dostane
26,74 USD = +0,053 R. Při r = 0 platí obě strany 21,88 USD = −0,044 R. Pro srovnání: spread 1,9 bp
(0,38 USD/oz) stojí tuto pozici 9,50 USD za celý obchod (0,019 R) a skluz market vstupu se stop výstupem
6,50 USD (0,013 R). **U vícedenních longů v prostředí vysokých sazeb je swap největší nákladovou
položkou**, větší než spread a skluz dohromady [E, dopočet]. Odpovídá tomu skutečný rozklad C3
DEV+OOS: spread 1 806 USD, skluz 1 145 USD, swap −2 892 USD (kapitola 0.5).

### Stres a scénáře

| Scénář | m | Spread | Skluz market / stop | Komise | Přirážka swapu |
|---|---|---|---|---|---|
| hrubě (frictionless) | 0 | 0 | 0 / 0 | 0 | swap vypnut úplně, včetně r |
| baseline | 1,0 | reálný | 0,3 / 1,0 bp | 0 | 2,25 % |
| stres ×1,5 | 1,5 | 1,5× | 0,45 / 1,5 bp | 0 | 3,375 % |
| stres ×2 | 2,0 | 2× | 0,6 / 2,0 bp | 0 | 4,5 % |
| ECN | 0,5 | 0,5× | 0,15 / 0,5 bp | 3,5 USD/lot/strana | 1,125 % |

Jak číst tabulku: stres škáluje spread symetricky kolem mid, takže hrubý PnL zůstává stejný a mění
se jen náklady. Co z toho plyne: stres ×2 je přísnější test, než se na první pohled zdá, protože
zdvojnásobí i swapovou přirážku a skluz stopů. Hrubý běh slouží jen k rozkladu gross/net. Podle
zadání se strategie, která funguje jen hrubě, zamítá.

**Neověřitelné předpoklady [U]:** historické spready konkrétního brokera (Dukascopy je ECN agregátor),
skluz stop příkazů v rychlém trhu (1 bp je odhad), historická swapová přirážka (kalibrace na 2024–2025),
komise ECN účtů (3,5 USD/lot/strana je typická hodnota), u některých brokerů trojitý swap na kovy
v pátek místo ve středu (v kódu konfigurovatelné, `triple_swap_weekday`). Latence je pro H4 systém
nepodstatná (kapitola 10, test zpoždění vstupu).

## 4.5 Konvence simulátoru

Implementace: `tradingsystem/brokers/simulated.py` (`SimBroker`) a `tradingsystem/backtest/runner.py`.
Stejný `SimBroker` slouží i pro paper trading (s okamžitým plněním na živé kotaci).

### Pořadí zpracování jednoho H1 baru

```
1. změnil se serverový den?  → rollover: swap všech otevřených pozic (trojitý ve středu)
2. market příkazy čekající ve frontě → fill na OPEN tohoto baru (spread guard může odložit)
3. čekající stop-entry příkazy → fill, pokud bar prošel úrovní (OCO zruší ostatní vstupy strategie)
4. ochranné stopy a take-profity otevřených pozic → výstup, pokud bar prošel úrovní
5. aktualizace MAE / MFE
6. TradingEngine.on_clock: risk stav (měsíční báze, denní/týdenní limity, kill switch)
7. strategie, jejichž svíčka (H1/H4/D1) se tímto barem uzavřela → on_bar → signály → příkazy do fronty
8. ocenění equity a expozice na close baru
```

### Pravidla plnění

| Situace | Pravidlo | Proč |
|---|---|---|
| signál a market příkaz | signál na close svíčky, fill na **open dalšího H1 baru** (long na ask, short na bid) + skluz | žádný look-ahead: close je známý až po uzavření svíčky |
| zpoždění (`delay_bars`) | fill o N H1 barů později | robustnostní test zpoždění vstupu |
| stop-entry (C4) | fill, když ask high (long) / bid low (short) dosáhne úrovně, na ceně max(úroveň, open) pro long, min(úroveň, open) pro short, + skluz stopu | gap přes úroveň se plní na horší ceně |
| ochranný stop | spouští se na bidu (long) / asku (short); fill na horší z (stop, open) ± skluz stopu | broker-side stop, gap se plní na open |
| SL i TP v jednom baru | předpoklad: nejdřív SL | konzervativní, cesta uvnitř baru není známa |
| stop v témže baru | pozice otevřená v baru může být v témže baru vystopována | konzervativní |
| stop už za trhem při fillu | vstup odmítnut (jako u skutečného brokera) | reálný broker neumožní stop na špatné straně ceny |
| posun stopu za trh | místo neplatného stopu výstup market příkazem | stejná logika v ExecutionEngine pro live |
| posun stopu | jen ve směru snížení rizika | trailing nikdy riziko nezvyšuje |
| výstupní signál | market příkaz na open dalšího baru (long zavírá na bidu) | jako vstup |
| exit-and-reverse | výstup a nový vstup ze stejné svíčky jsou povoleny | nutné pro session strategie (C8, C8b) |
| rollover | swap při každé změně serverového dne (17:00 NY), ×3 ve středu | konvence MT5 brokerů |
| spread guard | market příkaz se odloží, když spread na open > 4 bp, max. 3 odklady (3 H1 bary), pak se vyplní | po denní přestávce je spread 3× vyšší (kapitola 3.5) |
| granularita | stopy všech strategií (i H4 a D1) se vyhodnocují na H1 barech | jemnější než signální timeframe, bez tick dat |
| částečné fills, dopad na trh | nemodelováno | retail objemy (desetiny lotu) jsou pro XAUUSD zanedbatelné [I] |

Jak číst tabulku: každý řádek je pravidlo, které simulátor uplatní bez výjimky. Co z toho plyne:
simulace je **konzervativní**. V nejasných situacích (SL a TP v jednom baru, gap, stop v baru vstupu)
volí horší variantu pro strategii. Hlavní nekonzervativní předpoklad je H1 granularita: uvnitř H1
baru se neví, zda cena nejdřív zasáhla stop, nebo se vrátila. U H4 trendových strategií se stopy
3 × ATR(H4) je to ale málo významné [I]. Většinu pravidel ověřují testy (kapitola 4.9).

## 4.6 Position sizing

Implementace: `tradingsystem/risk/manager.py::RiskManager.size_entry`.

```
riziková báze   E_m  = equity na začátku kalendářního měsíce (serverový čas)
rozpočet        B    = risk_per_trade × váha strategie × E_m          (0,5 % × 1 × E_m ve výzkumu)
referenční cena ref  = ask (long) / bid (short) v okamžiku signálu, u stop-entry úroveň příkazu
vzdálenost      d    = abs(ref − stop)    (musí být ≥ 5 bp ceny, jinak odmítnuto)
objem           V    = zaokrouhlit DOLŮ na 0,01 lotu ( B / (d × 100 oz) )   (pod 0,01 → odmítnuto)
skutečné riziko R$   = V × 100 × d   (≤ B; vůči němu se počítá R obchodu)
```

**Proč měsíční báze:** riziko nezávisí na nedávných ziscích ani ztrátách uvnitř měsíce. Nenavyšuje se
po sérii zisků a hlavně se nenavyšuje po ztrátách (žádný martingale, žádné dohánění ztrát), jak
požaduje zadání (bod 18). **Proč zaokrouhlení dolů:** skutečné riziko nikdy nepřekročí rozpočet. Vedlejší
efekt: u malých účtů nebo širokých stopů je skutečné riziko výrazně menší než 0,5 % (příklad v kapitole
0.12: 488 místo 500 USD). **Proč stop v násobcích ATR:** objem je nepřímo úměrný volatilitě, což podle
Harvey et al. (2018) snižuje chvosty rozdělení (kapitola 5).

**Nastavení ve výzkumu:** jednotlivé strategie běží s `RiskConfig(enforce_loss_limits=False, max_open_risk=1,0,
max_gross_notional_x_equity=50, max_spread_bps=10⁹)`. Platí tedy jen sizing 0,5 %, minimální vzdálenost
stopu a min. lot, produkční limity (denní / týdenní ztráta, DD stopy, max. otevřené riziko) jsou vypnuté,
aby nezkreslovaly měření edge. **Portfolio běhy** (`s03_portfolio.py`, `s04_holdout.py`) mají produkční
limity zapnuté (kapitola 11 a 17). Každá strategie drží nejvýš jednu pozici (žádné pyramidování ani
průměrování). Re-entry je možný jen na nový signál.

## 4.7 Výpočet metrik

Implementace: `tradingsystem/backtest/metrics.py` (`summarize`, `trade_stats`, `yearly_table`). Definice
a intuice jsou v kapitole 0.5. Implementační detaily, které ovlivňují interpretaci:

- **Equity křivka** se oceňuje na close každého H1 baru včetně nerealizovaného PnL na efektivních
  kotacích (long na bidu, short na asku). MaxDD tedy zahrnuje i ztráty otevřených pozic.
- **Denní výnosy** = poslední hodnota equity v každém serverovém dni, procentní změna. Sharpe a Sortino
  se anualizují √252, i když serverových dní je zhruba 258 ročně (rozdíl je zanedbatelný).
- **Roky** pro CAGR a obchody za rok = (poslední bar − první bar) / 365,25 dne.
- **PF** se počítá z USD, **expectancy** a **t** z R (`r = pnl_net / risk_amount`).
- **Expozice** = podíl H1 marků s nenulovým čistým objemem.
- **Roční tabulky** přiřazují obchod k roku **výstupu**. Roční výnos je z equity křivky.
- **Koncentrace (brána 6)** = maximální roční čistý PnL / celkový čistý PnL za DEV+OOS. Pokud je celkový
  zisk záporný, je koncentrace nekonečná a brána automaticky selže (C8b).
- **Pozice otevřené na konci období** nejsou v obchodních statistikách, ale jsou v equity.
- **Pooled 2004–2026** (`s05_summary.py`): každý segment běží zvlášť se 100 000 USD (PRE a DEV na
  spojené řadě, OOS na spojené řadě = A, holdout na A), obchody se sloučí. t-statistika a PF jsou ze
  všech obchodů, Sharpe ze spojených denních výnosů.

## 4.8 Statistické nástroje

Implementace: `research/stats.py` a `research/s02_validate.py`.

### Trade bootstrap

`trade_bootstrap(r, years, risk=0,005, n=10 000, seed=7)`: ze skutečných R hodnot DEV+OOS se n-krát
vylosuje s vracením stejný počet obchodů. Equity simulace = součin (1 + 0,005 × R). Výstupem jsou
percentily p05 / p50 / p95 CAGR (na 13,99 let DEV+OOS), expectancy, PF, MaxDD, nejdelší série ztrát
a „zotavení“ (nejdelší úsek obchodů pod předchozím maximem) a P(expectancy > 0). Pro strategie
s ≥ 2 000 obchody (C8b) se z výpočetních důvodů použije 2 000 opakování. **Omezení:** předpokládá
nezávislé obchody a ignoruje shlukování režimů, proto se doplňuje blokovým bootstrapem.

### Blokový bootstrap denních výnosů

`block_bootstrap_daily(ret, block=20, n=5 000, seed=11)`: časová řada denních výnosů o délce T se
poskládá z ⌈T/20⌉ náhodně vybraných souvislých bloků po 20 dnech (začátky rovnoměrně z 0 … T − 20)
a ořízne na T. Výstupem je rozdělení Sharpe, CAGR a MaxDD a P(Sharpe > 0). Bloky zachovávají
autokorelaci a shluky volatility do délky zhruba jednoho měsíce.

### PBO metodou CSCV

`pbo_cscv(M)`: M = matice ročních výnosů (řádky 2010–2023, tedy 14 let, sloupce = konfigurace
perturbační mřížky, u C3/C2/C5/C9 125, u C8b 18). Pro všech C(14, 7) = 3 432 rozdělení let na dvě
poloviny: v „tréninkové“ polovině se vybere konfigurace s nejvyšším poměrem průměr / směrodatná
odchylka ročních výnosů, v „testovací“ polovině se zjistí její relativní pořadí ω mezi ostatními
konfiguracemi a spočítá logit λ = ln(ω / (1 − ω)). **PBO = podíl rozdělení s λ ≤ 0**, tedy kdy vítěz
tréninku skončil v testu na mediánu nebo pod ním.

### Deflated Sharpe ratio a PSR

`deflated_sharpe(ret, n_trials, sr_var_trials)` podle Bailey a López de Prado (2014), vzorce jsou
v kapitole 0.8. Vstupy: denní výnosy DEV+OOS (T = 3 605 dní) nebo jen OOS (T = 1 290), N = 60
(10 variant DEV screeningu + zhruba 50 implicitně zvažovaných oken revize C8b, deklarováno v
`DEV_SELECTION.md`), V = rozptyl denních Sharpe deseti variant DEV screeningu. Výsledné SR0 = 1,465
anualizovaně, tedy konzervativní laťka, protože rozptyl mezi heterogenními kandidáty (Sharpe od −1,41
do +0,48) je velký. Mírnější varianta (`dsr_within_grid.json`) používá N = 125 a rozptyl Sharpe uvnitř
perturbační mřížky dané strategie (SR0 0,20–0,32). Ta byla dopočtena až v commitu s holdoutem (87cd6b6)
a na žádné rozhodnutí neměla vliv.

### Režimy

`regime_frame(d1, macro)`: definice v kapitole 0.9. Implementační detaily: mid close D1 spojené řady,
log-výnosy, σ20 = klouzavá směrodatná odchylka 20 dní, medián σ20 za 252 dní (min. 120 pozorování),
trendová statistika abs(ln(C_t / C_t−60)) / (σ60 × √60). Všechny štítky XAUUSD posunuty o 1 den
(`shift(1)`), makro řady posunuty o +1 kalendářní den a doplněny dopředu. Obchod dostane štítek dne
svého vstupu. Expectancy v režimu = průměr R obchodů s daným štítkem. Denní Sharpe v režimu se počítá
jen z dní s daným štítkem.

### Walk-forward

Pro každý testovací rok Y = 2014 … 2023: tréninkové okno = roky Y − 4 … Y − 1. Ze 3 × 3 konfigurací
(dva hlavní parametry, třetí na defaultu) se vybere ta s nejvyšším anualizovaným Sharpe denních výnosů
v tréninkovém okně. Její denní výnosy v roce Y se připojí ke spojené walk-forward křivce. Pro srovnání
se reportuje i výnos defaultní konfigurace v tomtéž roce. Denní výnosy pocházejí ze souvislých běhů
každé konfigurace přes celé DEV+OOS, takže v testovacím roce může dobíhat pozice otevřená na konci
tréninkového roku. Jde o zjednodušení oproti „čistému“ restartu každého foldu, na velikost efektu má
ale malý vliv [I].

### Perturbace a timeframe

- **Mřížka:** plný kartézský součin tří os po 5 hodnotách (125 běhů DEV+OOS), u C5 a C9 navíc
  jednorozměrné řezy (OAT) dalších parametrů (C5: rank_n, max_hold; C9: usd_ma). Brána 4 počítá jen
  plnou mřížku.
- **Timeframe:** délky v barech se přepočtou poměrem počtu barů za serverový den (H1 24, H2 12, H3 8,
  H4 6, H6 4, D1 1), zaokrouhlí a omezí zdola na 2. Například C2 entry_n 55 na H4 → 110 na H2, 37 na H6,
  9 na D1. Stop v násobcích ATR se nemění, ATR se počítá na novém timeframu.
- **Zpoždění:** `delay_bars = 1` (fill o jeden H1 bar později) a varianta se skluzem 0,9 / 3,0 bp.

### Subperiody

Roční tabulka (rok výstupu obchodu: počet obchodů, expectancy R, čistý PnL, long a short PnL) a 3leté
bloky 2010–2012, 2013–2015, 2016–2018, 2019–2021, 2022–2023 (poslední dvouletý).

## 4.9 Testy kódu

Sada `tests/` obsahuje **14 testů** (13 v `tests/test_core.py`, 1 v `tests/test_parity.py`). Pro tento
dokument byly znovu spuštěny (`python -m pytest -q tests`): **14 passed** za 65 s [E].

| Test | Co garantuje |
|---|---|
| `test_market_order_fills_next_open_at_ask` | market příkaz se nevyplní na signálním baru, ale na open dalšího baru, long na asku |
| `test_stop_loss_gap_fills_at_open_and_sl_before_tp` | gap pod stop se plní na open (horší než stop) a při zásahu SL i TP v jednom baru vyhrává SL |
| `test_stop_entry_gap_and_same_bar_stop` | stop-entry se plní na úrovni, a pokud bar dosáhne i stop-lossu, pozice se zavře v témže baru |
| `test_frictionless_gross_equals_net_and_costs_add_up` | gross − spread − skluz − komise + swap = net přesně a při m = 0 je net = gross |
| `test_triple_swap_on_wednesday_rollover` | rollover ze středy na čtvrtek účtuje 3 noci, swap = −notional × r / 360 × 3 |
| `test_spread_guard_defers_market_orders` | při spreadu 10 bp se market příkaz odloží a vyplní, až se spread vrátí k normálu |
| `test_indicators_are_causal` | ATR, Donchian, RSI, z-score, efficiency ratio, SMA a percentil bandwidth mají na zkrácené historii stejnou poslední hodnotu jako na plné (žádný look-ahead) |
| `test_risk_sizing_rounds_down_and_respects_caps` | 500 USD / (20 USD × 100 oz) = 0,25 lotu; limit otevřeného rizika odmítne další vstup; ztráta 2,5 % za den spustí denní limit |
| `test_sizing_base_is_month_start_equity` | sizing báze se mění jen na začátku měsíce, ne po zisku uprostřed měsíce |
| `test_duplicate_signal_never_sends_two_orders` | stejný signál zpracovaný dvakrát vytvoří jen jeden příkaz (idempotence) |
| `test_duplicate_protection_survives_restart` | po restartu procesu s novým brokerem se z JSONL ledgeru obnoví odeslaná ID a příkaz se neodešle znovu |
| `test_server_time_roundtrip_and_daily_bar_alignment` | převod UTC → server → UTC je konzistentní a 17:00 New York = serverová půlnoc |
| `test_resample_bidask_drops_weekend_and_aggregates` | agregace na D1 ukotvená na serverovou půlnoc, správné open/close, žádné víkendové bary |
| `test_backtest_and_live_runner_produce_identical_trades` | backtest driver a live driver dávají na stejných datech stejné obchody (parita) |

Jak číst tabulku: každý test pokrývá jedno pravidlo z kapitol 4.4–4.6 nebo jednu vlastnost produkční
architektury (kapitola 17). Co z toho plyne: nejdůležitější konvence simulátoru (žádný look-ahead,
konzervativní fills, swapy, sizing) i produkční ochrany (idempotence, restart) jsou strojově ověřené.
Testy ale neověřují chování vůči skutečnému MT5 terminálu, to vyžaduje demo (kapitola 18).

### Test parity backtest vs. live

Riziko architektury „jeden kód pro backtest i live“ je, že se obě cesty v detailech liší (jiné pořadí
událostí, jiná kotace pro sizing, jiné časování). `tests/test_parity.py` to ověřuje takto:

1. Vytvoří syntetická H1 data (260 obchodních dní, 23 hodin denně, náhodná procházka se slabým driftem)
   s open každého baru rovným close předchozího baru, pro bid i ask. Díky tomu má fill na živé kotaci
   (close signálního baru) stejnou cenu jako fill v backtestu (open dalšího baru).
2. Spustí dvě strategie současně (Donchian 20/10 na H4 a session strategii Asie/Londýn na H1) přes
   **backtest driver** (`run_backtest`).
3. Totéž spustí přes **live driver** (`LiveRunner` + `TradingEngine` + `SimBroker` s okamžitým plněním
   a `HistoricalMarketData`, který simuluje plynutí času: otevření baru, intrabar stopy, uzavření baru).
4. Porovná obchody: počet (rozdíl nejvýš 2 kvůli pozicím otevřeným na konci), časy vstupu, směr,
   vstupní a výstupní ceny s tolerancí 10⁻⁶.

Pro tento dokument byl test zopakován s výpisem: oba drivery vytvořily **568 obchodů (513 session,
55 Donchian) a všech 568 je identických** včetně časů vstupu i výstupu, směru a cen [E, dopočet].
`REPORT.md` uvádí „165/165“. Číslo zřejmě pochází z dřívější verze testu, závěr (plná parita) se
nemění. Co test **nepokrývá**: rozdíl mezi open dalšího baru a živou kotací na skutečném trhu (gap
mezi close a open) a chování MT5 (odmítnutí, částečné fills). To ověří až PAPER/DEMO fáze
s metrikou „parita signálů s offline replay ≥ 99 %“ (kapitola 18).

## 4.10 Úplný seznam odchylek od předregistrace

Protokol vyžaduje, aby každá odchylka byla výslovně označena. Seznam obsahuje odchylky uvedené
v `REPORT.md` a navíc ty, které byly nalezeny při přípravě tohoto dokumentu z historie gitu a kódu.

| Č. | Odchylka | Kdy (commit) | Dopad na závěry |
|---|---|---|---|
| 1 | před commitem protokolu proběhl jeden smoke test C2 na DEV podmnožině 2016-09 – 2018-12 (kontrola enginu) | před 6a151db (uvedeno v `REPORT.md`, z gitu neověřitelné) | malý: C2 má literaturní parametry Turtle, OOS ani holdout nebyly dotčeny; výzkumník ale viděl jeden DEV výsledek C2 předem [U] |
| 2 | po prvním DEV screeningu opraveny dvě chyby enginu: (a) exit-and-reverse neotevřel novou pozici, takže krátká noha C8 se nikdy neotevřela; (b) bezfrikční běh odmítal kotace s nulovým spreadem. DEV screening zopakován | 41ce7b8 (diff `execution/engine.py`: množina `closing`, podmínka `ask < bid`) | opravy zjevných chyb, ne ladění; výzkumník ale viděl DEV screening dvakrát [I] |
| 3 | **C8b je data-driven revize C8** odvozená z hodinového profilu DEV (Asie long 02 → 09, Londýn short 09 → 15) | 41ce7b8 | vysoké riziko data-miningu, DEV výsledek C8b je optimistický; zahrnuto do N = 60 v DSR; C8b stejně zamítnuta |
| 4 | předvybrané C2, C6, C8 selhaly na DEV bráně 1 → do plné validace C5, C9, C3 (podle DEV t-statistiky) + C2 a C8b transparentně | 41ce7b8 (`DEV_SELECTION.md`, před OOS) | pravidlo náhrady bylo v protokolu, pořadí a doplňkové mřížky C3, C5, C9, C8b deklarovány před OOS; zvyšuje počet testů; všichni náhradníci jsou stejná rodina (trend) |
| 5 | rizikové váhy portfolia 1/3 na strategii určeny až po DEV+OOS portfolio analýze | cfe78c3 (před holdoutem) | váhy nejsou v protokolu; rozhodnutí motivované drawdownem DEV+OOS (kapitola 11), ne holdoutem |
| 6 | **pravidlo pro směr nebylo uplatněno:** protokol říká, že směr, který samostatně neprojde branami 1–2, se v produkci vypne. `frozen_spec.json` směry označuje (např. long C3 v DEV i OOS záporný), ale ponechává symetrická pravidla | cfe78c3 (před holdoutem) | v holdoutu by pravidlo uškodilo: long C3 tam vydělal a short ztrácel (kapitola 12); doporučení symetrických pravidel je odůvodněno malým vzorkem na směr |
| 7 | úprava `strategies/session.py` po DEV screeningu: podpora M30 a posunu ±30 min pro timeframe test C8b, min_periods denního rozpětí 20 → 19 pro H1, maximální držení škálované na timeframe | cfe78c3 | žádný: DEV výsledek C8b je v `s01` i `s02` identický (4 569 obchodů, expectancy 0,0026 R, PF 1,022) [E, dopočet] |
| 8 | oprava reportování bran: brána 5 (walk-forward) se u C8b bez parametrů dříve vypisovala jako PASS, nově N/A a souhrn „ALL“ ignoruje N/A | 87cd6b6 (s holdoutem) | žádný: C8b selhává v šesti jiných branách; jde o opravu výpisu, ne výsledku |
| 9 | sada C deklarována pro křížovou kontrolu, ale žádný skript ji nepoužil | 6a151db → dodnes | žádný; dodatečná kontrola v tomto dokumentu (korelace 0,87 s A, kapitola 3.4) |
| 10 | nepředregistrované doplňkové analýzy: deflated Sharpe uvnitř mřížky (`dsr_within_grid.json`), souhrn 2004–2026 (`s05_pooled`), komplementarita se čtyřmi strategiemi včetně C9 | 87cd6b6, a697f2f (po holdoutu) | jen reportovací, žádné rozhodnutí nezměnily; vyřazení C9 z pořadí je zmrazeno v `frozen_spec.json` před holdoutem, výsledkový soubor s korelací C2/C9 0,79 byl ale commitnut až po holdoutu (a697f2f) |
| 11 | předregistrované mřížky a timeframe testy pro C6 a C8 neproběhly | — | důsledek pravidla: C6 a C8 selhaly na DEV, plná validace se týká jen postupujících kandidátů |
| 12 | timeframe D1 pro C5 netestován (deklarovány jen H2–H6) | 41ce7b8 | malý: C5 je kladná na H2, H3, H4 i H6 |

Jak číst tabulku: odchylky 1–6 jsou uvedeny v `REPORT.md` (odchylka 6 v kapitole o long/short),
odchylky 7–12 byly doplněny při přípravě tohoto dokumentu z historie gitu (`git show`) a kódu. Co z toho
plyne: žádná odchylka nezměnila parametry finálních strategií po zhlédnutí OOS nebo holdoutu.
Nejzávažnější z hlediska přeučení jsou odchylky 3 (C8b odvozena z dat, zamítnuta) a 4 (náhrada
předvybraných kandidátů trendovými variantami). Proto výzkum počítá DSR s N = 60 a výslovně uvádí,
že tři finální strategie jsou jedna sázka vybraná po DEV. Odchylka 6 je věcně nejdůležitější pro další
zpracování: pravidla zůstávají symetrická a vypínání směru se nedoporučuje bez mnohem většího vzorku.

> **Závěr:** Metodika je postavena tak, aby výsledek co nejméně závisel na rozhodnutích udělaných po
> zhlédnutí dat: předregistrace, chronologické zmrazování, konzervativní simulace s reálným bid/ask,
> sedm nezávislých bran a statistické korekce na počet testů. Odchylky jsou zdokumentované a žádná
> nezlepšila výsledek finálních strategií. Hlavní zbývající slabiny jsou malé vzorky obchodů, data-driven
> výběr trendové rodiny po DEV a znalost obecného vývoje trhu zlata u výzkumníka.

*Zdrojové soubory: `research/PROTOCOL.md`, `research/DEV_SELECTION.md`, `research/frozen_spec.json`,
`REPORT.md` (kapitola 2, odchylky), git historie (`git log`, `git show` commitů 6a151db, 41ce7b8, cfe78c3,
87cd6b6, 91dbb12, a697f2f), `research/common.py`, `research/registry.py`, `research/stats.py`,
`research/s01_dev_screen.py`, `research/s02_validate.py`, `research/s03_portfolio.py`, `research/s04_holdout.py`,
`research/s05_summary.py`, `research/results/s01_dev_screen.json`, `research/results/s02_C3.json`,
`research/results/s02_C8b.json`, `research/results/dsr_within_grid.json`, `research/results/cache/s02.log`
(verze z cfe78c3), `tradingsystem/costs/model.py`, `tradingsystem/brokers/simulated.py`,
`tradingsystem/backtest/runner.py`, `tradingsystem/backtest/metrics.py`, `tradingsystem/risk/manager.py`,
`tradingsystem/execution/engine.py`, `tradingsystem/live/engine.py`, `tradingsystem/live/runner.py`,
`tradingsystem/data/instrument.py`, `tests/test_core.py`, `tests/test_parity.py`; dopočty: swapové příklady
podle vzorce v `costs/model.py`, opakovaný běh testů a testu parity s výpisem počtu obchodů.*
