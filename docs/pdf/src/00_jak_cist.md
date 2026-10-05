# 0. Jak číst tento dokument

## 0.1 Účel dokumentu

Dokument je podrobná a samostatná zpráva o nezávislém výzkumu systematických swing strategií pro
XAUUSD (spotové zlato proti americkému dolaru). Je určen pro **další zpracování**: navazující vývoj,
paper/demo trading a další výzkum. Čtenář nemusel být u výzkumu, přesto by měl pochopit:

- **co** bylo zvažováno a testováno: univerzum 11 kandidátů C1–C11, z nichž 9 bylo backtestováno
  (C10 netestována, C11 vyloučena), a k tomu data-driven revize C8b, tedy 10 variant v DEV screeningu,
- **jak** (předregistrovaný protokol, chronologické segmenty, realistické náklady, robustnostní testy),
- **s jakým výsledkem** (žádná strategie neprošla všemi sedmi předem stanovenými branami),
- **proč** je pořadí pro další zkoumání právě C3, C2, C5 a proč ostatní vypadly,
- **s jakou jistotou** (nízkou) a co by ji mohlo zvýšit nebo snížit.

Dokument rozšiřuje hlavní výstup repozitáře `REPORT.md` o vysvětlení, interpretace, úplné tabulky
a dopočty. Při rozporu mezi tímto dokumentem a `REPORT.md` platí surové výsledkové soubory
v `research/results/`, ze kterých jsou zde čísla převzata. Kde je číslo dopočítáno nově pro tento
dokument, je to v textu výslovně uvedeno.

> **Závěr v jedné větě:** Na XAUUSD 2004–2026 s realistickými náklady existuje nanejvýš jeden slabý
> zdroj edge, střednědobý trend na H4 (C3, C2, C5 jsou tři varianty téže sázky). Žádnou strategii nelze
> označit za robustní a doporučena je pouze pozorovací PAPER fáze bez kapitálu.

## 0.2 Struktura dokumentu

| Kapitola | Název | Co obsahuje |
|---|---|---|
| 0 | Jak číst tento dokument | legenda, slovník metrik a pojmů, ID kandidátů, rozebraný příklad obchodu |
| 1 | Manažerské shrnutí | verdikt, klíčová čísla, proč tyto tři a proč ne ostatní |
| 2 | Zadání a jeho naplnění | shrnutí zadání, kontrola všech 20 bodů a 24 výstupních sekcí |
| 3 | Data | zdroje, ověření časových zón, kvalita, spready, konstrukce barů, makro řady |
| 4 | Metodika, protokol a simulace | chronologie, předregistrace, brány, nákladový model, simulátor, statistika, testy, odchylky |
| 5 | Literatura | rešerše akademické a praktické evidence, rozlišení [E]/[R]/[I]/[U] |
| 6 | Kandidáti a scorecard | univerzum 11 kandidátů, váhy a skóre, předregistrovaný výběr |
| 7 | DEV screening | výsledky všech kandidátů na DEV 2010–2018, long/short, křížová kontrola zdrojů |
| 8 | Session efekt | hodinový profil zlata, C8 a jeho revize C8b |
| 9 | Výběr po DEV | pravidlo náhrady, proč C3, C5, C9 (+ C2, C8b) |
| 10 | Plná validace | C3, C2, C5, C9, C8b: segmenty, náklady, perturbace, timeframe, walk-forward, bootstrap, režimy, roky |
| 11 | Komplementarita a portfolio | korelace, překryvy pozic a drawdownů, portfolio se třemi variantami rizika |
| 12 | Holdout | jednorázový test 2024–2026 se zmrazenou specifikací |
| 13 | Souhrn 2004–2026 | pooled statistiky přes čtyři segmenty |
| 14 | Overfitting | PBO, deflated Sharpe, zdroje rizika přeučení |
| 15 | Finální pořadí a odůvodnění | pořadí C3, C2, C5, karty strategií, přesná pravidla |
| 16 | Doporučení pro další zpracování | co dělat dál a v jakém pořadí |
| 17 | Architektura | Python balíček `tradingsystem/`, broker realita MT5, risk framework |
| 18 | Roadmapa a promotion gates | fáze RESEARCH → PRODUCTION a objektivní brány |
| 19 | Rizika a omezení | co nevíme a co může výsledky zkreslit |
| 20 | Zdroje | literatura, data, dokumentace |
| A | Příloha – protokol | doslovné znění `research/PROTOCOL.md` |
| B | Příloha – DEV_SELECTION | doslovné znění `research/DEV_SELECTION.md` |
| C | Příloha – frozen_spec | `research/frozen_spec.json` (zmrazená specifikace před holdoutem) |
| D | Příloha – paper.toml | `config/paper.toml` (konfigurace PAPER fáze) |
| E | Příloha – kvalita dat | `research/results/data_quality.json` |
| F | Příloha – repozitář | seznam souborů a postup reprodukce |

Jak číst tabulku: kapitoly 1 a 15–16 stačí pro rozhodnutí, kapitoly 3–4 vysvětlují, proč lze čísla
brát vážně, kapitoly 7–14 obsahují důkazy. Co z toho plyne: kdo chce na výzkum navázat kódem, potřebuje
navíc kapitoly 17–18 a přílohy C a D. Kdo chce ověřit poctivost postupu, kapitolu 4 a přílohy A a B.

Doporučené pořadí čtení podle role:

- **Rozhodovatel / portfolio manažer:** 1 → 15 → 16 → 19.
- **Kvant / výzkumník:** 0 → 3 → 4 → 7 → 10 → 14 → 11 → 12 → 13.
- **Vývojář navazujícího systému:** 0 → 4.5–4.6 → 17 → 18 → přílohy C a D.

## 0.3 Legenda značek

Zadání požaduje u každého důležitého tvrzení rozlišit typ opory. Dokument používá čtyři značky:

| Značka | Význam | Příklad |
|---|---|---|
| [E] | empirický důkaz: měření v tomto výzkumu nebo publikovaná empirická studie | „C3 má v DEV+OOS 256 obchodů a expectancy +0,061 R“ |
| [R] | ekonomické zdůvodnění: mechanismus, proč by efekt mohl existovat | „pomalá difúze makro informací vytváří trendy“ |
| [I] | expertní inference: úsudek odvozený z důkazů, ale přímo neověřený | „long breakouty zlata čelí větším whipsawům kvůli inverzní asymetrii volatility“ |
| [U] | nepodložený předpoklad: nutný pro výpočet, ale neověřitelný | „swapová přirážka 2,25 % p.a. platila i v letech 2010–2016“ |

Jak číst tabulku: značka [E] neznamená „pravda“, jen „změřeno“. Měření může být zatížené šumem,
viz kapitola 14. Co z toho plyne: tvrzení [I] a [U] jsou první kandidáti na ověření v PAPER/DEMO fázi.

## 0.4 Konvence

- **Čísla** jsou česky: desetinná čárka (0,061), tisíce mezerou (14 437), procenta s mezerou (7,4 %).
- **Data** jsou ve formátu ISO (2024-01-01). Segmenty jsou polootevřené intervaly: DEV
  „2010-01-01 – 2018-12-31“ znamená všechny bary od 2010-01-01 00:00 do 2019-01-01 00:00 serverového času (bez něj).
- **Časy** jsou v serverovém čase (New York + 7 h), pokud není uvedeno jinak (kapitola 0.10).
- **R** je násobek rizika obchodu (kapitola 0.5). Výsledky v R nezávisí na velikosti účtu ani na sizingu.
- **PnL v USD** se vždy vztahuje k účtu 100 000 USD a riziku 0,5 % na obchod, pokud není uvedeno jinak.
- **Baseline náklady** znamenají reálný bid/ask z dat, skluz 0,3 / 1,0 bp, nulovou komisi a modelový swap (kapitola 4.4).

## 0.5 Slovník: výkonnostní metriky

Všechny metriky počítá `tradingsystem/backtest/metrics.py` z uzavřených obchodů a z equity křivky,
která se oceňuje na konci každého H1 baru včetně nerealizovaného zisku. Pro ilustraci jsou použita čísla
strategie C3 v období DEV+OOS 2010–2023 (`research/results/s02_C3.json`), pokud není uvedeno jinak.

### R-multiple (R)

**Definice:** čistý zisk nebo ztráta obchodu dělená skutečným rizikem obchodu, tedy částkou, kterou by
obchod ztratil při zásahu počátečního stop-lossu.

```
R = čistý PnL obchodu (USD) / riziko ke stopu (USD)
riziko ke stopu = objem (loty) × 100 oz × abs(vstupní cena − počáteční stop)
```

**Numerický příklad:** účet 100 000 USD, riziko 0,5 % = 500 USD na obchod. Stop je 20 USD od vstupu.
Jeden lot XAUUSD = 100 uncí, takže 1 lot ztratí na 20 USD pohybu 2 000 USD. Objem = 500 / (20 × 100)
= **0,25 lotu**. Pokud obchod skončí čistým ziskem +1 000 USD, je to **+2 R**; ztráta −500 USD je −1 R.
Tento přesný případ ověřuje test `test_risk_sizing_rounds_down_and_respects_caps`.

**Intuice:** R srovnává obchody různé velikosti a z různých období. Obchod za +2 R vydělal dvojnásobek
toho, co riskoval. Ztráta může být i horší než −1 R (gap přes stop, skluz, swap) nebo menší (trailing
stop už přitažený k ceně).

### Expectancy v R a její t-statistika

**Definice:** průměrný R na obchod. Je to nejdůležitější číslo celého dokumentu, protože říká, kolik
strategie v průměru vydělá na jednotku rizika po všech nákladech.

```
expectancy = průměr(R_i),  i = 1..n
t = expectancy / (směrodatná odchylka(R) / odmocnina(n))
```

**Příklad:** C3 DEV+OOS: n = 256, expectancy +0,061 R, t = 0,93. Z toho plyne směrodatná odchylka R
přibližně 1,05 (dopočet: 0,0611 × 16 / 0,927). **Intuice:** t vyjadřuje, kolikrát je průměr větší než jeho
statistická nejistota. Hodnota t ≈ 2 odpovídá zhruba 5% hladině významnosti pro jeden test. Při
mnoha testech je potřeba víc (Harvey, Liu, Zhu 2016 doporučují t > 3). Dopočet ukazuje, jak malý efekt
to je: aby C3 se stejnou expectancy a rozptylem dosáhla t = 2, potřebovala by přibližně 1 190 obchodů,
při jejích 18,3 obchodech ročně tedy zhruba 65 let dat [I].

### Win rate, průměrný zisk a průměrná ztráta v R

**Definice:** win rate je podíl obchodů s čistým PnL > 0. Průměrný zisk v R je průměr R ziskových
obchodů a průměrná ztráta v R je průměr R obchodů s R ≤ 0.

```
expectancy ≈ win rate × průměrný zisk R + (1 − win rate) × průměrná ztráta R
```

**Příklad:** C3: 0,348 × 1,127 + 0,652 × (−0,507) = +0,061 R. **Intuice:** trendové systémy mají nízkou
win rate (30–40 %) a vydělávají tím, že zisky jsou 2–3× větší než ztráty. Mean-reversion systémy mají
profil opačný (C6: win rate 64,6 % v DEV, přesto záporná expectancy). Samotná win rate o kvalitě
strategie nic neříká.

### Profit factor (PF)

**Definice:** součet čistých zisků ziskových obchodů dělený absolutní hodnotou součtu čistých ztrát
ztrátových obchodů. V tomto výzkumu se počítá **v USD** (ne v R).

```
PF = součet(PnL_i, PnL_i > 0) / abs(součet(PnL_i, PnL_i <= 0))
```

**Intuice:** PF = 1 je nula, PF 1,18 (C3) znamená, že na každý ztracený dolar připadlo 1,18 vydělaného.
Brány používají PF > 1,10 (DEV) a PF > 1,05 (OOS). PF pod 1,2 je u systematických strategií velmi tenká
rezerva: malé zvýšení nákladů ji smaže.

### Sharpe ratio

**Definice:** průměr denních výnosů equity dělený jejich směrodatnou odchylkou, anualizovaný √252.
Denní výnos je změna equity mezi konci dvou serverových dnů (obchodní den 17:00–17:00 New York),
včetně nerealizovaného PnL otevřených pozic.

```
Sharpe = průměr(r_d) / směr. odchylka(r_d) × odmocnina(252)
```

**Intuice:** výnos na jednotku kolísání. Je nezávislý na páce, ale ne na podílu času v trhu: strategie,
která je 73 % času mimo trh (C3), má mnoho nulových dnů. Užitečná pomůcka [I]: t-statistika průměrného
výnosu ≈ Sharpe × √(počet let). Pro C3 je 0,25 × √14 ≈ 0,93, což sedí s t expectancy. Sharpe 0,3 by
k t = 2 potřeboval (2 / 0,3)² ≈ 44 let dat.

### Sortino ratio

**Definice:** jako Sharpe, ale ve jmenovateli je jen „downside deviation“, odmocnina z průměru čtverců
záporných denních výnosů. Průměruje se přes všechny dny, kladné dny přispívají nulou.

```
Sortino = průměr(r_d) / odmocnina(součet(min(r_d,0)^2) / N) × odmocnina(252)
```

**Intuice:** trestá jen ztrátové kolísání. U trendových strategií s pozitivní šikmostí vychází Sortino
výrazně nad Sharpe (C3: 0,41 vs. 0,25).

### CAGR

**Definice:** složená roční míra růstu equity mezi začátkem a koncem období.

```
CAGR = (konečná equity / počáteční equity)^(1 / roky) − 1,   roky = dny / 365,25
```

**Intuice:** závisí na sizingu. Při 0,5 % riziku na obchod má C3 v DEV+OOS CAGR jen 0,53 %. Při
dvojnásobném riziku by byl zhruba dvojnásobný, ale stejně by vzrostl drawdown. Proto se strategie
srovnávají v R a Sharpe, ne v CAGR.

### Maximální drawdown (MaxDD) a doba pod vodou

**Definice:** největší relativní pokles equity od předchozího maxima. Equity se oceňuje každou hodinu,
takže zahrnuje i nerealizované ztráty otevřených pozic. Doba pod vodou je nejdelší úsek v kalendářních
dnech mezi maximem a jeho překonáním.

```
DD_t = equity_t / max(equity_0..t) − 1,   MaxDD = −min(DD_t)
```

**Příklad:** C3 DEV+OOS: MaxDD 7,4 %, nejdelší období pod vodou 1 666 dní (přes 4,5 roku). **Intuice:**
MaxDD je historický vzorek jedné cesty. Bootstrap (kapitola 0.8) ukazuje, jak by mohl vypadat při jiném
pořadí obchodů.

### Calmar ratio

**Definice:** CAGR / MaxDD. **Intuice:** kolik ročního výnosu připadá na jednotku nejhoršího propadu.
C3 má 0,07, tedy ročně vydělá 7 % svého maximálního drawdownu. Hodnoty pod 0,5 jsou pro samostatné
nasazení velmi slabé.

### Expozice

**Definice:** podíl H1 barů, na jejichž konci byla otevřená alespoň nějaká pozice (čistý objem ≠ 0).
**Příklad:** C3 27 %, C2 45 %, C5 32 %. **Intuice:** čím menší expozice, tím menší výnos „za nic“ (beta
ke zlatu), ale také víc nulových dní. U portfolia ukazuje, jak často je kapitál v riziku.

### Doba držení

**Definice:** čas mezi vstupem a výstupem v hodinách (průměr a medián). **Příklad:** C3 průměr 128 h,
medián 104,5 h, tedy zhruba 4–5 obchodních dní. Zadání vymezuje swing jako 4 h až 10 obchodních dní.

### Nejdelší série ztrát

**Definice:** nejvyšší počet po sobě jdoucích obchodů s čistým PnL ≤ 0. **Příklad:** C3 12, C2 8, C5 10
v DEV+OOS. **Intuice:** při 35% win rate je série deseti a více ztrát běžná. Kdo ji psychicky ani
procesně neunese, nemůže trendovou strategii provozovat. Bootstrap ukazuje i horší série (p95 = 17 u C3).

### Doba zotavení

**Definice:** ve výsledcích se objevuje ve dvou podobách: (a) nejdelší doba pod vodou v kalendářních
dnech z equity křivky, (b) v trade bootstrapu nejdelší počet po sobě jdoucích obchodů, během nichž
simulovaná equity nedosáhla nového maxima („obchodů od vrcholu k vrcholu“). **Intuice:** u slabého
edge je zotavení dlouhé: medián 109 obchodů u C3 znamená zhruba 6 let při 18 obchodech ročně.

### Gross vs. net PnL a rozklad nákladů

**Definice:** hrubý PnL obchodu se počítá z mid cen (průměr bid a ask) při vstupu a výstupu. Čistý
PnL obsahuje všechny náklady:

```
net = gross − spread − skluz − komise + swap
```

- **spread**: polovina bid/ask spreadu při vstupu a polovina při výstupu (obchoduje se na ask/bid, gross na mid),
- **skluz**: 0,3 bp ceny u market příkazu, 1,0 bp u stop příkazu (včetně stop-lossu),
- **komise**: USD na lot a stranu (baseline 0, ECN scénář 3,5),
- **swap**: noční financování pozice. Je se znaménkem: long platí, short podle úrovně sazeb dostává nebo platí.

**Příklad:** C3 DEV+OOS: gross 13 586 USD − spread 1 806 − skluz 1 145 − komise 0 + swap (−2 892) =
**net 7 743 USD**. Náklady tedy spotřebovaly 43 % hrubého zisku a největší položkou byl swap. Stejný
rozklad pro všechny strategie je v kapitole 10.

## 0.6 Slovník: nákladové scénáře

| Scénář | Spread | Skluz market / stop | Komise | Swapová přirážka | Účel |
|---|---|---|---|---|---|
| ×0 (hrubě) | 0 (obchod na mid) | 0 / 0 | 0 | swap vypnut úplně | rozklad gross/net, zjištění, zda efekt existuje před náklady |
| ×1 (baseline) | reálný bid/ask z dat | 0,3 / 1,0 bp | 0 | 2,25 % p.a. | hlavní realistický odhad |
| ×1,5 | 1,5× šířka kolem mid | 0,45 / 1,5 bp | 0 | 3,375 % p.a. | brána 3: musí zůstat expectancy > 0 |
| ×2 | 2× šířka kolem mid | 0,6 / 2,0 bp | 0 | 4,5 % p.a. | reportuje se, ukazuje rezervu |
| ECN | 0,5× šířka | 0,15 / 0,5 bp | 3,5 USD/lot/strana | 1,125 % p.a. | optimistický účet s komisí |

Jak číst tabulku: násobek škáluje všechny brokerské náklady, tedy spread, skluz, komisi a swapovou
přirážku. Tržní úroková sazba ve swapu (3M T-bill) se neškáluje, protože to není náklad brokera. ECN
scénář je v kódu implementován jako násobek 0,5 s komisí 7,0 USD, efektivně tedy 3,5 USD/lot/stranu
(`research/s02_validate.py`), takže polovinu dostává i skluz a swapová přirážka. Co z toho plyne: ECN
scénář je spíš optimistická horní mez než realistický odhad [I]. Strategie, která funguje jen ve ×0,
se podle zadání zamítá (C8b).

## 0.7 Slovník: validační postupy

### Segmenty PRE / DEV / OOS / HOLDOUT

| Segment | Období | Data | Role |
|---|---|---|---|
| PRE-SAMPLE | 2004-07-01 – 2009-12-31 | B | nepoužit k vývoji, zpětný nezávislý test |
| DEV | 2010-01-01 – 2018-12-31 | B do 2016-08-31, pak A | jediné místo, kde se smělo rozhodovat |
| OOS | 2019-01-01 – 2023-12-31 | A | jen vyhodnocení, žádné ladění |
| HOLDOUT | 2024-01-01 – 2026-08-31 | A | spuštěn jednou po zmrazení specifikace |

Jak číst tabulku: segmenty jdou striktně chronologicky a nikdy se nemíchají. Co z toho plyne: výsledek
na DEV je optimisticky zkreslený (vybíralo se na něm), OOS a holdout jsou poctivější, PRE-SAMPLE je
nezávislý test do minulosti. „DEV+OOS“ je souvislý běh 2010-01-01 – 2023-12-31, na kterém se dělaly
robustnostní testy (perturbace, timeframe, bootstrap, režimy). Každý segment začíná s 100 000 USD
a indikátory dostávají 400 dní historie před začátkem segmentu (warm-up), obchodovat se ale začíná
až prvním dnem segmentu. Pozice otevřená na konci segmentu se do statistik obchodů nezapočítá.

### Walk-forward

Klouzavé okno: 4 roky tréninku → 1 rok testu, testovací roky 2014–2023 (10 foldů). V každém foldu se
z mřížky 3 × 3 hodnot dvou hlavních parametrů vybere kombinace s nejvyšším Sharpe v tréninkových
4 letech a její denní výnosy v následujícím roce se připojí k „walk-forward OOS“ křivce. Brána 5
vyžaduje kladný spojený výnos. **Intuice:** walk-forward simuluje, co by dělal obchodník, který si
každý rok přeladí parametry podle posledních let. Pokud je výsledek podobný pevným parametrům,
výběr parametrů nemá hodnotu, což je pro robustnost dobrá zpráva.

### Perturbace parametrů

Plná mřížka 5 × 5 × 5 = 125 kombinací tří hlavních parametrů, přibližně ±25 % kolem výchozí hodnoty
(např. C3: fast {15, 17, 20, 23, 25} × slow {75, 85, 100, 115, 125} × stop {2,25 … 3,75} ATR), vždy na
DEV+OOS. Brána 4 vyžaduje, aby ≥ 70 % kombinací mělo kladnou čistou expectancy. **Intuice:** robustní
efekt tvoří „plató“, tedy okolí výchozích parametrů je také ziskové. Přeučená strategie má osamocenou
špičku.

### Timeframe robustnost a zpoždění vstupu

Strategie se spustí na sousedních timeframech (H2, H3, H6, D1), přičemž délky indikátorů se přepočtou
na stejný reálný čas (C2 H4 55/20 → H2 110/40). Zpoždění vstupu: market příkaz se vyplní o jeden H1 bar
později, ve druhé variantě navíc s trojnásobným skluzem (0,9 / 3,0 bp).

## 0.8 Slovník: statistické nástroje

### Trade bootstrap

Ze skutečných R hodnot obchodů se 10 000× vylosuje s vracením stejný počet obchodů. Equity každé
simulace roste násobením (1 + 0,005 × R) po každém obchodu. Z 10 000 cest se spočítají percentily
p05 / p50 / p95 expectancy, PF, CAGR, MaxDD, nejdelší série ztrát a doby zotavení a pravděpodobnost
P(expectancy > 0). Brána 7 vyžaduje P ≥ 90 %. **Intuice:** ukazuje, jak moc mohl výsledek záviset na
štěstí v pořadí a výběru obchodů. Předpokládá ale nezávislost obchodů.

### Blokový bootstrap

Denní výnosy equity se skládají z náhodně vybraných souvislých bloků po 20 obchodních dnech
(5 000 simulací). **Intuice:** zachovává krátkodobou závislost (shluky volatility, série ztrát), kterou
trade bootstrap ignoruje. Výsledkem je rozdělení Sharpe, CAGR a MaxDD a pravděpodobnost P(Sharpe > 0).

### PBO (Probability of Backtest Overfitting, metoda CSCV)

Bailey, Borwein, López de Prado, Zhu (2017). Matice M má v řádcích roky 2010–2023 (14 let) a ve
sloupcích všech 125 konfigurací z perturbační mřížky, v buňkách roční výnos. Roky se rozdělí všemi
způsoby na dvě poloviny po 7 letech (C(14,7) = 3 432 rozdělení). V první polovině („trénink“) se vybere
konfigurace s nejlepším poměrem průměr / směrodatná odchylka ročních výnosů a zjistí se, kde skončila
ve druhé polovině. PBO je podíl rozdělení, v nichž „nejlepší v tréninku“ skončila v testu na mediánu
nebo pod ním. **Intuice:** PBO 0,5 znamená, že výběr nejlepší konfigurace nemá žádnou prediktivní
hodnotu. PBO blízko 0 znamená, že dobrá konfigurace v minulosti zůstává dobrá. Vysoké PBO u hladkého
plató (C2: 0,70) neznamená katastrofu, jen to, že mezi podobnými konfiguracemi se vybírá šum.

### PSR a deflated Sharpe (DSR)

Bailey a López de Prado (2014). **PSR** (probabilistic Sharpe ratio) je pravděpodobnost, že skutečný
Sharpe je větší než nula, s korekcí na délku vzorku, šikmost a špičatost denních výnosů. **DSR** je
totéž, ale místo nuly se srovnává s hodnotou SR0, kterou by čekal nejlepší z N nezávislých bezcenných
pokusů:

```
SR0 = odmocnina(V) × ((1 − γ) × Φ⁻¹(1 − 1/N) + γ × Φ⁻¹(1 − 1/(N·e))),  γ = 0,5772
DSR = Φ( (SR − SR0) × odmocnina(T − 1) / odmocnina(1 − γ3·SR + (γ4 − 1)/4 · SR²) )
```

SR je denní (neanualizovaný) Sharpe, T počet denních pozorování (DEV+OOS: 3 605), γ3 šikmost, γ4
špičatost, V rozptyl Sharpe mezi pokusy a Φ distribuční funkce normálního rozdělení. Výzkum počítá dvě
varianty: **konzervativní** (N = 60 zvažovaných konfigurací, V z rozptylu Sharpe deseti kandidátů DEV
screeningu, SR0 = 1,465 anualizovaně) a **mírnější** (N = 125 bodů mřížky, V z rozptylu uvnitř mřížky,
SR0 0,20–0,32). Cíl je DSR ≥ 0,95. **Intuice:** čím víc věcí jste zkusili, tím vyšší Sharpe musí mít vítěz,
aby nebyl jen nejšťastnější z mnoha. Hodnoty pro jednotlivé strategie jsou v kapitole 14.

## 0.9 Slovník: režimy a brány

### Režimy (ex-ante)

Každý obchod dostane štítek podle dne vstupu. Štítky se počítají jen z informací známých do
předchozího dne (`research/stats.py::regime_frame`):

| Režim | Definice | Zdroj dat |
|---|---|---|
| trending / ranging | abs(log výnos za 60 dní) / (σ denních výnosů za 60 dní × √60) > 1 → trending | D1 mid close XAUUSD |
| high / low vol | σ za 20 dní > medián σ20 za posledních 252 dní → high vol | D1 mid close XAUUSD |
| strong / weak USD | 60denní log změna USD indexu > 0 → strong USD | USD index (DXY váhy, Fed H.10) |
| rising / falling yields | 60denní změna výnosu 10Y > 0 → rising | US Treasury 10Y |
| crisis / normal | VIX > 25 → crisis | CBOE VIX |

Jak číst tabulku: štítky XAUUSD jsou posunuté o jeden den, makro data o jeden kalendářní den
a doplněná poslední známou hodnotou. Co z toho plyne: režim nikdy nepoužívá budoucí informaci, takže
by šel v praxi použít i jako filtr. Výsledky v kapitole 10 ale ukazují, že by to nepomohlo.

### Brány přijetí

Strategie je **robustní kandidát** jen při splnění všech sedmi bran (osmá je jen reportovací):
(1) DEV expectancy > 0 a PF > 1,10; (2) OOS expectancy > 0, PF > 1,05, Sharpe > 0,3; (3) při nákladech
×1,5 expectancy DEV+OOS > 0; (4) ≥ 70 % kombinací perturbační mřížky s kladnou expectancy;
(5) kladný spojený walk-forward výsledek; (6) žádný kalendářní rok nepřinese > 50 % čistého zisku;
(7) trade bootstrap P(expectancy > 0) ≥ 90 %; (8) holdout se jen reportuje. Proč která brána existuje,
vysvětluje kapitola 4.3.

## 0.10 Čas: serverový čas a zarovnání svíček

**Serverový čas = čas New Yorku + 7 hodin.** Tuto konvenci používá většina MT4/MT5 brokerů (GMT+2
v zimě, GMT+3 v létě). Server se přepíná na letní čas spolu s New Yorkem, proto platí:

- serverová půlnoc = **17:00 New York** = denní rollover spotového zlata, kdy se účtuje swap,
- **D1 svíčka** = jeden obchodní den 17:00–17:00 New York. Týden má přesně 5 denních svíček
  (nedělní večerní otevření patří do pondělní svíčky),
- **H4 svíčky** začínají v 00, 04, 08, 12, 16 a 20 serverového času, tedy 17, 21, 01, 05, 09 a 13 hodin
  newyorského času. První H4 svíčka dne má jen 3 obchodní hodiny, protože 00–01 server (17–18 NY) je
  denní přestávka trhu,
- všechny svíčky jsou indexované **časem otevření**. Bar „2019-03-01 08:00“ pokrývá 08:00–12:00 serveru
  a jeho close je známý ve 12:00.

```
New York   17:00 | 18:00   ... 21:00 ... 01:00 ... 05:00 ... 09:00 ... 13:00 ... 17:00
Server     00:00 | 01:00   ... 04:00 ... 08:00 ... 12:00 ... 16:00 ... 20:00 ... 24:00
           přestávka|  H4 #1 (3 h)|  H4 #2  |  H4 #3  |  H4 #4  |  H4 #5  |  H4 #6  |
```

Proč na tom záleží: (a) D1 indikátory počítané z „kalendářních“ dnů UTC by měly 6 svíček týdně
včetně nedělního pahýlu a jiné hodnoty než u brokera, (b) session strategie (C8, C8b) pracují s přesnými
hodinami, (c) swap se účtuje v serverovou půlnoc. Převody zajišťují `tradingsystem/data/instrument.py`
(`utc_to_server`, `server_to_utc`) a ověřuje je test `test_server_time_roundtrip_and_daily_bar_alignment`.

## 0.11 ID kandidátů

| ID | Název v kódu | Rodina | TF | Ø držení DEV | Výsledek |
|---|---|---|---|---|---|
| C1 | tsmom_d1 | time-series momentum (60denní výnos) | D1 | 693 h | zamítnuta na DEV, mimo mandát držení |
| C2 | donchian_h4 | price-channel breakout 55/20 (Turtle) | H4 | 152 h | **#2 finálního pořadí** |
| C3 | ema_trend_h4 | MA trend EMA 20/100 s trailing stopem | H4 | 133 h | **#1 finálního pořadí** |
| C4 | volbreak_d1 | volatility / range-expansion breakout (OCO) | D1 | 48,6 h | zamítnuta na DEV |
| C5 | squeeze_h4 | momentum po konsolidaci (Bollinger squeeze) | H4 | 81,8 h | **#3 finálního pořadí** |
| C6 | rsi2_pullback_d1 | podmíněná mean reversion (RSI(2), SMA200) | D1 | 113,8 h | zamítnuta na DEV (záporná už hrubě) |
| C7 | zscore_mr_h1 | volatilitou podmíněná mean reversion (z-score) | H1 | 19,1 h | zamítnuta na DEV |
| C8 | session_drift_h1 | čas v dni (overnight long, US day short) | H1 | 9,6 h | zamítnuta na DEV (hrubě nula) |
| C8b | session_asia_london_h1 | revize C8: Asie long 02→09, Londýn short 09→15 | H1 | 6,5 h | zamítnuta po validaci (jen před náklady) |
| C9 | donchian_usd_h4 | C2 + filtr USD indexu (50denní průměr) | H4 | 155,6 h | vyřazena (korelace 0,79 s C2, OOS ≈ 0) |
| C10 | — | kalendářní sezónnost (long září + listopad) | měsíc | — | netestována (2 obchody ročně) |
| C11 | — | ML klasifikátor směru | — | — | vyloučena mandátem (chybí robustní baseline) |

Jak číst tabulku: průměrná doba držení je z DEV screeningu 2010–2018 (`s01_dev_screen.json`) a ukazuje,
zda strategie splňuje mandát 4 h – 10 obchodních dní. Co z toho plyne: všechny tři finální strategie
(C3, C2, C5) jsou trend/momentum na H4 s držením 3–7 dní. C8b je pod dolní hranicí mandátu, protože
drží zhruba 6,5 hodiny.

## 0.12 Reálný příklad jednoho obchodu z backtestu

Aby bylo jasné, co přesně simulátor dělá, je zde rozebrán první obchod strategie C3 z běhu
`run([registry.make('C3')], '2019-01-01', '2019-04-01', source='A')` (dopočet pro tento dokument, data A
s reálným bid/ask, baseline náklady, účet 100 000 USD, riziko 0,5 %).

**Signál.** H4 bar 2019-03-01 08:00 (08:00–12:00 serveru, 01:00–05:00 NY) se uzavřel na mid ceně
1 308,024. EMA20 = 1 319,830 klesla pod EMA100 = 1 320,108, zatímco na předchozím baru byla nad ní
(1 321,073 > 1 320,352). Vznikl tedy čerstvý cross dolů a signál **short**. ATR20 = 4,352, takže počáteční
stop = 1 308,024 + 3 × 4,352 = **1 321,08**.

| Položka | Hodnota | Jak vznikla |
|---|---|---|
| Směr / objem | short 0,37 lotu | riziko 500 USD / (vzdálenost stopu ≈ 13,20 USD × 100 oz) = 0,379 → zaokrouhleno dolů na 0,37 |
| Kotace při sizingu | bid 1 307,885 / ask 1 308,162 | close posledního H1 baru (11:00) v okamžiku signálu; short počítá vzdálenost od bid |
| Riziko obchodu | 488,22 USD | 0,37 × 100 × (1 321,08 − 1 307,885); kvůli zaokrouhlení dolů je menší než 500 USD |
| Vstup | 2019-03-01 12:00, cena 1 307,836 | open dalšího H1 baru: bid 1 307,875 (spread 0,287 USD = 2,19 bp, pod limitem 4 bp) − skluz 0,3 bp (0,039 USD) |
| Trailing stop | posouván na min. close 20 barů + 3 × ATR20 | jen zpřísňování; poslední posun po H4 baru 2019-03-08 00:00 na 1 294,70 |
| Výstup | 2019-03-08 09:00, cena 1 294,829, důvod stop_loss | ask high H1 baru 09:00 = 1 294,832 ≥ stop 1 294,70; výplň = stop + skluz stop příkazu 1 bp (0,129 USD) |
| Držení | 29 H4 barů (přes víkend) | pátek 12:00 → další pátek 09:00 |
| Hrubý PnL (mid → mid) | +499,20 USD | (1 308,019 − 1 294,527) × 0,37 × 100; výstupní mid = stop − polovina spreadu |
| Spread | −11,73 USD | polovina spreadu při vstupu (0,1435 × 37) + při výstupu (0,1735 × 37) |
| Skluz | −6,24 USD | vstup 0,039 × 37 + výstup 0,129 × 37 |
| Komise | 0,00 USD | spread-only účet |
| Swap | +1,92 USD | short dostává (r − 2,25 %) p.a.; r = 3M T-bill ≈ 2,44–2,47 %; 7 nocí (Pá, Po, Út, St × 3, Čt) |
| Čistý PnL | +483,15 USD | 499,20 − 11,73 − 6,24 + 0 + 1,92 |
| R | **+0,99 R** | 483,15 / 488,22 |
| MAE / MFE | 4,43 / 27,06 USD za unci | největší nepříznivý a příznivý pohyb během držení |

Jak číst tabulku: sloupec „Jak vznikla“ ukazuje, že každé číslo je dohledatelné z barů a nákladového
modelu (kontrolní součet gross − spread − skluz − komise + swap = net platí přesně, což ověřuje
`test_frictionless_gross_equals_net_and_costs_add_up`). Co z toho plyne:

- **Signál se počítá z mid cen, exekuce probíhá na bid/ask.** Mezi signálem a vstupem nevzniká
  look-ahead: rozhoduje close baru a vyplní se až open dalšího baru.
- **Trendový obchod vrací hodně zisku zpět.** Cena se v příznivém směru pohnula až o 27,06 USD, ale
  obchod zachytil 13,0 USD, protože trailing stop 3 × ATR je široký. To je cena za to, že stop nevyhodí
  pozici při běžném šumu.
- **Swap je u shortu při nízkých sazbách zanedbatelný, u longu ne.** Druhý obchod téže strategie
  (long 0,42 lotu, 2019-03-19 16:00 → 2019-03-21 19:00, 4 noci včetně trojitého středečního swapu)
  zaplatil na swapu −28,78 USD, tedy −0,06 R za dva dny. Jen tento swap se rovná celé průměrné expectancy
  C3 (+0,061 R na obchod). Celý ten obchod skončil hrubě −142,59 USD, čistě −190,68 USD (−0,39 R) [E].

*Zdrojové soubory: `REPORT.md` (struktura a značení), `research/PROTOCOL.md`, `research/DEV_SELECTION.md`,
`research/results/s01_dev_screen.json`, `research/results/s02_C3.json`, `research/results/dsr_within_grid.json`,
`research/stats.py`, `research/s02_validate.py`, `research/registry.py`, `research/common.py`,
`tradingsystem/backtest/metrics.py`, `tradingsystem/brokers/simulated.py`, `tradingsystem/costs/model.py`,
`tradingsystem/risk/manager.py`, `tradingsystem/data/instrument.py`, `tradingsystem/data/bars.py`,
`tradingsystem/strategies/trend.py`, `tests/test_core.py`; dopočet příkladu obchodu z `data/processed/A_H1.parquet`
a `A_H4.parquet` přes `research/common.py::run`.*
