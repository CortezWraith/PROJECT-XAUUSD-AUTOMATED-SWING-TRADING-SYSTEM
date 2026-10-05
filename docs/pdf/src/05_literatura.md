# 5. Rešerše literatury a důkazů

Tato kapitola rozšiřuje kapitolu 3 původního reportu („Internet evidence review“). Pro každé téma
uvádí, co zdroj skutečně zjistil (vzorek, období, rok publikace), jaký typ důkazu to je, jak
kvalitní ten důkaz je a hlavně **co z něj plyne pro návrh swingového systému na XAUUSD** a jak se
promítl do scorecardu a výběru kandidátů (kapitola 6). Tam, kde to šlo levně a bez zásahu do
předregistrovaného protokolu, je tvrzení literatury navíc **zkontrolováno na našich datech**
(deskriptivní dopočty z `data/processed`). Tyto kontroly vznikly až při přípravě tohoto dokumentu,
žádné rozhodnutí o výběru strategií neovlivnily a jsou tak i označeny.

## 5.1 Rozsah, postup a jak číst tuto kapitolu

**Postup.** Rešerše proběhla před prvním backtestem (pořadí kroků v kapitole 2 reportu: rešerše →
datová pipeline → předregistrace). Hledalo se podle témat, která vyjmenovává zadání: trend a
momentum, breakout, mean reversion, volatilitní režimy, sezónnost, makro filtry (USD, reálné sazby,
volatilita), čas v dni, nákladová citlivost a metodika proti overfittingu. Akademické zdroje mají
přednost; praktické a komunitní zdroje slouží jen jako sekundární doklad praktických pozorování.

**Omezení přístupu ke zdrojům.** Síťová politika sandboxu blokovala plné texty (arXiv, SSRN, RePEc,
Quantpedia a podobně). Vycházíme proto z abstraktů, souhrnů a citací dohledaných vyhledávačem. Při
přípravě této kapitoly byly vzorky a období klíčových studií znovu dohledány z vyhledávacích souhrnů
(2026-10-05); plné texty zůstaly nedostupné. Údaje, které nešlo ověřit, jsou výslovně označeny.

**Značení typu důkazu** (pravidlo ze zadání):

- **[E] empirický důkaz** – výsledek měření na datech (studie, nebo náš vlastní dopočet; ten je
  označen „[E, tato studie]“ nebo „[E, vlastní dopočet]“).
- **[R] ekonomické zdůvodnění** – mechanismus, proč by efekt měl existovat.
- **[I] expertní inference** – úsudek, který z důkazů rozumně plyne, ale přímo změřen nebyl.
- **[U] nepodložený předpoklad** – tvrzení bez opory v datech, nebo s oporou jen anekdotickou.

**Stupnice kvality důkazu** (zavedena pro tento dokument, aby bylo vidět, proč některé zdroje vážily víc):

| Kvalita | Kritérium | Příklad |
|---|---|---|
| Vysoká | recenzovaný časopis, dlouhý vzorek a/nebo mnoho trhů, nezávislé replikace | Moskowitz, Ooi, Pedersen (2012); Hurst, Ooi, Pedersen (2017) |
| Střední | recenzovaný, ale jeden trh, kratší vzorek nebo jiný horizont; nebo preprint renomovaných autorů s velkým vzorkem | Blose, Gondhalekar, Kort (2018); Kurth et al. (2026) |
| Nízká | diplomové práce, institucionální komentáře bez metodiky, praktici | „London bias“, diplomová práce k ORB na zlatě |
| Nevěrohodná | vnitřně nekonzistentní nebo v hrubém rozporu s ostatní evidencí | Singha et al. (2025) |

*Jak číst:* kvalita se týká síly důkazu pro samotný efekt v původním trhu a horizontu. Pro XAUUSD
swing (4 h – 10 dní) je navíc vždy potřeba přenos (jiný trh, jiný horizont, retailové náklady), a ten
je téměř vždy jen **[I]**. *Co z toho plyne:* ani „vysoká“ kvalita zdroje nezaručuje efekt na našem
instrumentu a horizontu – proto byl nutný předregistrovaný backtest.

**Pravidlo zadání o váze důkazů.** Zadání žádá dát větší váhu důkazům, které **předcházejí testovanému
období**, a výsledkům replikovaným napříč trhy nebo na dlouhých vzorcích. To má praktický důsledek:
řada citovaných studií končí svůj vzorek před naším DEV obdobím (2010–2018) nebo před OOS (2019–2023),
takže náš backtest je pro ně fakticky **post-publikačním (out-of-sample) testem** na jiném instrumentu.
Souhrn, co se udrželo a co ne, je v podkapitole 5.16.

## 5.2 Trend a time-series momentum (TSMOM)

Time-series momentum (TSMOM) znamená: obchoduj ve směru vlastního minulého výnosu instrumentu (je-li
výnos za posledních N období kladný, drž long, jinak short). Klouzavé průměry, cenové kanály
(Donchian) i breakouty jsou technicky různé podoby téže myšlenky.

### Co zdroje zjistily

- **Moskowitz, Ooi, Pedersen (2012, *Journal of Financial Economics* 104(2):228–250).** 58 likvidních
  futures a forwardů (akciové indexy, měny, komodity včetně zlata, dluhopisy), data od roku 1965 do
  2009. Výnos za posledních 1–12 měsíců predikuje výnos příštího měsíce; efekt trvá přibližně rok a
  potom se částečně obrací. Typ **[E]**, kvalita **vysoká** (mnoho trhů, desetiletí, nezávislé replikace).
  Horizont je ale **měsíční**, ne swingový.
- **Hurst, Ooi, Pedersen (2017, *Journal of Portfolio Management*).** Trend-following na 67 trzích od
  roku 1880 do 2016; konzistentně ziskový napříč dekádami a dobře fungující ve většině velkých krizí
  („crisis alpha“). Typ **[E]**, kvalita **vysoká**, horizont opět měsíční.
- **Szakmary, Shen, Sharma (2010, *Journal of Banking & Finance* 34(2):409–426).** Měsíční data,
  28 komoditních futures, 48 let. Všechny parametrizace dvojitého klouzavého průměru a kanálových
  strategií měly kladný průměrný nadvýnos po nákladech nejméně ve 22 z 28 trhů. Typ **[E]**, kvalita
  **vysoká** pro komodity, horizont měsíční.
- **Han, Hu, Yang (2016, *Journal of Banking & Finance* 70:214–234).** 35 komoditních futures řazených
  do tercilových portfolií; časování klouzavým průměrem porazilo buy-and-hold na seřazených
  portfoliích, výhoda pochází z úspěšného časování trhu. **Na jednotlivých futures byly výsledky
  nekonzistentní.** Typ **[E]**, kvalita **vysoká**, ale pro jeden instrument (náš případ) je
  nejdůležitější právě ta nekonzistence.
- **Levine, Pedersen (2016, *Financial Analysts Journal* 72(3):51–66, „Which Trend Is Your Friend?“).**
  Teoreticky i empiricky ukazují, že TSMOM a křížení klouzavých průměrů jsou v obecné podobě
  ekvivalentní reprezentace (lineární filtry ceny); stejně tak řada dalších filtrů (Hodrick–Prescott,
  Kalman). Typ **[E/R]**, kvalita **vysoká**.
- **Baltas, Kosowski (2013; kapitola v knize *Market Momentum*, 2020).** Podle dostupného souhrnu
  volba odhadu volatility a trendového pravidla mění obrat portfolia o více než třetinu, aniž by se
  podstatně změnil výkon. Typ **[E]**, kvalita **střední** (detaily neověřeny, jen souhrn).
- **Goulding, Harvey, Mazzoleni (2024, *Financial Analysts Journal* 80(1), „Breaking Bad Trends“).**
  Měsíční výnosy 43 futures (11 akciových indexů, 8 dluhopisových trhů, 24 komodit). Body obratu
  (období, kdy se pomalý a rychlý trendový signál neshodují) výrazně snižují výnos trendových
  strategií a v posledních letech jich přibylo. Typ **[E]**, kvalita **vysoká**.
- **Top Traders Unplugged / Quantica (zpráva 01/2025).** Komodity tvořily zhruba polovinu výnosů
  trendových CTA do 12/2024. Typ **[I]**, kvalita **nízká** (praktický komentář).

### Proč by trend měl existovat [R]

Literatura nabízí několik mechanismů: pomalá difúze informací a nedoreakce investorů na zprávy,
„hedging pressure“ (producenti a spotřebitelé komodit se zajišťují nezávisle na ceně), pomalý kapitál
(institucionální realokace trvají týdny až měsíce), stádní chování a zpětná vazba samotných trendových
fondů, jejichž obchody svým dopadem na cenu trend prodlužují (tento kanál zdůrazňují Kurth et al., viz
5.4). U zlata se k tomu přidávají dlouhé makro cykly – reálné sazby, síla USD, poptávka centrálních
bank – které se mění pomalu **[I]**.

### Co to znamená pro návrh

1. **Trend je nejlépe doložená rodina** – proto dostal trend nejvyšší skóre „důkazy“ (C1 85, C2 65,
   C3 60) a C2 se stala předregistrovanou volbou č. 1.
2. **Horizontový nesoulad.** Téměř všechna silná evidence je pro měsíční rebalancování a lookback
   1–12 měsíců. Mandát projektu je 4 h – 10 dní. Přenos na H4 je **[I]**, nikoli **[E]**. Proto byl
   C1 (denní TSMOM s 60denním lookbackem) jen benchmarkem: jeho přirozené držení je mimo mandát
   (v DEV skutečně průměrně 693 h, tj. zhruba 29 dní).
3. **Ekvivalence filtrů (Levine & Pedersen) = jedna sázka.** Donchian (C2), EMA cross (C3) i squeeze
   breakout (C5) jsou varianty téhož trendového filtru. Proto byla C3 při předregistraci záměrně
   vynechána z hlavní trojice ve prospěch odlišné rodiny (C6) – viz kapitola 6. Ex post se ekvivalence
   potvrdila: při současné pozici jsou C3, C2 a C5 ve stejném směru v 99–100 % času
   (`s03_portfolio.md`).
4. **Jeden instrument je slabší případ.** Han, Hu, Yang ukazují, že výhoda časování je robustní na
   portfoliích, ale nekonzistentní na jednotlivých futures. Systém na jediném instrumentu nemá
   diverzifikaci, ze které TSMOM literatura těží – očekávání musí být skromnější **[I]**.
5. **Body obratu (Goulding et al.)** jsou hlavní nepřítel trendu. To odpovídá našemu zjištění, že
   trendové varianty ztrácejí ve vysoké volatilitě a v krizích (níže a kapitola 5.5).

### Konfrontace s našimi výsledky [E, tato studie]

- Denní TSMOM (C1) byl v DEV prakticky nulový: −0,002 R na obchod po nákladech (hrubě 0,055 R).
- Trend na H4 (C3, C2) byl kladný ve všech čtyřech obdobích 2004–2026, ale slabě: souhrnná
  t-statistika 1,25 (C3) a 1,71 (C2) za 22 let (`s05_pooled.md`).
- **„Crisis alpha“ se na H4 nepřenesla.** Při VIX > 25 (ex ante, data k předchozímu dni) měly C3,
  C2 a C5 v DEV+OOS expectancy −0,158 R (34 obchodů), −0,311 R (54) a −0,229 R (64), v normálním režimu
  +0,095, +0,147 a +0,077 R (`s02_C3/C2/C5.json`, sekce regimes). Měsíční TSMOM z literatury v krizích
  vydělává; rychlejší swingový trend na zlatě v krizích ztrácí.

## 5.3 Skepse k technické analýze a data-snooping

### Co zdroje zjistily

- **Park, Irwin (2007, *Journal of Economic Surveys* 21(4):786–826).** Přehled literatury: z 95
  „moderních“ studií 56 našlo kladné výsledky technických pravidel, 20 záporné a 19 smíšené.
  Technické strategie byly konzistentně ziskové na různých spekulativních trzích **zhruba do začátku
  90. let**; většina studií ale trpí problémy – data-snooping, výběr pravidel ex post, obtížný odhad
  rizika a transakčních nákladů. Typ **[E]**, kvalita **vysoká** (systematický přehled).
- **Marshall, Cahan, Cahan (2008, *Journal of Banking & Finance* 32(9):1810–1819).** 15 hlavních
  komoditních futures, denní data 1984-01 až 2005-12. Po korekci na data-snooping (White's Reality
  Check) žádné statisticky významné překonání trhu. Typ **[E]**, kvalita **vysoká**.
- **Batten, Lucey, McGroarty, Peat, Urquhart (2018, *Journal of International Financial Markets,
  Institutions and Money* 52:102–113).** Intradenní data drahých kovů, tři populární pravidla
  klouzavých průměrů. **Se standardními parametry z literatury žádná prediktivní síla.** Při
  procházení celého „vesmíru“ parametrů se u zlata našly některé kombinace se signifikantní
  predikcí, u stříbra žádné. Typ **[E]**, kvalita **střední** (období vzorku jsme neověřili).

### Co to znamená pro návrh

Výsledek Battena et al. je učebnicový vzorec data-miningu: když se zkouší dost kombinací parametrů,
některé „vyjdou“. Pro náš návrh z toho plynou čtyři konkrétní pravidla, která se promítla do protokolu
(`research/PROTOCOL.md`):

1. **Parametry pouze z literatury a stanovené předem** (Turtle 55/20, EMA 20/100, RSI(2) 10/90 …),
   žádná optimalizace na DEV.
2. **Perturbační mřížky deklarované předem** (125 kombinací, ±25 % kolem defaultu) – robustní efekt
   nesmí záviset na jedné hodnotě parametru.
3. **Korekce na počet testů** – deflated Sharpe s N = 60 konfiguracemi a PBO (kapitola 5.12).
4. **Skromné očekávání:** pokud po 90. letech technická pravidla ve futures po korekci obvykle
   nepřežívají, je realistické čekat malý, statisticky křehký efekt.

V scorecardu se skepse promítla do kritéria **„odolnost vůči overfittingu“** (penalizace za počet
parametrů a za „lore“ bez recenzované podpory: C5 45, C7 45, C11 10) a do střízlivého skóre
„důkazy“ pro všechna technická pravidla (žádné nad 65 kromě C1).

*Konfrontace [E, tato studie]:* náš výsledek je s touto literaturou v souladu – nejlepší trendové
varianty mají t-statistiky 1,25–1,71 za 22 let, deflated Sharpe vůči 60 pokusům prakticky nulový a
nejlepší DEV výsledek (C5, t 1,40) se v OOS obrátil do záporu (−0,092 R).

## 5.4 Zánik krátkodobého trendu po roce 2009 a proč je zlato „small-tick“

### Co zjistili Kurth, Eisler, Rej, Bouchaud (2026)

**Kurth, Eisler, Rej, Bouchaud (2026-07, arXiv 2607.01550, „Is Trend Still Your Friend? A
Microstructural Account of the Demise of Short-Term Trend-Following“).** Typ **[E – preprint]**,
kvalita **střední** (renomovaní autoři z praxe i akademie, velký vzorek, ale bez recenzního řízení;
plný text jsme nečetli). Podle dostupných souhrnů:

- Vzorek: přibližně 100 likvidních futures, 1995–2025.
- Zhruba od roku 2009 krátkodobé trendy přestaly přinášet spolehlivé výnosy.
- Rozhodující průřezovou proměnnou je **velikost ticku normalizovaná volatilitou** (jak velký je
  minimální cenový krok vůči typickému dennímu pohybu) – ne třída aktiv, likvidita ani elektronizace
  trhu. Na **small-tick** kontraktech se P&L trendu po roce 2008 zhroutil (souhrny uvádějí „napříč
  horizonty signálu“), na **large-tick** kontraktech zůstal v podstatě zachován. Robustnostní testy
  podle souhrnů ukazují spíše plynulý gradient než ostrou dichotomii.
- Na úrovni portfolia s rovným rizikem uvádějí souhrny Sharpe před zlomem kolem 0,8 pro krátkodobý a
  kolem 1,4 pro dlouhodobý trend; po zlomu krátkodobý Sharpe zhruba nula (nejrychlejší signály mírně
  záporné).
- Mechanismus **[R]**: trendové obchody svým dopadem na cenu posilují pohyb, který je vyvolal
  (samonaplňující se smyčka). Po krizi začali dominovat HFT tvůrci trhu, kteří před předvídatelným
  směrovým tokem stahují likviditu; v hustých knihách small-tick kontraktů to smyčku přerušilo,
  v řidších knihách large-tick kontraktů zůstává dost hloubky.
- Jako příklady small-tick trhů souhrny uvádějí futures na S&P 500 a hlavní měnové páry; jako
  large-tick některé krátkodobé úrokové futures a vybrané komodity. **Zlato v dostupných souhrnech
  výslovně zařazeno není.**

### Výpočet: jak velký je tick zlata vůči jeho volatilitě [E, vlastní dopočet]

Minimální cenový krok futures GC (COMEX) je 0,10 USD za unci. Typický denní pohyb jsme spočítali
z denních svíček výzkumné řady (střed bid/ask, B do 2016-08, A od 2016-09) jako směrodatnou odchylku
denní změny ceny v USD. Pro srovnání uvádíme i medián ATR(20) na D1 a H4 a směrodatnou odchylku
hodinové změny – vše přepočteno na počet ticků 0,10 USD.

| Období | Ø cena USD | σ denní % | σ denní USD | σ denní v ticích | Tick / σ denní % | Medián ATR20 D1 (ticky) | Medián ATR20 H4 (ticky) | σ H1 (ticky) |
|---|---|---|---|---|---|---|---|---|
| PRE-SAMPLE 2004-07..2009 | 693 | 1,35 | 10,45 | 104 | 0,96 | 124 | 44 | 22 |
| DEV 2010–2018 | 1 342 | 0,98 | 13,67 | 137 | 0,73 | 171 | 63 | 28 |
| OOS 2019–2023 | 1 742 | 0,92 | 16,33 | 163 | 0,61 | 236 | 86 | 35 |
| HOLDOUT 2024–2026-08 | 3 328 | 1,35 | 54,75 | 548 | 0,18 | 445 | 179 | 112 |
| Celkem 2004-07..2026-08 | 1 513 | 1,12 | 22,94 | 229 | 0,44 | 192 | 71 | 47 |

*Jak číst:* „σ denní v ticích“ říká, kolik minimálních cenových kroků odpovídá jedné směrodatné
odchylce denního pohybu; „Tick / σ denní“ je převrácená hodnota v procentech. *Co z toho plyne:*
typický denní pohyb zlata je **stovky ticků** (104 až 548 podle období) a tick je **méně než 1 %**
denní volatility (0,18–0,96 %). I jedna hodinová svíčka má směrodatnou odchylku 22–112 ticků. Cenová
mřížka je tedy vůči pohybu velmi jemná – zlato je podle měřítka Kurth et al. typický **small-tick**
kontrakt. Toto zařazení je naše inference **[I]**: přesnou definici a práh z práce jsme neověřili.

Protože tick je pevný v USD, ale cena zlata za 22 let vzrostla zhruba jedenáctinásobně (průměr roku
2004 od července 417 USD, průměr roku 2026 do srpna 4 572 USD), relativní tick se s časem dál
zmenšoval:

| Rok | Ø cena USD | σ denní % | σ denní USD | σ denní v ticích | Tick / σ % |
|---|---|---|---|---|---|
| 2004 (od 07) | 417 | 0,83 | 3,45 | 35 | 2,89 |
| 2005 | 444 | 0,78 | 3,58 | 36 | 2,79 |
| 2006 | 604 | 1,53 | 9,31 | 93 | 1,07 |
| 2007 | 696 | 1,08 | 7,82 | 78 | 1,28 |
| 2008 | 872 | 1,98 | 16,73 | 167 | 0,60 |
| 2009 | 973 | 1,27 | 12,32 | 123 | 0,81 |
| 2010 | 1 226 | 1,02 | 12,46 | 125 | 0,80 |
| 2011 | 1 573 | 1,26 | 21,15 | 212 | 0,47 |
| 2012 | 1 669 | 0,92 | 15,31 | 153 | 0,65 |
| 2013 | 1 410 | 1,35 | 18,61 | 186 | 0,54 |
| 2014 | 1 266 | 0,90 | 11,24 | 112 | 0,89 |
| 2015 | 1 160 | 0,86 | 10,07 | 101 | 0,99 |
| 2016 | 1 250 | 0,98 | 12,23 | 122 | 0,82 |
| 2017 | 1 259 | 0,63 | 7,92 | 79 | 1,26 |
| 2018 | 1 269 | 0,61 | 7,79 | 78 | 1,28 |
| 2019 | 1 394 | 0,71 | 10,12 | 101 | 0,99 |
| 2020 | 1 772 | 1,20 | 21,29 | 213 | 0,47 |
| 2021 | 1 799 | 0,84 | 15,15 | 152 | 0,66 |
| 2022 | 1 802 | 0,94 | 16,99 | 170 | 0,59 |
| 2023 | 1 943 | 0,83 | 16,13 | 161 | 0,62 |
| 2024 | 2 390 | 0,95 | 23,15 | 231 | 0,43 |
| 2025 | 3 445 | 1,20 | 43,61 | 436 | 0,23 |
| 2026 (do 08) | 4 572 | 1,94 | 91,66 | 917 | 0,11 |

*Jak číst:* procentní volatilita (sloupec „σ denní %“) se v čase mění jen v rozmezí zhruba 0,6–2 %,
ale protože cena roste, roste i volatilita v USD a v ticích. *Co z toho plyne:* relativní tick zlata se
od roku 2004 zmenšil přibližně 26krát (z 2,89 % na 0,11 % denní σ). Kdyby hypotéza Kurth et al.
platila pro zlato jako plynulý gradient, krátkodobý trend na zlatě by měl s časem spíše slábnout
**[I]**. Naše data to nedokážou oddělit od jiných vlivů – holdout 2024–2026 s nejmenším relativním
tickem byl pro trend nejlepší, protože šlo o mimořádně silný býčí trh.

Doplňující údaj k mikrostruktuře spotového trhu: medián spreadu XAUUSD v datové sadě A byl podle roku
0,24–0,69 USD, tj. **2,4–6,9 ticků GC**, resp. 1,5–2,3 bp (`data_quality.json`). Spread tedy není
„přimáčknutý“ na jeden minimální krok, což je typický znak small-tick trhu **[I]**. XAUUSD je navíc OTC
spotový trh, ne burzovní kniha GC; že jeho cenová dynamika kopíruje GC (arbitráž mezi spotem a
futures), je předpoklad **[I]**.

### Co to znamená pro návrh

1. **Negativní apriorní důkaz pro rychlý trend na zlatě [I].** Proto C2 nedostala v scorecardu za
   důkazy víc než 65 (poznámka scorecardu výslovně cituje Kurth et al.) a C3 60.
2. **Volba horizontu.** Mandát dovoluje H1–D1; trendové kandidáty jsme postavili na H4 (držení 3–7
   dní), ne na H1, a vysokofrekvenční varianty (C7 na H1) dostaly nízké skóre i z nákladových důvodů.
3. **Realistické očekávání velikosti efektu:** i kdyby trend na zlatě přežil, Sharpe kolem 0,8 z
   předkrizového portfolia ~100 trhů je horní mez, ne cíl pro jeden instrument.

### Co naše data k hypotéze říkají (a neříkají) [E, tato studie]

- Trend na H4 je slabě kladný, ne nulový: souhrnný Sharpe 2004–2026 0,27 (C3), 0,40 (C2), 0,33 (C5)
  (`s05_pooled.json`). To je s hypotézou „krátkodobý trend na small-tick kontraktech je po 2009 mrtvý“
  v mírném napětí, ale statisticky od nuly neodlišitelné.
- **Uvnitř rozsahu H2–D1 nevidíme, že by rychlejší varianta byla systematicky horší** (DEV+OOS,
  expectancy R): C2 H2 0,129, H3 0,055, H4 0,081, H6 0,079, D1 0,026; C3 H2 0,020, H4 0,061, D1 0,039;
  C5 H2 0,117, H4 0,038, H6 0,089 (`s02_*.json`, sekce timeframes). Pořadí je spíše šum.
- Hypotézu tedy **nelze potvrdit ani vyvrátit** – nemáme kontrolní large-tick instrument a náš
  rozsah horizontů je úzký. Pro návrh zůstává jako apriorní varování, ne jako ověřený fakt.

## 5.5 Zlato jako safe haven a inverzní asymetrie volatility

### Co zdroje zjistily

- **Baur, McDermott (2010, *Journal of Banking & Finance* 34(8):1886–1898).** Období 1979–2009.
  Zlato je zajištěním (hedge) i bezpečným přístavem (safe haven) pro hlavní evropské akciové trhy a
  USA, nikoli však pro Austrálii, Kanadu, Japonsko a velké rozvíjející se trhy (BRIC). Na vrcholu
  finanční krize 2008 bylo silným bezpečným přístavem pro většinu vyspělých trhů. Autoři rozlišují
  slabou formu (zlato v krizi nekoreluje) a silnou formu (zlato v krizi roste). Typ **[E]**, kvalita
  **vysoká**.
- **Baur (2012, *Journal of Alternative Investments* 14(4):26–38).** **Inverzní asymetrie
  volatility:** kladné cenové šoky zvyšují volatilitu zlata víc než záporné (u akcií je to naopak).
  Autor to spojuje s rolí bezpečného přístavu – růst zlata investoři čtou jako signál budoucích potíží
  na jiných trzích. Výsledek platí pro slitky i mince, různé měny, frekvence, vzorky a rozdělení.
  Typ **[E]**, kvalita **střední až vysoká** (období vzorku jsme neověřili).

### Kontrola na našich datech: krizové dny a VIX [E, vlastní dopočet]

Pro každé období jsme vzali dny, kdy denní změna indexu VIX patřila mezi 5 % největších (akutní
stres na akciovém trhu), a spočítali průměrný výnos zlata v týž den.

| Období | Dní se skokem VIX v horních 5 % | Ø výnos zlata v tyto dny % | Podíl kladných dní | Ø výnos zlata všechny dny % |
|---|---|---|---|---|
| PRE 2004–09 | 69 | −0,319 | 42,0 % | 0,074 |
| DEV 2010–18 | 113 | 0,077 | 58,4 % | 0,004 |
| OOS 2019–23 | 64 | 0,096 | 59,4 % | 0,037 |
| HOLDOUT 2024–26 | 35 | −0,327 | 37,1 % | 0,112 |
| Celkem 2004–26 | 279 | −0,095 | 50,5 % | 0,042 |

*Jak číst:* je-li zlato silný bezpečný přístav, mělo by ve dnech skoku VIX v průměru růst; při slabé
formě by mělo být kolem nuly. *Co z toho plyne:* v denním měřítku se zlato v akutním stresu chová
nanejvýš jako **slabý** bezpečný přístav – průměr je v celém vzorku mírně záporný (−0,095 %) a polovina
dní je kladná. Navíc je ve stresu **výrazně volatilnější**: ve dnech, kdy předchozí den platilo
VIX > 25 (881 dní), byla směrodatná odchylka denního výnosu zlata 1,51 % proti 1,04 % v ostatních
4 708 dnech, při prakticky stejném průměru (0,054 % vs. 0,040 %). Pro trendový systém to znamená
víc „whipsawů“ (falešných průrazů), ne spolehlivý směr.

### Kontrola na našich datech: asymetrie volatility [E, vlastní dopočet]

Jednoduchý test (není to replikace GARCH modelu z Baurovy studie): absolutní výnos následujícího dne
jsme regresí vysvětlili absolutním výnosem dneška a jeho interakcí s poklesem (abs(r) × 1[r < 0]).
Kladný koeficient interakce znamená **klasickou** asymetrii (po poklesech je volatilita vyšší), záporný
by znamenal **inverzní** asymetrii, kterou popisuje Baur.

| Období | N dní | Ø abs. výnos další den po růstu % | po poklesu % | po 5 % největších růstech % | po 5 % největších poklesech % | Koef. u abs. výnosu (t) | Koef. navíc po poklesu (t) |
|---|---|---|---|---|---|---|---|
| PRE 2004–09 | 1400 | 0,901 | 1,045 | 1,191 | 1,227 | 0,053 (1,63) | 0,091 (2,45) |
| DEV 2010–18 | 2316 | 0,678 | 0,706 | 0,678 | 0,944 | 0,032 (1,20) | 0,096 (3,28) |
| OOS 2019–23 | 1290 | 0,665 | 0,664 | 0,748 | 0,778 | 0,066 (1,92) | −0,020 (−0,51) |
| HOLDOUT 2024–26 | 687 | 0,947 | 0,988 | 1,289 | 1,554 | 0,100 (2,07) | 0,129 (2,43) |
| Celkem 2004–26 | 5693 | 0,765 | 0,809 | 0,917 | 1,202 | 0,089 (5,37) | 0,074 (3,95) |

*Jak číst:* sloupce 3–6 porovnávají průměrnou velikost pohybu následujícího dne po růstových a
poklesových dnech; poslední sloupec je dodatečný vliv poklesu na budoucí volatilitu. t-statistiky jsou
z obyčejných nejmenších čtverců bez korekce na heteroskedasticitu, a proto spíše nadhodnocené. *Co z
toho plyne:* **inverzní asymetrii na našich datech 2004–2026 nevidíme** – po velkých poklesech je
následná volatilita vyšší než po velkých růstech (1,20 % vs. 0,92 %), interakční koeficient je kladný
ve třech ze čtyř období. Výjimkou je jen OOS 2019–2023 (koeficient blízko nuly). Původní report z
Baura odvodil úsudek **[I]**, že long breakouty čelí větším whipsawům; tato kontrola ho **nepodporuje**
a v tomto dokumentu ho přeřazujeme na **[U]**. Rozdíl může být dán metodou (GARCH vs. jednoduchá
regrese) i obdobím (Baurův vzorek končí dříve než náš).

### Co to znamená pro návrh

1. Bezpečný přístav je vlastnost **dlouhých horizontů a vyspělých akciových trhů**, ne spolehlivý
   denní signál. Žádný kandidát proto nestavěl na „long zlato při stresu“.
2. Krize a vysoká volatilita jsou **hlavní režim selhání** trendových variant (5.2): C3, C2, C5 ve
   vysoké volatilitě −0,114, −0,088 a −0,148 R; v nízké +0,228, +0,185 a +0,175 R (DEV+OOS,
   `s02_*.json`). Filtr na volatilitu by se nabízel, ale nebyl předregistrován – jeho zavedení po
   zhlédnutí výsledků by bylo data-snoopingem (kapitola 6 a navazující kapitoly výsledků).
3. Asymetrie mezi long a short stranou trendu, kterou pozorujeme, je **režimová** (short vydělával
   v medvědím 2013–2015, long v býčích 2019–2020 a 2024–2026), ne důsledek stabilní asymetrie
   volatility.

## 5.6 Reálné sazby, USD, rozpad vztahu po roce 2022 a centrální banky

### Co zdroje zjistily

- **Erb, Harvey (2013, *Financial Analysts Journal* 69(4), „The Golden Dilemma“; NBER WP 18706).**
  Zlato je inflačním zajištěním jen v horizontu staletí; na praktických investičních horizontech je
  nespolehlivé. Reálná cena zlata byla v době publikace historicky vysoká a v minulosti po nadprůměrné
  reálné ceně následovaly podprůměrné reálné výnosy (návrat k průměru). Reálná cena zlata souvisí
  negativně s reálnými výnosy (TIPS). Autoři zároveň upozorňují, že kdyby rozvíjející se ekonomiky
  zvýšily oficiální držbu zlata na úroveň vyspělých zemí, reálná cena by mohla dál růst. Typ **[E/R]**,
  kvalita **vysoká**. Aktualizace „Is There Still a Golden Dilemma?“ (2024, SSRN) – detaily neověřeny.
- **J.P. Morgan Private Bank, Janus Henderson (institucionální komentáře, 2024–2025).** Vztah zlata
  a reálných výnosů se po roce 2022 rozpadl: podle J.P. Morgan přibližně 84 % v letech 2005–2021 a
  přibližně 3 % v letech 2022–2023 (sekundární zdroj neuvádí jednoznačně, zda jde o korelaci, nebo
  R²). Typ **[E/I]**, kvalita **nízká až střední** (bez publikované metodiky).
- **World Gold Council (2025–2026, Gold Demand Trends, Mid-Year Outlook 2026).** Centrální banky
  nakoupily v letech 2022, 2023 i 2024 přes 1 000 t zlata ročně; podle sekundárních souhrnů dat WGC
  1 082 t (2022, nejvíce od roku 1950), 1 037 t (2023) a přibližně 1 045 t (2024). Typ **[E]** (data
  o tocích), kvalita **střední**; interpretace (cenově necitlivá poptávka převážila vliv reálných
  sazeb) je **[I]**.

### Kontrola na našich datech [E, vlastní dopočet]

Reálné výnosy (TIPS) jsme k dispozici neměli; používáme nominální 10letý výnos US Treasury, USD index
s vahami DXY a VIX (`macro_daily.parquet`). Korelace jsou současné (stejný den) – jde o popis vztahu,
nikoli o obchodovatelný signál (strategie makro data vždy zpožďují o jeden obchodní den). Roční výnos
zlata je spočten z cen na konci roku.

| Rok | Výnos zlata % | Korelace s Δ USD indexu | Korelace s Δ výnosu 10Y | Korelace s Δ VIX |
|---|---|---|---|---|
| 2004 (od 07) | 11,1 | −0,70 | −0,25 | −0,04 |
| 2005 | 17,8 | −0,48 | −0,08 | 0,00 |
| 2006 | 23,6 | −0,39 | −0,04 | −0,13 |
| 2007 | 30,7 | −0,48 | 0,13 | −0,32 |
| 2008 | 4,2 | −0,51 | −0,04 | −0,06 |
| 2009 | 26,6 | −0,26 | −0,11 | −0,03 |
| 2010 | 28,3 | −0,22 | −0,11 | −0,12 |
| 2011 | 11,1 | −0,22 | −0,07 | 0,03 |
| 2012 | 7,1 | −0,41 | −0,03 | −0,23 |
| 2013 | −27,9 | −0,36 | −0,24 | −0,17 |
| 2014 | −1,8 | −0,40 | −0,32 | 0,13 |
| 2015 | −10,6 | −0,39 | −0,26 | 0,05 |
| 2016 | 8,5 | −0,29 | −0,51 | 0,31 |
| 2017 | 13,1 | −0,40 | −0,64 | 0,20 |
| 2018 | −1,6 | −0,53 | −0,20 | 0,04 |
| 2019 | 18,3 | −0,38 | −0,62 | 0,25 |
| 2020 | 25,1 | −0,35 | −0,22 | −0,09 |
| 2021 | −3,6 | −0,46 | −0,34 | −0,11 |
| 2022 | −0,3 | −0,42 | −0,43 | −0,12 |
| 2023 | 13,1 | −0,44 | −0,52 | 0,20 |
| 2024 | 27,2 | −0,26 | −0,25 | −0,17 |
| 2025 | 64,6 | −0,37 | −0,09 | −0,02 |
| 2026 (do 08) | 3,0 | −0,45 | −0,26 | −0,28 |

*Jak číst:* záporná korelace s USD znamená, že zlato v daný den typicky roste, když dolar oslabuje;
záporná korelace s Δ výnosu 10Y znamená, že zlato roste, když výnosy klesají. *Co z toho plyne:*
**denní citlivost na USD je mimořádně stabilní** (záporná ve všech 23 letech, −0,22 až −0,70).
Citlivost na výnosy je záporná ve 22 z 23 let, ale její síla kolísá (−0,03 až −0,64). Vztah k VIX
mění znaménko z roku na rok – to je další doklad, že „zlato roste při strachu“ neplatí v denním
měřítku spolehlivě.

| Období | Denní korelace s Δ USD | Denní korelace s Δ 10Y | Denní korelace s Δ VIX | Korelace úrovní: log cena vs 10Y |
|---|---|---|---|---|
| 2005–2021 | −0,361 | −0,154 | −0,039 | −0,857 |
| 2022–2026-08 | −0,361 | −0,286 | −0,101 | 0,506 |
| DEV 2010–18 | −0,319 | −0,219 | 0,014 | −0,344 |
| OOS 2019–23 | −0,395 | −0,395 | −0,040 | 0,160 |

*Jak číst:* první tři sloupce popisují krátkodobou (denní) citlivost, poslední sloupec dlouhodobý vztah
úrovní – zda vysoké výnosy chodí s nízkou cenou zlata. *Co z toho plyne:* rozpad, o kterém píše
literatura, je rozpad **vztahu úrovní**: v letech 2005–2021 korelace logaritmu ceny zlata s
nominálním 10Y výnosem −0,857, v letech 2022–2026 **+0,506** (zlato i výnosy rostly současně). Denní
citlivost na výnosy se naopak nerozpadla, ale zesílila (−0,154 → −0,286), citlivost na USD zůstala
stejná (−0,361). Pozor: jde o nominální, ne reálné výnosy **[I]**.

### Co to znamená pro návrh

1. **Makro filtr postavený na úrovních nebo střednědobých trendech makro veličin je nestabilní.**
   Kandidát C9 (Donchian obchodovaný jen tehdy, když 50denní trend USD indexu souhlasí se směrem)
   dostal proto nízké skóre „robustnost napříč režimy“ (40) a „důkazy“ (50) – poznámka scorecardu
   výslovně zmiňuje rozpad vztahu zlata a reálných výnosů v letech 2022–2024.
2. **Ex post [E, tato studie]:** C9 měla nejvyšší DEV expectancy ze všech (0,192 R), ale v OOS
   −0,013 R, walk-forward −0,2 % a denní korelaci výnosů s C2 0,79 (`s03_portfolio_C2_C3_C5_C9.md`).
   Filtr tedy nepřinesl nezávislý zdroj edge, jen přeskupil obchody stejné trendové sázky.
3. **Regimová analýza nedává konzistentní makro obraz:** u C3 silný USD +0,118 R a slabý −0,014 R,
   u C2 téměř shodně (+0,080 vs. +0,083 R); rostoucí výnosy +0,054 (C3), +0,171 (C2), −0,028 R (C5).
   Žádný makro filtr proto nelze doporučit.
4. **Centrální banky jako nový tahoun [I]:** holdout 2024–2026 (cena z 2 063 USD na konci 2023 na
   4 448 USD k 2026-08-31, maximum denního close 5 415 USD dne 2026-01-28; výpočet z D1 dat) proběhl v režimu, který
   v DEV/OOS neexistoval. To je hlavní důvod, proč kladný holdout nelze číst jako potvrzení edge.

## 5.7 Makroekonomické zprávy

- **Elder, Miao, Ramchander (2012, *Journal of Banking & Finance* 36(1):51–65).** Intradenní data
  futures na zlato, stříbro a měď, 2002–2008. Reakce na překvapení v amerických makro zprávách je
  rychlá a významná; největší dopad mají zprávy v 8:30 ET, zejména nezemědělská zaměstnanost (NFP) a
  objednávky zboží dlouhodobé spotřeby. **Neočekávaně dobré zprávy o ekonomice zlato a stříbro
  snižují**, měď zvyšují. Typ **[E]**, kvalita **vysoká** (pro intradenní reakci).

*Co to znamená pro návrh:* zprávy jsou pro swingový systém **exekuční riziko**, ne signál – reakce
proběhne během minut, dávno před uzavřením H4 svíčky. Prakticky to znamená skluz stop příkazů a
mezery (gapy) v okamžiku zprávy. Simulátor proto plní stopy při mezeře na horší ceně (open) a
nákladový model počítá s vyšším skluzem stop příkazů (1,0 bp proti 0,3 bp u market příkazů). Test
zpoždění vstupu o jeden H1 bar ukázal, že trendové varianty na rychlosti reakce nezávisí (C3 0,061 →
0,056 R, C2 0,081 → 0,061 R, C5 0,038 → 0,037 R; `s02_*.json`, segment „delay +1 bar“). Filtr
na kalendář zpráv nebyl předregistrován a nebyl testován (mezera, viz 5.18).

## 5.8 Sezónnost a čas v dni

### Co zdroje zjistily

- **Blose, Gondhalekar, Kort (2018, *Journal of Economics and Finance* 42(3):526–549).** Období
  1985–2012. **Overnight výnosy zlata jsou významně kladné, výnosy během denní seance významně
  záporné** – v předním kontraktu COMEX, ve spotovém trhu (London Fix), v akciích těžařů a v
  uzavřených fondech a ETF na zlato (pro ETF kratší vzorek). Podle původní rešerše ekonomicky významné
  i po nákladech. Výklad autorů: cena zlata je při otevření trhů „příliš vysoko“. Typ **[E]**, kvalita
  **střední až vysoká** (recenzované, dlouhý vzorek, specificky zlato, ale bez replikace po 2012).
- **Blose, Gondhalekar (2013, *Accounting & Finance* 53(3):609–622).** Období 1975–2011. Výnosy zlata
  od pátečního do pondělního close jsou významně nižší než ve zbytku týdne – hlavně kvůli medvědím
  trhům (v býčích trzích rozdíl nevýznamný); souvisí se zápornou šikmostí víkendových výnosů. Typ
  **[E]**, kvalita **střední**.
- **Ma, Bouri, Xu, Zhou (2025, *Global Finance Journal* 64, „night effect“).** Čínské futures na zlato
  a stříbro: po zavedení nočního obchodování se intradenní profil objemu změnil z tvaru U na W;
  existuje intradenní momentum i reverze, záleží na trhu; po zavedení noční seance je hlavním
  prediktorem výnos první půlhodiny noční seance; realizovaná volatilita klesla zhruba o 40 %. Typ
  **[E]**, kvalita **střední** (jiný trh, intradenní horizont).
- **Caminschi, Heaney (2014, *Journal of Futures Markets* 34(11):1003–1039, „Fixing a Leaky
  Fixing“).** Futures GC a ETF GLD kolem londýnského odpoledního fixingu: výrazně zvýšený objem a
  volatilita hned po zahájení fixingu, ještě před zveřejněním výsledku; statisticky významná výhoda
  informovaných obchodníků v prvních 4 minutách; obchody v úvodních minutách predikují směr fixingu,
  v některých případech přes 90 %. Typ **[E]**, kvalita **střední**; pro swing irelevantní (minuty),
  ale dokládá, že intradenní struktura zlata je formována institucionálními událostmi.
- **„London bias“ (goldpriceforecast.com; FXStreet 2026-07: „gold up in Asian markets, down big in the
  West“).** Praktici popisují, že zlato roste v asijských hodinách a klesá během Londýna a New Yorku.
  Typ **[I/U]**, kvalita **nízká**.
- **Baur (2013, *Research in International Business and Finance* 27(1):1–11, „The autumn effect of
  gold“).** Denní data 1981-01 až 2010-12. Září a listopad jsou jediné měsíce s významně kladnými
  výnosy (průměrně přibližně 2,2 % a 1,8 %). Výklad: v tyto měsíce bývají slabé akcie. Typ **[E]**,
  kvalita **střední** (jeden trh, 30 pozorování na měsíc).

### Kontrola na našich datech: intradenní okna [E, vlastní dopočet]

Hodinové výnosy bid open-to-open (stejná metodika jako graf níže), sečtené za každý den v daném okně
serverového času (NY + 7 h), průměr přes dny a t-statistika průměru. Do součtu vstupují jen výnosy
mezi navazujícími hodinami (mezery přes víkend a svátky vynechány).

| Okno (serverový čas) | PRE 2004–09 bp (t) | DEV 2010–18 bp (t) | OOS 2019–23 bp (t) | HOLDOUT 2024–26 bp (t) |
|---|---|---|---|---|
| Asie 02→09 (19:00→02:00 NY) | 3,43 (2,62) | 2,98 (3,85) | 0,85 (0,88) | 2,29 (0,87) |
| Londýn 09→15 (02:00→08:00 NY) | −0,19 (−0,09) | −3,82 (−4,08) | 0,09 (0,07) | 4,40 (1,99) |
| US den 15→21 (08:00→14:00 NY) | 0,19 (0,07) | −0,88 (−0,61) | 0,34 (0,18) | −1,62 (−0,55) |
| Pozdní US 21→24 (14:00→17:00 NY) | 0,79 (1,08) | −0,30 (−0,53) | 0,08 (0,11) | 1,39 (1,07) |
| Původní C8 long 02→15 | 3,23 (1,40) | −0,85 (−0,70) | 0,94 (0,61) | 6,69 (2,01) |

*Jak číst:* hodnota je průměrný výnos v bazických bodech za den, který by přinesla pozice držená
v daném okně (před náklady); absolutní hodnotu t nad 2 lze brát jako statisticky významné. Čísla se mírně liší od
`DEV_SELECTION.md` (tam asijské okno začíná v 01, zde v 02 – shodně s pravidly C8/C8b). *Co z toho
plyne:*

- **„Den záporný“ z Blose et al. v našich datech není.** Okno americké denní seance (15→21 serveru,
  tj. 08:00–14:00 NY, přibližně seance COMEX) není významné v žádném období (t od −0,61 do 0,18).
- **Asijský kladný drift existoval v letech 2004–2018** (t 2,62 a 3,85), po roce 2019 už není
  významný. **Londýnský pokles byl silný jen v DEV** (−3,82 bp, t −4,08); v holdoutu je londýnské okno
  naopak kladné (+4,40 bp, t 1,99).
- Předregistrované okno C8 (long 02→15) smíchalo asijský růst s londýnským poklesem, a proto bylo
  v DEV mírně záporné už před náklady.
- Velikost efektu (jednotky bp za den) je stejného řádu jako náklady na jeden obchod: medián spreadu
  1,5–2,3 bp plus skluz 0,3 bp na každý market příkaz.

![Intradenní profil XAUUSD: kumulovaný průměrný hodinový výnos podle serverové hodiny (2004–2009, DEV 2010–2018, OOS 2019–2023); zeleně asijská long noha, červeně londýnská short noha C8b](research/results/figures/session_profile.png)

*Jak číst graf:* křivka je kumulovaný průměrný výnos během serverového dne; stoupající úsek znamená,
že zlato v těch hodinách v průměru rostlo. *Co z toho plyne:* modrá křivka (DEV) má výrazný vrchol
kolem 08–09 serveru a pokles během Londýna – právě z ní byla odvozena revize C8b. Oranžová křivka
(OOS 2019–2023) je v asijských i londýnských hodinách téměř plochá: vzor, na kterém C8b stojí,
v OOS zmizel.

### Kontrola na našich datech: kalendářní měsíce [E, vlastní dopočet]

Měsíční logaritmické výnosy z posledního denního close v měsíci (střed bid/ask), 2004-08 až 2026-08.
Rozdělení na roky 2004–2010 (překryv se vzorkem Baura 2013, který končí 2010-12) a 2011–2026 (po
konci jeho vzorku, tedy pro nás out-of-sample).

| Měsíc | 2004–10 Ø % | 2004–10 t | 2011–26 Ø % | 2011–26 t | Celkem Ø % | Celkem t | N (do 2010 / od 2011) |
|---|---|---|---|---|---|---|---|
| leden | 4,14 | 1,72 | 3,45 | 2,82 | 3,64 | 3,38 | 6 / 16 |
| únor | 2,40 | 2,79 | 0,84 | 0,64 | 1,27 | 1,29 | 6 / 16 |
| březen | −1,32 | −1,01 | 0,37 | 0,29 | −0,09 | −0,09 | 6 / 16 |
| duben | 2,15 | 0,90 | 1,38 | 1,40 | 1,59 | 1,69 | 6 / 16 |
| květen | 0,97 | 0,47 | −1,10 | −1,20 | −0,53 | −0,61 | 6 / 16 |
| červen | −0,18 | −0,10 | −1,09 | −0,72 | −0,84 | −0,72 | 6 / 16 |
| červenec | 0,14 | 0,11 | 1,68 | 1,52 | 1,26 | 1,43 | 6 / 16 |
| srpen | 0,18 | 0,10 | 2,68 | 2,44 | 1,92 | 1,99 | 7 / 16 |
| září | 4,34 | 2,51 | −1,70 | −1,21 | 0,22 | 0,18 | 7 / 15 |
| říjen | −0,15 | −0,05 | 1,10 | 1,35 | 0,70 | 0,63 | 7 / 15 |
| listopad | 6,14 | 3,24 | −1,06 | −0,91 | 1,23 | 1,01 | 7 / 15 |
| prosinec | 0,69 | 0,37 | 0,57 | 0,52 | 0,61 | 0,65 | 7 / 15 |

*Jak číst:* „Ø %“ je průměrný měsíční výnos, „t“ jeho t-statistika, poslední sloupec počet let
v každé části. *Co z toho plyne:* **podzimní efekt je v překryvu s Baurovým vzorkem silný** (září
+4,34 %, t 2,51; listopad +6,14 %, t 3,24), ale **po roce 2010 zmizel a obrátil se** (září −1,70 %,
listopad −1,06 %, obojí nevýznamné). To je typický obraz post-publikačního rozpadu anomálie. Silné
hodnoty jiných měsíců (leden, srpen po 2011) nelze brát vážně: při 12 testovaných měsících je
náhodný „významný“ výsledek očekávatelný.

### Co to znamená pro návrh

1. **C8 (session drift)** dostala v scorecardu nejvyšší „vhodnost pro XAUUSD“ (80) a „důkazy“ 65,
   protože jde o recenzovaný, specificky zlatý efekt s nulou laděných parametrů. Současně nejnižší
   „odolnost vůči nákladům“ (40) – přibližně 250 obchodů ročně (ve skutečnosti 503 obchodů ročně,
   protože každý den má dvě nohy) proti efektu v řádu bp. Výběr C8 do předregistrované trojice byl
   sázkou na nejlépe doloženou ne-trendovou anomálii; v DEV selhala (hrubě 0,001 R, čistě −0,018 R).
2. **C8b** (Asie long 02→09, Londýn short 09→15) je **data-driven revize** odvozená z DEV profilu –
   transparentně označená. Hrubý Sharpe v DEV 1,72 a v DEV+OOS 1,26 dokládá skutečnou hrubou anomálii
   v DEV, ale náklady ji pohltí: v DEV+OOS spread 56,5 tis. USD a skluz 17,0 tis. USD proti hrubému
   zisku 58,6 tis. USD, čistě −14,9 tis. USD (`s02_C8b.json`). Podle zadání („strategie fungující jen
   před náklady se zamítá“) byla zamítnuta.
3. **C10 (podzimní sezónnost)** byla vyloučena z testování: 2 obchody ročně (statisticky netestovatelné
   na 16 letech) a měsíční držení mimo mandát. Dodatečná kontrola výše potvrzuje, že vyloučení nic
   neztratilo – efekt po roce 2010 neexistuje.
4. **Víkendový efekt** (Blose & Gondhalekar 2013) se do pravidel nepromítl; trendové strategie drží
   pozice přes víkend a nesou riziko víkendového gapu, které simulátor modeluje plněním stopu na open.

## 5.9 Mean reversion a overreaction

- **Caporale, Plastun (CESifo WP 8445, 2020; *Financial Markets and Portfolio Management*, 2021).**
  Denní ceny zlata a ropy 2009-01-01 až 2019-09-01. V den abnormálního výnosu se cena do konce dne
  pohybuje ve směru abnormálního pohybu (momentum uvnitř dne); **následující den** je u zlata
  kontrariánský efekt (částečný návrat), u ropy pokračování. Typ **[E]**, kvalita **střední**
  (jeden trh, krátký vzorek, pracovní verze i časopisecká publikace).
- **Krátkodobá reverze ve futures obecně** – poznámka scorecardu k C6 („short-term reversal well
  documented in futures“) se neopírá o konkrétní citovanou studii; v tomto dokumentu ji vedeme jako
  **[I]**.
- **Connorsova pravidla RSI(2)** (pullback v dlouhodobém trendu) jsou praktická literatura bez
  recenzovaného ověření na zlatě – **[I/U]**.

*Co to znamená pro návrh:* mean reversion byla zařazena jako **komplementární** rodina k trendu
(vysoký win rate, krátké držení, jiný ekonomický mechanismus – likviditní šoky a přehnané reakce
**[R]**). Kontrariánský efekt Caporale & Plastun je ale jednodenní a podmíněný abnormálním dnem;
pravidla C6 (RSI(2) < 10 v trendu SMA200, držení až 10 dní) jsou jeho volnou analogií – přenos **[I]**.
Proto C6 dostala „důkazy“ jen 50 a „vhodnost pro XAUUSD“ 55. Hodinová reverze C7 dostala ještě méně
(35 a 45) kvůli nákladům a křehké definici „range“ režimu.

*Konfrontace [E, tato studie]:* C6 byla v DEV záporná **už před náklady** (hrubě −0,004 R, čistě
−0,018 R při win rate 64,6 %); C7 výrazně záporná (hrubě −0,067 R, čistě −0,117 R, t −4,35). Na
XAUUSD 2010–2018 tedy krátkodobá reverze v testovaných podobách neexistovala.

## 5.10 Volatility breakout, ORB a momentum po konsolidaci

- **Holmberg, Lönnbark, Lundström (2013, *Finance Research Letters* 10(1):27–33).** Opening Range
  Breakout (vstup, když se cena vzdálí od otevírací ceny o předem daný práh) na futures na ropu
  2001–2011: významně vyšší výnosy než nula a vyšší úspěšnost než „férová hra“. Typ **[E]**, kvalita
  **střední** (jeden trh, jiná komodita, intradenní).
- **ORB na zlatě** – jen diplomová práce (Sönnert, „Intraday momentum – day trading on the gold
  futures market using Opening Range Breakouts and GARCH“). Typ **[E]**, kvalita **nízká**.
- **Li, Sakkas, Urquhart (2022, *Journal of Financial Markets* 57, 100619).** Intradenní TSMOM na
  16 vyspělých akciových trzích: výnos první půlhodiny predikuje výnos poslední půlhodiny ve 12 z 16
  trhů, silněji při nízké likviditě, vysoké volatilitě a diskrétních informacích. Typ **[E]**, kvalita
  **vysoká**, ale **ne zlato** a intradenní horizont.
- **„Squeeze“ (Bollinger bandwidth)** – praktická literatura. Shlukování volatility (po klidu přichází
  pohyb) je robustní stylizovaný fakt **[E]**; že expanze po klidu má predikovatelný **směr**, doloženo
  není **[U]**.

*Co to znamená pro návrh:* volatility breakout (C4, denní OCO bracket close ± 0,5 × ATR14) dostal
„důkazy“ 45 a squeeze (C5) jen 30 – nejméně ze všech pravidlových kandidátů. *Konfrontace [E, tato
studie]:* C4 byla v DEV záporná (−0,036 R; hrubě jen 0,010 R při 77,5 obchodu ročně). C5 měla naopak
nejlepší DEV t-statistiku ze všech (1,40), prošla DEV bránou a dostala se až do finální trojice – ale
v OOS 2019–2023 byla záporná (−0,092 R). Kandidát s nejslabší literární oporou tak měl nejlepší DEV
výsledek a pak selhal mimo vzorek – přesně scénář, před kterým varuje 5.3.

## 5.11 Volatility targeting a sizing

- **Harvey, Hoyle, Korgaonkar, Rattray, Sargaison, Van Hemert (2018, *Journal of Portfolio Management*
  45(1):14–33, „The Impact of Volatility Targeting“).** 60 aktiv, denní data u některých od roku 1926.
  Řízení na cílovou volatilitu zvyšuje Sharpe jen u „rizikových aktiv“ (akcie, kredit), ne systematicky
  u dluhopisů, měn a komodit; u všech ale **zmírňuje levé chvosty**, protože ztrátové extrémy přicházejí
  v obdobích zvýšené volatility, kdy má portfolio menší expozici. Typ **[E]**, kvalita **vysoká**.

*Co to znamená pro návrh:* velikost pozice je ve všech strategiích odvozena od vzdálenosti stopu v ATR
(riziko 0,5 % equity na obchod / (abs(vstup − stop) × 100 oz)). Je to implicitní volatility targeting na
úrovni obchodu: při dvojnásobné volatilitě poloviční objem. Podle Harvey et al. od toho nelze čekat
vyšší výnos u komodity, ale lepší kontrolu ztrátových extrémů – ATR sizing je proto zdůvodněn
**rizikem, ne výnosem [I]**. V scorecardu se to promítlo do kritéria „kompatibilita s risk
managementem“ (strategie s jasným stopem a ATR sizingem 75–85, C11 ML 50).

## 5.12 Metodika proti overfittingu

- **Bailey, Borwein, López de Prado, Zhu (2017, *Journal of Computational Finance* 20(4)).**
  Pravděpodobnost přeučení backtestu (PBO) pomocí kombinatoricky symetrické křížové validace (CSCV):
  jak často konfigurace nejlepší v tréninkové části skončí v testovací části pod mediánem. Typ
  **[E/R]** (metodika), kvalita **vysoká**.
- **Bailey, López de Prado (2014, *Journal of Portfolio Management*).** Deflated Sharpe Ratio (DSR):
  pravděpodobnost, že pozorovaný Sharpe převyšuje očekávané maximum ze N bezcenných pokusů, s korekcí
  na délku vzorku, šikmost a špičatost. Kvalita **vysoká**.
- **Harvey, Liu, Zhu (2016, *Review of Financial Studies* 29(1)).** Při stovkách testovaných faktorů
  (autoři jich katalogizují 316) by hranice významnosti měla být t > 3, ne t > 2. Kvalita **vysoká**.
- **McLean, Pontiff (2016, *Journal of Finance* 71(1):5–32)** – doplněno při přípravě tohoto
  dokumentu, v původní rešerši nebylo. 97 prediktorů průřezu akciových výnosů: výnosy portfolií jsou
  o 26 % nižší mimo původní vzorek a o 58 % nižší po publikaci. Typ **[E]**, kvalita **vysoká**;
  pro nás jde o obecné varování, že publikované anomálie slábnou (akcie, ne zlato).

*Jak se to promítlo do protokolu:* chronologické splity, předregistrace před prvním během, zmrazení
specifikace před holdoutem, deflated Sharpe a PBO pro každého plně validovaného kandidáta.

*Konfrontace [E, tato studie]:* s N = 60 konfiguracemi je očekávaný maximální roční Sharpe z
bezcenných pokusů 1,46 (`s02_*.json`, `dsr_full.sr0_annual`). Pozorované roční Sharpe DEV+OOS jsou
0,25 (C3), 0,22 (C2), 0,17 (C5) a 0,24 (C9), takže DSR vychází prakticky nulový. V mírnější variantě
(N = 125 bodů vlastní perturbační mřížky, variance Sharpe uvnitř mřížky) je DSR 0,39 (C3), 0,53 (C2),
0,30 (C5) a 0,55 (C9) (`dsr_within_grid.json`) – stále daleko od 0,95. PBO: 0,47 (C3), 0,70 (C2),
0,24 (C5), 0,55 (C9). Souhrnné t-statistiky 2004–2026 (1,12–1,71) nedosahují ani klasické hranice 2,
natož hranice 3 podle Harvey, Liu, Zhu.

## 5.13 Nevěrohodná a nepodložená tvrzení

### Singha, Aguilera-Toste, Lahiri (2025, arXiv 2511.08571)

„Forecast-to-Fill: Benchmark-Neutral Alpha and Billion-Dollar Capacity in Gold Futures (2015–2025)“.
Podle abstraktu: walk-forward s 10letým tréninkem a 6měsíčním testem, 2 793 obchodních dní;
vyhlazený trend-momentum signál převedený na pozice s volatility targetingem, frakčním Kellyho
sizingem a ATR výstupy. Out-of-sample **Sharpe 2,88, maximální drawdown 0,52 %**, po nákladech
0,7 bp a odmocninovém dopadu; CAGR 43 % při cílové volatilitě 15 %, beta 0,03; kapacita kolem
1 mld. USD. Typ **[U]**, kvalita **nevěrohodná**. Proč:

1. **Rozpor s ostatní evidencí:** krátkodobý trend na portfoliu ~100 futures měl podle Kurth et al.
   Sharpe kolem 0,8 před rokem 2009 a zhruba nulu po něm; na jediném small-tick kontraktu je
   Sharpe 2,88 z jednoduchých signálů krajně nepravděpodobný **[I]**.
2. **Vnitřní nekonzistence [E, vlastní dopočet]:** při volatilitě 15 % ročně je denní směrodatná
   odchylka 0,945 %. Pro nezávislé normálně rozdělené denní výnosy s CAGR 43 % a volatilitou 15 % by
   zhruba 24 % dní samo o sobě ztratilo víc než 0,52 % (tj. kolem 674 z 2 793 dní). Simulace 20 000
   cest po 2 793 dnech dává medián maximálního drawdownu 14,2 % (1. percentil 9,5 %) a **žádná
   z 20 000 cest neměla drawdown ≤ 0,52 %**. Udávaná kombinace výnosu, volatility a drawdownu je tedy
   neslučitelná, pokud výnosy nejsou extrémně nenormální nebo pokud volatilita není výrazně nižší, než
   se uvádí.
3. Studie nebyla použita k ničemu – ani jako podpora trendu, ani jako benchmark.

### Další tvrzení se slabou oporou

- **„London bias“** (praktici, 5.8) – **[I/U]**; v našich datech londýnský pokles existoval jen v
  DEV 2010–2018.
- **„Zlato roste v krizi“** jako obchodovatelný denní signál – **[U]** (5.5).
- **Inverzní asymetrie volatility jako důvod slabší long strany breakoutů** – původně **[I]**, po
  kontrole na našich datech **[U]** (5.5).
- **Populární retailové strategie** (SMC/ICT, order blocks, ručně kreslené úrovně, Elliottovy vlny)
  nemají v recenzované literatuře žádnou oporu a zadání je vylučuje (kapitola 6).

## 5.14 Broker dokumentace a praktické parametry

- **RoboForex – specifikace XAUUSD (účty Pro/Standard).** 1 lot = 100 oz, minimální objem 0,01 lotu,
  krok 0,01; swap long −60 / short +19 bodů, trojitý swap ve středu; ECN účty s komisí. Typ **[E]**
  (dokumentace), kvalita **střední** – platí pro jednoho brokera a jeden okamžik.
- **MQL5 – dokumentace Python integrace MetaTrader 5.** `symbol_info` (`trade_contract_size`,
  `volume_min`, `volume_step`, `filling_mode`), `order_send`, režimy plnění FOK/IOC. Typ **[E]**,
  kvalita **vysoká** (oficiální dokumentace).

*Co to znamená pro návrh:* nákladový model počítá se swapem long −(3M T-bill + 2,25 % p.a.) a short
+(3M T-bill − 2,25 % p.a.), kalibrovaným na typický retailový swap 2024–2025; přirážka 2,25 % je
**[U]** pro historická období (historické swapy brokerů nejsou k dispozici). Sizing se zaokrouhluje
**dolů** na krok 0,01 lotu, adaptér MT5 čte velikost kontraktu, krok objemu a režim plnění ze
`symbol_info`. U vícedenních longů je swap významná nákladová položka (např. C5 DEV+OOS: swap
−6,3 tis. USD při spreadu 6,3 tis. a skluzu 2,5 tis. USD). Někteří brokeři účtují trojitý swap na
kovy v pátek místo ve středu **[I]** – je nutné ověřit u konkrétního brokera.

## 5.15 Souhrnná tabulka tvrzení

| Tvrzení | Typ | Zdroj (rok) | Důsledek pro XAUUSD swing |
|---|---|---|---|
| TSMOM 1–12 měsíců funguje napříč 58 trhy | [E] | Moskowitz, Ooi, Pedersen (2012) | Trend je nejlépe doložená rodina; horizont je ale měsíční, přenos na H4 jen [I] |
| Trend ziskový 1880–2016, crisis alpha | [E] | Hurst, Ooi, Pedersen (2017) | Na H4 se crisis alpha nepřenesla: při VIX > 25 záporná expectancy všech trendových variant |
| MA a kanály ziskové ve většině komodit | [E] | Szakmary, Shen, Sharma (2010) | Podpora C2 a C3; měsíční data |
| MA timing robustní na portfoliích, nekonzistentní na jednotlivých futures | [E] | Han, Hu, Yang (2016) | Jeden instrument = slabší případ, nižší očekávání |
| TSMOM a MA crossover jsou ekvivalentní filtry | [E/R] | Levine, Pedersen (2016) | C2, C3, C5 jsou jedna sázka; C3 nahrazena v předregistraci C6 |
| Body obratu snižují výnos trendu | [E] | Goulding, Harvey, Mazzoleni (2024) | Režimy s vysokou volatilitou a obraty jsou hlavní riziko |
| Technická analýza zisková zhruba do 90. let, studie trpí data-snoopingem | [E] | Park, Irwin (2007) | Pevné literaturní parametry, předregistrace, skromná očekávání |
| Po korekci na data-snooping timing v komoditách neziskový | [E] | Marshall, Cahan, Cahan (2008) | Korekce na počet testů (DSR, PBO) |
| Standardní intradenní MA na drahých kovech bez síly; některé kombinace u zlata ano | [E] | Batten et al. (2018) | Varování před laděním parametrů; perturbační mřížky |
| Krátkodobý trend po 2009 mrtvý na small-tick kontraktech | [E – preprint] | Kurth, Eisler, Rej, Bouchaud (2026) | Zlato je small-tick [I] (tick 0,18–0,96 % denní σ); negativní apriorní důkaz, horizont H4 místo H1 |
| Zlato je safe haven pro USA a Evropu | [E] | Baur, McDermott (2010) | V denním měřítku jen slabý přístav; v krizi vyšší volatilita, trend ztrácí |
| Inverzní asymetrie volatility zlata | [E] | Baur (2012) | Na našich datech 2004–2026 nepotvrzeno; úsudek o long whipsawech přeřazen na [U] |
| Reálná cena zlata souvisí s reálnými sazbami, zlato nespolehlivý inflační hedge | [E/R] | Erb, Harvey (2013) | Makro filtry založené na úrovních jsou riskantní |
| Vztah zlato–reálné výnosy se po 2022 rozpadl | [E/I] | J.P. Morgan PB, Janus Henderson | U nás korelace úrovní s nominálním 10Y −0,857 → +0,506; C9 penalizována a v OOS selhala |
| Centrální banky nakupují přes 1 000 t ročně (2022–2024) | [E] | World Gold Council | Nový režim poptávky; holdout 2024–26 nelze číst jako potvrzení edge |
| Makro zprávy hýbou zlatem během minut, dobré zprávy = zlato dolů | [E] | Elder, Miao, Ramchander (2012) | Exekuční riziko (gapy, skluz stopů), ne swingový signál |
| Overnight výnosy zlata kladné, denní záporné | [E] | Blose, Gondhalekar, Kort (2018) | Podklad pro C8; u nás „den záporný“ neprokázán, C8 v DEV nulová před náklady |
| Asijské hodiny nahoru, Londýn/NY dolů | [I/U] | praktici (goldpriceforecast, FXStreet 2026) | Asijský drift jen do 2018, londýnský pokles jen v DEV; C8b zamítnuta |
| Víkendové výnosy nižší, hlavně v medvědích trzích | [E] | Blose, Gondhalekar (2013) | Nevyužito; víkendový gap modelován v simulaci |
| Září a listopad významně kladné | [E] | Baur (2013) | Po 2010 efekt zmizel; C10 vyloučena (2 obchody ročně) |
| Den po abnormálním pohybu kontrariánský efekt u zlata | [E] | Caporale, Plastun (2020/2021) | Volná podpora C6; C6 v DEV záporná už před náklady |
| ORB ziskový na ropě 2001–2011 | [E] | Holmberg et al. (2013) | Slabá podpora C4; C4 v DEV záporná |
| Intradenní TSMOM na 16 akciových trzích | [E] | Li, Sakkas, Urquhart (2022) | Ne zlato; jen nepřímá podpora breakout logiky |
| Volatility targeting nezvyšuje Sharpe komodit, snižuje levé chvosty | [E] | Harvey et al. (2018) | ATR sizing zdůvodněn rizikem, ne výnosem |
| PBO, DSR, t > 3 při mnoha testech | [E/R] | Bailey et al. (2017), Bailey, López de Prado (2014), Harvey, Liu, Zhu (2016) | Žádný kandidát nedosáhl DSR 0,95 ani t > 2 |
| Publikované anomálie slábnou o 26–58 % | [E] | McLean, Pontiff (2016) | Očekávej slábnutí; podzimní a session efekt na zlatě se po publikaci rozpadly |
| Sharpe 2,88 a max DD 0,52 % z jednoduchého trendu na zlatě | [U] | Singha et al. (2025) | Nevěrohodné, vnitřně nekonzistentní; nepoužito |
| 1 lot = 100 oz, krok 0,01, swap −60/+19 bodů | [E] | RoboForex, MQL5 | Kalibrace nákladů a sizingu; swapová přirážka historicky [U] |

*Jak číst:* jeden řádek = jedno tvrzení, jeho typ a hlavní důsledek pro náš návrh. *Co z toho
plyne:* literatura dává nejsilnější oporu trendu, ale v jiném horizontu a pro portfolia trhů; všechny
gold-specifické anomálie (session, sezónnost, mean reversion po šocích) mají kratší vzorky a na našich
navazujících datech se neudržely.

## 5.16 Literatura jako post-publikační test: co se na XAUUSD udrželo

Řada citovaných studií končí svůj vzorek dříve, než začínají naše data DEV/OOS. Náš backtest je pro ně
tedy skutečným testem mimo vzorek (jiný instrument nebo jiné období). Přehled:

| Efekt | Zdroj (konec vzorku) | Naše navazující období | Výsledek u nás |
|---|---|---|---|
| Time-series momentum (měsíční) | Moskowitz et al. (2009) | 2010–2026 | Denní TSMOM C1 v DEV −0,002 R; H4 trend slabě kladný (Sharpe 0,27–0,40 souhrnně) |
| Overnight kladný, den záporný | Blose et al. (2012) | 2013–2026 | Den (08–14 NY) nevýznamný ve všech obdobích; asijský drift po 2019 nevýznamný |
| Podzimní efekt | Baur (2010) | 2011–2026 | Září −1,70 %, listopad −1,06 % (nevýznamné); efekt zmizel |
| Zlato a reálné výnosy (úrovně) | Erb, Harvey (publikace 2013, konec vzorku neověřen) | 2022–2026 | Korelace úrovní s nominálním 10Y +0,506 místo záporné |
| Kontrariánský efekt po abnormálním dni | Caporale, Plastun (2019) | překryv 2010–2019 | C6 (volná analogie) v DEV záporná před náklady |
| Inverzní asymetrie volatility | Baur (publikace 2012, období neověřeno) | 2004–2026 | Nepotvrzeno; klasická asymetrie ve 3 ze 4 období |
| Krátkodobý trend mrtvý na small-tick | Kurth et al. (2025) | překryv 2004–2025 | Nelze nezávisle ověřit (vzorky se překrývají); H4 trend slabě kladný |

*Jak číst:* sloupec „konec vzorku“ je poslední rok dat původní studie (u Moskowitz et al. 2009, u
Blose et al. 2012 atd.); kde konec vzorku neznáme, je uveden rok publikace. *Co z toho plyne:* **žádný gold-specifický kalendářní ani intradenní efekt se
po konci původního vzorku na XAUUSD neudržel.** Jediný směr, který zůstal slabě kladný, je trend –
tedy efekt s nejširší a nejstarší evidencí napříč trhy. To je v souladu s McLean & Pontiff i s
Park & Irwin a je to nejdůležitější poučení z rešerše pro další vývoj.

## 5.17 Jak se rešerše promítla do scorecardu a výběru

| Kritérium scorecardu | Hlavní literatura, která ho ovlivnila | Kandidáti nejvíce dotčení |
|---|---|---|
| Důkazy | Moskowitz et al., Hurst et al., Szakmary et al., Kurth et al., Blose et al., Baur (2013) | C1 85 (nejvíc), C2 65 (sníženo kvůli Kurth et al.), C8 65, C5 30 (jen praktici) |
| Ekonomické zdůvodnění | TSMOM mechanismy, Erb & Harvey, Blose et al. | trend a C9 70, C10 35 (sezónnost bez mechanismu) |
| Robustnost napříč režimy | Goulding et al., rozpad zlato–sazby po 2022 | C9 40, C4 40, C7 35 |
| Odolnost vůči overfittingu | Park & Irwin, Marshall et al., Batten et al., Bailey et al. | C8 85 (nula laděných parametrů), C5 45, C7 45, C11 10 |
| Odolnost vůči nákladům | Elder et al., Kurth et al. (cena exekuce), broker dokumentace | C8 40, C7 35, C4 45 |
| Vhodnost pro XAUUSD | Blose et al., Baur & McDermott, Erb & Harvey | C8 80 (specificky zlato), C7 45 |
| Kompatibilita s risk managementem | Harvey et al. (2018) | strategie s ATR stopem 75–85, C11 50 |

*Jak číst:* tabulka ukazuje, odkud se v scorecardu vzala apriorní informace. *Co z toho plyne:*
literatura určila hlavně **pořadí rodin** (trend > session > mean reversion > breakout > ML) a
**penalizaci složitosti**. Kapitola 6 ukazuje, že apriorní skóre nakonec výsledky v DEV
nepředpověděla (pořadová korelace 0,17 na 9 kandidátech) – literatura je dobrá k vymezení hypotéz,
ne k předpovědi, která konkrétní varianta projde.

## 5.18 Co literatura nepokrývá (mezery)

1. **Swingový horizont 4 h – 10 dní na spotovém XAUUSD.** Recenzovaná evidence je buď měsíční (TSMOM),
   nebo intradenní (ORB, session, makro zprávy). Horizont, pro který systém stavíme, je mezi nimi téměř
   prázdný.
2. **Retailové CFD náklady.** Swapové přirážky, rozšiřování spreadu kolem denního rolloveru (v našich
   datech mediánový spread v serverové hodině 00 19,08 bp a v hodině 23 6,21 bp, ve zbytku dne
   1,85–2,31 bp; `data_quality.json`), rozdíly mezi brokery – akademická literatura je nepokrývá vůbec.
3. **Režim po roce 2022.** Poptávka centrálních bank a rozpad vztahu k reálným sazbám jsou zdokumentovány
   jen v institucionálních komentářích, bez recenzovaných studií o dopadu na systematické strategie.
4. **Asymetrie long/short u trendu na zlatě** – literatura ji nezkoumá; naše data ukazují, že je režimová.
5. **Interakce trendu s makro zprávami na H4** – netestováno v literatuře ani u nás.
6. **Small-tick hypotéza pro OTC spot** – Kurth et al. pracují s burzovními futures; přenos na spotový
   XAUUSD u retailového brokera je **[I]**.
7. **Alternativní data** – implikovaná volatilita (GVZ), pozice spekulantů (COT), toky ETF, intermarket
   (stříbro, AUD, těžaři): nebyla rešeršována do hloubky ani testována.
8. **Replikace po publikaci** – pro gold-specifické anomálie (session, sezónnost, víkend) jsme
   nenašli nezávislé replikace; naše kontroly v 5.8 naznačují rozpad.
9. **Crisis alpha v krátkém horizontu** – evidence je měsíční; pro dny až týdny chybí.

## 5.19 Omezení rešerše

- **Plné texty nedostupné** (arXiv, SSRN, RePEc a další blokovány síťovou politikou sandboxu).
  Použity abstrakty, souhrny vyhledávače a sekundární texty. Abstrakty zjednodušují; čísla ze
  sekundárních souhrnů (např. 84 % vs. 3 % u J.P. Morgan, nákupy centrálních bank) mohou být
  nepřesně interpretována (korelace vs. R²).
- **Kurth et al. (2026)** je preprint bez recenze; přesná definice velikosti ticku, práh i zařazení
  zlata nejsou ověřeny. Jeho vzorek (1995–2025) se překrývá s naším, takže nejde o nezávislý důkaz
  vůči našemu testu.
- **Narativní, ne systematický přehled.** Rešerše nesledovala formální protokol (např. předem daná
  vyhledávací hesla a kritéria zařazení), takže může trpět výběrem známých a anglicky psaných zdrojů.
- **Riziko hindsight biasu výzkumníka [U].** Obecný vývoj trhu zlata do roku 2026 (včetně býčího trhu
  2024–2026) byl znám; zmrazení specifikace chrání pravidla, ne volbu rodiny strategií.
- **Vlastní kontroly v této kapitole** (tick/volatilita, VIX, asymetrie volatility, korelace s makrem,
  intradenní okna, měsíce) jsou deskriptivní, vznikly po dokončení výzkumu, nebyly předregistrovány a
  neovlivnily výběr. Testy t nejsou korigovány na autokorelaci ani heteroskedasticitu a na počet
  souběžných testů.

> **Závěr:** Literatura podporuje trend/momentum jako jedinou rodinu s širokou, starou a replikovanou
> evidencí – ale pro měsíční horizont a portfolia trhů, ne pro swing na jednom small-tick instrumentu,
> kde novější evidence (Kurth et al. 2026) naznačuje zánik krátkodobého trendu. Všechny gold-specifické
> anomálie, které vypadaly jako komplementární zdroje edge (session drift, podzimní sezónnost,
> kontrariánská reakce), se na navazujících datech XAUUSD neudržely. Výsledek „slabý H4 trend,
> nic dalšího“ je proto s literaturou konzistentní a neměl by překvapit.

*Zdrojové soubory: `REPORT.md` (kap. 3, 17, 23, 24 – seznam zdrojů a původní rešerše);
`research/scorecard.py` a `research/results/scorecard.md` (skóre a poznámky); `research/PROTOCOL.md`;
`research/DEV_SELECTION.md`; `research/results/data_quality.json` (spready); `research/results/s01_dev_screen.json`
(DEV výsledky C1–C9, C8b); `research/results/s02_C3.json`, `s02_C2.json`, `s02_C5.json`, `s02_C9.json`,
`s02_C8b.json` (režimy, timeframy, zpoždění, náklady, DSR); `research/results/dsr_within_grid.json`;
`research/results/s03_portfolio.md` a `s03_portfolio_C2_C3_C5_C9.md` (shoda směru, korelace C2/C9);
`research/results/s05_pooled.json`; `research/results/figures/session_profile.png`; vlastní dopočty
z `data/processed/A_*.parquet`, `B_*.parquet` a `macro_daily.parquet` přes `research/common.py`
(`stitched`, `macro`) – tick vs. volatilita, VIX a asymetrie volatility, korelace s USD/10Y/VIX,
intradenní okna, měsíční sezónnost, Monte Carlo kontrola tvrzení Singha et al.; literární údaje
z abstraktů a vyhledávacích souhrnů dohledaných 2026-10-05.*
