# 11. Komplementarita strategií a portfolio

Zadání požaduje tři strategie, které jsou robustní a pokud možno se navzájem doplňují. Kapitola 10
ukázala, že jedinou rodinou s konzistentně kladnou čistou expectancy je střednědobý trend na H4
(C3, C2, C5 a vyřazená C9). Tato kapitola odpovídá na navazující otázku: **jsou C3, C2 a C5 tři
různé zdroje výnosu, nebo jedna sázka ve třech převlecích?** A pokud jedna sázka, jak s ní zacházet
v řízení rizika. Všechny výsledky kromě podkapitoly 11.9 (dopočet z uložené equity) a výslovně
označených kontrol na holdoutu pocházejí ze skriptu `research/s03_portfolio.py` a pokrývají období
**DEV+OOS 2010-01 – 2023-12**. Holdout 2024–2026 se v analýze komplementarity nepoužil a rozhodnutí
o vahách portfolia (1/3) padlo před jeho spuštěním (kapitola 12).

## 11.1 Postup a definice ukazatelů

Skript `s03_portfolio.py` běžel dvakrát: jednou pro finální trojici C3, C2, C5 (`s03_portfolio.json/.md`)
a jednou pro čtveřici včetně C9 (`s03_portfolio_C2_C3_C5_C9.json/.md`), aby bylo vidět, proč C9 vypadla.
Vstupem jsou samostatné běhy jednotlivých strategií za DEV+OOS (riziko 0,5 % na obchod, baseline
náklady, uložené v `research/results/cache/<K>_full.pkl`) a z nich odvozené ukazatele:

| Ukazatel | Jak se počítá | Co měří |
|---|---|---|
| Korelace denních výnosů | Pearsonova korelace denních změn equity dvou strategií (dny bez pozice = 0) | podobnost denního P&L |
| Čas v trhu | podíl hodin H1 mřížky 2010–2023, kdy má strategie otevřenou pozici | jak často je strategie aktivní |
| Současně v trhu | podíl hodin, kdy mají pozici obě strategie | skutečný překryv expozice |
| Očekáváno při nezávislosti | součin časů v trhu obou strategií | překryv, který by vznikl čistou náhodou |
| Stejný směr | podíl hodin překryvu, kdy jsou obě pozice long nebo obě short | zda jde o stejnou sázku na směr |
| Korelace drawdownů | korelace denních řad hloubky drawdownu (equity / maximum − 1) | zda se strategie propadají současně |
| Společný hluboký DD | podíl dní, kdy jsou obě strategie ve svém nejhlubším 20% pásmu drawdownu | souběh nejhorších období |
| Režimový překryv | expectancy v R podle ex-ante režimu ke dni vstupu (kapitola 4.8) | zda strategie ztrácejí ve stejném prostředí |

Jak číst tabulku: první pět řádků měří překryv v čase a směru, další dva souběh ztrát, poslední
souběh prostředí, ve kterém se nedaří. Co z toho plyne: komplementarita se nedá posoudit jen korelací
denních výnosů. Dvě strategie mohou mít nízkou denní korelaci (protože jsou v trhu v jiné dny) a přesto
sázet na totéž a ztrácet ve stejných obdobích. Proto se měří i směr, drawdowny a režimy.

Hranice „hlubokého drawdownu“ je 20. percentil denní hloubky drawdownu každé strategie. Pokud by
strategie byly nezávislé, byly by obě současně v hlubokém drawdownu v 0,2 × 0,2 = 4 % dní [E, definice
v kódu].

## 11.2 Korelace denních výnosů

| | C3 | C2 | C5 | C9 |
|---|---|---|---|---|
| C3 | 1,00 | 0,45 | 0,34 | 0,32 |
| C2 | 0,45 | 1,00 | 0,43 | 0,79 |
| C5 | 0,34 | 0,43 | 1,00 | 0,33 |
| C9 | 0,32 | 0,79 | 0,33 | 1,00 |

Jak číst tabulku: korelace denních výnosů equity, DEV+OOS 2010–2023, 3 605 obchodních dní. Matice
pro trojici C3/C2/C5 v `s03_portfolio.json` je s touto shodná. Co z toho plyne: korelace uvnitř finální
trojice je **středně vysoká (0,34–0,45)**, nikoli blízká nule, jak by to bylo u nezávislých zdrojů
výnosu. Pár C2/C9 má korelaci **0,79**, protože C9 je C2 s filtrem USD indexu: filtr jen vynechá část
obchodů, zbytek je identický [E]. To je hlavní kvantitativní důvod, proč C9 nepřináší nic nového.

Pro posouzení stability jsem korelaci dopočítal po tříletých blocích a na holdoutu [E, vlastní dopočet
z `cache/<K>_full.pkl` a `cache/<K>_holdout.pkl`, stejná metoda jako ve skriptu]:

| Období | C3 / C2 | C3 / C5 | C2 / C5 | C2 / C9 |
|---|---|---|---|---|
| 2010–2012 | 0,42 | 0,32 | 0,39 | 0,80 |
| 2013–2015 | 0,44 | 0,37 | 0,46 | 0,86 |
| 2016–2018 | 0,49 | 0,43 | 0,45 | 0,78 |
| 2019–2021 | 0,34 | 0,27 | 0,32 | 0,79 |
| 2022–2023 | 0,59 | 0,29 | 0,52 | 0,70 |
| Holdout 2024–2026 | 0,45 | 0,43 | 0,49 | 0,75 |

Jak číst tabulku: stejná korelace denních výnosů, ale počítaná zvlášť v každém bloku. Holdout je
z jednorázového holdoutového běhu (kapitola 12), dopočet nemění žádné rozhodnutí. Co z toho plyne:
korelace v čase kolísá v pásmu zhruba 0,3–0,6, ale **nikdy neklesla k nule** a v holdoutu je stejná
jako v DEV+OOS. Vztah mezi strategiemi tedy není artefakt jednoho období, ale stabilní vlastnost
rodiny [E]. Vysoká korelace C2/C9 (0,70–0,86) platí ve všech blocích.

## 11.3 Párové překryvy: čas v trhu, směr a drawdowny

| Pár | Korelace denních výnosů | Čas v trhu a | Čas v trhu b | Současně v trhu | Očekáváno při nezávislosti | Poměr | Stejný směr (z překryvu) |
|---|---|---|---|---|---|---|---|
| C2 / C3 | 0,45 | 45,2 % | 27,1 % | 18,2 % | 12,2 % | 1,48 | 100,0 % |
| C2 / C5 | 0,43 | 45,2 % | 32,5 % | 18,8 % | 14,7 % | 1,28 | 98,9 % |
| C3 / C5 | 0,34 | 27,1 % | 32,5 % | 11,3 % | 8,8 % | 1,28 | 98,7 % |
| C2 / C9 | 0,79 | 45,2 % | 27,5 % | 27,3 % | 12,4 % | 2,19 | 100,0 % |
| C3 / C9 | 0,32 | 27,1 % | 27,5 % | 9,7 % | 7,5 % | 1,31 | 100,0 % |
| C5 / C9 | 0,33 | 32,5 % | 27,5 % | 11,7 % | 8,9 % | 1,31 | 98,7 % |

Jak číst tabulku: „a“ a „b“ jsou první a druhá strategie páru. „Současně v trhu“ je podíl všech hodin
2010–2023, kdy mají obě strategie otevřenou pozici. „Poměr“ je můj dopočet: skutečný překryv / překryv
při nezávislosti. „Stejný směr“ je podíl hodin překryvu, kdy jsou obě pozice na stejné straně. Co
z toho plyne:

- **Strategie jsou v trhu častěji současně, než by odpovídalo náhodě** (1,28–1,48× u finální trojice,
  2,19× u C2/C9). Signály tedy nevznikají nezávisle, reagují na tytéž pohyby zlata [E].
- **Když jsou dvě strategie zároveň v trhu, jsou prakticky vždy ve stejném směru** (98,7–100 %).
  Opačné pozice se vyskytly jen u párů s C5 a jen v 1,1–1,3 % hodin překryvu, typicky když C5 už
  otočila směr po rychlém proražení a pomalejší strategie ještě držela starou pozici [I]. Kombinace
  tedy **nikdy nesází proti sobě** a při současné expozici sčítá riziko na jeden směr.
- Nízká denní korelace (0,34 u C3/C5) neznamená odlišnou sázku: plyne hlavně z toho, že C3 je v trhu
  jen 27 % a C5 33 % času, takže většinu dní má jedna z nich nulový P&L. Když jsou v trhu obě, sázejí
  na totéž.

| Pár | Korelace drawdownů | Společný hluboký DD | Očekáváno při nezávislosti | Násobek | Podíl hlubokých DD dní a, kdy je v hlubokém DD i b |
|---|---|---|---|---|---|
| C2 / C3 | 0,70 | 14,1 % | 4,0 % | 3,5 | 70 % |
| C2 / C5 | 0,67 | 14,8 % | 4,0 % | 3,7 | 74 % |
| C3 / C5 | 0,68 | 16,1 % | 4,0 % | 4,0 | 80 % |
| C2 / C9 | 0,86 | 15,8 % | 4,0 % | 4,0 | 79 % |
| C3 / C9 | 0,70 | 15,6 % | 4,0 % | 3,9 | 78 % |
| C5 / C9 | 0,87 | 16,8 % | 4,0 % | 4,2 | 84 % |

Jak číst tabulku: „Společný hluboký DD“ je podíl dní, kdy jsou obě strategie současně ve svém
nejhorším 20% pásmu drawdownu. „Násobek“ a poslední sloupec jsou můj dopočet (skutečný podíl / 4 %,
resp. skutečný podíl / 20 %). Co z toho plyne: **korelace drawdownů (0,67–0,70 v trojici) je výrazně
vyšší než korelace denních výnosů (0,34–0,45)**. Strategie se tedy liší v tom, kdy přesně vydělávají
den po dni, ale propadají se ve stejných měsících a letech. Hluboké drawdowny přicházejí 3,5–4× častěji
společně, než by odpovídalo nezávislosti: když je jedna strategie ve svém nejhorším pásmu, druhá je
v něm také v 70–80 % takových dní [E]. Pro risk management je to podstatnější než denní korelace,
protože kapitál ničí právě souběžné hluboké propady.

**Kontrola na holdoutu** [E, vlastní dopočet z holdoutových obchodů v `cache/<K>_holdout.pkl`, hodinová
mřížka dat A 2024-01 – 2026-08]: C3 byla v trhu 21,6 % času, C2 46,0 %, C5 31,6 %, C9 25,4 %. Překryv
C2/C3 12,4 % (při nezávislosti 9,9 %), C2/C5 18,8 % (14,5 %), C3/C5 8,9 % (6,8 %), C2/C9 25,1 %
(11,7 %); ve stejném směru 99–100 % hodin překryvu. Alespoň jedna z trojice měla pozici v 65,3 %
hodin, všechny tři long současně ve 4,0 % a všechny tři short ve 2,1 % hodin. Vzorec z DEV+OOS se tedy
v holdoutu zopakoval beze změny.

## 11.4 Simultánní expozice

| Ukazatel | C3 + C2 + C5 | C3 + C2 + C5 + C9 |
|---|---|---|
| Alespoň jedna otevřená pozice | 64,9 % hodin | 65,1 % hodin |
| Všechny strategie současně long | 4,0 % hodin | 1,8 % hodin |
| Všechny strategie současně short | 4,4 % hodin | 3,0 % hodin |
| Max. počet současných pozic ve stejném směru | 3 | 4 |

Jak číst tabulku: hodnoty `net_direction` ze `s03_portfolio*.json` (hodinová mřížka 2010–2023,
samostatné běhy strategií). Co z toho plyne: v kombinaci je téměř dvě třetiny času otevřená alespoň
jedna pozice. Současné plné nasazení všech strategií je vzácné (8,4 % hodin u trojice), ale nastává
a je vždy jednosměrné. Maximální souběžné riziko na jeden směr je proto součet rizik všech členů.

Pro úplnost jsem dopočítal rozdělení počtu současně otevřených pozic trojice [E, vlastní dopočet, stejná
hodinová mřížka a pozice jako ve skriptu]:

| Počet otevřených pozic | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Podíl hodin 2010–2023 | 35,1 % | 33,6 % | 22,9 % | 8,4 % |

Jak číst tabulku: podíl hodin, kdy je otevřeno 0, 1, 2 nebo 3 pozic C3, C2, C5 současně. Co z toho plyne:
dvě a více pozic současně je otevřeno v 31,4 % hodin a v 98,9 % z nich jsou všechny ve stejném směru.
Čistá směrová expozice rodiny je tedy v praxi „žádná / jedna / dvě / tři jednotky rizika na stejnou
stranu“, nikdy vzájemné zajištění. To je přímý argument pro to, aby limit rizika platil pro rodinu jako
celek (podkapitola 11.10).

## 11.5 Režimový překryv

| Dimenze | Stav | C3 | C2 | C5 | C9 | Průměr C3/C2/C5 | Záporných z C3/C2/C5 |
|---|---|---|---|---|---|---|---|
| Krize (VIX) | krize (VIX > 25) | −0,158 | −0,311 | −0,229 | −0,234 | −0,233 | 3 |
| Krize (VIX) | normál | 0,095 | 0,147 | 0,077 | 0,178 | 0,106 | 0 |
| Výnosy 10Y (60 d) | klesající | 0,069 | −0,006 | 0,105 | −0,029 | 0,056 | 1 |
| Výnosy 10Y (60 d) | rostoucí | 0,054 | 0,171 | −0,028 | 0,281 | 0,066 | 1 |
| Trend (60 d) | bez trendu (range) | 0,079 | −0,039 | 0,024 | 0,016 | 0,021 | 1 |
| Trend (60 d) | trend | −0,007 | 0,423 | 0,075 | 0,392 | 0,164 | 1 |
| USD (60 d) | silný USD | 0,118 | 0,080 | 0,066 | 0,051 | 0,088 | 0 |
| USD (60 d) | slabý USD | −0,014 | 0,083 | 0,008 | 0,195 | 0,026 | 1 |
| Volatilita (σ20) | vysoká | −0,114 | −0,088 | −0,148 | −0,229 | −0,117 | 3 |
| Volatilita (σ20) | nízká | 0,228 | 0,185 | 0,175 | 0,322 | 0,196 | 0 |

Jak číst tabulku: expectancy v R obchodů vstupujících v daném režimu, DEV+OOS, baseline náklady
(`regime_exp_r` ze `s03_portfolio_C2_C3_C5_C9.json`; trojice v `s03_portfolio.json` má shodná čísla).
Režimy jsou ex-ante štítky ke dni vstupu s daty do předchozího dne (definice v kapitole 0.9).
Poslední dva sloupce jsou můj dopočet: prostý průměr tří expectancy a počet záporných hodnot. Co z toho
plyne:

- **Společné režimy selhání:** krize (VIX > 25) a vysoká volatilita jsou záporné pro všechny čtyři
  strategie. Jinými slovy, když jedna trendová strategie ztrácí kvůli prostředí, ztrácejí i ostatní.
  To je opak toho, co by portfolio potřebovalo [E].
- **Společné příznivé režimy:** normální trh (VIX ≤ 25) a nízká volatilita jsou kladné pro všechny.
- **Jediná režimová odlišnost** je v dimenzi trend / range: C2 (a C9) vydělávají hlavně v silném
  trendu (+0,423 R), zatímco C3 je v trendovém režimu kolem nuly a vydělává spíš v režimu „range“.
  Je to logické [I]: C3 vstupuje křížením EMA pozdě a dlouhý trend už má za sebou, kdežto Donchian
  proráží 55barové maximum hned na začátku silného pohybu. Toto je jediný zárodek skutečné
  komplementarity, ale stojí na 53 obchodech C3 v trendovém režimu, takže jde o slabý důkaz.
- Dimenze USD a sazby nedávají konzistentní obraz (znaménka se mezi strategiemi liší a rozdíly jsou
  malé vůči šumu), proto z nich nelze odvodit makro filtr ani váhy podle režimu.

Počty obchodů za jednotlivé režimy [E, `regimes` v `s02_<K>.json`]:

| Dimenze | Stav | C3 | C2 | C5 | C9 |
|---|---|---|---|---|---|
| Krize (VIX) | krize (VIX > 25) | 34 | 54 | 64 | 34 |
| Krize (VIX) | normál | 222 | 319 | 446 | 194 |
| Trend (60 d) | trend | 53 | 97 | 140 | 61 |
| Trend (60 d) | bez trendu (range) | 203 | 276 | 370 | 167 |
| Volatilita (σ20) | vysoká | 125 | 142 | 216 | 85 |
| Volatilita (σ20) | nízká | 131 | 231 | 294 | 143 |
| USD (60 d) | silný USD | 146 | 228 | 269 | 124 |
| USD (60 d) | slabý USD | 110 | 145 | 241 | 104 |
| Výnosy 10Y (60 d) | rostoucí | 138 | 183 | 255 | 107 |
| Výnosy 10Y (60 d) | klesající | 118 | 190 | 255 | 121 |

Jak číst tabulku: kolik obchodů stojí za každou buňkou předchozí tabulky. Co z toho plyne: krizové
buňky mají jen 34–64 obchodů. Záporná expectancy v krizi je u všech čtyř strategií, takže jde
o konzistentní vzorec, ale přesná velikost (−0,16 až −0,31 R) je nejistá. Vysoká volatilita má
125–216 obchodů na strategii, a tedy pevnější základ. Holdout tento vzorec potvrdil: obchody vstupující
ve vysoké volatilitě byly v letech 2024–2026 záporné u C3, C2 i C5 (kapitola 12.6).

## 11.6 Tři varianty portfolia

Skript spojil strategie do jednoho běhu přes celý engine (sdílený účet 100 000 USD, společný risk
manager, stejný simulátor jako v kapitole 10) ve třech variantách:

| Varianta | Riziko na obchod | Limity risk manageru |
|---|---|---|
| A) jeden rizikový rozpočet | 0,5 % × 1/3 = 0,167 % na každou strategii | zapnuté |
| B) plné riziko pro každou | 0,5 % na každou strategii | zapnuté |
| C) bez limitů | 0,5 % na každou strategii | vypnuté (jen sizing) |

Produkční limity (`RiskConfig` v `tradingsystem/risk/manager.py`, stejné hodnoty jsou v
`research/frozen_spec.json` a `config/paper.toml`): součet otevřeného rizika ke stopům ≤ 1,5 % equity,
hrubý notional ≤ 3× equity, denní ztráta 2 % a týdenní 4 % blokují nové vstupy, strategie se vypne při
drawdownu svého P&L > 10 % equity, portfolio se při drawdownu 15 % od maxima uzavře a zastaví
(kill switch), vstup se odmítne při spreadu > 6 bp. Varianta C používá výzkumné nastavení jednotlivých
běhů (bez denních a týdenních limitů a bez kill switche).

| Varianta | Obch. | Obch./rok | Win % | Exp. R | t | PF | Sharpe | Sortino |
|---|---|---|---|---|---|---|---|---|
| A) váhy 1/3, limity zapnuté | 1 107 | 79,2 | 33,7 % | 0,052 | 1,11 | 1,10 | 0,24 | 0,39 |
| B) 0,5 % každá, limity zapnuté | 918 | 65,6 | 33,7 % | 0,059 | 1,12 | 1,10 | 0,24 | 0,40 |
| C) 0,5 % každá, bez limitů | 1 139 | 81,4 | 33,9 % | 0,057 | 1,25 | 1,10 | 0,26 | 0,43 |

| Varianta | CAGR | MaxDD | Calmar | Pod vodou (dny) | Expozice | Ø držení (h) | Max. série ztrát | Konečná equity (USD) |
|---|---|---|---|---|---|---|---|---|
| A) váhy 1/3, limity zapnuté | 0,65 % | 7,5 % | 0,087 | 2 164 | 64,0 % | 113 | 20 | 109 548 |
| B) 0,5 % každá, limity zapnuté | 1,66 % | 15,1 % | 0,110 | 2 164 | 53,1 % | 112 | 18 | 125 869 |
| C) 0,5 % každá, bez limitů | 2,01 % | 23,1 % | 0,087 | 2 164 | 65,0 % | 113 | 20 | 132 148 |

Jak číst tabulky: DEV+OOS 2010-01-04 – 2023-12-29 (13,98 roku), hodnoty z `portfolio`,
`portfolio_full_weights` a `portfolio_no_limits` v `s03_portfolio.json`. Expectancy v R je na sizingu
nezávislá, CAGR a MaxDD na něm závisí lineárně až nadlineárně. „Pod vodou“ je nejdelší doba
v kalendářních dnech bez nového maxima equity. Co z toho plyne:

- **Expectancy, PF a Sharpe jsou ve všech variantách prakticky stejné** (0,05–0,06 R, PF 1,10, Sharpe
  0,24–0,26). Kombinace tří strategií nevytvořila lepší edge než samotné strategie (C3 sama: 0,061 R,
  Sharpe 0,25). Riziková varianta mění jen měřítko výnosu a drawdownu.
- **Plné riziko pro každou strategii (B, C) vede k drawdownu 15–23 %** při CAGR jen 1,7–2,0 %. Varianta
  bez limitů ztratila od vrcholu 23,1 %, tedy zhruba jedenáct let svého průměrného ročního výnosu
  (CAGR 2,0 %). To je nepřijatelný poměr výnosu a rizika pro strategii s nízkou důvěrou.
- **Varianta A** (jeden rozpočet) má MaxDD 7,5 % a CAGR 0,65 % p. a. Calmar 0,087 je stejný jako
  u varianty C, tedy poměr výnosu a drawdownu se škálováním nezměnil.
- Všechny tři varianty mají stejnou nejdelší dobu pod vodou 2 164 dní: vrchol equity nastal ve všech
  třech **2018-01-25** a do konce roku 2023 nebyl překonán (podkapitola 11.9). Varianta A a C mají
  i stejné dno drawdownu (2023-08-07) [E, vlastní dopočet z opakovaného běhu, viz níže]. Tvar
  drawdownu je ve všech variantách týž, liší se jen hloubkou, což je další projev jedné sázky.

Rozklad P&L a nákladů:

| Varianta | Hrubý PnL | Spread | Skluz | Swap | Čistý PnL | Náklady / hrubý | Obch. long / short | Exp. R long / short | PnL long / short |
|---|---|---|---|---|---|---|---|---|---|
| A) váhy 1/3, limity zapnuté | 20 736 | 3 758 | 1 947 | −5 615 | 9 415 | 55 % | 576 / 531 | 0,044 / 0,060 | 4 260 / 5 155 |
| B) 0,5 % každá, limity zapnuté | 58 582 | 10 991 | 5 584 | −16 139 | 25 869 | 56 % | 480 / 438 | 0,039 / 0,080 | 8 624 / 17 245 |
| C) 0,5 % každá, bez limitů | 72 618 | 13 714 | 7 051 | −20 192 | 31 661 | 56 % | 586 / 553 | 0,051 / 0,065 | 15 085 / 16 576 |

Jak číst tabulku: částky v USD z `s03_portfolio.json`; „Náklady / hrubý“ je můj dopočet (spread + skluz
− swap) / hrubý PnL. Komise je ve všech variantách 0 (spread-only účet). Co z toho plyne: **náklady
berou 55–56 % hrubého zisku portfolia** a největší položkou je swap vícedenních pozic (−5 615 USD ve
variantě A, více než spread). Výsledek je tedy silně závislý na swapových podmínkách brokera
(kapitola 4.4). Long a short strana přispívají v DEV+OOS podobně; směrová asymetrie se objevuje až
v holdoutu (kapitola 12).

### Události ve variantě B: kill switch v listopadu 2021

Pro výklad variant jsem běhy zopakoval přes `research/common.py` se stejnými parametry jako skript
(výsledky jsou identické do posledního dolaru: 1 107 / 918 / 1 139 obchodů, konečná equity 109 547,52 /
125 868,89 / 132 148,32 USD) a dopočítal průběh drawdownu [E, vlastní dopočet]:

| Varianta | Vrchol equity | Dno | Hloubka | Stav na konci 2023 |
|---|---|---|---|---|
| A) váhy 1/3 | 2018-01-25: 113 545 USD | 2023-08-07: 105 011 USD | 7,5 % | 109 548 USD, 3,5 % pod vrcholem |
| B) 0,5 % každá, limity | 2018-01-25: 148 189 USD | 2021-11-04: 125 869 USD | 15,1 % | zastaveno, 125 869 USD |
| C) 0,5 % každá, bez limitů | 2018-01-25: 150 863 USD | 2023-08-07: 115 951 USD | 23,1 % | 132 148 USD, 12,4 % pod vrcholem |

Jak číst tabulku: vrchol a dno maximálního drawdownu z hodinové equity. Co z toho plyne: ve variantě B
portfolio 2021-11-04 překročilo drawdown 15 %, risk manager uzavřel všechny tři otevřené pozice
a zastavil obchodování (`halt_reason: portfolio drawdown stop at 2021-11-04 02:00:00`). Stejný den byla
C5 označena jako vypnutá strategickým stopem (`squeeze_h4: strategy drawdown 10.4%`): její P&L
drawdown dosáhl 13 319 USD právě uzavřením posledního obchodu při zastavení, ještě v říjnu 2021 byl
11 616 USD. Strategický stop C5 a portfoliový kill switch tedy nastaly fakticky současně, nikoli
postupně, což je další ilustrace toho, že ztráty jednotlivých členů rodiny přicházejí najednou.
Po zastavení zůstala equity varianty B do konce roku 2023 beze změny.

**Proč varianta B vypadá na papíře lépe než C (Calmar 0,110 vs. 0,087):** kill switch ji vyřadil před
ztrátovým rokem 2022, ale také před ziskovým rokem 2023. Lepší poměr je tedy dílem náhody v načasování
zastavení, ne vlastností strategie. Ve variantě se čtyřmi strategiemi (tabulky níže) nastal kill switch
už **2018-12-21**, takže její „nejlepší“ metriky (exp. 0,108 R, Sharpe 0,34) popisují v podstatě jen DEV
2010–2018 a nejsou s ostatními srovnatelné.

### Varianta se čtyřmi strategiemi (včetně C9)

| Varianta | Obch. | Obch./rok | Win % | Exp. R | t | PF | Sharpe | Sortino |
|---|---|---|---|---|---|---|---|---|
| A) váhy 1/4, limity zapnuté | 1 332 | 95,2 | 33,0 % | 0,061 | 1,33 | 1,12 | 0,27 | 0,44 |
| B) 0,5 % každá, limity zapnuté | 810 | 57,9 | 35,4 % | 0,108 | 1,92 | 1,19 | 0,34 | 0,58 |
| C) 0,5 % každá, bez limitů | 1 367 | 97,7 | 33,4 % | 0,067 | 1,49 | 1,10 | 0,28 | 0,46 |

| Varianta | CAGR | MaxDD | Calmar | Pod vodou (dny) | Expozice | Ø držení (h) | Max. série ztrát | Konečná equity (USD) |
|---|---|---|---|---|---|---|---|---|
| A) váhy 1/4, limity zapnuté | 0,73 % | 8,4 % | 0,087 | 1 239 | 64,1 % | 119 | 23 | 110 722 |
| B) 0,5 % každá, limity zapnuté | 2,74 % | 15,1 % | 0,182 | 2 164 | 41,3 % | 123 | 16 | 146 017 |
| C) 0,5 % každá, bez limitů | 2,70 % | 31,1 % | 0,087 | 1 239 | 65,1 % | 118 | 23 | 145 122 |

Jak číst tabulky: hodnoty ze `s03_portfolio_C2_C3_C5_C9.json`, období a definice jako výše. Varianta B
byla zastavena kill switchem 2018-12-21 (`halt_reason`), proto má nízkou expozici 41,3 % a dobu pod
vodou 2 164 dní (od zastavení do konce 2023 se equity nehýbe). Co z toho plyne: přidání C9 zvýší
Sharpe varianty A jen z 0,24 na 0,27 a MaxDD vzroste ze 7,5 % na 8,4 %. Bez limitů by drawdown
čtyřčlenné rodiny dosáhl **31,1 %**. Přínos C9 je malý a stojí na DEV, kde byla C9 silná; v OOS byla
C9 nulová (−0,013 R, kapitola 10.4). Protože C9 navíc vyžaduje živý USD index a s C2 koreluje 0,79,
zmrazená specifikace ji z portfolia vynechala [E].

## 11.7 Odmítnutí risk managerem

Ve variantě A risk manager odmítl **79 vstupních signálů, všechny z důvodu „spread too wide“** (spread
nad 6 bp v okamžiku rozhodnutí, `risk_rejections` v `s03_portfolio.json`); ve čtyřčlenné variantě 90.
Rozbor odmítnutí z opakovaného běhu [E, vlastní dopočet z tabulky rozhodnutí risk manageru]:

| Ukazatel | Hodnota |
|---|---|
| Vstupních signálů celkem / odmítnuto | 1 187 / 79 (6,7 %) |
| Odmítnutí podle strategie | C5 37, C3 22, C2 20 |
| Ztracené obchody proti variantě C | C3 22 z 256 (8,6 %), C2 4 z 373, C5 6 z 510 |
| Odmítnutí na signálu H4 baru 20:00–24:00 serverového času | 71 ze 79 (90 %) |
| Ostatní hodiny (bary 00, 12, 16) | 2 + 3 + 3 |
| Data B (do 2016-08) / data A (od 2016-09) | 41 / 38 |
| Denní, týdenní, strategický a portfoliový limit | ani jednou |

Jak číst tabulku: signál H4 baru 20:00–24:00 se vyhodnocuje na jeho uzavření o serverové půlnoci, tj.
v 17:00 New York, kdy trh denně uzavírá a znovu otevírá a spread je nejširší (kapitola 3.5). Co z toho
plyne: limit spreadu zasahuje téměř výhradně do této jedné hodiny. Breakout strategie C2 a C5 o obchod
většinou nepřijdou, protože jejich podmínka (close nad kanálem, close mimo pásmo) trvá i na dalším baru
a vstup proběhne o 4 hodiny později. C3 reaguje na jednorázovou událost (překřížení EMA), takže odmítnutý
signál se už nezopakuje a C3 ve variantě A přichází o 8,6 % obchodů [E].

Poznámka k implementaci [I]: živý driver (`tradingsystem/live/runner.py`) uzavřený bar nevyhodnotí
během denní přestávky ani při spreadu nad 4 bp a rozhodnutí odloží až o 180 minut. V živém provozu by
proto většina těchto odmítnutí pravděpodobně nenastala a varianta A je v tomto ohledu mírně
konzervativnější než skutečná implementace. Vliv na výsledek je malý (rozdíl obchodů A vs. C je 2,8 %),
v PAPER fázi ho lze změřit přímo.

Ostatní limity ve variantě A nikdy nezasáhly: nejhorší den portfolia byl −0,80 % (2014-12-01), nejhorší
týden −1,01 %, největší drawdown P&L jednotlivých strategií 5 978 USD (C5), 4 668 USD (C2) a 2 025 USD
(C3), tedy hluboko pod strategickým stopem 10 % equity [E, vlastní dopočet]. Ve variantě B naopak
risk manager po zastavení odmítl 488 signálů, 72 kvůli spreadu, 10 kvůli limitu otevřeného rizika
1,5 % (tři souběžné pozice po 0,5 %) a 1 kvůli dennímu limitu ztráty.

## 11.8 Portfolio po letech

| Rok | Zlato | 3 str.: výnos | 3 str.: obch. | 3 str.: win % | 3 str.: exp. R | 3 str.: PF | 4 str.: výnos | 4 str.: obch. | 4 str.: exp. R | 4 str.: PF |
|---|---|---|---|---|---|---|---|---|---|---|
| 2010 | +28,3 % | −1,2 % | 82 | 30 % | −0,139 | 0,71 | −1,2 % | 96 | −0,146 | 0,72 |
| 2011 | +11,1 % | +1,7 % | 79 | 44 % | 0,190 | 1,46 | +2,7 % | 98 | 0,284 | 1,65 |
| 2012 | +7,1 % | −0,5 % | 71 | 34 % | −0,059 | 0,88 | −0,2 % | 82 | −0,036 | 0,93 |
| 2013 | −27,9 % | +2,5 % | 76 | 34 % | 0,227 | 1,43 | +3,2 % | 89 | 0,314 | 1,68 |
| 2014 | −1,8 % | +0,7 % | 82 | 28 % | 0,051 | 1,09 | +0,2 % | 102 | 0,000 | 1,02 |
| 2015 | −10,6 % | +1,9 % | 74 | 38 % | 0,168 | 1,31 | +2,0 % | 91 | 0,187 | 1,33 |
| 2016 | +8,5 % | +3,1 % | 85 | 35 % | 0,209 | 1,51 | +3,3 % | 99 | 0,260 | 1,59 |
| 2017 | +13,1 % | +3,8 % | 75 | 41 % | 0,162 | 1,37 | +2,9 % | 92 | 0,088 | 1,19 |
| 2018 | −1,6 % | −2,8 % | 88 | 33 % | −0,077 | 0,84 | −2,6 % | 104 | −0,061 | 0,88 |
| 2019 | +18,3 % | +0,3 % | 75 | 29 % | −0,013 | 0,97 | −0,2 % | 91 | −0,099 | 0,82 |
| 2020 | +25,1 % | +1,0 % | 74 | 28 % | 0,114 | 1,30 | +2,1 % | 88 | 0,281 | 1,59 |
| 2021 | −3,6 % | −2,1 % | 77 | 25 % | −0,172 | 0,68 | −2,5 % | 94 | −0,241 | 0,60 |
| 2022 | −0,3 % | −1,7 % | 80 | 30 % | −0,141 | 0,74 | −1,9 % | 100 | −0,165 | 0,69 |
| 2023 | +13,1 % | +2,9 % | 89 | 40 % | 0,203 | 1,42 | +2,8 % | 106 | 0,203 | 1,44 |

Jak číst tabulku: „3 str.“ je varianta A trojice C3/C2/C5 (váhy 1/3), „4 str.“ varianta A čtveřice
(váhy 1/4); hodnoty z tabulek „Portfolio by year“ v `s03_portfolio.md` a `s03_portfolio_C2_C3_C5_C9.md`.
Výnos je změna equity za kalendářní rok (včetně otevřených pozic), obchody, win rate, expectancy a PF
podle roku výstupu obchodu. Sloupec „Zlato“ je roční změna mid close D1 spojené řady (kapitola 10). Co
z toho plyne:

- Trojice byla kladná v **9 ze 14 let**, roční výnos v rozmezí −2,8 % až +3,8 %. Ztrátové roky jsou
  mělké, ale řadí se za sebou: 2018–2022 je pět let, z nichž tři jsou ztrátové a dva téměř nulové.
- **Výnos portfolia nesleduje cenu zlata:** 2010 (zlato +28 %) skončil ztrátou −1,2 %, zatímco 2013
  (zlato −28 %) přinesl +2,5 % díky short obchodům. Trendová rodina tedy není jen skrytý long zlata.
  Vydělává na dlouhých souvislých pohybech v obou směrech a ztrácí v rozkolísaném trhu s obraty
  (2010, 2018, 2021, 2022) [E/I].
- Roční profil čtveřice je téměř totožný (kladná v 8 ze 14 let). C9 posiluje dobré roky (2011, 2013,
  2020) a prohlubuje špatné (2019, 2021), protože je to zesílená C2.

## 11.9 Doba pod vodou a blokový bootstrap drawdownu portfolia

Dopočet z uložené hodinové equity varianty A (`research/results/cache/portfolio_full.pkl`, 82 058
hodinových bodů, konečná equity 109 547,52 USD shodná s `s03_portfolio.json`) [E, vlastní dopočet]:

| Období pod vodou (od vrcholu do nového vrcholu) | Délka (dny) | Poznámka |
|---|---|---|
| 2018-01-25 → konec DEV+OOS (2023-12-29) | 2 164 | nezotaveno; na konci 3,5 % pod vrcholem 113 545 USD; uvnitř leží MaxDD 7,5 % (dno 2023-08-07) |
| 2010-04-12 → 2012-05-16 | 765 | — |
| 2013-06-28 → 2014-10-31 | 490 | — |
| 2014-11-07 → 2015-11-03 | 361 | — |

Jak číst tabulku: čtyři nejdelší úseky, kdy equity nebyla na novém maximu. Co z toho plyne: **portfolio
bylo v DEV+OOS pod vodou téměř šest let v kuse** (2018-01 až 2023-12) a jeho nejhlubší propad přišel až
na konci tohoto období. Celý čistý výnos 9,4 % za 14 let vznikl v letech 2013–2017 (equity na konci roku
2012 99 928 USD, na konci roku 2017 112 419 USD); úseky 2010–2012 a 2018–2023 byly dohromady ztrátové
[E, vlastní dopočet z equity]. Pokud bychom
na konec DEV+OOS hypoteticky navázali holdoutový běh portfolia (který začínal znovu na 100 000 USD)
a spojili výnosy násobením, vrchol z 2018-01-25 by byl překonán až **2025-11-13**, tedy po zhruba
7,8 letech (2 849 dnech) [I, vlastní dopočet; spojení je přibližné, protože sizing se počítá z equity
na začátku měsíce]. Kdo by tuto rodinu obchodoval, musí počítat s mnohaletými obdobími bez nového
maxima, i když edge existuje.

Blokový bootstrap denních výnosů varianty A (3 605 denních výnosů, bloky 20 dní, 5 000 simulací,
`seed = 11`, stejný algoritmus jako `block_bootstrap_daily` v `research/stats.py`, doplněný o další
percentily) [E, vlastní dopočet]:

| Percentil MaxDD | p05 | p10 | p25 | p50 | p75 | p90 | p95 | p99 |
|---|---|---|---|---|---|---|---|---|
| MaxDD portfolia (14 let) | 4,9 % | 5,5 % | 6,6 % | 8,3 % | 10,5 % | 13,1 % | 14,9 % | 18,6 % |

Jak číst tabulku: rozdělení maximálního drawdownu za 14 let, které by portfolio se stejným rozdělením
denních výnosů mohlo mít při jiném pořadí měsíců. Hodnoty z `REPORT.md` (medián 8,3 %, p90 13,1 %,
p95 14,9 %) **ověřeny** a sedí na desetinu procenta. Doplňkové pravděpodobnosti ze stejných simulací:
P(MaxDD ≥ 7,5 %, tj. alespoň skutečná hodnota) = 60,8 %, P(MaxDD > 10 %) = 29,4 %, P(MaxDD ≥ 15 %)
= 4,9 %. Sharpe p05 / p50 / p95 = −0,19 / 0,23 / 0,64, P(Sharpe > 0) = 82,1 %. Co z toho plyne:

- Skutečný MaxDD 7,5 % je mírně pod mediánem simulací, historie tedy nebyla extrémně nepříznivá ani
  příznivá.
- **Portfoliový kill switch 15 % odpovídá p95** a demotion práh v promotion gates (p90 ≈ 13 %) odpovídá
  p90 tohoto rozdělení (kapitola 18). Jsou tedy nastaveny tak, aby je normální průběh překročil jen
  zřídka, ale skutečné selhání edge je zachytilo.
- I u portfolia je P(Sharpe > 0) jen 82 %. Kombinace strategií statistickou jistotu nezvýšila (C3 sama:
  80,7 %), protože jde o jednu sázku.

## 11.10 Závěr „jedna sázka“ a proč jeden rizikový rozpočet

Důkazy pro to, že C3, C2 a C5 jsou fakticky **jedna podkladová sázka na střednědobý trend zlata**:

1. **Směr:** při současné pozici stejný směr v 98,7–100 % hodin; opačné pozice prakticky neexistují [E].
2. **Překryv:** v trhu současně 1,3–1,5× častěji, než by odpovídalo nezávislosti [E].
3. **Drawdowny:** korelace drawdownů 0,67–0,70, společné hluboké drawdowny 3,5–4× častěji než při
   nezávislosti; všechny tři varianty portfolia mají vrchol equity ve stejný den (2018-01-25) [E].
4. **Režimy:** všechny ztrácejí ve stejných prostředích (VIX > 25, vysoká volatilita) [E].
5. **Stabilita:** korelace 0,3–0,6 ve všech tříletých blocích i v holdoutu [E].
6. **Teorie:** Levine a Pedersen (2016) ukazují, že time-series momentum, křížení klouzavých průměrů
   a breakout kanálu jsou různě vážené lineární filtry minulých výnosů, tedy matematicky příbuzné
   signály [E/R, kapitola 5.2].

Z toho plyne pravidlo pro řízení rizika: **jedna sázka smí dostat jen jeden rizikový rozpočet.**
Kdyby každá strategie riskovala 0,5 % na obchod, rodina by v 8,4 % hodin riskovala 1,5 % na jeden
směr jedné teze a drawdown v DEV+OOS by dosáhl 15 % (s kill switchem v 11/2021) až 23 % (bez limitů).
S váhami 1/3 riskuje každá strategie 0,167 % a celá rodina nejvýše 0,5 %, tedy právě tolik, kolik by
riskovala jedna samostatná strategie. MaxDD 7,5 % je pak srovnatelný s C3 samotnou při 0,5 % (7,4 %)
a nižší než u C2 (13,4 %) a C5 (16,9 %) při 0,5 % (kapitola 10).

**Proč stejné váhy a ne optimalizované:** rozdíly mezi strategiemi (Sharpe 0,17–0,25 v DEV+OOS) jsou
v rámci statistického šumu (kapitola 14), takže pro odlišné váhy neexistuje robustní důvod. Optimalizace
vah by byla další stupeň volnosti nastavený na stejných datech. Váhy 1/3 byly určeny po analýze
DEV+OOS a zmrazeny v `research/frozen_spec.json` (commit `cfe78c3`) před holdoutem. Že nejsou
v původním protokolu, je evidováno jako odchylka č. 5 (kapitola 4.10).

## 11.11 Přináší kombinace diverzifikaci a kolik?

Diverzifikace uvnitř trojice existuje, ale jen v **časování vstupů a výstupů**. Každá strategie reaguje
na trend jiným mechanismem: C3 křížením EMA 20/100 (pozdní, ale stabilní vstup), C2 proražením
55barového kanálu (rychlý vstup na začátku silného pohybu), C5 výjezdem z období nízké volatility
(krátké držení ~3 dny). Proto se liší dny, kdy vydělávají, a denní korelace je jen 0,34–0,45. V měsících
a letech, kdy trend chybí, ale ztrácejí všechny.

Velikost diverzifikačního přínosu jsem kvantifikoval z denních výnosů samostatných běhů [E/I, vlastní
dopočet z `cache/<K>_full.pkl`, DEV+OOS]:

| Ukazatel | Hodnota | Výklad |
|---|---|---|
| Průměrná párová korelace trojice | 0,406 | průměr 0,451, 0,341 a 0,427 |
| Efektivní počet nezávislých sázek | 1,66 | N / (1 + (N − 1) · ρ̄) pro N = 3 |
| Diverzifikační poměr | 1,26 | vážený součet volatilit / volatilita kombinace |
| Sharpe jednotlivě (C3 / C2 / C5) | 0,25 / 0,22 / 0,17 | průměr 0,213 |
| Sharpe prosté kombinace 1/3 denních výnosů | 0,262 | bez interakcí risk manageru |
| Teoretický Sharpe pro ρ̄ = 0,406 | 0,274 | průměrný Sharpe × odmocnina(3 / 1,812), platí pro stejné volatility |
| Sharpe portfolia přes engine (varianta A) | 0,239 | s limity a odmítnutím 79 vstupů |
| Sharpe portfolia bez limitů (varianta C) | 0,264 | `s03_portfolio.json` |

Jak číst tabulku: efektivní počet sázek říká, kolika úplně nezávislým strategiím se stejným rizikem
kombinace odpovídá (vzorec předpokládá stejné volatility, jde tedy o přibližnou míru [I]). Diverzifikační
poměr 1 znamená žádnou diverzifikaci. Pro tři nezávislé strategie s volatilitami, jaké mají C3, C2
a C5 (2,2 %, 4,9 % a 3,9 % ročně při 0,5 % riziku), by byl 1,66. Co z toho plyne:

- **Kombinace tří strategií odpovídá zhruba 1,7 nezávislé sázky**, ne třem. Diverzifikační poměr 1,26
  leží blíž jedné sázce (1,00) než třem nezávislým (1,66).
- Proti průměrné jednotlivé strategii zvyšuje kombinace Sharpe zhruba o 23 % (0,213 → 0,262). Proti
  nejlepší jednotlivé (C3, 0,249) je zlepšení jen asi 5 % a ve skutečném enginu s limity (0,239) žádné.
  Prakticky měřitelný přínos je tedy **hladší equity a víc obchodů** (79 ročně místo 18–37), ne vyšší
  výkonnost na jednotku rizika [I].
- Víc obchodů má pro další zpracování praktickou hodnotu: v PAPER a DEMO fázi se rychleji nasbírá vzorek
  pro měření nákladů a implementační věrnosti (brány v kapitole 18 počítají obchody za rodinu).
- **Diverzifikace nefunguje tam, kde by byla nejpotřebnější.** Ve vysoké volatilitě, v krizi
  a v hlubokých drawdownech se strategie chovají jako jedna. Portfolio proto nesnižuje riziko
  víceletých období pod vodou (2018–2023).
- **C9 diverzifikaci nepřidává:** s C2 koreluje 0,79 a překrývá se s ní 2,2× víc, než by odpovídalo
  nezávislosti. Čtveřice by z pohledu rizika byla jen „trojice s dvojnásobnou vahou Donchianu“.

> **Závěr:** C3, C2 a C5 nejsou tři komplementární strategie, ale **jedna sázka na střednědobý trend
> zlata** se třemi různými spouštěči. Když jsou v trhu současně, jsou vždy ve stejném směru, propadají
> se společně a selhávají ve stejných režimech. Kombinace přináší jen skromnou diverzifikaci v časování
> (efektivně asi 1,7 nezávislé sázky, Sharpe 0,24–0,26 proti 0,25 u samotné C3) a žádnou ochranu ve
> špatných režimech. Proto má rodina **jeden rizikový rozpočet: 0,5 % na obchod celkem, váhy 1/3**,
> s produkčními limity (15% kill switch ≈ p95 blokového bootstrapu). I tak je třeba počítat s MaxDD
> kolem 8 % (medián bootstrapu) až 15 % (p95) a s mnohaletými obdobími bez nového maxima. Slot pro
> druhý a třetí skutečně nezávislý zdroj výnosu zůstává neobsazený.

*Zdrojové soubory: `research/results/s03_portfolio.json`, `research/results/s03_portfolio.md`,
`research/results/s03_portfolio_C2_C3_C5_C9.json`, `research/results/s03_portfolio_C2_C3_C5_C9.md`,
`research/results/s02_C3.json`, `s02_C2.json`, `s02_C5.json`, `s02_C9.json` (počty obchodů podle režimů,
metriky jednotlivých strategií), `research/results/cache/portfolio_full.pkl` (hodinová equity varianty A),
`research/results/cache/C3_full.pkl`, `C2_full.pkl`, `C5_full.pkl`, `C9_full.pkl` (denní výnosy a obchody
DEV+OOS), `research/results/cache/C3_holdout.pkl`, `C2_holdout.pkl`, `C5_holdout.pkl`, `C9_holdout.pkl`
(kontrola na holdoutu), `research/frozen_spec.json`, `config/paper.toml`; kód `research/s03_portfolio.py`,
`research/stats.py`, `research/common.py`, `research/registry.py`, `tradingsystem/risk/manager.py`,
`tradingsystem/backtest/metrics.py`, `tradingsystem/live/runner.py`. Vlastní dopočty (bez zápisu do
repozitáře): korelace po tříletých blocích a v holdoutu; překryvy pozic v holdoutu; rozdělení počtu
současně otevřených pozic; opakované běhy tří variant portfolia přes `research/common.py` (rozbor
odmítnutí risk manageru, průběh drawdownů, kill switch, nejhorší den a týden, drawdowny P&L
strategií); nejdelší období pod vodou a hypotetické spojení s holdoutem; blokový bootstrap MaxDD
a Sharpe portfolia (5 000 simulací, bloky 20 dní); efektivní počet sázek, diverzifikační poměr a Sharpe
prosté kombinace; podíly „Poměr“, „Násobek“ a průměry v tabulkách.*
