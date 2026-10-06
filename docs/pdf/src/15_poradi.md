# 15. Které strategie jsou nejlepší a proč – finální pořadí a odůvodnění

## 15.1 Co znamená „nejlepší“

Zadání rozlišuje **nejlepší historický výsledek** a **nejlepšího kandidáta pro budoucí live
robustnost**. Hlavním cílem je to druhé. Pořadí proto neurčuje nejvyšší zisk v backtestu, ale tato
kritéria v pořadí důležitosti:

1. **Konzistence napříč nezávislými obdobími**: kladná čistá expectancy v DEV, OOS i mimo vývoj (PRE).
2. **Odolnost vůči volbě parametrů**: plató v perturbační mřížce, nízké PBO, literaturní defaulty.
3. **Odolnost vůči nákladům a exekuci**: ×1,5 a ×2 náklady, zpoždění vstupu, skluz.
4. **Ekonomické zdůvodnění a literatura**.
5. **Jednoduchost a přenositelnost** (počet parametrů, datové nároky, broker).
6. Teprve potom **velikost historického výsledku** (expectancy, Sharpe).

Pořadí bylo stanoveno a zmrazeno (`research/frozen_spec.json`, commit `cfe78c3`) **před** holdoutem.
Holdout ho nezměnil.

## 15.2 Trychtýř výběru: kde kdo vypadl

| Kandidát | Fáze vyřazení | Důvod (čísla) |
|---|---|---|
| C10 Podzimní sezónnost | scorecard | ~2 obchody ročně, za 16 let nelze statisticky testovat; držení měsíc (mimo mandát) |
| C11 ML klasifikátor | scorecard | mandát: ML jen nad robustní baseline, žádná neexistuje |
| C1 TSMOM D1 | DEV | exp. −0,002 R, PF 0,98; držení týdny až měsíce (mimo mandát) |
| C4 Volatility breakout D1 | DEV | exp. −0,036 R, PF 0,89; hrubě jen +0,010 R |
| C6 RSI(2) pullback D1 | DEV | exp. −0,018 R, PF 0,88; **záporná už před náklady** (−0,004 R) |
| C7 Z-score MR H1 | DEV | exp. −0,117 R, t −4,35; hrubě −0,067 R |
| C8 Session drift H1 | DEV | exp. −0,018 R, PF 0,89; hrubě +0,001 R (nulový efekt) |
| C8b Asie long / Londýn short | validace | DEV PF 1,02 (brána 1 NE); OOS −0,017 R, holdout −0,015 R; 0 % kladných variant mřížky |
| C9 Donchian + USD filtr | výběr po validaci | korelace s C2 0,79; OOS −0,013 R; WF −0,2 %; potřebuje živý USD index |
| **C5 Squeeze H4** | **#3** | kladná v PRE, DEV, HOLDOUT; OOS −0,092 R |
| **C2 Donchian H4** | **#2** | kladná ve všech 4 segmentech |
| **C3 EMA trend H4** | **#1** | kladná ve všech 4 segmentech, nejvyrovnanější profil |

## 15.3 Předregistrované brány (DEV+OOS) a holdout

| Brána | C3 | C2 | C5 | C9 | C8b |
|---|---|---|---|---|---|
| 1 DEV: exp > 0 a PF > 1,10 | ANO (1,22) | NE (1,094) | ANO (1,24) | ANO (1,31) | NE (1,02) |
| 2 OOS: exp > 0, PF > 1,05, Sharpe > 0,3 | NE (Sharpe 0,16) | NE (Sharpe 0,26) | NE (exp −0,092) | NE (exp −0,013) | NE |
| 3 Náklady ×1,5: exp > 0 | ANO (0,041) | ANO (0,047) | ANO (0,013) | ANO (0,083) | NE (−0,014) |
| 4 Kladní sousedé ≥ 70 % | ANO (90 %) | ANO (96 %) | ANO (100 %) | ANO (100 %) | NE (0 %) |
| 5 Walk-forward > 0 | ANO (+7,4 %) | ANO (+5,4 %) | ANO (+30,9 %) | NE (−0,2 %) | N/A |
| 6 Žádný rok > 50 % zisku | NE (70 %) | NE (68 %) | NE (74 %) | NE (70 %) | NE |
| 7 Bootstrap P(exp > 0) ≥ 90 % | NE (82 %) | NE (78 %) | NE (73 %) | NE (78 %) | NE (10 %) |
| **Všechny brány** | **NE** | **NE** | **NE** | **NE** | **NE** |
| Holdout 2024–26, exp. R | +0,106 | +0,197 | +0,162 | +0,180 | −0,015 |

> **Žádná strategie nesplnila všechny brány.** Pořadí níže tedy řadí kandidáty pro *další zkoumání*,
> ne strategie připravené k obchodování.

## 15.4 #1 – C3 EMA trend H4

- **Jádro edge:** střednědobá persistence trendu zlata (dny), zachycená křížením EMA(20) a EMA(100)
  na H4 svíčkách s trailing stopem.
- **Proč může existovat:** pomalá difúze makro informací (sazby, USD, poptávka centrálních bank),
  hedging pressure, stádní chování a zpětná vazba trendových fondů [R]. Široká literatura
  o time-series momentum (Moskowitz–Ooi–Pedersen 2012, Hurst–Ooi–Pedersen 2017) [E]. Pro krátké
  horizonty po roce 2009 ale existuje negativní evidence (Kurth et al. 2026) [E, preprint].
- **Přesná pravidla:** long při křížení EMA20 nad EMA100, short opačně. Počáteční stop 3 × ATR(20)
  od close, trailing stop 3 × ATR od 20barového extrému close (jen zpřísňuje). Výstup opačným
  křížením nebo stopem. Jedna pozice, žádné pyramidování.
- **Nejlepší timeframe:** H4. Kladná i na H2, H3, H6 a D1; H4 měla nejvyšší expectancy.
- **Držení:** průměr 128 h (~5 dní), 18 obchodů ročně.
- **Long/short:** symetrická pravidla. V DEV a OOS vydělávala short strana (+0,131 / +0,070 R)
  a long byla ≈ 0. V holdoutu to bylo naopak (long +0,380 R, short −0,136 R). Asymetrie je režimová.
- **Režim selhání:** krize (VIX > 25: −0,158 R), vysoká volatilita (−0,114 R), rok 2020 (−0,297 R).
- **Citlivost na náklady:** nízká až střední. Náklady berou ~45 % hrubého zisku; kladná i při 2×
  nákladech (+0,021 R), jako jediná z trojice.
- **Silné stránky:** nejnižší max DD (7,4 % při 0,5 % riziku), PBO 0,47 (nejnižší z C2/C3/C9),
  nejvyšší t v DEV+OOS (0,93), kladný walk-forward, bootstrap P(exp > 0) 82 % (nejvyšší z kandidátů).
- **Slabé stránky:** nejmenší expectancy (0,061 R DEV+OOS), OOS Sharpe jen 0,16, zisk koncentrovaný
  do roku 2023 (70 %).
- **Co by kandidáta vyvrátilo:** záporná expectancy na datech vlastního brokera, realizované náklady
  > 1,5× model, nebo série ztrát nad bootstrap p95 (17 obchodů) během paper/demo fáze.
- **Skóre:** robustnost 45/100 · implementační složitost 15/100 · kvalita důkazů 50/100 ·
  riziko přeučení 35/100 · **důvěra NÍZKÁ**.

## 15.5 #2 – C2 Donchian channel breakout H4

- **Jádro edge:** pokračování pohybu po proražení ~9,5denního maxima/minima (Turtle logika 55/20).
- **Proč může existovat:** stejné důvody jako u C3, navíc koncentrace stop příkazů a breakout
  obchodníků za hranicemi kanálu [R/I].
- **Přesná pravidla:** long při close nad maximem předchozích 55 H4 barů, short při close pod
  minimem. Stop 2 × ATR(20). Trailing na 20barový opačný kanál, výstup close přes něj.
  Time-stop 90 barů (15 dní).
- **Nejlepší timeframe:** H4 (H2 a H6 podobné, D1 slabší).
- **Držení:** průměr 149 h (~6 dní), 27 obchodů ročně.
- **Long/short:** za 22 let výrazně silnější long (+0,384 R) než short (−0,147 R). V holdoutu short
  −0,696 R (úspěšnost 9,7 %).
- **Režim selhání:** krize (−0,311 R), trh bez trendu (−0,039 R), vysoká volatilita (−0,088 R).
- **Citlivost na náklady:** střední. Při 2× nákladech je na nule (+0,007 R).
- **Silné stránky:** **nejlepší historický výsledek**: pooled 2004–2026 exp. 0,149 R, t 1,71,
  Sharpe 0,40; holdout 0,197 R. Předregistrovaná volba, takže ji netýká selekce po DEV.
  96 % kladných sousedů.
- **Slabé stránky:** v DEV těsně neprošla bránou PF (1,094), PBO 0,70, max DD 13,4 %, zisk
  koncentrovaný do roku 2020 (68 %), výrazně závislá na long straně, tedy na býčím trhu.
- **Skóre:** robustnost 45/100 · složitost 15/100 · kvalita důkazů 55/100 · riziko přeučení 35/100 ·
  **důvěra NÍZKÁ**.

## 15.6 #3 – C5 Squeeze breakout H4

- **Jádro edge:** po období nízké volatility přichází expanze; vstup ve směru proražení Bollingerova pásma.
- **Proč může existovat:** shlukování volatility je robustní fakt [E]. Že má expanze předvídatelný
  směr, je slabě podložené [I/U].
- **Přesná pravidla:** squeeze = šířka pásma v dolních 20 % za 120 barů kdykoli v posledních 5 barech.
  Vstup při close mimo Bollinger(20, 2). Stop 2 × ATR(20). Výstup při close přes SMA20 nebo po 30 barech.
- **Držení:** průměr 78 h (~3 dny), 36 obchodů ročně.
- **Silné stránky:** 100 % kladných sousedů, nejnižší PBO (0,24), pooled t 1,46, nejvíc obchodů.
- **Slabé stránky:** OOS 2019–2023 záporné (−0,092 R) a celé období 2018–2023 ztrátové; 8 parametrů;
  při 2× nákladech záporná; holdout nad bootstrap pásmem, což ukazuje na režimovou závislost.
- **Skóre:** robustnost 30/100 · složitost 25/100 · kvalita důkazů 35/100 · riziko přeučení 50/100 ·
  **důvěra NÍZKÁ**.

## 15.7 Přímé srovnání C3 vs. C2

| Kritérium | C3 EMA trend | C2 Donchian | Lepší |
|---|---|---|---|
| Exp. R PRE / DEV / OOS / HOLDOUT | 0,064 / 0,074 / 0,038 / 0,106 | 0,316 / 0,064 / 0,094 / 0,197 | C2 (velikost), obě kladné |
| Pooled exp. R, t (2004–2026) | 0,067; 1,25 | 0,149; 1,71 | C2 |
| Sharpe DEV+OOS | 0,25 | 0,22 | C3 |
| Max DD DEV+OOS (0,5 % riziko) | 7,4 % | 13,4 % | C3 |
| DEV brána 1 (PF > 1,10) | ANO | NE | C3 |
| PBO | 0,47 | 0,70 | C3 |
| Kladní sousedé | 90 % | 96 % | C2 |
| Exp. R při 2× nákladech | +0,021 | +0,007 | C3 |
| Walk-forward | +7,4 % | +5,4 % | C3 |
| Bootstrap P(exp > 0) | 82 % | 78 % | C3 |
| Závislost na long straně (2004–2026) | long 0,101 / short 0,035 | long 0,384 / short −0,147 | C3 (vyrovnanější) |
| Předregistrovaná volba | ne (náhrada po DEV) | ano | C2 |

**Proč je C3 #1, i když C2 má lepší historický výsledek:** C3 vyhrává ve většině kritérií robustnosti
(drawdown, náklady, PBO, bootstrap, DEV brána, vyrovnanost směrů). C2 vyhrává ve velikosti výsledku,
ten je ale tažen pre-sample 2004–2009 a holdoutem (oba býčí trhy) a silně závislý na long straně.
Pro budoucí robustnost je vyrovnanější profil cennější než vyšší historický zisk. **Rozdíl mezi
nimi je ale v rámci statistického šumu.**

## 15.8 Proč C5, a ne C9, na třetím místě

- C9 je s C2 korelovaná 0,79 a v drtivé většině času drží stejnou pozici. Jako třetí člen
  by nepřinesla téměř žádnou diverzifikaci. C5 má s C2 korelaci 0,43 a s C3 0,34.
- C9 potřebuje živý USD index (výpočet z FX párů u brokera), což je datová závislost navíc.
- C9 měla walk-forward −0,2 % a OOS −0,013 R. C5 měla walk-forward +30,9 %, i když OOS −0,092 R.
- C9 je v mřížce bod po bodu lepší než C2. Filtr tedy něco přidává, ale za cenu poloviční
  frekvence obchodů a závislosti na stabilitě vztahu zlato–USD, který se po roce 2022 změnil.
  Je to vhodný kandidát pro budoucí předregistrovaný test, ne pro současnou trojici.

## 15.9 Citlivost pořadí

| Kdyby rozhodovalo… | Pořadí |
|---|---|
| Pooled t-statistika 2004–2026 | C2 (1,71), C5 (1,46), C3 (1,25) |
| Holdout exp. R | C2, C9, C5, C3 |
| Sharpe DEV+OOS | C3, C9, C2, C5 |
| Max DD a náklady ×2 | C3, C2, C5 |
| Počet kladných segmentů | C3 = C2 (4), C5 = C9 (3) |

Na první dvě místa se tedy podle kritéria střídají C3 a C2, třetí místo je vždy slabší. Prakticky
z toho plyne, že **C3 a C2 je rozumné zpracovávat společně**.

## 15.10 Důsledek „jedna sázka“ a doporučená forma pro další zpracování

Všechny tři strategie sázejí na totéž (pokračování střednědobého trendu). Když jsou dvě zároveň
v pozici, jsou v 99–100 % případů ve stejném směru, korelace drawdownů je 0,67–0,70 a hluboké
drawdowny přicházejí 3,5–4× častěji společně, než by odpovídalo nezávislosti. Proto doporučujeme:

1. **Trendový ensemble C3 + C2 + C5** jako *jednu* strategii se sdíleným rizikovým rozpočtem:
   0,5 % na obchod celkem, 1/3 na každou složku (`config/paper.toml`).
2. **Symetrická pravidla**, žádné vypínání směru na základě historické asymetrie (kapitola 12.5).
3. **Literaturní parametry beze změny**. Žádná „vylepšení“ podle OOS nebo holdoutu (například kratší
   stop u C5 nebo jiný timeframe) bez nového předregistrovaného testu.
4. **Hledat druhý, nezávislý zdroj edge** (kapitola 16). Současná trojice diverzifikaci nepřináší.

> **Shrnutí:** Nejlepší kandidáti pro další zpracování jsou C3 EMA trend H4 (#1), C2 Donchian H4 (#2)
> a C5 Squeeze H4 (#3). Jsou to jediné strategie, jejichž čistá expectancy je kladná napříč nezávislými
> obdobími, parametry, timeframy a zvýšenými náklady, a mají oporu v literatuře. Efekt je ale malý,
> statisticky neprůkazný a koncentrovaný do několika let. Jde o jednu sázku na trend s nízkou důvěrou,
> vhodnou jen pro pozorovací paper fázi, ne pro reálný kapitál.

*Zdrojové soubory: research/frozen_spec.json, research/results/s01_dev_screen.json, s02_C3.json,
s02_C2.json, s02_C5.json, s02_C9.json, s02_C8b.json, s03_portfolio.json, s03_portfolio_C2_C3_C5_C9.json,
s04_holdout.json, s05_pooled.json, dsr_within_grid.json, config/paper.toml.*
