# 2. Zadání a jeho naplnění

## 2.1 Zdroj zadání

Zadání je v souboru `Project XAUUSD.docx` v kořeni repozitáře (anglicky, název „PROJECT: XAUUSD
AUTOMATED SWING TRADING SYSTEM“, podtitul „TASK: INDEPENDENT INTERNET RESEARCH + QUANTITATIVE
BACKEND VERIFICATION“). Text byl pro tuto kapitolu vytažen přímo z `word/document.xml` uvnitř souboru,
takže shrnutí níže vychází z doslovného znění, ne z jeho interpretace v `REPORT.md`.

## 2.2 Role a cíl

Zadání žádá, aby autor jednal jako kombinace pěti rolí:

1. senior systematický / kvantitativní trader,
2. portfolio manažer se zkušeností z více tržních režimů,
3. kvantitativní výzkumník,
4. risk manažer,
5. architekt Python obchodních systémů.

**Cíl:** nezávisle určit, které **tři** obchodní strategie jsou nejsilnějšími kandidáty pro robustní
automatizovaný swing trading systém na XAUUSD, a připravit jejich implementaci v deterministickém
Python TradingSystemu. Zadání výslovně říká, že úkolem **není potvrdit** žádnou předem zvolenou
strategii. Robustnost a opakovatelnost mají přednost před maximálním historickým výnosem. Pokud
důkazy podporují méně než tři skutečně silné přístupy, má to být výslovně řečeno.

## 2.3 Dvacet sekcí požadavků

| Č. | Sekce zadání | Podstata požadavku |
|---|---|---|
| 1 | Research objective | najít a seřadit 3 nejrobustnější deterministické swing strategie; nevybírat podle nejvyššího CAGR; přiznat, je-li silných přístupů méně |
| 2 | Independent internet research | široká rešerše (akademie, SSRN, futures, trend, zlato, makro, sezónnost, náklady); u tvrzení rozlišit důkaz / zdůvodnění / inferenci / předpoklad; citovat s daty |
| 3 | Strategy universe | sestavit univerzum rodin; vyloučit SMC/ICT, ručně kreslené úrovně, Elliott, martingale, grid, průměrování ztrát; ML jen nad robustní baseline |
| 4 | Define swing | signály H1/H4/D1, držení 4 h – 10 obchodních dní, ne scalping, dost obchodů pro statistiku |
| 5 | Initial strategy ranking | shortlist 6–10 rodin, skóre 0–100 v 11 kritériích, vysvětlit skórování, vybrat 3 k testu |
| 6 | Backend quantitative verification | nezávislý test v Pythonu; dlouhá data (ideálně 2010–2026); oddělit bar-level výzkum od bid/ask validace; nemíchat zdroje potichu; zaznamenat zdroj, zónu, typ ceny, chybějící data, omezení |
| 7 | Data split | striktně chronologicky ~50–60 / 20–25 / 20–25 %; nikdy nemíchat, neoptimalizovat na holdoutu; ideálně holdout 2024–2026 |
| 8 | Strategy construction rules | přesná deterministická pravidla (TF, indikátory, vstup, výstup, stop, sizing, long/short, souběh, re-entry); málo parametrů vysvětlených předem; žádná brute-force optimalizace |
| 9 | Long and short analysis | testovat celek, long a short zvlášť; přiznat, pokud jeden směr nemá edge |
| 10 | Cost model | žádný bezfrikční backtest; spread, komise, skluz, swap, latence; baseline, ×1,5 a ×2; strategii fungující jen před náklady zamítnout |
| 11 | Robustness testing | A walk-forward, B perturbace parametrů, C timeframe, D zpoždění vstupu, E Monte Carlo / bootstrap, F režimy bez budoucí informace, G stabilita po letech a blocích |
| 12 | Metrics | 18 povinných metrik (obchody, win rate, expectancy, PF, Sharpe, Sortino, CAGR, MaxDD, Calmar, expozice, držení, série ztrát, long/short, gross vs. net, citlivost na náklady); intervaly spolehlivosti |
| 13 | Overfitting check | posoudit parameter mining, výběr režimu, survivorship, data-snooping, look-ahead, nerealistické fills, malý vzorek, jedno výjimečné období; penalizovat stupně volnosti |
| 14 | Final selection | seřadit finální trojici, pro každou 14 povinných polí (edge, proč existuje, pravidla, TF, držení, long/short, režim selhání, náklady, 4 skóre /100, důvěra); odlišit „nejlepší historický výsledek“ od „nejlepšího kandidáta pro live robustnost“ |
| 15 | Portfolio complementarity | korelace výnosů, překryv obchodů, souběžná směrová expozice, překryv režimů a drawdownů; přiznat, jsou-li dvě strategie stejnou sázkou |
| 16 | Python TradingSystem architecture | vrstvy DATA → SIGNALS → STRATEGY → RISK → EXECUTION → PORTFOLIO → BROKER ADAPTER → LOGGING → MONITORING; strategie nesmí posílat příkazy; stejná logika pro backtest, paper, demo i live |
| 17 | Broker reality | MetaTrader 5, XAUUSD; contract size, min lot, lot step, margin, páka, bid/ask, komise, swap, odmítnuté příkazy, částečné fills, reconnect, ochrana proti duplicitám, staré kotace, hranice session |
| 18 | Risk framework | konzervativní hodnoty: riziko na obchod, max. expozice, denní a týdenní ztráta, DD stop strategie a portfolia, volatility sizing; žádný martingale; riziko nezávislé na nedávných ziscích |
| 19 | Do not confuse research with production | oddělit RESEARCH, BACKTEST, OOS VALIDATION, PAPER, DEMO, SMALL LIVE, PRODUCTION; objektivní promotion gates |
| 20 | Required final output | výstup ve 24 předepsaných sekcích (EXECUTIVE CONCLUSION … SOURCES) |

Jak číst tabulku: druhý sloupec je originální název sekce, třetí její podstata v jedné větě. Co z toho
plyne: zadání je metodicky náročnější než běžný „najdi ziskovou strategii“. Většina požadavků
(sekce 6–13) míří na **ověření, že výsledek není náhoda nebo artefakt**, ne na maximalizaci výnosu.

## 2.4 Kritické pravidlo

Zadání končí blokem „CRITICAL RULE“, který je pro interpretaci celého dokumentu klíčový:

> **„Do NOT tell me what you think I want to hear.“** Pokud všechny testované strategie selžou
> v robustní validaci, je třeba to říct. Strategii podporovanou literaturou, která selže na XAUUSD,
> je třeba zamítnout. Strategii s dobrým backtestem, ale slabým ekonomickým zdůvodněním a nestabilními
> parametry je třeba penalizovat nebo zamítnout. Pokud důkazy neopravňují označení „robustní“, je
> třeba to výslovně říct. Cílem není vyprodukovat tři atraktivní strategie, ale najít tři nejsilnější
> kandidáty, které by autor byl ochoten dál zkoumat, kdyby na výsledku závisel jeho vlastní kapitál.

Jak bylo pravidlo uplatněno: (a) výsledek „žádná strategie neprošla všemi branami“ je uveden hned
v první větě shrnutí; (b) literaturou podporované favority C6 (Connors RSI(2)) a C8 (overnight drift)
byly zamítnuty, protože na XAUUSD selhaly už před náklady; (c) C8b se silnou hrubou anomálií byla
zamítnuta, protože funguje jen před náklady; (d) tři „nejsilnější“ kandidáti jsou výslovně označeni za
**jednu** podkladovou sázku s důvěrou LOW.

## 2.5 Kontrolní tabulka naplnění 20 bodů zadání

Stavy: **splněno** = požadavek naplněn v plném rozsahu; **splněno s omezením** = naplněn, ale s
dokumentovaným omezením (data, prostředí); **nesplněno** = požadavek naplněn nebyl.

| Č. | Bod zadání | Kde v dokumentu | Stav | Poznámka / omezení |
|---|---|---|---|---|
| 1 | Research objective | kap. 1, 15 | splněno | pořadí C3, C2, C5 pro další zkoumání; výslovně řečeno, že důkazy podporují nanejvýš jeden (slabý) přístup, ne tři |
| 2 | Internet research | kap. 5, 20 | splněno s omezením | síťová politika sandboxu blokovala plné texty (arXiv, SSRN, FRED); vychází se z abstraktů a citací, neověřené detaily jsou označeny; komunitní zdroje jen sekundárně |
| 3 | Strategy universe | kap. 6 | splněno | 11 kandidátů (C1–C11) z různých rodin; zakázané přístupy vyloučeny předem; carry/swap posouzen a zamítnut [R]; ML (C11) vyloučeno pravidlem zadání |
| 4 | Define swing | kap. 6, 0.11, 10 | splněno | horizont 4 h – 10 dní je tvrdá podmínka scorecardu; C1 a C10 jsou mimo mandát; finální strategie drží 78–149 h |
| 5 | Initial ranking | kap. 6 | splněno | 11 kritérií se zveřejněnými vahami, skóre a zdůvodněním; výběr C2, C8, C6 předregistrován před backtestem |
| 6 | Backend verification | kap. 3, 4, 7, 10 | splněno s omezením | tick data nedostupná → bar-level výzkum s exekucí na reálném bid/ask (A); 2004–2016 jen bid a syntetický ask (B); zdroje se nemíchají potichu (sloupec `source`, přechod 2016-09-01) |
| 7 | Data split | kap. 3.8, 4.1 | splněno s omezením | 54 / 30 / 16 % (2010–2026) + PRE-SAMPLE 2004–2009; holdout 2024–2026 zachován a spuštěn jednou; holdout je kratší než doporučených 20–25 %, protože zadání preferuje právě 2024–2026 |
| 8 | Construction rules | kap. 10, 15, příl. C | splněno | literaturní defaulty zapsané před během; 4–8 parametrů na strategii; žádná brute-force optimalizace (mřížky jen pro robustnost) |
| 9 | Long/short | kap. 7, 10, 12, 13 | splněno | každá strategie a každý segment zvlášť long a short; režimová asymetrie výslovně popsána |
| 10 | Cost model | kap. 4.4, 10 | splněno s omezením | baseline, ×1,5, ×2, hrubě a ECN; historické spready a swapy konkrétního brokera nelze ověřit [U]; latence testována zpožděním vstupu |
| 11 | Robustness A–G | kap. 10, 11, 14 | splněno s omezením | všech 7 testů pro C3, C2, C5 (i C9, C8b); režim „sazby“ používá nominální 10Y, reálné výnosy (TIPS) nebyly dostupné; detail v kap. 2.6 |
| 12 | Metrics | kap. 0.5, 10 | splněno | všech 18 metrik; intervaly spolehlivosti z bootstrapu; detail v kap. 2.6 |
| 13 | Overfitting | kap. 14 | splněno | 8 zdrojů rizika pro každou strategii, PBO (CSCV), deflated Sharpe ve dvou variantách |
| 14 | Final selection | kap. 15 | splněno | všech 14 polí pro C3, C2, C5; „nejlepší historický výsledek“ (C2) odlišen od „nejlepšího kandidáta pro budoucí robustnost“ (C3) |
| 15 | Complementarity | kap. 11 | splněno | korelace, překryv pozic, směrová shoda, režimy, drawdowny; výslovně: C3, C2, C5 jsou jedna sázka, C2 a C9 prakticky totožné |
| 16 | Architecture | kap. 17 | splněno | balíček `tradingsystem/` se všemi požadovanými rozhraními; strategie vrací jen `Signal`; jeden `TradingEngine` pro všechny režimy; test parity backtest vs. live |
| 17 | Broker reality | kap. 17 | splněno s omezením | MT5 adaptér (`brokers/mt5.py`) adresuje všech 14 témat ze zadání, ale **nebyl spuštěn proti skutečnému terminálu** (sandbox bez Windows/MT5) → nutné ověření na demu |
| 18 | Risk framework | kap. 17, 16, příl. D | splněno | hodnoty v `config/paper.toml`; sizing z equity na začátku měsíce; žádný martingale; jeden rizikový rozpočet pro celou trendovou rodinu |
| 19 | Research vs production | kap. 18 | splněno | 7 fází, objektivní brány pro každý přechod, demotion pravidla; live vyžaduje explicitní příznak a vyplněnou bránu |
| 20 | Required output | kap. 2.8, `REPORT.md` | splněno | `REPORT.md` má přesně 24 předepsaných sekcí; toto PDF je přeskupuje (mapování v kap. 2.8) |

Jak číst tabulku: sloupec „Kde“ odkazuje na kapitoly tohoto PDF. „Splněno s omezením“ neznamená, že
práce chybí, ale že výsledek stojí na předpokladu nebo na datech, která nešlo plně ověřit. Co z toho
plyne: **žádný bod není nesplněn.** Omezení se soustřeďují do čtyř oblastí: (1) chybějící tick data
a neznámý původ GitHub mirrorů, (2) neověřitelné historické náklady konkrétního brokera, (3) MT5
adaptér neotestovaný proti reálnému terminálu, (4) nedostupné plné texty literatury a reálné výnosy
TIPS. Všechny čtyři jsou úkoly pro navazující fáze (kapitoly 16 a 18).

## 2.6 Detail: robustnostní testy (bod 11) a metriky (bod 12)

| Test (bod 11) | Co požadováno | Jak provedeno | Pro které strategie | Kde |
|---|---|---|---|---|
| A Walk-forward | sekvenční train/test, bez agresivní reoptimalizace | 4 roky trénink → 1 rok test, 2014–2023, výběr z mřížky 3 × 3 podle Sharpe | C3, C2, C5, C9 (C8b nemá parametry → jen roční řez) | kap. 10 |
| B Perturbace parametrů | okolní hodnoty, žádný kolaps mimo jednu hodnotu | plná mřížka 125 kombinací ±25 %, u C5 a C9 navíc jednorozměrné řezy; PBO | C3, C2, C5, C9; C8b 18 oken + 4 stopy | kap. 10, 14 |
| C Timeframe | logicky ekvivalentní sousední TF se stejným reálným horizontem | H2, H3, H4, H6 (+ D1) s přepočtem délek; C8b M30 vs. H1 a posun ±30 min | C3, C2, C9 (H2–D1), C5 (H2–H6), C8b | kap. 10 |
| D Zpoždění vstupu | +1 bar, vyšší skluz | +1 H1 bar; +1 H1 bar a skluz ×3 | všech 5 | kap. 10 |
| E Monte Carlo / bootstrap | CAGR, expectancy, PF, MaxDD, série ztrát, zotavení | trade bootstrap 10 000× a blokový bootstrap denních výnosů (bloky 20 dní, 5 000×) | všech 5 + portfolio | kap. 10, 11 |
| F Režimy | 10 režimů bez budoucí informace | trend/range, vysoká/nízká vol, silný/slabý USD, rostoucí/klesající výnosy, krize/normál; štítky z dat do předchozího dne | všech 5 | kap. 10, 11 |
| G Subperiody | po letech a víceletých blocích, penalizace koncentrace | roční tabulky, 3leté bloky, brána 6 (žádný rok > 50 % zisku) | všech 5 | kap. 10 |

Jak číst tabulku: každý z testů A–G byl proveden pro všechny tři finální strategie. Jediná mezera je
D1 timeframe u C5, který nebyl v mřížce deklarované v `DEV_SELECTION.md`. Co z toho plyne: rozsah
testů odpovídá zadání. Hlavní omezení není v počtu testů, ale v délce dat a malém počtu obchodů
(kap. 14).

| Metrika (bod 12) | Vykázáno | Poznámka |
|---|---|---|
| total trades, trades/year | ANO | každý segment, každá strategie |
| win rate | ANO | podíl obchodů s čistým PnL > 0 |
| average win / average loss | ANO | v R (ve výsledkových JSON i v USD) |
| expectancy per trade | ANO | v R i USD, s t-statistikou |
| profit factor | ANO | v USD |
| Sharpe, Sortino | ANO | denní výnosy equity, anualizace √252 |
| CAGR, maximum drawdown, Calmar | ANO | při 0,5 % riziku na obchod |
| exposure | ANO | podíl H1 barů s otevřenou pozicí |
| average holding time | ANO | průměr i medián v hodinách |
| longest losing streak | ANO | plus nejdelší doba pod vodou ve dnech |
| long/short contribution | ANO | PnL a expectancy po směrech |
| gross vs. net performance | ANO | rozklad spread / skluz / komise / swap |
| sensitivity to costs | ANO | ×0, ×1, ×1,5, ×2, ECN |
| intervaly spolehlivosti | ANO | p05 / p50 / p95 z obou bootstrapů |

Jak číst tabulku: všechny metriky požadované zadáním jsou v surových výsledcích
(`research/results/s02_*.json`) a v tabulkách kapitoly 10. Definice a vzorce jsou v kapitole 0.5.

## 2.7 Výslovné povinnosti „řekni to otevřeně“

Zadání na několika místech nežádá jen výpočet, ale výslovné přiznání nepříjemného výsledku. Tabulka
ukazuje, jak byla každá z těchto povinností naplněna.

| Povinnost ze zadání | Odpověď výzkumu | Kde |
|---|---|---|
| Podporují-li důkazy méně než tři silné přístupy, řekni to | ANO: podporují nanejvýš jeden, slabý (H4 trend) | kap. 1, 15 |
| Nemá-li jeden směr edge, reportuj to | ANO: long/short asymetrie je režimová; C2 short za 22 let −0,147 R | kap. 10, 12, 13 |
| Strategii fungující jen před náklady zamítni | ANO: C8b (hrubě +0,016 R, čistě −0,004 R v DEV+OOS) zamítnuta | kap. 8, 10 |
| Uveď nákladové předpoklady, které nelze historicky ověřit | ANO: spready jiného brokera, skluz stopů, swapová přirážka, komise ECN | kap. 4.4, 19 |
| Jsou-li dvě strategie stejnou sázkou, řekni to | ANO: C3, C2, C5 = jedna sázka; C2 a C9 korelace 0,79 | kap. 11 |
| Odliš „nejlepší historický výsledek“ od „nejlepšího pro live“ | ANO: historicky C2, pro budoucí robustnost C3 | kap. 15 |
| Strategii z literatury, která selže na XAUUSD, zamítni | ANO: C6 (RSI(2)) a C8 (overnight drift) zamítnuty už na DEV | kap. 7 |
| Úspěšný backtest automaticky neopravňuje další fázi | ANO: každý přechod má objektivní bránu; dnes jen pozorovací PAPER | kap. 18 |
| Pokud nic neprojde robustní validací, řekni to | ANO: žádná strategie neprošla všemi 7 branami | kap. 1, 10, 15 |

Jak číst tabulku: každý řádek odpovídá jedné větě zadání typu „explicitly state / report / reject“.
Co z toho plyne: výzkum ve všech bodech volil přiznání slabého výsledku před přikrášlením. To je
zároveň hlavní důvod, proč je finální doporučení tak opatrné.

## 2.8 Mapování 24 povinných výstupních sekcí na kapitoly tohoto PDF

Zadání předepisuje strukturu odpovědi ve 24 sekcích. `REPORT.md` ji dodržuje doslova. Toto PDF obsah
přeskupuje podle logiky výzkumu (data → metodika → důkazy → závěry) a rozšiřuje ho. Tabulka ukazuje,
kde najít obsah každé povinné sekce.

| Č. | Povinná sekce | Kapitola PDF | Sekce v REPORT.md |
|---|---|---|---|
| 1 | EXECUTIVE CONCLUSION | 1 | 1 |
| 2 | RESEARCH METHODOLOGY | 3, 4 | 2 |
| 3 | INTERNET EVIDENCE REVIEW | 5 | 3 |
| 4 | CANDIDATE STRATEGY UNIVERSE | 6 (a 0.11) | 4 |
| 5 | CANDIDATE SCORECARD | 6 | 5 |
| 6 | THREE SELECTED STRATEGIES | 7, 9, 15 | 6 |
| 7 | EXACT STRATEGY DEFINITIONS | 15, 10, příloha C | 7 |
| 8 | QUANTITATIVE BACKTEST RESULTS | 10, 13 | 8 |
| 9 | OOS RESULTS | 10 | 9 |
| 10 | WALK-FORWARD RESULTS | 10 | 10 |
| 11 | MONTE CARLO / BOOTSTRAP | 10, 11 | 11 |
| 12 | PARAMETER ROBUSTNESS | 10, 14 | 12 |
| 13 | TIMEFRAME ROBUSTNESS | 10 | 13 |
| 14 | COST STRESS | 10, 12 | 14 |
| 15 | REGIME ANALYSIS | 10, 11 | 15 |
| 16 | LONG VS SHORT ANALYSIS | 7, 10, 12, 13 | 16 |
| 17 | OVERFITTING ASSESSMENT | 14 | 17 |
| 18 | CROSS-STRATEGY CORRELATION | 11 | 18 |
| 19 | FINAL RANKING | 15 | 19 |
| 20 | PYTHON TRADINGSYSTEM ARCHITECTURE | 17 | 20 |
| 21 | IMPLEMENTATION ROADMAP | 18, 16 | 21 |
| 22 | OBJECTIVE PROMOTION GATES | 18 | 22 |
| 23 | MAJOR UNKNOWNS / LIMITATIONS | 19 | 23 |
| 24 | SOURCES | 20 | 24 |

Jak číst tabulku: první uvedená kapitola je hlavní místo, další obsahují doplňující tabulky. Co z toho
plyne: všech 24 povinných sekcí je v dokumentu pokryto. Kapitoly 0, 2, 8, 9 a 16 a přílohy A–F jsou
navíc nad rámec předepsané struktury a slouží k vysvětlení a reprodukovatelnosti.

## 2.9 Souhrnné hodnocení naplnění

> **Závěr:** Zadání je naplněno ve všech 20 bodech a ve všech 24 výstupních sekcích. Šest bodů je
> „splněno s omezením“ (2, 6, 7, 10, 11, 17). Omezení jsou dána prostředím (blokovaná síť, žádný MT5
> terminál) a dostupností dat (žádná tick data, žádné reálné výnosy TIPS, žádné historické náklady
> konkrétního brokera), ne vynecháním práce. Věcný výsledek je negativní: zadání žádalo tři robustní
> strategie, výzkum našel nula robustních a jednu slabou rodinu. Podle kritického pravidla zadání je
> to legitimní a požadovaná odpověď.

Co z toho plyne pro další zpracování:

1. Omezení z bodů 6 a 10 (data a náklady) se odstraní re-validací na historii a nákladech vlastního
   brokera (fáze 1 roadmapy, kapitola 18).
2. Omezení bodu 17 (MT5) se odstraní integračními testy na demo účtu (fáze 2).
3. Omezení bodů 2 a 11 (literatura, reálné výnosy) jsou pro současný závěr méně kritická: změnit by
   mohla jen motivaci makro filtrů (C9), které už byly zamítnuty z jiných důvodů.

*Zdrojové soubory: `Project XAUUSD.docx` (`word/document.xml`, text zadání), `REPORT.md` (struktura 24
sekcí), `research/PROTOCOL.md`, `research/DEV_SELECTION.md`, `research/frozen_spec.json`,
`research/registry.py`, `research/s02_validate.py`, `research/results/s01_dev_screen.json`,
`research/results/s02_C3.json`, `research/results/s02_C2.json`, `research/results/s02_C5.json`,
`research/results/s02_C9.json`, `research/results/s02_C8b.json`, `research/results/s03_portfolio.json`,
`research/results/s05_pooled.json`, `tradingsystem/brokers/mt5.py`, `config/paper.toml`.*
