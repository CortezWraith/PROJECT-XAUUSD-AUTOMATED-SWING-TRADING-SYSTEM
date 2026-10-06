# 10. Plná validace vybraných strategií (DEV+OOS 2010–2023)

Tato kapitola je jádrem empirické části. Pro pět strategií, které prošly výběrem po DEV (kapitola 9),
uvádí **všechny výstupy plné validace** ze skriptu `research/s02_validate.py` (commit `cfe78c3`, tedy
před zmrazením specifikace a před holdoutem). Holdout 2024–2026 se v této kapitole nevyhodnocuje
(kapitola 12). Ke každé tabulce je krátký komentář „jak číst“ a „co z toho plyne“. Na konci každé
podkapitoly je celkové hodnocení strategie a na konci kapitoly srovnání všech pěti.

**Proč právě těchto pět.** Předregistrovaný výběr C2, C8 a C6 na DEV neuspěl: C6 i C8 byly záporné už
před náklady a C2 těsně neprošla bránou 1 (PF 1,094 místo > 1,10). Podle pravidla náhrady zapsaného
v `research/DEV_SELECTION.md` před OOS postoupili kandidáti, kteří bránu 1 splnili, seřazení podle DEV
t-statistiky: **C5** (t 1,40), **C9** (t 1,15) a **C3** (t 0,86). Navíc byly transparentně
validovány **C2** jako předregistrovaná reference trendové rodiny a **C8b** jako jediná ne-momentum
anomálie se silným hrubým efektem („cost-conditional“, tedy podmíněná náklady). Podkapitoly jsou
seřazeny podle zmrazeného pořadí (`research/frozen_spec.json`): C3, C2, C5, potom vyřazená C9
a zamítnutá C8b.

**Společné nastavení všech běhů.** Účet 100 000 USD, riziko 0,5 % equity na obchod (equity
rebasovaná na začátku měsíce), baseline náklady (reálný bid/ask, skluz 0,3 / 1,0 bp, komise 0, modelový
swap), jedna pozice na strategii. PRE-SAMPLE 2004-07 – 2009-12 běží jen na datech B (bid + modelový
spread), DEV 2010–2018 na spojené řadě (B do 2016-08-31, A od 2016-09-01), OOS 2019–2023 čistě na A
s reálným bid/ask. Signály se počítají z mid cen na uzavřeném baru, plnění je na open dalšího baru,
stopy se vyhodnocují na H1 granularitě. Definice metrik jsou v kapitole 0.5, statistické nástroje
v kapitole 4.8, brány v kapitole 4.3.

**Co se testovalo a proč.** Každá strategie prošla stejnou sadou testů ve stejném pořadí:

| Test | Co přesně | K čemu slouží | Brána |
|---|---|---|---|
| Segmenty | PRE 2004–2009, DEV 2010–2018, OOS 2019–2023 a spojené DEV+OOS 2010–2023 | stabilita v čase; PRE je zpětný out-of-sample test na datech, která výzkum nepoužil | 1, 2 |
| Long vs. short | samostatné běhy jen s long a jen se short obchody (DEV, OOS, DEV+OOS) | zda edge nestojí jen na jednom směru, tedy na betě k trendu zlata | pravidlo pro směr |
| Nákladový stres | hrubě ×0, baseline ×1, ×1,5, ×2 a ECN scénář (spread ×0,5 + komise 3,5 USD/lot/strana), DEV+OOS i OOS | ekonomická rezerva vůči horšímu brokerovi | 3 |
| Zpoždění vstupu | fill o jeden H1 bar později; navíc skluz ×3 | závislost na rychlosti a kvalitě exekuce | — |
| Perturbace | plná mřížka 5 × 5 × 5 = 125 kombinací (±25 % kolem defaultu), u C5 a C9 jednorozměrné řezy (OAT), PBO metodou CSCV | zda edge nezávisí na přesné hodnotě parametru a zda výběr podle tréninku má hodnotu | 4 |
| Timeframe | H2, H3, H4, H6 (a D1) s délkami přepočtenými na stejný reálný čas | zda efekt není artefakt jedné mřížky barů | — |
| Walk-forward | 10 foldů: 4 roky trénink, 1 rok test (2014–2023), výběr z mřížky 3 × 3 podle tréninkového Sharpe | realistický proces pravidelné rekalibrace | 5 |
| Bootstrap | 10 000× převzorkování obchodů (riziko 0,5 %) a 5 000× blokový bootstrap denních výnosů (bloky 20 dní) | statistická nejistota expectancy, drawdownu a doby zotavení | 7 |
| Režimy | ex-ante štítky ke dni vstupu (trend, volatilita, USD, sazby, VIX) | ve kterém prostředí strategie ztrácí | — |
| Roky a bloky | čistý PnL po letech (rok výstupu) a po 3letých blocích | koncentrace zisku do jednoho období | 6 |
| Deflated Sharpe | PSR a DSR pro N = 60 (konzervativně) a N = 125 (v rámci mřížky) | korekce na počet vyzkoušených variant | — |
| Brány 1–7 | souhrn předregistrovaných podmínek | rozhodnutí „robustní kandidát ano / ne“ | 1–7 |

Jak číst tabulku: každý řádek je jeden blok, který se v podkapitolách opakuje ve stejném pořadí.
Sloupec „Brána“ říká, který blok přímo rozhoduje o které předregistrované bráně. Co z toho plyne:
validace nehledá nejlepší variantu, ale zkouší zlomit pevnou, předem zapsanou specifikaci z mnoha
nezávislých úhlů. Strategie je „robustní kandidát“ jen tehdy, když přežije všechny.

**Několik konvencí pro čtení tabulek.** Expectancy (Exp. R) je průměrný čistý výsledek obchodu
v násobcích rizika, sloupec „t“ je její t-statistika (pro konvenční významnost by měla být
alespoň kolem 2). PF se počítá z USD. Sharpe a Sortino jsou anualizované z denních výnosů. CAGR
a MaxDD jsou malé, protože riziko 0,5 % na obchod je konzervativní; výsledky v R na sizingu nezávisí.
„Pod vodou (dny)“ je nejdelší doba v kalendářních dnech mezi dvěma maximy equity. Ve sloupci
„Náklady / hrubý“ je podíl explicitních nákladů (spread + skluz + komise + záporný swap) na hrubém
PnL téhož běhu. Celkový dopad nákladů je ale větší, protože s bid/ask exekucí se mění i samotná cesta
obchodů (dřívější zásahy stopů na bid/ask, odklady vstupů spread guardem, jiná velikost pozic). Proto
u každé strategie uvádím i rozklad „bezfrikční čistý PnL → baseline čistý PnL“ na přímou a nepřímou
část [E, vlastní dopočet z `s02_<K>.json`].

**Kontext trhu.** Pro výklad ročních tabulek je užitečné vědět, co dělalo zlato [E, vlastní dopočet
z `data/processed` přes `research/common.py`, mid close D1 spojené řady]:

| Rok | Zdroj | Close na konci roku (USD) | Změna za rok | Max. denní close | Min. denní close | Volatilita p. a. |
|---|---|---|---|---|---|---|
| 2010 | B | 1 408,3 | +28,3 % | 1 423,2 | 1 062,7 | 16,1 % |
| 2011 | B | 1 564,6 | +11,1 % | 1 900,1 | 1 313,6 | 20,1 % |
| 2012 | B | 1 675,0 | +7,1 % | 1 790,6 | 1 538,6 | 14,6 % |
| 2013 | B | 1 208,4 | −27,9 % | 1 692,5 | 1 190,1 | 21,5 % |
| 2014 | B | 1 186,9 | −1,8 % | 1 382,4 | 1 141,6 | 14,3 % |
| 2015 | B | 1 060,9 | −10,6 % | 1 301,8 | 1 051,9 | 13,7 % |
| 2016 | B → A | 1 151,4 | +8,5 % | 1 365,4 | 1 074,8 | 15,6 % |
| 2017 | A | 1 302,9 | +13,1 % | 1 349,2 | 1 159,0 | 10,0 % |
| 2018 | A | 1 282,6 | −1,6 % | 1 358,4 | 1 174,2 | 9,7 % |
| 2019 | A | 1 517,5 | +18,3 % | 1 552,2 | 1 270,9 | 11,3 % |
| 2020 | A | 1 898,4 | +25,1 % | 2 063,5 | 1 471,2 | 19,1 % |
| 2021 | A | 1 829,5 | −3,6 % | 1 950,1 | 1 683,7 | 13,3 % |
| 2022 | A | 1 823,9 | −0,3 % | 2 050,3 | 1 622,5 | 14,9 % |
| 2023 | A | 2 062,9 | +13,1 % | 2 077,8 | 1 811,1 | 13,2 % |

Jak číst tabulku: volatilita je anualizovaná směrodatná odchylka denních log-výnosů (√252). Pro
PRE-SAMPLE: close 2004-07-02 byl 397,8 USD a 2009-12-31 1 097,6 USD. Co z toho plyne: DEV obsahuje
býčí fázi do 2011–2012, výrazný medvědí trh 2013–2015 a klidné roky 2017–2018 s nejnižší volatilitou.
OOS obsahuje silný růst 2019–2020 (včetně krize v březnu 2020), dva roky bez směru 2021–2022
a růst v roce 2023. Trendové strategie by tedy měly mít příležitosti v obou směrech; to, že short strany v DEV
vydělávaly a long strany v OOS, je do velké míry dáno právě tímto sledem režimů [I].

## 10.1 C3 EMA trend H4

C3 je **#1 zmrazeného pořadí** pro další zkoumání. Do plné validace postoupila jako třetí náhradník
(DEV t 0,86), tedy s nejslabší DEV statistikou z trojice C5, C9, C3. Na první místo se dostala ne
díky nejvyššímu výnosu, ale díky nejvyrovnanějšímu profilu napříč testy (kapitola 15).

### Rekapitulace pravidel

- **Data a timeframe:** H4 bary z mid cen ((bid + ask) / 2), ukotvené na serverovou půlnoc (NY+7).
- **Indikátory:** EMA(20) a EMA(100) z close; ATR(20) jako prostý průměr true range; `hc` a `lc` =
  nejvyšší a nejnižší close posledních 20 barů.
- **Vstup long:** EMA20 překříží EMA100 nahoru (stav +1, předchozí stav ≤ 0). **Vstup short:**
  zrcadlově. Vstupuje se jen na čerstvém crossu, když strategie nemá pozici.
- **Počáteční stop:** close ∓ 3,0 × ATR20.
- **Trailing stop:** long max(stávající stop, hc − 3 × ATR20), short min(stávající stop, lc + 3 × ATR20);
  stop se posouvá jen ve směru snížení rizika.
- **Výstup:** zásah stopu nebo opačný stav EMA (signál na close, fill na open dalšího baru). Žádný
  take-profit, žádný time-stop. Při opačném crossu se pozice jen zavře; opačná pozice vznikne až při
  dalším čerstvém crossu (`EmaTrend.on_bar`).
- **Parametry:** 4 (fast 20, slow 100, atr_n 20, stop_atr 3,0), všechny literaturní default.

Jak strategie fakticky vystupuje [E, vlastní dopočet, DEV+OOS]: z 256 obchodů skončilo 238 zásahem
(většinou trailing) stopu s průměrem +0,082 R a jen 18 opačným crossem s průměrem −0,214 R. C3 je tedy
v praxi „vstup na crossu EMA + výstup ATR trailing stopem“. Cross jako výstup nastává jen u obchodů,
které se nerozvinuly.

### Segmenty

| Segment | Obchody | Obch./rok | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF |
|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 107 | 19,4 | 37,4 | 1,11 | −0,56 | 0,064 | 0,63 | 1,18 |
| DEV 2010–2018 | 163 | 18,1 | 35,0 | 1,16 | −0,51 | 0,074 | 0,85 | 1,22 |
| OOS 2019–2023 | 93 | 18,6 | 34,4 | 1,07 | −0,51 | 0,038 | 0,38 | 1,12 |
| DEV+OOS 2010–2023 | 256 | 18,3 | 34,8 | 1,13 | −0,51 | 0,061 | 0,93 | 1,18 |

Jak číst tabulku: tři horní řádky jsou navzájem nezávislá období, čtvrtý je spojený běh DEV+OOS.
Co z toho plyne: C3 je **kladná ve všech třech nezávislých obdobích** a profil obchodů je velmi
stabilní (win rate 34–37 %, průměrný zisk 1,07–1,16 R, průměrná ztráta kolem −0,5 R) [E]. OOS je zhruba
poloviční proti DEV (0,038 vs. 0,074 R), což je běžná degradace. Žádný segment ale není sám o sobě
statisticky významný (t 0,38–0,93). Průměrná ztráta −0,51 R místo −1 R ukazuje, že trailing stop
většinu ztrátových obchodů ukončí dřív, než dojdou k počátečnímu stopu [I]. Důležitá je i křížová
kontrola zdrojů dat za 2016-09 – 2018-12 (kapitola 7, `s01_dev_screen.md`): C3 dala na datech A
0,200 R a na datech B 0,189 R, tedy prakticky totéž. U breakout variant (C2, C5, C9) byla data B
výrazně optimističtější než A, u C3 ne. DEV výsledek C3 tak nejméně závisí na tom, že do 2016-08 běží
na datech B [E].

| Segment | Sharpe | Sortino | CAGR | MaxDD | Calmar | Expozice | Ø držení h | Medián h | Max. série ztrát | Pod vodou (dny) |
|---|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 0,26 | 0,42 | 0,61 % | 3,7 % | 0,17 | 30 % | 132 | 95 | 11 | 762 |
| DEV 2010–2018 | 0,31 | 0,51 | 0,65 % | 3,7 % | 0,18 | 28 % | 133 | 110 | 12 | 1 045 |
| OOS 2019–2023 | 0,16 | 0,27 | 0,36 % | 7,4 % | 0,05 | 26 % | 120 | 101 | 11 | 1 595 |
| DEV+OOS 2010–2023 | 0,25 | 0,41 | 0,53 % | 7,4 % | 0,07 | 27 % | 128 | 104 | 12 | 1 666 |

Jak číst tabulku: rizikové a časové charakteristiky stejných běhů. Co z toho plyne: Sharpe 0,25 za
14 let a nejdelší období pod vodou 1 666 dní (přes 4,5 roku) ukazují, že i kdyby edge byl skutečný,
v praxi by znamenal dlouhá období bez nového maxima. Strategie je v trhu jen asi čtvrtinu času,
průměrně drží 128 hodin (zhruba 5 dní včetně víkendů), což odpovídá mandátu 4 h – 10 dní. MaxDD 7,4 %
přišel v OOS; nejdelší série ztrát byla 12 obchodů.

| Segment | Hrubý PnL | Spread | Skluz | Swap | Čistý PnL | Náklady / hrubý | Obch. L / S | Long PnL | Short PnL |
|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 5 569 | 599 | 383 | −1 187 | 3 401 | 39 % | 53 / 54 | 6 443 | −3 043 |
| DEV 2010–2018 | 9 739 | 1 104 | 711 | −1 942 | 5 981 | 39 % | 79 / 84 | −70 | 6 051 |
| OOS 2019–2023 | 3 762 | 663 | 409 | −893 | 1 797 | 52 % | 47 / 46 | −460 | 2 258 |
| DEV+OOS 2010–2023 | 13 586 | 1 806 | 1 145 | −2 892 | 7 743 | 43 % | 126 / 130 | −581 | 8 324 |

Jak číst tabulku: PnL v USD na účtu 100 000 USD, komise je v baseline nulová. Co z toho plyne:
náklady berou 39–52 % hrubého zisku a **největší položkou je swap**, ne spread [E]. Je to důsledek
vícedenního držení: v letech s 3M T-bill pod 2,25 % platí podle modelu swap obě strany. Rozložení zisku
podle směru je nápadné: v DEV i OOS vydělala jen short strana, v PRE naopak jen long strana. Celý čistý
zisk 2010–2023 (7 743 USD) pochází ze shortů (8 324 USD), longy skončily mírně ve ztrátě.

### Long vs. short

| Strana / segment | Obchody | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF | Sharpe | Čistě % kapitálu | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|---|
| long DEV | 88 | 31,8 | 1,00 | −0,49 | −0,015 | −0,15 | 0,95 | −0,05 | −0,7 % | 121 |
| long OOS | 49 | 28,6 | 1,21 | −0,51 | −0,020 | −0,14 | 0,95 | −0,04 | −0,5 % | 104 |
| long DEV+OOS | 137 | 30,7 | 1,07 | −0,50 | −0,017 | −0,21 | 0,95 | −0,05 | −1,2 % | 115 |
| short DEV | 87 | 35,6 | 1,28 | −0,50 | 0,131 | 1,00 | 1,40 | 0,36 | 5,6 % | 135 |
| short OOS | 49 | 38,8 | 0,96 | −0,49 | 0,070 | 0,53 | 1,24 | 0,22 | 1,7 % | 133 |
| short DEV+OOS | 136 | 36,8 | 1,16 | −0,50 | 0,109 | 1,14 | 1,34 | 0,31 | 7,4 % | 134 |

Jak číst tabulku: každý řádek je samostatný běh, ve kterém je povolen jen jeden směr. Součet obchodů
(137 + 136 = 273) je vyšší než 256 v kombinovaném běhu, protože v něm opačný cross jen zavírá otevřenou
pozici a nový vstup čeká na další cross. Co z toho plyne: v letech 2010–2023 měla C3 kladnou
expectancy **jen na short straně** (+0,109 R, t 1,14), long strana byla v DEV i OOS mírně záporná [E].
Předregistrované pravidlo pro směr („směr, který samostatně neprojde branami 1–2, se vypne“) by
doslovně neprošla ani jedna strana: long selhal už na bráně 1 (DEV −0,015 R), short prošel bránou 1,
ale ne bránou 2 (OOS Sharpe 0,22 < 0,3) [E, vlastní dopočet]. Protože neprošla ani strategie jako
celek, pravidlo se do produkční specifikace nepromítlo a zmrazená specifikace ponechává obě strany.
Že to bylo správně, naznačuje holdout 2024–2026, kde se poměr obrátil (kapitola 12): asymetrie směrů
u C3 sleduje režim zlata (medvědí trh 2013–2015 přál shortům), ne trvalou vlastnost pravidla [I].

### Nákladový stres

| Scénář | D+O obch. | D+O exp. R | D+O PF | D+O Sharpe | D+O CAGR | D+O MaxDD | OOS exp. R | OOS PF | OOS Sharpe | OOS CAGR | OOS MaxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | 256 | 0,108 | 1,34 | 0,42 | 0,95 % | 6,6 % | 0,093 | 1,30 | 0,36 | 0,84 % | 6,6 % |
| baseline ×1,0 | 256 | 0,061 | 1,18 | 0,25 | 0,53 % | 7,4 % | 0,038 | 1,12 | 0,16 | 0,36 % | 7,4 % |
| stres ×1,5 | 256 | 0,041 | 1,12 | 0,17 | 0,35 % | 8,1 % | 0,018 | 1,06 | 0,08 | 0,17 % | 7,8 % |
| stres ×2,0 | 256 | 0,021 | 1,06 | 0,09 | 0,18 % | 8,9 % | −0,002 | 1,00 | 0,01 | −0,01 % | 8,3 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | 256 | 0,084 | 1,26 | 0,33 | 0,74 % | 7,1 % | 0,071 | 1,22 | 0,28 | 0,63 % | 7,1 % |

Jak číst tabulku: „D+O“ = DEV+OOS 2010–2023, vpravo totéž jen pro OOS 2019–2023. Stres násobí spread,
skluz, komisi i swapovou přirážku (kapitola 4.4). Co z toho plyne: C3 **splňuje bránu 3** s rezervou
(×1,5: +0,041 R) a zůstává kladná i při ×2 za DEV+OOS (+0,021 R). V samotném OOS je ale ×2 už na nule
(−0,002 R). ECN účet s polovičním spreadem a komisí by výsledek zlepšil na 0,084 R. Každý přírůstek
nákladů o 0,5 násobku ubírá zhruba 0,02 R na obchod.

| Scénář | Období | Hrubý PnL | Spread | Skluz | Komise | Swap | Čistý PnL | Náklady / hrubý |
|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | DEV+OOS | 14 079 | 0 | 0 | 0 | 0 | 14 079 | 0 % |
| hrubě ×0 | OOS | 4 238 | 0 | 0 | 0 | 0 | 4 238 | 0 % |
| baseline ×1,0 | DEV+OOS | 13 586 | 1 806 | 1 145 | 0 | −2 892 | 7 743 | 43 % |
| baseline ×1,0 | OOS | 3 762 | 663 | 409 | 0 | −893 | 1 797 | 52 % |
| stres ×1,5 | DEV+OOS | 13 620 | 2 658 | 1 686 | 0 | −4 287 | 4 989 | 63 % |
| stres ×1,5 | OOS | 3 827 | 985 | 608 | 0 | −1 382 | 852 | 78 % |
| stres ×2,0 | DEV+OOS | 13 970 | 3 489 | 2 215 | 0 | −5 652 | 2 614 | 81 % |
| stres ×2,0 | OOS | 3 922 | 1 297 | 803 | 0 | −1 859 | −37 | 101 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | DEV+OOS | 14 224 | 919 | 581 | 455 | −1 470 | 10 798 | 24 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | OOS | 4 302 | 337 | 206 | 135 | −439 | 3 185 | 26 % |

Jak číst tabulku: rozklad v USD; hrubý PnL je mid-to-mid výsledek obchodů tak, jak proběhly v daném
scénáři. Co z toho plyne: při ×2 náklady spotřebují 81 % hrubého zisku DEV+OOS a v OOS celý. Swap je
ve všech scénářích největší jednotlivou položkou. Rozklad celkového dopadu nákladů [E, vlastní dopočet]:
bezfrikční čistý PnL 14 079 USD klesne na 7 743 USD (o 45 %); z rozdílu 6 335 USD připadá 5 842 USD na
explicitní náklady a jen asi 490 USD na nepřímý vliv (jiná cesta obchodů). C3 je tedy vůči exekučním
detailům málo citlivá, protože její trailing stop leží daleko od ceny (3 ATR).

### Zpoždění vstupu

| Varianta | Obchody | Exp. R | Změna R | Změna % | PF | Sharpe | CAGR | MaxDD |
|---|---|---|---|---|---|---|---|---|
| baseline (fill na open dalšího baru) | 256 | 0,0611 | — | — | 1,18 | 0,25 | 0,53 % | 7,4 % |
| zpoždění +1 H1 bar | 255 | 0,0555 | −0,0055 | −9 % | 1,16 | 0,23 | 0,49 % | 7,6 % |
| zpoždění +1 H1 bar a skluz ×3 | 255 | 0,0378 | −0,0232 | −38 % | 1,10 | 0,15 | 0,31 % | 8,3 % |

Jak číst tabulku: expectancy je zde na čtyři desetinná místa, aby byl rozdíl čitelný. Co z toho
plyne: hodinové zpoždění vstupu stojí jen 0,0055 R (−9 %). Křížení EMA na H4 není časově kritický
signál, latence MT5 ani výpadek na desítky minut výsledek podstatně nezmění [E]. Trojnásobný skluz
(0,9 / 3,0 bp) je dražší než samotné zpoždění, ale strategie zůstává kladná.

### Perturbace parametrů

| Ukazatel | Hodnota |
|---|---|
| Počet bodů mřížky | 125 |
| Podíl bodů s exp. R > 0 (brána 4) | 90,4 % |
| Podíl bodů s PF > 1 | 89,6 % |
| Sharpe p10 / medián / p90 | 0,01 / 0,15 / 0,34 |
| Exp. R min / p10 / medián / p90 / max | −0,031 / 0,004 / 0,037 / 0,089 / 0,119 |
| Podíl bodů se Sharpe > 0,3 | 12,8 % |
| Počet obchodů min / max | 205 / 366 |
| MaxDD min / medián / max | 5,4 % / 8,8 % / 11,0 % |
| PBO (CSCV, roční bloky) | 0,47 |
| Počet rozdělení CSCV / medián logitu | 3 432 / 0,16 |
| Default: podíl bodů mřížky s nižší exp. R / nižším Sharpe | 71 % / 73 % |
| 26 nejbližších sousedů defaultu: podíl exp. R > 0 / medián exp. R | 100 % / 0,062 |
| Nejlepší bod (exp. R) | fast 17, slow 115, stop_atr 2,625: 0,119 R, Sharpe 0,44 |
| Nejhorší bod (exp. R) | fast 17, slow 85, stop_atr 2,25: −0,031 R, Sharpe −0,13 |
| Nejvyšší Sharpe | fast 17, slow 115, stop_atr 2,625: Sharpe 0,44, 0,119 R |

Jak číst tabulku: mřížka fast {15, 17, 20, 23, 25} × slow {75, 85, 100, 115, 125} × stop_atr
{2,25; 2,625; 3,0; 3,375; 3,75}, vše DEV+OOS. Řádky od „Exp. R min“ níže a řádky o defaultu a sousedech
jsou vlastní dopočet z `grid_C3.csv`; „26 sousedů“ jsou všechny body o jeden krok v libovolné ose.
Co z toho plyne: **brána 4 je splněna** (90 % bodů kladných) a všech 26 bezprostředních sousedů defaultu
je kladných [E]. Default není vybraný vrchol, leží na 71. percentilu mřížky. Záporných je 12 bodů a
všechny leží na okraji: 10 z nich má krátké slow (75 nebo 85) a současně extrémní stop (2,25 nebo
3,75), zbylé dva fast 23–25 se slow 115 a stopem 3,75. Jen 12,8 % bodů má Sharpe nad 0,3, tedy nad
úrovní požadovanou v OOS bráně 2. PBO 0,47 s mediánem logitu 0,16 znamená, že nejlepší konfigurace
z tréninkové poloviny let skončí v testovací polovině nad mediánem jen o málo častěji než v polovině
případů. Výběr parametrů podle minulosti tedy nemá prokazatelnou hodnotu, ale ani neškodí [I].

| Osa | Hodnota | Medián exp. R | Medián PF | Medián Sharpe | Medián MaxDD | Medián obchodů |
|---|---|---|---|---|---|---|
| fast (EMA) | 15 | 0,034 | 1,09 | 0,14 | 8,3 % | 289 |
| fast (EMA) | 17 | 0,062 | 1,16 | 0,24 | 8,0 % | 272 |
| fast (EMA) | 20 | 0,036 | 1,10 | 0,16 | 8,5 % | 256 |
| fast (EMA) | 23 | 0,040 | 1,09 | 0,14 | 8,9 % | 245 |
| fast (EMA) | 25 | 0,035 | 1,09 | 0,15 | 9,1 % | 237 |
| slow (EMA) | 75 | 0,027 | 1,07 | 0,12 | 8,6 % | 309 |
| slow (EMA) | 85 | 0,026 | 1,06 | 0,11 | 9,6 % | 285 |
| slow (EMA) | 100 | 0,058 | 1,16 | 0,22 | 8,8 % | 256 |
| slow (EMA) | 115 | 0,058 | 1,18 | 0,25 | 8,2 % | 235 |
| slow (EMA) | 125 | 0,044 | 1,11 | 0,16 | 8,3 % | 226 |
| stop_atr | 2,25 | 0,021 | 1,04 | 0,08 | 8,6 % | 263 |
| stop_atr | 2,625 | 0,045 | 1,11 | 0,18 | 8,0 % | 259 |
| stop_atr | 3 | 0,058 | 1,16 | 0,23 | 8,1 % | 256 |
| stop_atr | 3,375 | 0,052 | 1,15 | 0,22 | 10,0 % | 254 |
| stop_atr | 3,75 | 0,017 | 1,04 | 0,08 | 9,8 % | 251 |

Jak číst tabulku: každý řádek je medián přes 25 bodů mřížky s danou hodnotou jedné osy (sloupce
„Medián MaxDD“ a „Medián obchodů“ jsou vlastní dopočet z `grid_C3.csv`). Co z toho plyne: osa fast je
plochá (kromě mírně lepší hodnoty 17), osa slow ukazuje lepší výsledky pro delší EMA (100–125) než pro
75–85 a osa stop_atr má tvar obráceného U s vrcholem kolem 3,0 ATR, tedy právě na literaturním
defaultu. Velmi těsný stop (2,25) je vystopován šumem, velmi široký (3,75) vrací příliš zisku [I].
Delší slow EMA snižuje počet obchodů (309 → 226) a tím i náklady.

![Perturbační mřížka C3: medián expectancy (R) podle fast × slow, medián přes pět hodnot stop_atr, DEV+OOS 2010–2023](research/results/figures/grid_C3.png)

Jak číst obrázek: každé pole je medián expectancy přes pět hodnot stop_atr pro danou dvojici fast
× slow; zelená je kladná, červená záporná, škála ±0,2 R. Co z toho plyne: povrch je **mělké kladné
plato** (0,00 až 0,10 R) bez osamocené špičky. Nejlepší oblast je slow 115 s fast 15–20 a slow 125
s fast 15–17 (0,08–0,10 R), slabší pás je slow 75–85 (0,00–0,05 R). Default (fast 20, slow 100: 0,06 R)
leží uprostřed plata, ne na jeho okraji.

### Timeframe

| TF | Parametry | Obchody | Exp. R | t | PF | Sharpe | CAGR | MaxDD | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|
| H2 | fast 40, slow 200, ATR 40 | 263 | 0,020 | 0,25 | 1,04 | 0,07 | 0,15 % | 7,2 % | 64 |
| H3 | fast 27, slow 133, ATR 27 | 256 | 0,032 | 0,44 | 1,08 | 0,12 | 0,26 % | 8,0 % | 99 |
| H4 | fast 20, slow 100, ATR 20 (default) | 256 | 0,061 | 0,93 | 1,18 | 0,25 | 0,53 % | 7,4 % | 128 |
| H6 | fast 13, slow 67, ATR 13 | 248 | 0,013 | 0,21 | 1,03 | 0,06 | 0,11 % | 10,6 % | 173 |
| D1 | fast 3, slow 17, ATR 3 | 166 | 0,039 | 0,77 | 1,19 | 0,17 | 0,22 % | 4,4 % | 449 |

Jak číst tabulku: délky v barech jsou přepočtené tak, aby odpovídaly stejnému reálnému času (počet
barů za serverový den: H2 12, H3 8, H4 6, H6 4, D1 1); stop v násobcích ATR je stejný. Co z toho plyne:
**všech pět timeframů je kladných**, efekt tedy není artefakt H4 mřížky [E]. Velikost efektu ale
kolísá: H4 je nejlepší a H6 i H2 dávají jen 0,013–0,020 R. Protože H4 byl zvolen předem z literatury
a ne podle tohoto testu, nejde o výběr, ale výsledek naznačuje, že část H4 výsledku je štěstí konkrétní
mřížky [I]. D1 varianta s EMA 3/17 a ATR(3) je fakticky jiná, mnohem pomalejší strategie (držení
449 h).

### Walk-forward

| Test | Trénink | Vybrané parametry | Train Sharpe | Test výnos | Default výnos | Rozdíl p. b. |
|---|---|---|---|---|---|---|
| 2014 | 2010–2013 | fast 15, slow 125, stop_atr 3 | 0,67 | 0,8 % | 0,6 % | 0,2 |
| 2015 | 2011–2014 | fast 15, slow 125, stop_atr 3 | 0,74 | −0,2 % | 0,4 % | −0,6 |
| 2016 | 2012–2015 | fast 15, slow 125, stop_atr 3 | 0,62 | 3,4 % | 2,3 % | 1,1 |
| 2017 | 2013–2016 | fast 15, slow 125, stop_atr 3 | 0,82 | 2,4 % | 2,5 % | −0,1 |
| 2018 | 2014–2017 | fast 15, slow 125, stop_atr 3 | 0,71 | −1,0 % | −1,6 % | 0,5 |
| 2019 | 2015–2018 | fast 15, slow 125, stop_atr 3 | 0,51 | −0,8 % | −0,1 % | −0,7 |
| 2020 | 2016–2019 | fast 15, slow 125, stop_atr 3 | 0,43 | −2,8 % | −3,1 % | 0,3 |
| 2021 | 2017–2020 | fast 25, slow 75, stop_atr 3 | −0,18 | 1,3 % | 0,6 % | 0,6 |
| 2022 | 2018–2021 | fast 25, slow 75, stop_atr 3 | −0,18 | −1,8 % | −0,9 % | −0,9 |
| 2023 | 2019–2022 | fast 25, slow 75, stop_atr 3 | −0,24 | 6,3 % | 5,3 % | 1,0 |

Jak číst tabulku: v každém foldu se z mřížky fast {15, 20, 25} × slow {75, 100, 125} (stop_atr pevně
3,0) vybere konfigurace s nejvyšším Sharpe za 4 předchozí roky a její výnos se změří v testovacím roce.
„Default výnos“ je výnos pevné konfigurace 20/100 v témže roce, sloupec „Rozdíl“ je vlastní dopočet.
Co z toho plyne: spojený walk-forward výnos je **+7,4 %** (Sharpe 0,31, kladných 5 z 10 let), **brána 5
je splněna**. Spojený výnos pevného defaultu za stejných 10 let je +6,1 % [E, vlastní dopočet],
walk-forward byl lepší v 6 z 10 let. Přínos výběru je tedy zhruba 1,3 procentního bodu za 10 let, což
je v rámci šumu. Zajímavá je stabilita volby: sedm let po sobě vyhrála stejná konfigurace 15/125
(nejširší rozestup EMA). Od 2021 byl nejlepší tréninkový Sharpe záporný, takže všech devět konfigurací
mělo v oknech 2017–2020 až 2019–2022 záporný Sharpe [E]. Výběr „nejméně špatné“ varianty pak nemá
vypovídací hodnotu.

### Bootstrap

| Metrika (trade bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| CAGR | −0,42 % | 0,51 % | 1,55 % |
| Expectancy R | −0,044 | 0,058 | 0,172 |
| Profit factor | 0,87 | 1,18 | 1,56 |
| Max drawdown | 3,5 % | 6,1 % | 11,4 % |
| Nejdelší série ztrát (obchody) | 8 | 11 | 17 |
| Nejdelší úsek pod maximem (obchody) | 45 | 109 | 243 |

Jak číst tabulku: 10 000× vylosováno 256 obchodů s vracením z empirického rozdělení R, equity
složena jako součin (1 + 0,005 × R). P(expectancy > 0) = **82,2 %**. Co z toho plyne: **brána 7
(≥ 90 %) splněna není**. 90% interval expectancy (−0,044 až 0,172 R) zahrnuje nulu. Pro plánování
rizika jsou důležitější ostatní řádky: medián nejdelší série ztrát je 11 obchodů a v 5 % scénářů 17
a víc. Medián nejdelšího úseku pod maximem je 109 obchodů, což při 18,3 obchodu ročně odpovídá asi
6 letům; p95 243 obchodů znamená zhruba 13 let [E, vlastní dopočet]. MaxDD v 95 % scénářů nepřekročí
11,4 % při riziku 0,5 % na obchod.

| Metrika (blokový bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| Sharpe | −0,21 | 0,23 | 0,65 |
| CAGR | −0,46 % | 0,48 % | 1,46 % |
| Max drawdown | 3,9 % | 6,7 % | 12,3 % |

Jak číst tabulku: 5 000× poskládaná řada denních výnosů z náhodných 20denních bloků, které zachovávají
krátkodobou autokorelaci a shluky volatility. P(Sharpe > 0) = **80,7 %**. Co z toho plyne: blokový
bootstrap dává prakticky stejný obraz jako bootstrap obchodů. Sharpe v intervalu −0,21 až 0,65 je
slučitelný jak s nulovým, tak se slušným edge. MaxDD v p95 (12,3 %) je o něco vyšší než u nezávislých
obchodů, protože bloky zachovávají shlukování ztrát [I].

### Režimy

| Dimenze | Stav | Obchody | Exp. R | Win % | PF | Long exp. R | Short exp. R | Denní Sharpe |
|---|---|---|---|---|---|---|---|---|
| trend | range (bez trendu) | 203 | 0,079 | 36,9 | 1,24 | 0,008 | 0,154 | 0,42 |
| trend | trending | 53 | −0,007 | 26,4 | 0,98 | −0,103 | 0,056 | −0,23 |
| volatilita | vysoká | 125 | −0,114 | 28,0 | 0,67 | −0,090 | −0,137 | −0,32 |
| volatilita | nízká | 131 | 0,228 | 41,2 | 1,72 | 0,068 | 0,381 | 0,70 |
| USD (60 d) | silný USD | 146 | 0,118 | 36,3 | 1,37 | 0,049 | 0,199 | 0,49 |
| USD (60 d) | slabý USD | 110 | −0,014 | 32,7 | 0,96 | −0,110 | 0,057 | −0,08 |
| výnosy 10Y (60 d) | klesající | 118 | 0,069 | 34,7 | 1,23 | 0,004 | 0,135 | 0,19 |
| výnosy 10Y (60 d) | rostoucí | 138 | 0,054 | 34,8 | 1,15 | −0,022 | 0,126 | 0,30 |
| VIX | krize (VIX > 25) | 34 | −0,158 | 29,4 | 0,53 | −0,443 | 0,018 | −0,63 |
| VIX | normál | 222 | 0,095 | 35,6 | 1,29 | 0,040 | 0,152 | 0,38 |

Jak číst tabulku: obchod dostane štítek podle dne vstupu, štítky používají jen data do předchozího
dne. Trending = abs(ln(C(t) / C(t−60))) / (σ60 × √60) > 1, vysoká volatilita = σ20 nad 252denním mediánem,
USD a sazby podle 60denní změny, krize = VIX > 25. Denní Sharpe se počítá ze všech dní s daným štítkem
(včetně pozic otevřených dříve). Co z toho plyne: **hlavní režim selhání je vysoká volatilita
(−0,114 R) a krize (−0,158 R)**, kde whipsawy a rozšířené stopy berou edge [E]. V nízké volatilitě je
C3 výrazně kladná (+0,228 R, PF 1,72). Překvapivé je, že C3 vydělává v režimu „range“ a ne v režimu
„trending“. EMA cross totiž typicky vstupuje na začátku nového trendu po předchozím klidu, ne uprostřed
zavedeného trendu [I]. Pozor na malé vzorky (krize 34 obchodů) a na to, že se dimenze překrývají:
z 531 krizových dní 2010–2023 je 390 (73 %) zároveň dny vysoké volatility, při základním podílu
45 % [E, vlastní dopočet z `research/stats.py` `regime_frame`]. Při deseti srovnáních na strategii by
filtr postavený na této tabulce byl další data-mining [I].

### Roky a bloky

| Rok | Segment | Obchody | Exp. R | Čistý PnL | Long PnL | Short PnL | Kumulativně |
|---|---|---|---|---|---|---|---|
| 2010 | DEV | 19 | −0,162 | −1 457 | 146 | −1 603 | −1 457 |
| 2011 | DEV | 16 | 0,148 | 1 107 | 1 145 | −38 | −350 |
| 2012 | DEV | 16 | 0,010 | 84 | −1 405 | 1 489 | −266 |
| 2013 | DEV | 17 | 0,226 | 1 845 | −305 | 2 150 | 1 579 |
| 2014 | DEV | 18 | 0,075 | 632 | −1 629 | 2 260 | 2 211 |
| 2015 | DEV | 17 | 0,003 | −2 | −274 | 273 | 2 209 |
| 2016 | DEV | 21 | 0,258 | 2 776 | 1 199 | 1 577 | 4 985 |
| 2017 | DEV | 14 | 0,123 | 848 | −31 | 879 | 5 833 |
| 2018 | DEV | 25 | 0,012 | 149 | 1 084 | −936 | 5 981 |
| 2019 | OOS | 19 | −0,007 | −91 | −682 | 591 | 5 890 |
| 2020 | OOS | 22 | −0,297 | −3 282 | −2 627 | −655 | 2 609 |
| 2021 | OOS | 15 | 0,087 | 629 | −33 | 661 | 3 237 |
| 2022 | OOS | 18 | −0,099 | −904 | 70 | −974 | 2 334 |
| 2023 | OOS | 19 | 0,563 | 5 410 | 2 760 | 2 650 | 7 743 |

Jak číst tabulku: obchod patří do roku svého výstupu, PnL v USD, sloupec „Kumulativně“ je vlastní
dopočet. Co z toho plyne: kladných je 9 ze 14 let, ale **největší rok 2023 přinesl 5 410 USD, tedy
70 % celkového čistého zisku** (brána 6 vyžaduje ≤ 50 %). Bez roku 2023 by za 14 let zbylo 2 334 USD
[E, vlastní dopočet]. Nejhorší rok 2020 (−3 282 USD) připadl na rok, kdy zlato vzrostlo o 25 %: březnový
krach a prudké obraty kolem COVID krize vystopovaly longy i shorty (krizový režim v tabulce výše) [I].
Kumulativní zisk po maximu na konci roku 2018 čtyři roky klesal a nové maximum přinesl až
rok 2023. Brána 6 je u strategií s malým celkovým ziskem přísná, protože jeden dobrý rok snadno
převýší polovinu malého součtu. Selhání je ale věcné: bez
jednoho roku je výsledek OOS záporný.

| Blok | Obchody | Exp. R | PF | Čistý PnL |
|---|---|---|---|---|
| 2010–2012 | 51 | −0,011 | 0,97 | −266 |
| 2013–2015 | 52 | 0,101 | 1,27 | 2 475 |
| 2016–2018 | 60 | 0,124 | 1,38 | 3 772 |
| 2019–2021 | 56 | −0,096 | 0,74 | −2 744 |
| 2022–2023 | 37 | 0,241 | 1,87 | 4 506 |

Jak číst tabulku: tříleté bloky, poslední je dvouletý. Co z toho plyne: tři z pěti bloků jsou kladné,
blok 2019–2021 je zřetelně záporný (−0,096 R). Výsledek C3 tedy není rovnoměrně rozložený, střídají se
víceletá dobrá a špatná období. To je u trendových systémů typické, ale pro důvěru v edge nepříznivé [I].

### Deflated Sharpe a PSR

| Varianta | N | T (dní) | SR (anual.) | SR0 (anual.) | PSR (SR > 0) | DSR |
|---|---|---|---|---|---|---|
| DEV+OOS, N = 60 (konzervativní) | 60 | 3 605 | 0,25 | 1,46 | 0,83 | 0,00 |
| jen OOS, N = 60 | 60 | 1 290 | 0,15 | 1,46 | 0,64 | 0,00 |
| DEV+OOS, N = 125 (v rámci mřížky) | 125 | 3 605 | 0,25 | 0,32 | 0,83 | 0,39 |

Jak číst tabulku: PSR je pravděpodobnost, že skutečný Sharpe je kladný (bez korekce na počet pokusů).
DSR porovnává pozorovaný Sharpe s očekávaným maximem SR0 z N bezcenných pokusů. Konzervativní varianta
bere rozptyl Sharpe deseti heterogenních kandidátů DEV screeningu (SR0 1,46), mírnější varianta
rozptyl uvnitř perturbační mřížky C3 (SR0 0,32, `dsr_within_grid.json`). Co z toho plyne: PSR 0,83
říká, že kladný Sharpe je pravděpodobnější než ne, ale po korekci na výběr je DSR 0,00, resp. 0,39,
daleko pod konvenční hranicí 0,95. **Pozorovaný Sharpe 0,25 je slučitelný s tím, že jde o nejlepší
výsledek z mnoha bezcenných pokusů** [E]. Statistická síla je zásadní problém: při Sharpe 0,25 roste
t-statistika přibližně jako 0,25 × √(počet let), takže k t = 2 by bylo potřeba asi 65 let dat [I,
vlastní dopočet (2 / 0,249)²].

### Brány

| Brána | Podmínka | Hodnota | Splněno |
|---|---|---|---|
| 1 | DEV: exp. R > 0 a PF > 1,10 | exp. 0,074 R, PF 1,221 | ANO |
| 2 | OOS: exp. R > 0, PF > 1,05, Sharpe > 0,3 | exp. 0,038 R, PF 1,12, Sharpe 0,16 | NE |
| 3 | náklady ×1,5: exp. R DEV+OOS > 0 | 0,041 R | ANO |
| 4 | ≥ 70 % bodů mřížky s exp. R > 0 | 90 % | ANO |
| 5 | walk-forward spojený výsledek > 0 | 7,4 % | ANO |
| 6 | žádný rok > 50 % čistého zisku | 70 % | NE |
| 7 | bootstrap P(exp. R > 0) ≥ 90 % | 82,2 % | NE |
| Vše | brány 1–7 současně | splněno 4 ze 7 | NE |

Jak číst tabulku: hodnoty jsou přímo z `s02_C3.json`, ANO / NE podle předregistrovaných prahů. Co
z toho plyne: C3 splňuje brány, které měří **odolnost** (náklady, parametry, rekalibrace), a selhává na
branách, které měří **stabilitu v čase a statistickou jistotu** (OOS Sharpe, koncentrace, bootstrap).
Robustním kandidátem podle protokolu není.

### Celkové hodnocení C3

> **Závěr:** C3 je nejvyrovnanější člen trendové rodiny. Je kladná ve všech třech nezávislých obdobích
> (PRE, DEV, OOS), na mělkém plató parametrů (90 % mřížky kladné, všech 26 sousedů defaultu kladných),
> na všech pěti timeframech, při nákladech ×2 (DEV+OOS) a je necitlivá na zpoždění vstupu. Efekt je ale
> malý (+0,061 R, Sharpe 0,25, t 0,93), statisticky nerozlišitelný od nuly (bootstrap 82 %, DSR 0,00 /
> 0,39), závislý na jednom roce (2023 = 70 % zisku) a v letech 2010–2023 nesený výhradně short stranou.
> Splnila 4 ze 7 bran. Důvěra: **nízká**. Proč přesto #1: ze všech kandidátů má nejméně slabých míst,
> která by ukazovala na přeučení (PBO 0,47, default uprostřed plata, nejmenší citlivost na exekuci).

Typ důkazu: výsledky segmentů, nákladů, mřížky a bootstrapu jsou [E]; vysvětlení, proč C3 selhává
ve vysoké volatilitě a proč vydělává v režimu „range“, jsou [I]; ekonomické zdůvodnění trendu
(pomalá difúze makro informací, hedging pressure, stádní chování) je [R] a rozebírá ho kapitola 5.

## 10.2 C2 Donchian H4

C2 je **předregistrovaná volba #1** a **#2 zmrazeného pořadí**. Na DEV těsně neprošla bránou 1
(PF 1,094), proto byla validována jen jako transparentní reference trendové rodiny bez nároku na
označení „robustní“. Má nejlepší historický výsledek za celé období 2004–2026 (kapitola 13), ale
v DEV byla nejslabší z trendových variant.

### Rekapitulace pravidel

- **Data a timeframe:** H4 bary z mid cen, ukotvené na serverovou půlnoc.
- **Indikátory:** HH55 / LL55 = nejvyšší high / nejnižší low **předchozích** 55 barů (asi 9,5 obchodního
  dne, bez aktuálního baru); XH20 / XL20 = totéž pro 20 barů (asi 3,5 dne); ATR(20).
- **Vstup long:** close > HH55. **Vstup short:** close < LL55. Jen bez otevřené pozice, nový vstup
  vyžaduje nové proražení.
- **Počáteční stop:** close ∓ 2,0 × ATR20 (Turtle „2N“).
- **Trailing:** stop se posouvá na XL20 (long) / XH20 (short), pokud je těsnější.
- **Výstup:** zásah stopu, close pod XL20 / nad XH20, nebo time-stop po 90 barech (15 obchodních dní).
- **Parametry:** 5 (entry_n 55, exit_n 20, atr_n 20, stop_atr 2,0, max_hold 90), Turtle System 2 default.

Jak strategie fakticky vystupuje [E, vlastní dopočet, DEV+OOS]: 355 ze 373 obchodů skončilo zásahem
stopu (převážně posunutého na výstupní kanál) s průměrem −0,044 R a součtem −15,6 R. Jen 18 obchodů
(5 %) skončilo signálem (close za výstupním kanálem nebo time-stop), ale s průměrem +2,55 R a součtem
+45,9 R. **Celý čistý výsledek C2 (+30,3 R) tedy nese 18 dlouhých trendových obchodů.** To je klasický
profil breakoutu: mnoho malých ztrát, vzácné velké výhry. Výsledek je proto velmi závislý na tom, zda
v daném období několik takových trendů nastane.

### Segmenty

| Segment | Obchody | Obch./rok | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF |
|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 146 | 26,5 | 33,6 | 2,62 | −0,85 | 0,316 | 1,60 | 1,54 |
| DEV 2010–2018 | 241 | 26,8 | 32,4 | 1,99 | −0,86 | 0,064 | 0,56 | 1,09 |
| OOS 2019–2023 | 132 | 26,4 | 28,8 | 2,45 | −0,86 | 0,094 | 0,46 | 1,14 |
| DEV+OOS 2010–2023 | 373 | 26,7 | 31,4 | 2,13 | −0,86 | 0,081 | 0,79 | 1,13 |

Jak číst tabulku: stejné segmenty jako u C3. Co z toho plyne: C2 je **kladná ve všech třech
nezávislých obdobích** [E]. Nejsilnější je PRE 2004–2009 (+0,316 R, t 1,60), které nebylo použito
k vývoji. Šlo ale o silný býčí trh (397,8 → 1 097,6 USD), ve kterém breakout systémy vydělávají
snadno [I]. OOS (+0,094 R) je jako u jediné strategie lepší než DEV (+0,064 R), díky jedinému roku 2020
(níže). Profil obchodu se liší od C3: nižší win rate (31 %), ale průměrný zisk 2,13 R proti ztrátě
−0,86 R. Ztráty jsou blíž plnému riziku, protože počáteční stop 2 ATR je těsnější než 3 ATR u C3.
Křížová kontrola zdrojů za 2016-09 – 2018-12 (kapitola 7) dala C2 na datech A 0,056 R a na datech B
0,115 R. Data B jsou pro breakout zhruba dvakrát optimističtější, takže DEV výsledek C2 do 2016-08
je spíš horní odhad [E/I].

| Segment | Sharpe | Sortino | CAGR | MaxDD | Calmar | Expozice | Ø držení h | Medián h | Max. série ztrát | Pod vodou (dny) |
|---|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 0,82 | 1,33 | 4,13 % | 8,3 % | 0,50 | 52 % | 176 | 137 | 7 | 506 |
| DEV 2010–2018 | 0,19 | 0,31 | 0,83 % | 8,5 % | 0,10 | 46 % | 152 | 132 | 8 | 1 489 |
| OOS 2019–2023 | 0,26 | 0,41 | 1,19 % | 13,5 % | 0,09 | 44 % | 142 | 118 | 8 | 1 239 |
| DEV+OOS 2010–2023 | 0,22 | 0,35 | 1,00 % | 13,4 % | 0,07 | 45 % | 149 | 125 | 8 | 1 489 |

Jak číst tabulku: rizikové a časové charakteristiky. Co z toho plyne: C2 je v trhu téměř polovinu času
(45 %) a drží v průměru 149 hodin (přes 6 dní). Má vyšší CAGR než C3 (1,00 % vs. 0,53 %), ale za cenu
skoro dvojnásobného MaxDD (13,4 %). Calmar je u obou stejně nízký (0,07). Nejdelší období pod vodou
1 489 dní (přes 4 roky) připadá na DEV. Realizovaná nejdelší série ztrát (8) je kratší než u C3 (12), i když
C2 má nižší win rate. Jde spíš o štěstí konkrétní cesty, bootstrap níže dává medián 13 obchodů [I].

| Segment | Hrubý PnL | Spread | Skluz | Swap | Čistý PnL | Náklady / hrubý | Obch. L / S | Long PnL | Short PnL |
|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 31 852 | 1 297 | 818 | −4 827 | 24 909 | 22 % | 83 / 63 | 34 398 | −9 489 |
| DEV 2010–2018 | 15 840 | 2 473 | 1 594 | −5 042 | 6 731 | 58 % | 131 / 110 | −251 | 6 983 |
| OOS 2019–2023 | 11 337 | 1 483 | 910 | −3 247 | 5 697 | 50 % | 73 / 59 | 12 770 | −7 073 |
| DEV+OOS 2010–2023 | 29 740 | 4 077 | 2 578 | −8 648 | 14 437 | 51 % | 204 / 169 | 15 072 | −635 |

Jak číst tabulku: PnL v USD. Co z toho plyne: **swap (−8 648 USD) je největší nákladová položka**
a spolu se spreadem a skluzem bere 51 % hrubého zisku DEV+OOS [E]. Důvodem je dlouhé držení (expozice
45 %). Směrová skladba se mezi segmenty obrací: v PRE vydělal long (+34 398 USD) a short ztrácel, v DEV
vydělal short a long byl na nule, v OOS opět long (+12 770 USD) a short ztrácel (−7 073 USD). Za celé
DEV+OOS je zisk prakticky celý z longů.

### Long vs. short

| Strana / segment | Obchody | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF | Sharpe | Čistě % kapitálu | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|---|
| long DEV | 131 | 31,3 | 1,83 | −0,81 | 0,014 | 0,09 | 1,01 | 0,06 | 0,4 % | 154 |
| long OOS | 73 | 30,1 | 3,23 | −0,87 | 0,362 | 1,08 | 1,57 | 0,60 | 13,4 % | 152 |
| long DEV+OOS | 204 | 31,4 | 2,30 | −0,83 | 0,151 | 0,97 | 1,25 | 0,29 | 15,1 % | 154 |
| short DEV | 110 | 33,6 | 2,17 | −0,92 | 0,124 | 0,70 | 1,19 | 0,21 | 6,4 % | 150 |
| short OOS | 59 | 27,1 | 1,37 | −0,84 | −0,238 | −1,39 | 0,61 | −0,51 | −6,6 % | 131 |
| short DEV+OOS | 169 | 31,4 | 1,93 | −0,89 | −0,003 | −0,02 | 0,99 | 0,00 | −0,7 % | 143 |

Jak číst tabulku: samostatné běhy jen s jedním směrem; součet obchodů (204 + 169) odpovídá
kombinovanému běhu (373). Co z toho plyne: **mezi DEV a OOS se znaménko směrů úplně obrátilo**: short
+0,124 → −0,238 R, long +0,014 → +0,362 R [E]. Za DEV+OOS je long +0,151 R a short nula. Průměrný zisk
longů v OOS (3,23 R) ukazuje, že několik dlouhých býčích trendů 2019–2020 neslo celý výsledek.
Pravidlo pro směr by nepropustilo ani jednu stranu: long neprošel bránou 1 (DEV PF 1,01), short neprošel
bránou 2 (OOS −0,238 R) [E, vlastní dopočet]. Za 22 let (kapitola 13) je long strana C2 jasně silnější
než short. To je konzistentní s dlouhodobým růstem zlata, ale znamená to i riziko, že část „edge“ je
jen beta k býčímu trhu [I].

### Nákladový stres

| Scénář | D+O obch. | D+O exp. R | D+O PF | D+O Sharpe | D+O CAGR | D+O MaxDD | OOS exp. R | OOS PF | OOS Sharpe | OOS CAGR | OOS MaxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | 368 | 0,207 | 1,37 | 0,52 | 2,64 % | 11,0 % | 0,230 | 1,39 | 0,58 | 3,00 % | 11,0 % |
| baseline ×1,0 | 373 | 0,081 | 1,13 | 0,22 | 1,00 % | 13,4 % | 0,094 | 1,14 | 0,26 | 1,19 % | 13,5 % |
| stres ×1,5 | 373 | 0,047 | 1,07 | 0,13 | 0,54 % | 14,0 % | 0,058 | 1,08 | 0,17 | 0,70 % | 14,0 % |
| stres ×2,0 | 374 | 0,007 | 1,00 | 0,02 | 0,00 % | 14,5 % | 0,023 | 1,03 | 0,09 | 0,29 % | 14,5 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | 372 | 0,121 | 1,20 | 0,32 | 1,51 % | 13,0 % | 0,125 | 1,20 | 0,34 | 1,63 % | 13,0 % |

Jak číst tabulku: stejná struktura jako u C3. Co z toho plyne: **brána 3 je splněna** (×1,5: +0,047 R),
ale při ×2 je C2 za DEV+OOS **na nule** (+0,007 R; v USD dokonce −305, protože výsledky v USD váží
obchody podle velikosti účtu v daném měsíci, zatímco průměr R je váží stejně [I]). Hrubá expectancy
0,207 R je nejvyšší z trojice C3/C2/C5, ale náklady z ní berou nejvíc. ECN účet by C2 výrazně pomohl
(0,121 R), protože polovina spreadu a swapové přirážky převáží komisi.

| Scénář | Období | Hrubý PnL | Spread | Skluz | Komise | Swap | Čistý PnL | Náklady / hrubý |
|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | DEV+OOS | 43 260 | 0 | 0 | 0 | 0 | 43 260 | 0 % |
| hrubě ×0 | OOS | 15 340 | 0 | 0 | 0 | 0 | 15 340 | 0 % |
| baseline ×1,0 | DEV+OOS | 29 740 | 4 077 | 2 578 | 0 | −8 648 | 14 437 | 51 % |
| baseline ×1,0 | OOS | 11 337 | 1 483 | 910 | 0 | −3 247 | 5 697 | 50 % |
| stres ×1,5 | DEV+OOS | 29 255 | 5 895 | 3 723 | 0 | −12 144 | 7 493 | 74 % |
| stres ×1,5 | OOS | 11 260 | 2 190 | 1 341 | 0 | −4 530 | 3 200 | 72 % |
| stres ×2,0 | DEV+OOS | 27 182 | 7 537 | 4 770 | 0 | −15 180 | −305 | 101 % |
| stres ×2,0 | OOS | 11 513 | 2 865 | 1 764 | 0 | −5 765 | 1 119 | 90 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | DEV+OOS | 32 296 | 2 125 | 1 346 | 1 035 | −4 896 | 22 894 | 29 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | OOS | 11 428 | 756 | 465 | 301 | −1 918 | 7 987 | 30 % |

Jak číst tabulku: rozklad v USD. Co z toho plyne: rozklad celkového dopadu nákladů je u C2 nápadně
jiný než u C3 [E, vlastní dopočet]. Bezfrikční čistý PnL 43 260 USD klesne na 14 437 USD (o 67 %).
Z rozdílu 28 823 USD jsou explicitní náklady jen 15 303 USD a **13 520 USD (47 %) je nepřímý vliv**:
hrubý PnL baseline běhu (29 740) je o třetinu nižší než u bezfrikčního běhu. Pravděpodobný mechanismus
[I]: stop C2 se posouvá přesně na extrém výstupního kanálu spočítaný z mid cen. Při exekuci na bid/ask
ho zasáhne už pouhý retest extrému, zvlášť v hodinách se širokým spreadem (denní znovuotevření).
U C3 je trailing stop 3 ATR od ceny a tento efekt tam téměř chybí. Pro PAPER fázi z toho plyne
konkrétní kontrola: měřit, kolik stopů C2 bylo zasaženo jen díky spreadu.

### Zpoždění vstupu

| Varianta | Obchody | Exp. R | Změna R | Změna % | PF | Sharpe | CAGR | MaxDD |
|---|---|---|---|---|---|---|---|---|
| baseline (fill na open dalšího baru) | 373 | 0,0811 | — | — | 1,13 | 0,22 | 1,00 % | 13,4 % |
| zpoždění +1 H1 bar | 372 | 0,0608 | −0,0203 | −25 % | 1,09 | 0,17 | 0,71 % | 13,2 % |
| zpoždění +1 H1 bar a skluz ×3 | 372 | 0,0344 | −0,0468 | −58 % | 1,04 | 0,10 | 0,36 % | 13,8 % |

Jak číst tabulku: stejně jako u C3. Co z toho plyne: hodinové zpoždění stojí C2 0,020 R na obchod
(čtvrtinu edge), tedy téměř čtyřikrát víc než C3 [E]. Breakout má část pokračování hned v první hodině
po proražení a pozdější vstup ji nezachytí [I]. Strategie zůstává kladná, ale exekuce by u C2 měla být
rychlejší a spolehlivější než u C3. Varianta se skluzem ×3 snižuje edge o 58 %.

### Perturbace parametrů

| Ukazatel | Hodnota |
|---|---|
| Počet bodů mřížky | 125 |
| Podíl bodů s exp. R > 0 (brána 4) | 96,0 % |
| Podíl bodů s PF > 1 | 94,4 % |
| Sharpe p10 / medián / p90 | 0,07 / 0,18 / 0,27 |
| Exp. R min / p10 / medián / p90 / max | −0,020 / 0,024 / 0,066 / 0,093 / 0,125 |
| Podíl bodů se Sharpe > 0,3 | 3,2 % |
| Počet obchodů min / max | 305 / 512 |
| MaxDD min / medián / max | 7,5 % / 13,6 % / 21,1 % |
| PBO (CSCV, roční bloky) | 0,70 |
| Počet rozdělení CSCV / medián logitu | 3 432 / −0,71 |
| Default: podíl bodů mřížky s nižší exp. R / nižším Sharpe | 74 % / 70 % |
| 26 nejbližších sousedů defaultu: podíl exp. R > 0 / medián exp. R | 92 % / 0,057 |
| Nejlepší bod (exp. R) | entry_n 63, exit_n 25, stop_atr 1,5: 0,125 R, Sharpe 0,26 |
| Nejhorší bod (exp. R) | entry_n 41, exit_n 23, stop_atr 1,75: −0,020 R, Sharpe −0,04 |
| Nejvyšší Sharpe | entry_n 55, exit_n 17, stop_atr 2,25: Sharpe 0,33, 0,108 R |

Jak číst tabulku: mřížka entry_n {41, 47, 55, 63, 69} × exit_n {15, 17, 20, 23, 25} × stop_atr
{1,5; 1,75; 2,0; 2,25; 2,5} (předregistrovaná už v `PROTOCOL.md`). Co z toho plyne: **brána 4 je
splněna** s nejvyšším podílem z trojice (96 %) a default leží na 74. percentilu. Všech pět záporných
bodů má exit_n 23 a krátký vstupní kanál (41 nebo 47) [E]. Jde o úzké „údolí“ uprostřed osy (exit_n
20 i 25 jsou v pořádku), tedy spíš o náhodný vzor konkrétní cesty cen než o strukturu [I]. Mřížka je
plochá: jen 3,2 % bodů má Sharpe nad 0,3. **PBO 0,70 s mediánem logitu −0,71** znamená, že
konfigurace, která byla nejlepší v jedné polovině let, skončí v druhé polovině většinou pod mediánem.
Mezi téměř stejně dobrými konfiguracemi rozhoduje šum a výběr „nejlepší“ je horší než náhodný [I].
Vysoké PBO zde neznamená, že default je přeučený, ale že **ladění parametrů C2 nemá smysl**. Totéž
potvrzuje walk-forward níže.

| Osa | Hodnota | Medián exp. R | Medián PF | Medián Sharpe | Medián MaxDD | Medián obchodů |
|---|---|---|---|---|---|---|
| entry_n | 41 | 0,047 | 1,06 | 0,14 | 15,6 % | 454 |
| entry_n | 47 | 0,041 | 1,05 | 0,12 | 14,1 % | 427 |
| entry_n | 55 | 0,074 | 1,11 | 0,20 | 13,1 % | 385 |
| entry_n | 63 | 0,083 | 1,12 | 0,22 | 12,7 % | 365 |
| entry_n | 69 | 0,077 | 1,10 | 0,18 | 11,7 % | 347 |
| exit_n | 15 | 0,064 | 1,10 | 0,19 | 14,0 % | 413 |
| exit_n | 17 | 0,084 | 1,14 | 0,24 | 14,3 % | 396 |
| exit_n | 20 | 0,076 | 1,11 | 0,20 | 14,3 % | 384 |
| exit_n | 23 | 0,032 | 1,04 | 0,09 | 13,6 % | 380 |
| exit_n | 25 | 0,068 | 1,10 | 0,18 | 12,0 % | 371 |
| stop_atr | 1,5 | 0,066 | 1,08 | 0,17 | 17,5 % | 413 |
| stop_atr | 1,75 | 0,055 | 1,08 | 0,16 | 15,3 % | 400 |
| stop_atr | 2 | 0,054 | 1,07 | 0,16 | 13,1 % | 386 |
| stop_atr | 2,25 | 0,073 | 1,12 | 0,22 | 12,1 % | 375 |
| stop_atr | 2,5 | 0,068 | 1,12 | 0,21 | 9,5 % | 371 |

Jak číst tabulku: mediány přes 25 bodů s danou hodnotou osy. Co z toho plyne: delší vstupní kanál
(55–69) je lepší než krátký (41–47): méně obchodů, vyšší expectancy, nižší MaxDD. Turtle default 55 leží
na začátku lepší oblasti. Osa stop_atr je z hlediska expectancy plochá (0,054–0,073 R), ale širší stop
výrazně snižuje MaxDD (17,5 % → 9,5 %). Při stejném riziku v USD znamená širší stop menší pozici
a stop se stejně brzy posune na výstupní kanál [I]. Pokles u exit_n 23 je vidět i v mediánech.

![Perturbační mřížka C2: medián expectancy (R) podle entry_n × exit_n, medián přes pět hodnot stop_atr, DEV+OOS 2010–2023](research/results/figures/grid_C2.png)

Jak číst obrázek: pole = medián expectancy přes pět hodnot stop_atr. Co z toho plyne: horní tři řádky
(entry_n 55–69) tvoří souvislé plato 0,04–0,10 R, dolní dva (41–47) jsou slabší (0,00–0,07 R).
Sloupec exit_n 23 je ve všech řádcích nejslabší (−0,00 až 0,04 R). Default (55, 20) má medián 0,09 R
a leží uvnitř lepší oblasti. Špička v jednom bodě chybí.

### Timeframe

| TF | Parametry | Obchody | Exp. R | t | PF | Sharpe | CAGR | MaxDD | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|
| H2 | vstup 110, výstup 40, ATR 40, max 180 | 431 | 0,129 | 1,04 | 1,17 | 0,29 | 1,80 % | 18,0 % | 119 |
| H3 | vstup 73, výstup 27, ATR 27, max 120 | 399 | 0,055 | 0,50 | 1,07 | 0,14 | 0,65 % | 17,5 % | 135 |
| H4 | vstup 55, výstup 20, ATR 20, max 90 (default) | 373 | 0,081 | 0,79 | 1,13 | 0,22 | 1,00 % | 13,4 % | 149 |
| H6 | vstup 37, výstup 13, ATR 13, max 60 | 342 | 0,079 | 0,86 | 1,15 | 0,24 | 0,92 % | 10,3 % | 168 |
| D1 | vstup 9, výstup 3, ATR 3, max 15 | 270 | 0,026 | 0,52 | 1,09 | 0,14 | 0,23 % | 4,7 % | 228 |

Jak číst tabulku: délky kanálů, ATR a time-stopu přepočtené na stejný reálný čas. Co z toho plyne:
**všech pět timeframů je kladných** [E]. H2 má dokonce nejvyšší expectancy (0,129 R) i t (1,04),
H4 a H6 jsou si podobné, D1 je nejslabší. Kanál 9/3 dní s ATR(3) na D1 je ale hrubé přiblížení.
Efekt C2 tedy nezávisí na volbě H4 a mírně slábne směrem k pomalejším timeframům.

### Walk-forward

| Test | Trénink | Vybrané parametry | Train Sharpe | Test výnos | Default výnos | Rozdíl p. b. |
|---|---|---|---|---|---|---|
| 2014 | 2010–2013 | entry_n 69, exit_n 20, stop_atr 2 | 0,40 | −4,8 % | −3,9 % | −1,0 |
| 2015 | 2011–2014 | entry_n 41, exit_n 15, stop_atr 2 | 0,35 | 0,7 % | 1,6 % | −1,0 |
| 2016 | 2012–2015 | entry_n 69, exit_n 15, stop_atr 2 | 0,28 | 2,9 % | 2,1 % | 0,8 |
| 2017 | 2013–2016 | entry_n 41, exit_n 20, stop_atr 2 | 0,37 | 6,2 % | 4,8 % | 1,4 |
| 2018 | 2014–2017 | entry_n 41, exit_n 20, stop_atr 2 | 0,48 | −4,2 % | −2,7 % | −1,5 |
| 2019 | 2015–2018 | entry_n 41, exit_n 20, stop_atr 2 | 0,39 | −0,7 % | 1,0 % | −1,8 |
| 2020 | 2016–2019 | entry_n 55, exit_n 15, stop_atr 2 | 0,31 | 9,0 % | 6,8 % | 2,2 |
| 2021 | 2017–2020 | entry_n 55, exit_n 15, stop_atr 2 | 0,67 | −4,4 % | −4,9 % | 0,5 |
| 2022 | 2018–2021 | entry_n 69, exit_n 15, stop_atr 2 | 0,29 | −4,1 % | −1,9 % | −2,2 |
| 2023 | 2019–2022 | entry_n 55, exit_n 25, stop_atr 2 | 0,23 | 5,8 % | 5,8 % | 0,0 |

Jak číst tabulku: výběr z mřížky entry_n {41, 55, 69} × exit_n {15, 20, 25}, stop pevně 2,0. Co z toho
plyne: spojený walk-forward výnos **+5,4 %** (Sharpe 0,13, kladných 5 z 10 let), **brána 5 je
splněna**. Pevný default by ale za stejných 10 let vydělal **+8,5 %** a walk-forward ho porazil jen ve
4 letech z 10 [E, vlastní dopočet]. Vybraný vstupní kanál skáče mezi extrémy (69 → 41 → 69 → 41 … 55),
stabilní optimum neexistuje. To je v souladu s vysokým PBO: **rekalibrace C2 škodí** a pevný literaturní
default je lepší volbou [I].

### Bootstrap

| Metrika (trade bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| CAGR | −1,22 % | 0,94 % | 3,30 % |
| Expectancy R | −0,086 | 0,080 | 0,257 |
| Profit factor | 0,86 | 1,14 | 1,45 |
| Max drawdown | 7,9 % | 13,8 % | 25,3 % |
| Nejdelší série ztrát (obchody) | 9 | 13 | 20 |
| Nejdelší úsek pod maximem (obchody) | 70 | 174 | 363 |

Jak číst tabulku: 10 000× převzorkováno 373 obchodů. P(expectancy > 0) = **78,2 %**. Co z toho plyne:
**brána 7 splněna není** a interval expectancy (−0,086 až 0,257 R) je širší než u C3, protože výsledek
stojí na malém počtu velkých výher. Riziková čísla jsou výrazně horší než u C3: medián MaxDD 13,8 %,
v 5 % scénářů přes 25 %. Medián série ztrát je 13 obchodů. Medián úseku pod maximem 174 obchodů
odpovídá při 26,7 obchodu ročně asi 6,5 roku, p95 363 obchodů zhruba 13,6 roku [E, vlastní dopočet].

| Metrika (blokový bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| Sharpe | −0,22 | 0,21 | 0,64 |
| CAGR | −1,12 % | 0,92 % | 3,26 % |
| Max drawdown | 8,8 % | 14,7 % | 26,0 % |

Jak číst tabulku: blokový bootstrap denních výnosů. P(Sharpe > 0) = **79,4 %**. Co z toho plyne:
obraz je stejný jako u bootstrapu obchodů. Sharpe 0,21 v mediánu s intervalem −0,22 až 0,64 neumožňuje
odlišit C2 od nuly.

### Režimy

| Dimenze | Stav | Obchody | Exp. R | Win % | PF | Long exp. R | Short exp. R | Denní Sharpe |
|---|---|---|---|---|---|---|---|---|
| trend | range (bez trendu) | 276 | −0,039 | 30,8 | 0,93 | 0,003 | −0,089 | 0,04 |
| trend | trending | 97 | 0,423 | 33,0 | 1,73 | 0,560 | 0,251 | 0,52 |
| volatilita | vysoká | 142 | −0,088 | 26,1 | 0,84 | −0,071 | −0,109 | −0,29 |
| volatilita | nízká | 231 | 0,185 | 34,6 | 1,32 | 0,291 | 0,060 | 0,65 |
| USD (60 d) | silný USD | 228 | 0,080 | 32,9 | 1,12 | 0,215 | −0,081 | −0,12 |
| USD (60 d) | slabý USD | 145 | 0,083 | 29,0 | 1,13 | 0,051 | 0,123 | 0,60 |
| výnosy 10Y (60 d) | klesající | 190 | −0,006 | 30,0 | 0,97 | 0,058 | −0,088 | 0,23 |
| výnosy 10Y (60 d) | rostoucí | 183 | 0,171 | 32,8 | 1,30 | 0,253 | 0,080 | 0,21 |
| VIX | krize (VIX > 25) | 54 | −0,311 | 27,8 | 0,48 | −0,436 | −0,203 | −0,46 |
| VIX | normál | 319 | 0,147 | 32,0 | 1,24 | 0,233 | 0,039 | 0,35 |

Jak číst tabulku: stejné ex-ante štítky jako u C3. Co z toho plyne: C2 je **silně závislá na
předchozím trendu**: v režimu „trending“ +0,423 R (PF 1,73), v režimu „range“ −0,039 R [E]. Je to
opačný obraz než u C3: breakout 55barového extrému v již zavedeném trendu je pokračováním trendu,
kdežto v rozsahu je to typicky falešné proražení [I]. Krize (VIX > 25, 54 obchodů) má **nejhorší expectancy
ze všech režimových tabulek pěti strategií** (−0,311 R). Vysoká volatilita je také záporná. Dimenze USD je
v expectancy neutrální (0,080 vs. 0,083 R), ale denní Sharpe ukazuje opak (−0,12 vs. 0,60). Obě míry
se mohou rozcházet, protože expectancy přiřazuje obchod ke dni vstupu, kdežto denní Sharpe počítá
všechny dny s daným štítkem [I]. Makro dimenze proto nedávají spolehlivý filtr.

### Roky a bloky

| Rok | Segment | Obchody | Exp. R | Čistý PnL | Long PnL | Short PnL | Kumulativně |
|---|---|---|---|---|---|---|---|
| 2010 | DEV | 27 | −0,310 | −4 067 | −387 | −3 681 | −4 067 |
| 2011 | DEV | 30 | 0,252 | 3 287 | 4 726 | −1 440 | −781 |
| 2012 | DEV | 25 | 0,060 | 654 | 1 708 | −1 054 | −127 |
| 2013 | DEV | 24 | 0,502 | 5 986 | 42 | 5 944 | 5 859 |
| 2014 | DEV | 32 | −0,242 | −4 084 | −4 751 | 667 | 1 775 |
| 2015 | DEV | 27 | 0,137 | 1 674 | −1 145 | 2 819 | 3 449 |
| 2016 | DEV | 24 | 0,208 | 2 507 | 659 | 1 847 | 5 956 |
| 2017 | DEV | 27 | 0,161 | 2 197 | −834 | 3 031 | 8 153 |
| 2018 | DEV | 25 | −0,101 | −1 421 | −270 | −1 151 | 6 731 |
| 2019 | OOS | 25 | −0,022 | −257 | 1 251 | −1 508 | 6 474 |
| 2020 | OOS | 23 | 0,800 | 9 803 | 12 710 | −2 907 | 16 277 |
| 2021 | OOS | 29 | −0,362 | −5 839 | −3 693 | −2 146 | 10 438 |
| 2022 | OOS | 27 | −0,132 | −1 921 | 59 | −1 980 | 8 517 |
| 2023 | OOS | 28 | 0,392 | 5 920 | 4 996 | 923 | 14 437 |

Jak číst tabulku: rok výstupu obchodu, USD. Co z toho plyne: kladných je 8 ze 14 let. **Rok 2020
přinesl 9 803 USD, tedy 68 % celkového zisku** (brána 6 selhává), téměř celý z longů (+12 710 USD)
v býčím roce zlata (+25 %) [E]. Bez roku 2020 by zbylo 4 634 USD. Rozkyv mezi roky je velký, od
−5 839 (2021) do +9 803 USD (2020). Rok 2010 byl i přes růst zlata o 28 % ztrátový kvůli shortům
(−3 681 USD) [E]. To ilustruje, že symetrický breakout v býčím roce opakovaně zkouší falešné poklesy [I].

| Blok | Obchody | Exp. R | PF | Čistý PnL |
|---|---|---|---|---|
| 2010–2012 | 82 | 0,008 | 0,99 | −127 |
| 2013–2015 | 83 | 0,096 | 1,13 | 3 576 |
| 2016–2018 | 76 | 0,089 | 1,15 | 3 282 |
| 2019–2021 | 77 | 0,096 | 1,14 | 3 707 |
| 2022–2023 | 55 | 0,135 | 1,24 | 3 999 |

Jak číst tabulku: tříleté bloky. Co z toho plyne: na úrovni bloků je C2 **nejrovnoměrnější ze všech
pěti strategií**. Čtyři bloky po roce 2012 jsou kladné se ziskem 3,3–4,0 tis. USD a první je na nule
[E]. Koncentrace do jednoho roku (brána 6) a rovnoměrnost na tříletém horizontu si neodporují: C2
potřebuje na zachycení několika dlouhých trendů zhruba tři roky. To je důležité pro očekávání
v PAPER fázi: rok nebo dva bez výsledku nic nevyvracejí ani nepotvrzují [I].

### Deflated Sharpe a PSR

| Varianta | N | T (dní) | SR (anual.) | SR0 (anual.) | PSR (SR > 0) | DSR |
|---|---|---|---|---|---|---|
| DEV+OOS, N = 60 (konzervativní) | 60 | 3 605 | 0,22 | 1,46 | 0,80 | 0,00 |
| jen OOS, N = 60 | 60 | 1 290 | 0,27 | 1,46 | 0,73 | 0,00 |
| DEV+OOS, N = 125 (v rámci mřížky) | 125 | 3 605 | 0,22 | 0,20 | 0,80 | 0,53 |

Jak číst tabulku: stejná metodika jako u C3. Co z toho plyne: v mírnější variantě má C2 nejvyšší DSR
z trojice C3/C2/C5 (0,53). Mřížka C2 je totiž úzká (malý rozptyl Sharpe mezi konfiguracemi, SR0 0,20),
takže výběr defaultu z ní statisticky „nestojí“ mnoho. I tak jde jen o něco víc než hod mincí
a konzervativní DSR je 0,00. K t = 2 by při Sharpe 0,22 bylo potřeba asi 82 let dat [I, vlastní
dopočet (2 / 0,221)²].

### Brány

| Brána | Podmínka | Hodnota | Splněno |
|---|---|---|---|
| 1 | DEV: exp. R > 0 a PF > 1,10 | exp. 0,064 R, PF 1,094 | NE |
| 2 | OOS: exp. R > 0, PF > 1,05, Sharpe > 0,3 | exp. 0,094 R, PF 1,14, Sharpe 0,26 | NE |
| 3 | náklady ×1,5: exp. R DEV+OOS > 0 | 0,047 R | ANO |
| 4 | ≥ 70 % bodů mřížky s exp. R > 0 | 96 % | ANO |
| 5 | walk-forward spojený výsledek > 0 | 5,4 % | ANO |
| 6 | žádný rok > 50 % čistého zisku | 68 % | NE |
| 7 | bootstrap P(exp. R > 0) ≥ 90 % | 78,2 % | NE |
| Vše | brány 1–7 současně | splněno 3 ze 7 | NE |

Jak číst tabulku: hodnoty z `s02_C2.json`. Co z toho plyne: C2 selhala těsně na bráně 1 (PF 1,094
proti 1,10) a těsně na bráně 2 (OOS Sharpe 0,26 proti 0,3). Selhání na branách 6 a 7 je věcné:
výsledek stojí na jednom roce a statisticky není odlišitelný od nuly.

### Celkové hodnocení C2

> **Závěr:** C2 má nejlepší historický výsledek z trendové rodiny: kladná je ve všech třech
> nezávislých obdobích, nejsilnější v nepoužitém PRE-SAMPLE, s nejvyšší hrubou expectancy a nejrovnějšími
> tříletými bloky. Robustní je vůči parametrům (96 % mřížky kladné) i timeframu (5 z 5). Slabá místa
> jsou ale vážnější než u C3: celý výsledek nese 5 % obchodů, za DEV+OOS stojí zisk na long straně
> (DEV a OOS mají opačné směrové znaménko), při nákladech ×2 je na nule, hodinové zpoždění ubere čtvrtinu
> edge, nepřímý dopad bid/ask exekuce na stopy je velký, PBO 0,70 a walk-forward je horší než pevný default.
> Splnila 3 ze 7 bran. Důvěra: **nízká**. Proto #2 za C3: vyšší výnos, ale víc závislostí na
> exekuci, směru a několika trendech.

Typ důkazu: čísla jsou [E]; vysvětlení nepřímého dopadu nákladů přes stopy na extrému kanálu
a interpretace PBO jsou [I] a v PAPER fázi je lze ověřit.

## 10.3 C5 Squeeze H4

C5 („momentum po konsolidaci“) byla **nejsilnějším kandidátem po DEV** (DEV t 1,40, Sharpe 0,48)
a do plné validace šla jako první náhradník. V OOS ale selhala nejvýrazněji z trendové rodiny. Ve
zmrazeném pořadí je **#3**, hlavně proto, že je to třetí, časováním odlišná varianta téže sázky,
ne kvůli síle důkazů.

### Rekapitulace pravidel

- **Data a timeframe:** H4 bary z mid cen.
- **Indikátory:** Bollingerova pásma (SMA20 ± 2σ, σ populační); bandwidth = 4σ / SMA20; percentilové
  pořadí bandwidth v posledních 120 barech (podíl předchozích hodnot, které jsou nižší); ATR(20).
- **Squeeze:** pořadí bandwidth < 0,20 kdykoli v posledních 5 barech.
- **Vstup long:** squeeze a close nad horním pásmem. **Vstup short:** squeeze a close pod dolním pásmem.
- **Stop:** close ∓ 2,0 × ATR20, bez trailingu.
- **Výstup:** close přes střední pásmo (SMA20) proti pozici, nebo po 30 barech (5 obchodních dní).
- **Parametry:** 8 (bb_n 20, bb_k 2,0, rank_n 120, squeeze_pct 0,2, lookback 5, atr_n 20, stop_atr 2,0,
  max_hold 30). Nejvíc stupňů volnosti z trojice.

Jak strategie fakticky vystupuje [E, vlastní dopočet, DEV+OOS]: 357 z 510 obchodů skončilo přes
střední pásmo nebo time-stopem (průměr +0,49 R, win rate 50 %, součet +175,7 R), 153 obchodů (30 %)
skončilo plným stopem (průměr −1,02 R, součet −156,2 R). Čistý výsledek +19,5 R je tedy **malý rozdíl
dvou velkých čísel**. Stačí mírná změna poměru výstupů a výsledek se překlopí. To vysvětluje, proč
je C5 citlivější na náklady i na období než C3 [I].

### Segmenty

| Segment | Obchody | Obch./rok | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF |
|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 205 | 37,3 | 39,0 | 1,51 | −0,76 | 0,122 | 1,24 | 1,26 |
| DEV 2010–2018 | 331 | 36,8 | 38,4 | 1,44 | −0,72 | 0,109 | 1,40 | 1,24 |
| OOS 2019–2023 | 179 | 35,9 | 29,6 | 1,50 | −0,76 | −0,092 | −0,94 | 0,82 |
| DEV+OOS 2010–2023 | 510 | 36,5 | 35,3 | 1,46 | −0,74 | 0,038 | 0,63 | 1,07 |

Jak číst tabulku: stejné segmenty jako výše. Co z toho plyne: PRE a DEV jsou si nápadně podobné
(+0,122 a +0,109 R, PF 1,26 a 1,24), takže do roku 2018 vypadala C5 jako nejkonzistentnější strategie
celého výzkumu. **V OOS se ale obrátila do ztráty** (−0,092 R, PF 0,82). Win rate klesl z 38 % na 30 %,
zatímco průměrná výhra a ztráta zůstaly stejné [E]. Změnila se tedy úspěšnost proražení, ne
velikost pohybů. Spojené DEV+OOS je kladné (+0,038 R) jen díky silnému DEV. K jeho síle ale
přispěla i data B (rozbor u tabulky let níže).

| Segment | Sharpe | Sortino | CAGR | MaxDD | Calmar | Expozice | Ø držení h | Medián h | Max. série ztrát | Pod vodou (dny) |
|---|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 0,53 | 0,87 | 2,20 % | 5,7 % | 0,38 | 35 % | 83 | 72 | 10 | 392 |
| DEV 2010–2018 | 0,48 | 0,81 | 1,92 % | 6,4 % | 0,30 | 34 % | 82 | 76 | 7 | 1 455 |
| OOS 2019–2023 | −0,41 | −0,61 | −1,66 % | 15,2 % | −0,11 | 29 % | 72 | 61 | 10 | 1 752 |
| DEV+OOS 2010–2023 | 0,17 | 0,27 | 0,62 % | 16,9 % | 0,04 | 32 % | 78 | 72 | 10 | 2 164 |

Jak číst tabulku: rizikové a časové charakteristiky. Co z toho plyne: C5 drží nejkratší dobu
z trendových variant (průměr 78 h, asi 3 dny) a obchoduje nejčastěji (36,5 obchodu ročně). MaxDD za
DEV+OOS je s 16,9 % nejvyšší z trojice a **nejdelší období pod vodou 2 164 dní** (téměř 6 let) zabírá
celé OOS a část DEV. Strategie dosáhla maxima equity koncem roku 2017 a do konce roku 2023 ho
nepřekonala (tabulka let níže).

| Segment | Hrubý PnL | Spread | Skluz | Swap | Čistý PnL | Náklady / hrubý | Obch. L / S | Long PnL | Short PnL |
|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 17 906 | 1 839 | 757 | −2 585 | 12 725 | 29 % | 111 / 94 | 13 595 | −870 |
| DEV 2010–2018 | 28 188 | 3 914 | 1 555 | −4 028 | 18 691 | 34 % | 162 / 169 | 9 967 | 8 724 |
| OOS 2019–2023 | −3 267 | 2 014 | 804 | −1 924 | −8 009 | n/a | 94 / 85 | −8 368 | 359 |
| DEV+OOS 2010–2023 | 24 213 | 6 309 | 2 511 | −6 318 | 9 075 | 63 % | 256 / 254 | 81 | 8 994 |

Jak číst tabulku: „n/a“ znamená záporný hrubý PnL, podíl nákladů nedává smysl. Co z toho plyne:
**v OOS byl záporný už hrubý výsledek** (−3 267 USD), C5 tedy v letech 2019–2023 neselhala kvůli
nákladům, ale proto, že signál přestal fungovat [E]. V DEV byla C5 jako jediná trendová varianta
vyvážená mezi směry (long 9 967, short 8 724 USD). Za DEV+OOS jsou spread (6 309 USD) a swap
(−6 318 USD) prakticky stejně velké. Spread má u C5 relativně větší váhu než u ostatních trendových
variant, protože C5 obchoduje nejčastěji.

### Long vs. short

| Strana / segment | Obchody | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF | Sharpe | Čistě % kapitálu | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|---|
| long DEV | 162 | 40,7 | 1,31 | −0,72 | 0,110 | 1,10 | 1,25 | 0,35 | 8,8 % | 86 |
| long OOS | 94 | 28,7 | 1,26 | −0,77 | −0,187 | −1,50 | 0,66 | −0,59 | −8,3 % | 73 |
| long DEV+OOS | 256 | 36,3 | 1,30 | −0,74 | 0,001 | 0,01 | 1,00 | 0,00 | −0,2 % | 81 |
| short DEV | 169 | 36,1 | 1,58 | −0,73 | 0,107 | 0,91 | 1,22 | 0,33 | 9,0 % | 78 |
| short OOS | 85 | 30,6 | 1,75 | −0,75 | 0,013 | 0,09 | 1,01 | 0,04 | 0,3 % | 72 |
| short DEV+OOS | 254 | 34,3 | 1,63 | −0,73 | 0,076 | 0,81 | 1,14 | 0,23 | 9,3 % | 76 |

Jak číst tabulku: samostatné běhy s jedním směrem; součty obchodů odpovídají kombinovanému běhu.
Co z toho plyne: v DEV byly obě strany kladné a téměř stejně silné (+0,110 a +0,107 R). **Selhání v OOS
je hlavně na long straně** (−0,187 R, t −1,50) [E]. Podle tabulky let níže longy neztrácely v býčím
roce 2019 (+1 998 USD), ale hlavně v roce 2021 bez směru (−6 028 USD) a dále v letech 2020, 2022
a 2023. Long proražení po konsolidaci tedy selhávala hlavně tam, kde po růstu nenásledovalo pokračování.
Je to konzistentní i s inverzní asymetrií volatility zlata (kladné šoky zvyšují volatilitu víc než
záporné, kapitola 5), která u long proražení vytváří víc whipsawů [I]. Pravidlo pro směr: obě strany prošly bránou 1, obě
selhaly na bráně 2 [E, vlastní dopočet].

### Nákladový stres

| Scénář | D+O obch. | D+O exp. R | D+O PF | D+O Sharpe | D+O CAGR | D+O MaxDD | OOS exp. R | OOS PF | OOS Sharpe | OOS CAGR | OOS MaxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | 510 | 0,095 | 1,19 | 0,42 | 1,66 % | 12,3 % | −0,034 | 0,93 | −0,14 | −0,65 % | 11,8 % |
| baseline ×1,0 | 510 | 0,038 | 1,07 | 0,17 | 0,62 % | 16,9 % | −0,092 | 0,82 | −0,41 | −1,66 % | 15,2 % |
| stres ×1,5 | 510 | 0,013 | 1,02 | 0,06 | 0,18 % | 18,7 % | −0,116 | 0,78 | −0,53 | −2,08 % | 16,7 % |
| stres ×2,0 | 510 | −0,013 | 0,97 | −0,06 | −0,29 % | 20,8 % | −0,140 | 0,75 | −0,63 | −2,47 % | 17,9 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | 510 | 0,060 | 1,11 | 0,27 | 1,03 % | 15,3 % | −0,071 | 0,86 | −0,31 | −1,29 % | 14,0 % |

Jak číst tabulku: stejně jako výše. Co z toho plyne: **brána 3 je splněna jen těsně** (×1,5: +0,013 R)
a při ×2 je C5 za DEV+OOS záporná (−0,013 R). Je tak nejcitlivější na náklady z trendové trojice:
každých +0,5 násobku nákladů ubere asi 0,025 R. V OOS je záporná ve všech scénářích včetně
bezfrikčního (−0,034 R). Ani ECN účet by OOS nezachránil.

| Scénář | Období | Hrubý PnL | Spread | Skluz | Komise | Swap | Čistý PnL | Náklady / hrubý |
|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | DEV+OOS | 25 866 | 0 | 0 | 0 | 0 | 25 866 | 0 % |
| hrubě ×0 | OOS | −3 189 | 0 | 0 | 0 | 0 | −3 189 | n/a |
| baseline ×1,0 | DEV+OOS | 24 213 | 6 309 | 2 511 | 0 | −6 318 | 9 075 | 63 % |
| baseline ×1,0 | OOS | −3 267 | 2 014 | 804 | 0 | −1 924 | −8 009 | n/a |
| stres ×1,5 | DEV+OOS | 24 256 | 9 073 | 3 614 | 0 | −9 035 | 2 535 | 90 % |
| stres ×1,5 | OOS | −3 075 | 2 960 | 1 184 | 0 | −2 744 | −9 962 | n/a |
| stres ×2,0 | DEV+OOS | 23 729 | 11 594 | 4 644 | 0 | −11 528 | −4 038 | 117 % |
| stres ×2,0 | OOS | −2 771 | 3 878 | 1 550 | 0 | −3 529 | −11 728 | n/a |
| ECN (×0,5 + 3,5 USD/lot/strana) | DEV+OOS | 24 954 | 3 267 | 1 298 | 1 568 | −3 366 | 15 455 | 38 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | OOS | −3 370 | 1 023 | 408 | 402 | −1 079 | −6 281 | n/a |

Jak číst tabulku: rozklad v USD. Co z toho plyne: v baseline náklady spotřebují 63 % hrubého zisku,
což je nejvíc z trojice. Rozklad celkového dopadu [E, vlastní dopočet]: bezfrikční čistý PnL 25 866 USD
klesne na 9 075 USD (o 65 %). Z rozdílu 16 790 USD je 15 138 USD explicitních nákladů a jen asi
1 650 USD nepřímý vliv. Problém C5 jsou tedy přímé náklady vysokého obratu, ne exekuční detaily.

### Zpoždění vstupu

| Varianta | Obchody | Exp. R | Změna R | Změna % | PF | Sharpe | CAGR | MaxDD |
|---|---|---|---|---|---|---|---|---|
| baseline (fill na open dalšího baru) | 510 | 0,0383 | — | — | 1,07 | 0,17 | 0,62 % | 16,9 % |
| zpoždění +1 H1 bar | 509 | 0,0370 | −0,0013 | −3 % | 1,07 | 0,17 | 0,61 % | 17,2 % |
| zpoždění +1 H1 bar a skluz ×3 | 509 | 0,0187 | −0,0195 | −51 % | 1,03 | 0,09 | 0,28 % | 18,9 % |

Jak číst tabulku: stejně jako výše. Co z toho plyne: samotné hodinové zpoždění C5 téměř nevadí
(−0,0013 R). Trojnásobný skluz ale ubere polovinu edge, protože C5 má nejvíc obchodů a nejkratší
držení, takže náklad na obchod tvoří větší část výsledku [I]. Pro exekuci je u C5 důležitější kvalita
plnění (skluz) než rychlost.

### Perturbace parametrů

| Ukazatel | Hodnota |
|---|---|
| Počet bodů mřížky | 125 |
| Podíl bodů s exp. R > 0 (brána 4) | 100,0 % |
| Podíl bodů s PF > 1 | 100,0 % |
| Sharpe p10 / medián / p90 | 0,14 / 0,30 / 0,45 |
| Exp. R min / p10 / medián / p90 / max | 0,013 / 0,029 / 0,066 / 0,125 / 0,230 |
| Podíl bodů se Sharpe > 0,3 | 49,6 % |
| Počet obchodů min / max | 388 / 706 |
| MaxDD min / medián / max | 10,3 % / 15,3 % / 22,7 % |
| PBO (CSCV, roční bloky) | 0,24 |
| Počet rozdělení CSCV / medián logitu | 3 432 / 1,14 |
| Default: podíl bodů mřížky s nižší exp. R / nižším Sharpe | 20 % / 15 % |
| 26 nejbližších sousedů defaultu: podíl exp. R > 0 / medián exp. R | 100 % / 0,065 |
| Nejlepší bod (exp. R) | bb_n 25, squeeze_pct 0,15, stop_atr 1,5: 0,230 R, Sharpe 0,63 |
| Nejhorší bod (exp. R) | bb_n 20, squeeze_pct 0,175, stop_atr 2,5: 0,013 R, Sharpe 0,06 |
| Nejvyšší Sharpe | bb_n 25, squeeze_pct 0,15, stop_atr 1,5: Sharpe 0,63, 0,230 R |

Jak číst tabulku: mřížka bb_n {15, 17, 20, 23, 25} × squeeze_pct {0,15; 0,175; 0,2; 0,225; 0,25} ×
stop_atr {1,5; 1,75; 2,0; 2,25; 2,5}, deklarovaná v `DEV_SELECTION.md` před OOS. Co z toho plyne:
**všech 125 bodů je kladných** (brána 4 splněna) a polovina má Sharpe nad 0,3. Zarážející je, že
**default patří k nejslabším konfiguracím**: lepší expectancy má 80 % mřížky a lepší Sharpe 85 % [E].
Medián mřížky (0,066 R) je o 74 % vyšší než expectancy defaultu (0,038 R). PBO 0,24 s kladným mediánem logitu
(1,14) říká, že pořadí konfigurací je v čase **perzistentní**: co bylo lepší v jedné polovině let,
bývá lepší i v druhé. C5 tedy na parametrech záleží víc než C3 a C2 [I]. To je dvojsečné: plato je
kladné všude, ale zvolený default stojí v jeho slabší části a výsledek C5 závisí na volbě parametrů
víc, než by bylo žádoucí.

| Osa | Hodnota | Medián exp. R | Medián PF | Medián Sharpe | Medián MaxDD | Medián obchodů |
|---|---|---|---|---|---|---|
| bb_n | 15 | 0,037 | 1,08 | 0,20 | 16,4 % | 627 |
| bb_n | 17 | 0,075 | 1,16 | 0,37 | 14,7 % | 601 |
| bb_n | 20 | 0,045 | 1,09 | 0,22 | 16,0 % | 510 |
| bb_n | 23 | 0,068 | 1,13 | 0,28 | 16,3 % | 473 |
| bb_n | 25 | 0,115 | 1,20 | 0,43 | 14,9 % | 444 |
| squeeze_pct | 0,15 | 0,072 | 1,12 | 0,25 | 15,4 % | 437 |
| squeeze_pct | 0,175 | 0,058 | 1,11 | 0,28 | 16,6 % | 472 |
| squeeze_pct | 0,2 | 0,067 | 1,13 | 0,32 | 15,8 % | 510 |
| squeeze_pct | 0,225 | 0,067 | 1,14 | 0,34 | 15,2 % | 536 |
| squeeze_pct | 0,25 | 0,063 | 1,12 | 0,30 | 14,8 % | 567 |
| stop_atr | 1,5 | 0,113 | 1,17 | 0,40 | 18,5 % | 542 |
| stop_atr | 1,75 | 0,085 | 1,15 | 0,35 | 16,6 % | 533 |
| stop_atr | 2 | 0,067 | 1,13 | 0,31 | 15,8 % | 528 |
| stop_atr | 2,25 | 0,054 | 1,12 | 0,28 | 14,8 % | 524 |
| stop_atr | 2,5 | 0,044 | 1,10 | 0,25 | 13,4 % | 521 |

Jak číst tabulku: mediány přes 25 bodů s danou hodnotou osy. Co z toho plyne: **osa stop_atr je
monotónní**: čím těsnější stop, tím vyšší expectancy (1,5 ATR: 0,113 R; 2,5 ATR: 0,044 R), ale také
vyšší MaxDD. Těsnější stop zvětšuje pozici při stejném riziku a rychleji ukončí neúspěšné proražení
[I]. Osa bb_n je nemonotónní (17 a 25 lepší než 20), squeeze_pct je plochá. **Parametry se
neměnily**: přechod na bb_n 25 nebo stop 1,5 ATR po zhlédnutí OOS by byl data-snooping a zmrazená
specifikace drží literaturní default.

| Parametr | Hodnota | Obchody | Exp. R | PF | Sharpe | CAGR | MaxDD |
|---|---|---|---|---|---|---|---|
| rank_n | 90 | 512 | 0,045 | 1,08 | 0,20 | 0,75 % | 14,3 % |
| rank_n | 105 | 514 | 0,028 | 1,05 | 0,12 | 0,45 % | 16,0 % |
| rank_n | 120 | 510 | 0,038 | 1,07 | 0,17 | 0,62 % | 16,9 % |
| rank_n | 135 | 508 | 0,055 | 1,10 | 0,24 | 0,93 % | 13,6 % |
| rank_n | 150 | 512 | 0,051 | 1,09 | 0,22 | 0,85 % | 13,2 % |
| max_hold | 22 | 521 | 0,044 | 1,08 | 0,21 | 0,76 % | 15,4 % |
| max_hold | 26 | 512 | 0,028 | 1,05 | 0,13 | 0,46 % | 17,2 % |
| max_hold | 30 | 510 | 0,038 | 1,07 | 0,17 | 0,62 % | 16,9 % |
| max_hold | 34 | 510 | 0,037 | 1,07 | 0,16 | 0,61 % | 18,2 % |
| max_hold | 38 | 508 | 0,050 | 1,09 | 0,22 | 0,83 % | 18,5 % |

Jak číst tabulku: jednorozměrné řezy (one-at-a-time, OAT) dalších dvou parametrů, ostatní na defaultu
(řádky 120 a 30 jsou default). Co z toho plyne: všech deset variant je kladných (0,028–0,055 R) a průběh
je nemonotónní, bez systematického trendu. Délka okna pro pořadí bandwidth ani maximální doba držení
výsledek nemění zásadně [E]. Do brány 4 se OAT body nezapočítávají.

![Perturbační mřížka C5: medián expectancy (R) podle bb_n × squeeze_pct, medián přes pět hodnot stop_atr, DEV+OOS 2010–2023](research/results/figures/grid_C5.png)

Jak číst obrázek: pole = medián expectancy přes pět hodnot stop_atr. Co z toho plyne: celý povrch je
kladný (0,02–0,15 R). Nejsilnější je řádek bb_n 25 (0,09–0,15 R), nejslabší řádky bb_n 15 a 20. Default
(bb_n 20, squeeze 0,2: 0,04 R) leží v **nejslabším pásu** mřížky. Na rozdíl od C3 a C2 tu existuje
zřetelný gradient, což odpovídá nízkému PBO.

### Timeframe

| TF | Parametry | Obchody | Exp. R | t | PF | Sharpe | CAGR | MaxDD | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|
| H2 | BB 40, rank 240, lookback 10, ATR 40, max 60 | 593 | 0,117 | 1,49 | 1,17 | 0,41 | 2,32 % | 17,9 % | 68 |
| H3 | BB 27, rank 160, lookback 7, ATR 27, max 40 | 534 | 0,059 | 0,86 | 1,10 | 0,23 | 1,03 % | 14,1 % | 75 |
| H4 | BB 20, rank 120, lookback 5, ATR 20, max 30 (default) | 510 | 0,038 | 0,63 | 1,07 | 0,17 | 0,62 % | 16,9 % | 78 |
| H6 | BB 13, rank 80, lookback 3, ATR 13, max 20 | 444 | 0,089 | 1,54 | 1,22 | 0,43 | 1,36 % | 7,2 % | 86 |

Jak číst tabulku: délky přepočtené na stejný reálný čas; D1 se u C5 netestoval (deklarováno předem).
Co z toho plyne: všechny čtyři timeframy jsou kladné, ale **H4 je z nich nejslabší** [E]. H2 a H6
mají t 1,49 a 1,54 a H6 navíc MaxDD jen 7,2 %. Předem zvolený H4 tedy patří k horším variantám, stejně
jako default v mřížce. Přechod na H2 nebo H6 by byl výběr po OOS, proto se neprovádí. Pro budoucí
výzkum na nových datech je to ale legitimní hypotéza [I].

### Walk-forward

| Test | Trénink | Vybrané parametry | Train Sharpe | Test výnos | Default výnos | Rozdíl p. b. |
|---|---|---|---|---|---|---|
| 2014 | 2010–2013 | bb_n 15, squeeze_pct 0,2, stop_atr 2 | 0,33 | 7,9 % | 5,3 % | 2,6 |
| 2015 | 2011–2014 | bb_n 15, squeeze_pct 0,2, stop_atr 2 | 0,67 | 3,3 % | 3,4 % | −0,1 |
| 2016 | 2012–2015 | bb_n 15, squeeze_pct 0,2, stop_atr 2 | 0,91 | 9,9 % | 6,9 % | 3,0 |
| 2017 | 2013–2016 | bb_n 15, squeeze_pct 0,2, stop_atr 2 | 1,32 | 0,4 % | 5,3 % | −4,9 |
| 2018 | 2014–2017 | bb_n 25, squeeze_pct 0,15, stop_atr 2 | 1,27 | −3,3 % | −4,7 % | 1,4 |
| 2019 | 2015–2018 | bb_n 25, squeeze_pct 0,15, stop_atr 2 | 0,85 | 4,8 % | 0,0 % | 4,8 |
| 2020 | 2016–2019 | bb_n 25, squeeze_pct 0,15, stop_atr 2 | 0,94 | 9,5 % | −1,9 % | 11,4 |
| 2021 | 2017–2020 | bb_n 25, squeeze_pct 0,15, stop_atr 2 | 0,96 | −0,6 % | −2,2 % | 1,5 |
| 2022 | 2018–2021 | bb_n 25, squeeze_pct 0,15, stop_atr 2 | 0,61 | −3,4 % | −2,1 % | −1,3 |
| 2023 | 2019–2022 | bb_n 25, squeeze_pct 0,15, stop_atr 2 | 0,63 | −0,1 % | −2,2 % | 2,1 |

Jak číst tabulku: výběr z mřížky bb_n {15, 20, 25} × squeeze_pct {0,15; 0,2; 0,25}, stop pevně 2,0.
Co z toho plyne: spojený walk-forward výnos **+30,9 %** (Sharpe 0,67, kladných 6 z 10 let), tedy
**brána 5 splněna s velkou rezervou**. Jde o nejlepší walk-forward ze všech strategií. Pevný default by
za stejných 10 let vydělal jen +7,3 % a byl kladný jen ve 4 letech. Walk-forward ho porazil v 7 letech
z 10 [E, vlastní dopočet]. Od roku 2018 se stabilně volila konfigurace bb_n 25 / squeeze 0,15 a ta
v OOS letech 2019–2020 vydělala 4,8 % a 9,5 %, zatímco default byl na nule nebo ve ztrátě. Je to
legitimní walk-forward bez pohledu do budoucnosti a souhlasí s nízkým PBO. **Bránu 5 ale splňuje
proces rekalibrace, ne zmrazená specifikace s defaultem.** Navíc i walk-forward byl v letech 2021–2023
mírně záporný, takže ani adaptivní C5 v posledních třech letech nevydělávala [E]. Walk-forward C5 je
kandidát na samostatnou hypotézu pro další výzkum s novými daty, ne důvod ke změně parametrů teď [I].

### Bootstrap

| Metrika (trade bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| CAGR | −1,17 % | 0,60 % | 2,46 % |
| Expectancy R | −0,060 | 0,038 | 0,139 |
| Profit factor | 0,88 | 1,08 | 1,31 |
| Max drawdown | 7,2 % | 12,7 % | 23,4 % |
| Nejdelší série ztrát (obchody) | 9 | 12 | 18 |
| Nejdelší úsek pod maximem (obchody) | 99 | 251 | 498 |

Jak číst tabulku: 10 000× převzorkováno 510 obchodů. P(expectancy > 0) = **73,0 %**, nejméně
z trendové trojice. Co z toho plyne: **brána 7 splněna není**. Medián úseku pod maximem 251 obchodů
odpovídá při 36,5 obchodu ročně asi 6,9 roku, p95 498 obchodů zhruba 13,7 roku [E, vlastní dopočet].
MaxDD v p95 přesahuje 23 %.

| Metrika (blokový bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| Sharpe | −0,24 | 0,17 | 0,57 |
| CAGR | −1,00 % | 0,60 % | 2,24 % |
| Max drawdown | 7,0 % | 12,0 % | 21,8 % |

Jak číst tabulku: blokový bootstrap denních výnosů. P(Sharpe > 0) = **75,1 %**. Co z toho plyne:
shodně s bootstrapem obchodů je C5 z trojice statisticky nejslabší. Žádná z bootstrapových metod ale
nezachytí to podstatné, totiž **časový trend** výsledků (silné DEV, záporné OOS). Převzorkování
předpokládá stacionaritu, kterou C5 zjevně nesplňuje [I].

### Režimy

| Dimenze | Stav | Obchody | Exp. R | Win % | PF | Long exp. R | Short exp. R | Denní Sharpe |
|---|---|---|---|---|---|---|---|---|
| trend | range (bez trendu) | 370 | 0,024 | 34,6 | 1,04 | −0,010 | 0,059 | 0,16 |
| trend | trending | 140 | 0,075 | 37,1 | 1,15 | 0,029 | 0,125 | 0,18 |
| volatilita | vysoká | 216 | −0,148 | 31,5 | 0,70 | −0,052 | −0,245 | −0,67 |
| volatilita | nízká | 294 | 0,175 | 38,1 | 1,39 | 0,039 | 0,313 | 0,79 |
| USD (60 d) | silný USD | 269 | 0,066 | 36,8 | 1,12 | 0,190 | −0,034 | 0,20 |
| USD (60 d) | slabý USD | 241 | 0,008 | 33,6 | 1,02 | −0,166 | 0,233 | 0,14 |
| výnosy 10Y (60 d) | klesající | 255 | 0,105 | 38,0 | 1,22 | 0,075 | 0,137 | 0,30 |
| výnosy 10Y (60 d) | rostoucí | 255 | −0,028 | 32,5 | 0,93 | −0,078 | 0,019 | 0,03 |
| VIX | krize (VIX > 25) | 64 | −0,229 | 31,2 | 0,56 | −0,225 | −0,232 | −0,98 |
| VIX | normál | 446 | 0,077 | 35,9 | 1,15 | 0,031 | 0,124 | 0,33 |

Jak číst tabulku: stejné štítky jako výše. Co z toho plyne: nízká volatilita je kladná (+0,175 R), vysoká
záporná (−0,148 R), a **v denním Sharpe je rozdíl obou stavů u C5 největší z trojice** (0,79 vs.
−0,67). Krize je silně záporná (−0,229 R, denní Sharpe −0,98) [E]. Logika squeeze, tedy konsolidace a následné proražení,
funguje v klidném trhu. V nervózním trhu jsou „squeeze“ jen krátké pauzy mezi velkými pohyby a
proražení pásma je často falešné [I]. Dimenze USD má protichůdné znaménko pro long a short (slabý USD:
long −0,166, short +0,233 R), což je spíš náhodná struktura malého vzorku než využitelný filtr [I].

### Roky a bloky

| Rok | Segment | Obchody | Exp. R | Čistý PnL | Long PnL | Short PnL | Kumulativně |
|---|---|---|---|---|---|---|---|
| 2010 | DEV | 36 | 0,001 | 13 | 126 | −113 | 13 |
| 2011 | DEV | 36 | 0,100 | 1 739 | 2 301 | −563 | 1 751 |
| 2012 | DEV | 35 | −0,111 | −2 018 | −2 233 | 215 | −267 |
| 2013 | DEV | 36 | 0,109 | 1 917 | −3 152 | 5 069 | 1 650 |
| 2014 | DEV | 37 | 0,293 | 5 408 | −62 | 5 470 | 7 058 |
| 2015 | DEV | 34 | 0,198 | 3 550 | 4 623 | −1 073 | 10 608 |
| 2016 | DEV | 41 | 0,293 | 6 713 | 5 805 | 908 | 17 321 |
| 2017 | DEV | 37 | 0,221 | 4 786 | 3 799 | 986 | 22 107 |
| 2018 | DEV | 39 | −0,141 | −3 416 | −1 240 | −2 176 | 18 691 |
| 2019 | OOS | 34 | 0,004 | −29 | 1 998 | −2 027 | 18 662 |
| 2020 | OOS | 32 | −0,120 | −2 250 | −1 421 | −829 | 16 412 |
| 2021 | OOS | 33 | −0,122 | −2 510 | −6 028 | 3 518 | 13 902 |
| 2022 | OOS | 37 | −0,122 | −2 478 | −1 804 | −674 | 11 424 |
| 2023 | OOS | 43 | −0,097 | −2 348 | −2 630 | 282 | 9 075 |

Jak číst tabulku: rok výstupu obchodu, USD. Co z toho plyne: obraz je jednoznačný. **2013–2017 bylo pět
silných let po sobě (celkem +22 373 USD), 2018–2023 šest záporných let po sobě** (v USD celkem
−13 031 USD; rok 2019 je přitom prakticky na nule) [E, vlastní dopočet]. Kumulativní zisk vrcholil na konci roku 2017 (22 107 USD) a do roku 2023 z něj
zbylo 9 075 USD. Největší rok 2016 tvoří 74 % celkového zisku (brána 6 selhává). Zlom přišel až v roce
2018, tedy ne přesně v okamžiku přechodu ze zdroje B na A (2016-09), a rok 2017 byl na datech A ještě
silný (+4 786 USD). Křížová kontrola zdrojů ale varuje [E, `s01_dev_screen.md`, kapitola 7]: za
stejné období 2016-09 – 2018-12 dala C5 na datech A jen 0,014 R, kdežto na datech B (bid + modelový
spread) 0,093 R. Část síly C5 v DEV, kde do 2016-08 běží data B, tak může pocházet z vlastností dat B.
Modelový spread je medián podle hodiny a nezachytí rozšíření spreadu v rušných chvílích, kdy breakout
vstupuje [I]. Vysvětlení je tedy pravděpodobně kombinací změny chování trhu, optimismu dat B a štěstí
v DEV.

| Blok | Obchody | Exp. R | PF | Čistý PnL |
|---|---|---|---|---|
| 2010–2012 | 107 | −0,002 | 0,99 | −267 |
| 2013–2015 | 107 | 0,201 | 1,42 | 10 875 |
| 2016–2018 | 117 | 0,126 | 1,27 | 8 083 |
| 2019–2021 | 99 | −0,078 | 0,84 | −4 789 |
| 2022–2023 | 80 | −0,109 | 0,80 | −4 827 |

Jak číst tabulku: tříleté bloky. Co z toho plyne: dva silné bloky uprostřed DEV, dva záporné bloky
v OOS a nulový začátek. To je profil **efektu, který zeslábl nebo zmizel**, ne rovnoměrně slabého
edge [I]. Z hlediska důvěry je to u C5 nejvážnější varovný signál.

### Deflated Sharpe a PSR

| Varianta | N | T (dní) | SR (anual.) | SR0 (anual.) | PSR (SR > 0) | DSR |
|---|---|---|---|---|---|---|
| DEV+OOS, N = 60 (konzervativní) | 60 | 3 605 | 0,17 | 1,46 | 0,74 | 0,00 |
| jen OOS, N = 60 | 60 | 1 290 | −0,41 | 1,46 | 0,18 | 0,00 |
| DEV+OOS, N = 125 (v rámci mřížky) | 125 | 3 605 | 0,17 | 0,30 | 0,74 | 0,30 |

Jak číst tabulku: stejná metodika jako výše. Co z toho plyne: C5 má nejnižší PSR i DSR z trojice.
V mírnější variantě je SR0 (0,30) vyšší než pozorovaný Sharpe defaultu (0,17), protože mřížka C5 má
velký rozptyl a default leží v její slabší části. PSR samotného OOS (0,18) říká, že OOS Sharpe byl
spíš záporný než kladný. K t = 2 by při Sharpe 0,17 bylo potřeba asi 140 let dat [I, vlastní dopočet
(2 / 0,169)²].

### Brány

| Brána | Podmínka | Hodnota | Splněno |
|---|---|---|---|
| 1 | DEV: exp. R > 0 a PF > 1,10 | exp. 0,109 R, PF 1,236 | ANO |
| 2 | OOS: exp. R > 0, PF > 1,05, Sharpe > 0,3 | exp. −0,092 R, PF 0,82, Sharpe −0,41 | NE |
| 3 | náklady ×1,5: exp. R DEV+OOS > 0 | 0,013 R | ANO |
| 4 | ≥ 70 % bodů mřížky s exp. R > 0 | 100 % | ANO |
| 5 | walk-forward spojený výsledek > 0 | 30,9 % | ANO |
| 6 | žádný rok > 50 % čistého zisku | 74 % | NE |
| 7 | bootstrap P(exp. R > 0) ≥ 90 % | 73,0 % | NE |
| Vše | brány 1–7 současně | splněno 4 ze 7 | NE |

Jak číst tabulku: hodnoty z `s02_C5.json`. Co z toho plyne: formálně splnila 4 ze 7 bran jako C3,
kvalita splnění je ale horší. Brána 3 prošla o 0,013 R, brána 5 prošla díky rekalibraci, ne díky
defaultu, a brána 2 selhala s nejhorším OOS z trojice (záporný už hrubý výsledek).

### Celkové hodnocení C5

> **Závěr:** C5 je nejrozporuplnější kandidát. Pro ni mluví 100% kladná mřížka, nízké PBO (0,24),
> nejlepší walk-forward (+30,9 %), kladné PRE a všechny čtyři timeframy. Proti ní mluví OOS záporné už
> před náklady, šest záporných let po sobě (2018–2023), nejvyšší citlivost na náklady (×2 záporná),
> nejvyšší MaxDD a nejdelší období pod vodou z trojice, 8 parametrů a default i timeframe ve slabší
> části prostoru. Splnila 4 ze 7 bran. Důvěra: **nízká**, nejnižší z trojice. Ve zmrazeném pořadí
> zůstala jako #3, protože časuje vstupy jinak než C3 a C2 (denní korelace 0,34–0,43, kapitola 11).
> Je to ale pořád stejná trendová sázka a v portfoliu by měla dostat nejmenší důvěru.

Typ důkazu: čísla jsou [E]; vysvětlení selhání long strany přes asymetrii volatility a interpretace
časového vývoje jako „slábnoucího efektu“ jsou [I]; ekonomické zdůvodnění, že po konsolidaci přichází
expanze volatility, je [E] (shlukování volatility), ale že má expanze předvídatelný směr, je jen [I/U].

## 10.4 C9 USD-filtrovaný Donchian H4

C9 je C2 s makro filtrem: breakout se obchoduje jen tehdy, když trend amerického dolaru „souhlasí“
(zlato je oceněné v USD). V DEV měla nejvyšší expectancy ze všech kandidátů (0,192 R, t 1,15) a do plné
validace šla jako druhý náhradník. Ve zmrazené specifikaci je jen pro úplnost a do pořadí se
nedostala. Důvody shrnuje závěr podkapitoly.

### Rekapitulace pravidel

- **Základ:** pravidla C2 beze změny (vstup na proražení 55barového kanálu, stop 2 × ATR20, posun stopu
  na 20barový kanál, výstup přes kanál nebo po 90 barech).
- **Filtr:** USD index (váhy DXY, denní kurzy Fed H.10) proti svému 50dennímu klouzavému průměru,
  posunutý o 1 den (zveřejnění). **Long** je povolen, jen když je index pod průměrem (dolar neposiluje),
  **short** jen když je nad průměrem. Bez platné hodnoty indexu se nevstupuje. Filtr působí jen na
  vstup, výstupy jsou stejné jako u C2.
- **Parametry:** 6 (5 parametrů C2 a usd_ma 50).

Jak strategie fakticky vystupuje [E, vlastní dopočet, DEV+OOS]: 216 z 228 obchodů skončilo stopem
(průměr −0,018 R) a 12 signálem nebo time-stopem (průměr +2,54 R, součet +30,4 R). Stejně jako u C2
nese výsledek hrstka dlouhých trendů. Filtr odstraní zhruba 39 % obchodů C2 (228 místo 373).

### Segmenty

| Segment | Obchody | Obch./rok | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF |
|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 102 | 18,5 | 29,4 | 2,55 | −0,89 | 0,123 | 0,58 | 1,18 |
| DEV 2010–2018 | 144 | 16,0 | 34,0 | 2,23 | −0,86 | 0,192 | 1,15 | 1,31 |
| OOS 2019–2023 | 84 | 16,8 | 25,0 | 2,50 | −0,85 | −0,013 | −0,05 | 0,96 |
| DEV+OOS 2010–2023 | 228 | 16,3 | 30,7 | 2,31 | −0,85 | 0,117 | 0,80 | 1,17 |

Jak číst tabulku: stejné segmenty jako výše. Co z toho plyne: filtr **zlepšil DEV** (0,192 vs. 0,064 R
u C2), ale **zhoršil PRE** (0,123 vs. 0,316 R) **i OOS** (−0,013 vs. +0,094 R) [E]. Filtr přitom nebyl
laděn na DEV (usd_ma 50 je předem deklarovaný default), takže nejde o klasické přeučení. Vztah
zlato–dolar ale prospíval breakoutům jen v jednom období. To odpovídá literatuře o nestabilitě makro
vztahů zlata (kapitola 5) [I]. OOS je prakticky nulové a win rate klesl na 25 %. Křížová kontrola
zdrojů za 2016-09 – 2018-12 (kapitola 7) ukazuje u C9 největší rozdíl ze všech strategií: data A
0,031 R, data B 0,142 R [E]. Silné DEV výsledky C9 z let 2010–2016 (data B) jsou tedy obzvlášť
nejisté.

| Segment | Sharpe | Sortino | CAGR | MaxDD | Calmar | Expozice | Ø držení h | Medián h | Max. série ztrát | Pod vodou (dny) |
|---|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 0,27 | 0,42 | 1,05 % | 6,6 % | 0,16 | 33 % | 156 | 110 | 8 | 785 |
| DEV 2010–2018 | 0,37 | 0,61 | 1,44 % | 5,7 % | 0,25 | 28 % | 156 | 126 | 7 | 940 |
| OOS 2019–2023 | 0,00 | 0,00 | −0,11 % | 12,4 % | −0,01 | 26 % | 132 | 105 | 13 | 1 239 |
| DEV+OOS 2010–2023 | 0,24 | 0,38 | 0,88 % | 12,5 % | 0,07 | 28 % | 147 | 118 | 13 | 1 239 |

Jak číst tabulku: rizikové a časové charakteristiky. Co z toho plyne: filtr snižuje expozici
(28 % proti 45 % u C2) a MaxDD (12,5 % proti 13,4 %). OOS je ale ve znamení nejdelší série ztrát ze všech
trendových variant (13 obchodů) a období pod vodou 1 239 dní, tedy téměř celého OOS.

| Segment | Hrubý PnL | Spread | Skluz | Swap | Čistý PnL | Náklady / hrubý | Obch. L / S | Long PnL | Short PnL |
|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 10 205 | 827 | 530 | −2 924 | 5 924 | 42 % | 63 / 39 | 14 338 | −8 414 |
| DEV 2010–2018 | 19 572 | 1 604 | 1 016 | −3 278 | 13 674 | 30 % | 75 / 69 | 2 481 | 11 193 |
| OOS 2019–2023 | 2 069 | 902 | 552 | −1 538 | −923 | 145 % | 36 / 48 | 7 622 | −8 545 |
| DEV+OOS 2010–2023 | 21 987 | 2 631 | 1 645 | −5 028 | 12 683 | 42 % | 111 / 117 | 11 289 | 1 394 |

Jak číst tabulku: PnL v USD. Co z toho plyne: v OOS náklady (2 992 USD) převýšily hrubý zisk (2 069 USD)
a výsledek skončil ve ztrátě [E]. Směrová skladba má stejný vzorec jako C2: v DEV vydělal short, v OOS
long a short ztrácel. Filtr asymetrii neodstranil.

### Long vs. short

| Strana / segment | Obchody | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF | Sharpe | Čistě % kapitálu | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|---|
| long DEV | 75 | 29,3 | 2,25 | −0,81 | 0,091 | 0,39 | 1,13 | 0,13 | 2,9 % | 152 |
| long OOS | 36 | 30,6 | 3,56 | −0,91 | 0,453 | 0,78 | 1,67 | 0,51 | 8,0 % | 157 |
| long DEV+OOS | 111 | 29,7 | 2,69 | −0,84 | 0,208 | 0,85 | 1,33 | 0,28 | 11,2 % | 153 |
| short DEV | 69 | 39,1 | 2,21 | −0,92 | 0,302 | 1,26 | 1,53 | 0,39 | 10,5 % | 160 |
| short OOS | 48 | 20,8 | 1,33 | −0,81 | −0,362 | −1,98 | 0,42 | −0,77 | −8,2 % | 112 |
| short DEV+OOS | 117 | 31,6 | 1,97 | −0,87 | 0,030 | 0,18 | 1,04 | 0,05 | 1,4 % | 140 |

Jak číst tabulku: samostatné běhy s jedním směrem. Co z toho plyne: **long strana C9 je jediný směr
ze všech pěti strategií, který samostatně prošel branami 1 i 2** (DEV 0,091 R / PF 1,13; OOS 0,453 R /
PF 1,67 / Sharpe 0,51) [E, vlastní dopočet]. Nesmí se to ale přeceňovat. OOS long má jen 36 obchodů
a t 0,78, výsledek nesou dva býčí roky 2019–2020 a v DEV byl long výrazně slabší než short. Short OOS
(−0,362 R, t −1,98) je naopak nejhorší směrový výsledek mezi trendovými strategiemi. Celkově jde
o stejný režimový obrat jako u C2.

### Nákladový stres

| Scénář | D+O obch. | D+O exp. R | D+O PF | D+O Sharpe | D+O CAGR | D+O MaxDD | OOS exp. R | OOS PF | OOS Sharpe | OOS CAGR | OOS MaxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | 222 | 0,282 | 1,48 | 0,53 | 2,18 % | 9,5 % | 0,162 | 1,26 | 0,35 | 1,36 % | 9,5 % |
| baseline ×1,0 | 228 | 0,117 | 1,17 | 0,24 | 0,88 % | 12,5 % | −0,013 | 0,96 | 0,00 | −0,11 % | 12,4 % |
| stres ×1,5 | 228 | 0,083 | 1,12 | 0,17 | 0,61 % | 13,1 % | −0,047 | 0,91 | −0,08 | −0,42 % | 13,2 % |
| stres ×2,0 | 228 | 0,049 | 1,06 | 0,10 | 0,34 % | 13,8 % | −0,082 | 0,86 | −0,15 | −0,69 % | 13,8 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | 226 | 0,171 | 1,27 | 0,34 | 1,32 % | 11,4 % | 0,035 | 1,04 | 0,09 | 0,28 % | 11,4 % |

Jak číst tabulku: stejně jako výše. Co z toho plyne: za DEV+OOS je C9 nákladově nejodolnější
z trendových variant (×2: +0,049 R), protože má méně obchodů a vyšší průměrnou výhru. **V OOS je ale
záporná ve všech scénářích kromě bezfrikčního a ECN** [E]. Hrubá OOS expectancy 0,162 R ukazuje, že
v letech 2019–2023 nějaký hrubý efekt existoval, ale nepřežil běžné náklady.

| Scénář | Období | Hrubý PnL | Spread | Skluz | Komise | Swap | Čistý PnL | Náklady / hrubý |
|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | DEV+OOS | 34 590 | 0 | 0 | 0 | 0 | 34 590 | 0 % |
| hrubě ×0 | OOS | 6 455 | 0 | 0 | 0 | 0 | 6 455 | 0 % |
| baseline ×1,0 | DEV+OOS | 21 987 | 2 631 | 1 645 | 0 | −5 028 | 12 683 | 42 % |
| baseline ×1,0 | OOS | 2 069 | 902 | 552 | 0 | −1 538 | −923 | 145 % |
| stres ×1,5 | DEV+OOS | 22 187 | 3 845 | 2 400 | 0 | −7 379 | 8 563 | 61 % |
| stres ×1,5 | OOS | 2 077 | 1 340 | 820 | 0 | −2 308 | −2 391 | 215 % |
| stres ×2,0 | DEV+OOS | 22 300 | 5 102 | 3 133 | 0 | −9 591 | 4 474 | 80 % |
| stres ×2,0 | OOS | 2 183 | 1 755 | 1 085 | 0 | −3 065 | −3 722 | 271 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | DEV+OOS | 25 128 | 1 352 | 847 | 654 | −2 566 | 19 709 | 22 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | OOS | 2 653 | 453 | 279 | 180 | −746 | 995 | 63 % |

Jak číst tabulku: rozklad v USD. Co z toho plyne: stejně jako u C2 je **nepřímý vliv nákladů velký**
[E, vlastní dopočet]. Bezfrikční čistý PnL DEV+OOS 34 590 USD klesne na 12 683 USD. Z rozdílu 21 906 USD
je jen 9 304 USD explicitních nákladů a 12 602 USD (58 %) připadá na jinou cestu obchodů. V OOS je
nepřímý vliv (4 386 USD) dokonce větší než explicitní náklady (2 992 USD). Mechanismus je zřejmě stejný
jako u C2: stop na extrému kanálu a exekuce na bid/ask [I].

### Zpoždění vstupu

| Varianta | Obchody | Exp. R | Změna R | Změna % | PF | Sharpe | CAGR | MaxDD |
|---|---|---|---|---|---|---|---|---|
| baseline (fill na open dalšího baru) | 228 | 0,1166 | — | — | 1,17 | 0,24 | 0,88 % | 12,5 % |
| zpoždění +1 H1 bar | 227 | 0,0964 | −0,0203 | −17 % | 1,14 | 0,20 | 0,71 % | 12,7 % |
| zpoždění +1 H1 bar a skluz ×3 | 227 | 0,0698 | −0,0468 | −40 % | 1,09 | 0,14 | 0,50 % | 13,3 % |

Jak číst tabulku: stejně jako výše. Co z toho plyne: absolutní ztráta ze zpoždění je **prakticky stejná
jako u C2** (−0,0203 vs. −0,0203 R; se skluzem ×3 −0,0468 vs. −0,0468 R). Penalizace za pozdní vstup je
tedy vlastností breakout vstupu, ne filtru [E]. Relativně je ztráta menší (−17 %), protože C9 má vyšší
výchozí expectancy.

### Perturbace parametrů

| Ukazatel | Hodnota |
|---|---|
| Počet bodů mřížky | 125 |
| Podíl bodů s exp. R > 0 (brána 4) | 100,0 % |
| Podíl bodů s PF > 1 | 100,0 % |
| Sharpe p10 / medián / p90 | 0,17 / 0,27 / 0,36 |
| Exp. R min / p10 / medián / p90 / max | 0,013 / 0,076 / 0,131 / 0,172 / 0,237 |
| Podíl bodů se Sharpe > 0,3 | 33,6 % |
| Počet obchodů min / max | 190 / 303 |
| MaxDD min / medián / max | 7,0 % / 12,2 % / 19,2 % |
| PBO (CSCV, roční bloky) | 0,55 |
| Počet rozdělení CSCV / medián logitu | 3 432 / −0,13 |
| Default: podíl bodů mřížky s nižší exp. R / nižším Sharpe | 38 % / 40 % |
| 26 nejbližších sousedů defaultu: podíl exp. R > 0 / medián exp. R | 100 % / 0,112 |
| Nejlepší bod (exp. R) | entry_n 63, exit_n 25, stop_atr 1,5: 0,237 R, Sharpe 0,37 |
| Nejhorší bod (exp. R) | entry_n 47, exit_n 23, stop_atr 2: 0,013 R, Sharpe 0,04 |
| Nejvyšší Sharpe | entry_n 55, exit_n 17, stop_atr 2,25: Sharpe 0,42, 0,187 R |

Jak číst tabulku: stejná mřížka jako u C2, usd_ma na defaultu 50. Co z toho plyne: všech 125 bodů je
kladných a medián expectancy (0,131 R) je nejvyšší ze všech strategií [E]. Při porovnání bod po bodu
je C9 v DEV+OOS lepší než C2 **ve všech 125 konfiguracích** (medián rozdílu +0,067 R) a má přitom
mediánově 61 % obchodů C2 [E, vlastní dopočet z `grid_C9.csv` a `grid_C2.csv`]. To ale platí pro
spojené DEV+OOS, kde dominuje DEV. PBO 0,55 (medián logitu −0,13) je blízko hodu mincí. Default leží
na 38. percentilu, tedy v dolní polovině mřížky.

| Osa | Hodnota | Medián exp. R | Medián PF | Medián Sharpe | Medián MaxDD | Medián obchodů |
|---|---|---|---|---|---|---|
| entry_n | 41 | 0,112 | 1,16 | 0,25 | 12,1 % | 267 |
| entry_n | 47 | 0,105 | 1,15 | 0,23 | 11,7 % | 259 |
| entry_n | 55 | 0,144 | 1,21 | 0,28 | 11,9 % | 234 |
| entry_n | 63 | 0,142 | 1,20 | 0,27 | 12,1 % | 228 |
| entry_n | 69 | 0,139 | 1,20 | 0,27 | 13,5 % | 219 |
| exit_n | 15 | 0,107 | 1,18 | 0,25 | 12,1 % | 255 |
| exit_n | 17 | 0,149 | 1,25 | 0,33 | 12,6 % | 243 |
| exit_n | 20 | 0,135 | 1,20 | 0,27 | 12,9 % | 234 |
| exit_n | 23 | 0,078 | 1,12 | 0,18 | 12,9 % | 232 |
| exit_n | 25 | 0,156 | 1,22 | 0,30 | 10,8 % | 224 |
| stop_atr | 1,5 | 0,149 | 1,19 | 0,27 | 16,3 % | 253 |
| stop_atr | 1,75 | 0,107 | 1,15 | 0,21 | 15,0 % | 243 |
| stop_atr | 2 | 0,101 | 1,15 | 0,22 | 12,6 % | 234 |
| stop_atr | 2,25 | 0,153 | 1,27 | 0,34 | 9,3 % | 225 |
| stop_atr | 2,5 | 0,137 | 1,25 | 0,32 | 7,8 % | 222 |

Jak číst tabulku: mediány přes 25 bodů s danou hodnotou osy. Co z toho plyne: tvar os je stejný jako
u C2 (lepší delší vstupní kanál, pokles u exit_n 23, širší stop s nižším MaxDD), jen posunutý nahoru.
Filtr tedy nemění strukturu, jen vybírá podmnožinu obchodů C2 [I]. Pokles u exit_n 23, který se
objevuje u obou strategií, je vlastností konkrétní cesty cen, ne parametru.

| entry_n (řádek) / exit_n (sloupec) | 15 | 17 | 20 | 23 | 25 |
|---|---|---|---|---|---|
| 41 | 0,104 | 0,149 | 0,131 | 0,078 | 0,137 |
| 47 | 0,096 | 0,147 | 0,119 | 0,068 | 0,134 |
| 55 | 0,127 | 0,167 | 0,156 | 0,107 | 0,172 |
| 63 | 0,117 | 0,152 | 0,142 | 0,092 | 0,171 |
| 69 | 0,118 | 0,158 | 0,149 | 0,101 | 0,168 |

Jak číst tabulku: medián expectancy (R) přes pět hodnot stop_atr pro každou dvojici entry_n × exit_n,
tedy stejná konstrukce jako heatmapy C3, C2 a C5. Pro C9 obrázek v `research/results/figures/`
neexistuje, tabulka je vlastní dopočet z `grid_C9.csv`. Co z toho plyne: plato 0,07–0,17 R bez
osamocené špičky; default (55, 20) má medián 0,156 R a leží v lepší části.

| Parametr | Hodnota | Obchody | Exp. R | PF | Sharpe | CAGR | MaxDD |
|---|---|---|---|---|---|---|---|
| usd_ma | 38 | 231 | 0,106 | 1,16 | 0,23 | 0,81 % | 10,0 % |
| usd_ma | 44 | 229 | 0,146 | 1,23 | 0,29 | 1,12 % | 10,5 % |
| usd_ma | 50 | 228 | 0,117 | 1,17 | 0,24 | 0,88 % | 12,5 % |
| usd_ma | 56 | 225 | 0,135 | 1,20 | 0,27 | 1,02 % | 13,1 % |
| usd_ma | 63 | 225 | 0,102 | 1,14 | 0,21 | 0,75 % | 13,5 % |

Jak číst tabulku: jednorozměrný řez délkou průměru USD indexu, ostatní parametry na defaultu. Co
z toho plyne: všech pět délek je kladných (0,102–0,146 R) a počet obchodů se téměř nemění (225–231).
Na přesné délce průměru výsledek nezávisí [E]. Robustnost vůči usd_ma ale nic neříká o tom, zda vztah
zlato–dolar bude platit i v budoucnu (OOS ukazuje, že spíš ne).

### Timeframe

| TF | Parametry | Obchody | Exp. R | t | PF | Sharpe | CAGR | MaxDD | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|
| H2 | vstup 110, výstup 40, ATR 40, max 180 | 255 | 0,255 | 1,41 | 1,33 | 0,40 | 2,20 % | 17,2 % | 119 |
| H3 | vstup 73, výstup 27, ATR 27, max 120 | 235 | 0,149 | 0,92 | 1,20 | 0,27 | 1,17 % | 16,2 % | 136 |
| H4 | vstup 55, výstup 20, ATR 20, max 90 (default) | 228 | 0,117 | 0,80 | 1,17 | 0,24 | 0,88 % | 12,5 % | 147 |
| H6 | vstup 37, výstup 13, ATR 13, max 60 | 208 | 0,126 | 0,96 | 1,23 | 0,29 | 0,90 % | 7,6 % | 167 |
| D1 | vstup 9, výstup 3, ATR 3, max 15 | 171 | 0,023 | 0,34 | 1,08 | 0,10 | 0,14 % | 4,9 % | 220 |

Jak číst tabulku: stejné přepočty jako u C2, filtr USD je denní a nemění se. Co z toho plyne: všech pět
timeframů je kladných a pořadí kopíruje C2 (H2 nejlepší, D1 nejslabší) [E].

### Walk-forward

| Test | Trénink | Vybrané parametry | Train Sharpe | Test výnos | Default výnos | Rozdíl p. b. |
|---|---|---|---|---|---|---|
| 2014 | 2010–2013 | entry_n 69, exit_n 20, stop_atr 2 | 0,75 | −2,8 % | −2,4 % | −0,4 |
| 2015 | 2011–2014 | entry_n 41, exit_n 15, stop_atr 2 | 0,57 | 1,1 % | 2,2 % | −1,1 |
| 2016 | 2012–2015 | entry_n 69, exit_n 25, stop_atr 2 | 0,51 | 4,8 % | 5,0 % | −0,2 |
| 2017 | 2013–2016 | entry_n 41, exit_n 20, stop_atr 2 | 0,58 | 1,3 % | 0,3 % | 1,0 |
| 2018 | 2014–2017 | entry_n 41, exit_n 20, stop_atr 2 | 0,46 | −2,7 % | −2,6 % | 0,0 |
| 2019 | 2015–2018 | entry_n 41, exit_n 20, stop_atr 2 | 0,51 | −2,5 % | −1,8 % | −0,8 |
| 2020 | 2016–2019 | entry_n 41, exit_n 20, stop_atr 2 | 0,16 | 4,5 % | 5,7 % | −1,3 |
| 2021 | 2017–2020 | entry_n 55, exit_n 15, stop_atr 2 | 0,26 | −3,4 % | −4,9 % | 1,5 |
| 2022 | 2018–2021 | entry_n 69, exit_n 15, stop_atr 2 | 0,18 | −2,1 % | −1,2 % | −0,9 |
| 2023 | 2019–2022 | entry_n 55, exit_n 25, stop_atr 2 | 0,08 | 2,1 % | 2,0 % | 0,1 |

Jak číst tabulku: stejná 3 × 3 mřížka jako u C2. Co z toho plyne: spojený walk-forward výnos je
**−0,2 %** (Sharpe 0,01, kladných 5 z 10 let), **brána 5 splněna není** [E]. Ani pevný default nebyl
o moc lepší (+1,8 % za 10 let) a walk-forward ho porazil jen ve 3 letech [E, vlastní dopočet].
Nejlepší tréninkový Sharpe s výkyvy klesá z 0,75 (okno 2010–2013) na 0,08 (okno 2019–2022). Filtr
ztrácel účinnost i uvnitř tréninkových oken, což je další známka slábnoucího vztahu [I].

### Bootstrap

| Metrika (trade bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| CAGR | −0,98 % | 0,83 % | 2,95 % |
| Expectancy R | −0,113 | 0,113 | 0,374 |
| Profit factor | 0,82 | 1,19 | 1,67 |
| Max drawdown | 6,3 % | 11,1 % | 21,0 % |
| Nejdelší série ztrát (obchody) | 8 | 12 | 19 |
| Nejdelší úsek pod maximem (obchody) | 44 | 106 | 222 |

Jak číst tabulku: 10 000× převzorkováno 228 obchodů. P(expectancy > 0) = **78,3 %**. Co z toho plyne:
**brána 7 splněna není**. Interval expectancy (−0,113 až 0,374 R) je nejširší ze všech strategií,
protože C9 má málo obchodů a výsledek závisí na několika velkých výhrách. Medián úseku pod maximem
106 obchodů odpovídá při 16,3 obchodu ročně asi 6,5 roku [E, vlastní dopočet].

| Metrika (blokový bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| Sharpe | −0,24 | 0,22 | 0,66 |
| CAGR | −0,94 % | 0,80 % | 2,74 % |
| Max drawdown | 7,3 % | 12,2 % | 21,7 % |

Jak číst tabulku: blokový bootstrap denních výnosů. P(Sharpe > 0) = **78,9 %**. Co z toho plyne:
stejný závěr jako u ostatních trendových variant, kladný Sharpe je pravděpodobnější než záporný,
ale nula leží hluboko uvnitř intervalu.

### Režimy

| Dimenze | Stav | Obchody | Exp. R | Win % | PF | Long exp. R | Short exp. R | Denní Sharpe |
|---|---|---|---|---|---|---|---|---|
| trend | range (bez trendu) | 167 | 0,016 | 31,1 | 1,02 | 0,040 | −0,006 | 0,20 |
| trend | trending | 61 | 0,392 | 29,5 | 1,58 | 0,662 | 0,130 | 0,31 |
| volatilita | vysoká | 85 | −0,229 | 24,7 | 0,62 | −0,341 | −0,139 | −0,36 |
| volatilita | nízká | 143 | 0,322 | 34,3 | 1,55 | 0,494 | 0,143 | 0,69 |
| USD (60 d) | silný USD | 124 | 0,051 | 33,1 | 1,06 | 0,268 | −0,041 | −0,18 |
| USD (60 d) | slabý USD | 104 | 0,195 | 27,9 | 1,32 | 0,178 | 0,235 | 0,66 |
| výnosy 10Y (60 d) | klesající | 121 | −0,029 | 28,1 | 0,93 | −0,044 | −0,012 | 0,16 |
| výnosy 10Y (60 d) | rostoucí | 107 | 0,281 | 33,6 | 1,48 | 0,528 | 0,072 | 0,34 |
| VIX | krize (VIX > 25) | 34 | −0,234 | 29,4 | 0,55 | −0,310 | −0,202 | 0,31 |
| VIX | normál | 194 | 0,178 | 30,9 | 1,27 | 0,260 | 0,090 | 0,22 |

Jak číst tabulku: stejné štítky jako výše. Co z toho plyne: profil je stejný jako u C2 (trending
+0,392 R, nízká volatilita +0,322 R, vysoká volatilita −0,229 R, krize −0,234 R). Zajímavý je rozpor
v krizovém řádku: expectancy obchodů vstoupených v krizi je záporná, ale denní Sharpe krizových dní je
kladný (0,31). Ve dnech s VIX > 25 totiž vydělávaly pozice otevřené už před krizí [I]. Long
v režimu „silný USD“ (+0,268 R) je překvapivě lepší než v režimu „slabý USD“ (+0,178 R). 60denní
změna dolaru tedy nejde se zvoleným filtrem (index proti 50dennímu průměru) dohromady tak, jak by
předpokládala ekonomická logika filtru [I].

### Roky a bloky

| Rok | Segment | Obchody | Exp. R | Čistý PnL | Long PnL | Short PnL | Kumulativně |
|---|---|---|---|---|---|---|---|
| 2010 | DEV | 14 | −0,183 | −1 239 | 1 035 | −2 275 | −1 239 |
| 2011 | DEV | 20 | 0,590 | 5 603 | 5 698 | −95 | 4 364 |
| 2012 | DEV | 11 | 0,214 | 1 218 | 1 066 | 152 | 5 582 |
| 2013 | DEV | 13 | 0,821 | 5 507 | 126 | 5 380 | 11 089 |
| 2014 | DEV | 21 | −0,225 | −2 646 | −3 094 | 448 | 8 443 |
| 2015 | DEV | 17 | 0,271 | 2 395 | −2 511 | 4 906 | 10 839 |
| 2016 | DEV | 14 | 0,725 | 5 560 | 2 665 | 2 895 | 16 398 |
| 2017 | DEV | 17 | −0,241 | −2 393 | −2 137 | −255 | 14 006 |
| 2018 | DEV | 17 | −0,032 | −332 | −368 | 36 | 13 674 |
| 2019 | OOS | 16 | −0,504 | −4 453 | −1 631 | −2 822 | 9 221 |
| 2020 | OOS | 14 | 1,163 | 8 862 | 11 216 | −2 354 | 18 083 |
| 2021 | OOS | 18 | −0,568 | −5 811 | −1 200 | −4 611 | 12 272 |
| 2022 | OOS | 19 | −0,132 | −1 391 | 633 | −2 024 | 10 881 |
| 2023 | OOS | 17 | 0,202 | 1 802 | −211 | 2 013 | 12 683 |

Jak číst tabulku: rok výstupu obchodu, USD. Co z toho plyne: kladných je 7 ze 14 let a **rok 2020 tvoří
70 % celkového zisku** (brána 6 selhává). Bez něj by zbylo 3 821 USD [E, vlastní dopočet]. Roční
výsledky C9 jsou ze všech trendových variant nejrozkolísanější (expectancy od −0,568 do +1,163 R),
protože jde o málo obchodů ročně (11–21) s velkými výhrami.

| Blok | Obchody | Exp. R | PF | Čistý PnL |
|---|---|---|---|---|
| 2010–2012 | 45 | 0,258 | 1,50 | 5 582 |
| 2013–2015 | 51 | 0,207 | 1,31 | 5 256 |
| 2016–2018 | 48 | 0,115 | 1,18 | 2 836 |
| 2019–2021 | 48 | −0,042 | 0,93 | −1 402 |
| 2022–2023 | 36 | 0,025 | 1,04 | 411 |

Jak číst tabulku: tříleté bloky. Co z toho plyne: **postupný pokles** od +0,258 R v prvním bloku
přes +0,207 a +0,115 až k −0,042 R; poslední dvouletý blok je jen mírně nad nulou (+0,025 R) [E]. Filtr fungoval nejlépe na začátku DEV a postupně
ztrácel účinnost. To je v souladu s klesajícím tréninkovým Sharpe ve walk-forward.

### Deflated Sharpe a PSR

| Varianta | N | T (dní) | SR (anual.) | SR0 (anual.) | PSR (SR > 0) | DSR |
|---|---|---|---|---|---|---|
| DEV+OOS, N = 60 (konzervativní) | 60 | 3 605 | 0,24 | 1,46 | 0,82 | 0,00 |
| jen OOS, N = 60 | 60 | 1 290 | −0,01 | 1,46 | 0,49 | 0,00 |
| DEV+OOS, N = 125 (v rámci mřížky) | 125 | 3 605 | 0,24 | 0,21 | 0,82 | 0,55 |

Jak číst tabulku: stejná metodika jako výše. Co z toho plyne: v mírnější variantě má C9 nejvyšší DSR
ze všech (0,55), protože pozorovaný Sharpe za DEV+OOS je relativně vysoký a mřížka úzká. OOS PSR 0,49
ale znamená, že v samotném OOS je kladný a záporný Sharpe stejně pravděpodobný. Vysoké DSR za
DEV+OOS tedy stojí na DEV [I].

### Brány

| Brána | Podmínka | Hodnota | Splněno |
|---|---|---|---|
| 1 | DEV: exp. R > 0 a PF > 1,10 | exp. 0,192 R, PF 1,310 | ANO |
| 2 | OOS: exp. R > 0, PF > 1,05, Sharpe > 0,3 | exp. −0,013 R, PF 0,96, Sharpe 0,00 | NE |
| 3 | náklady ×1,5: exp. R DEV+OOS > 0 | 0,083 R | ANO |
| 4 | ≥ 70 % bodů mřížky s exp. R > 0 | 100 % | ANO |
| 5 | walk-forward spojený výsledek > 0 | −0,2 % | NE |
| 6 | žádný rok > 50 % čistého zisku | 70 % | NE |
| 7 | bootstrap P(exp. R > 0) ≥ 90 % | 78,3 % | NE |
| Vše | brány 1–7 současně | splněno 3 ze 7 | NE |

Jak číst tabulku: hodnoty z `s02_C9.json`. Co z toho plyne: C9 je jediná trendová varianta, která
neprošla walk-forward bránou. Selhání na branách 2 a 5 jsou dvě nezávislé známky, že výhoda filtru
z DEV se do pozdějších let nepřenesla.

### Celkové hodnocení C9

> **Závěr:** C9 je učebnicový případ filtru, který vypadá skvěle v DEV (nejvyšší expectancy 0,192 R,
> 100% kladná mřížka, nejvyšší DSR v mírnější variantě) a nepřežije OOS (−0,013 R, walk-forward −0,2 %,
> postupně slábnoucí tříleté bloky). Prakticky jde o podmnožinu obchodů C2: denní korelace výnosů C2 a C9 je
> 0,79, korelace drawdownů 0,86 a když jsou obě v trhu, jsou ve 100 % případů ve stejném směru
> (`s03_portfolio_C2_C3_C5_C9.md`, kapitola 11). Navíc vyžaduje živý a včas aktualizovaný USD index
> s vahami DXY, což je další provozní závislost. Splnila 3 ze 7 bran. **Vyřazena** z pořadí: k C2
> nepřidává diverzifikaci a její navíc přidaná logika (filtr) v OOS nefungovala.

Typ důkazu: čísla jsou [E]; ekonomické zdůvodnění filtru (zlato je oceněné v USD, slabý dolar
podporuje zlato) je [R], ale jeho stabilita v čase je v datech vyvrácena spíš než potvrzena; vysvětlení
rozporu v krizovém řádku je [I].

## 10.5 C8b Session (zamítnutá)

C8b je **datově odvozená revize** předregistrované session strategie C8, která na DEV selhala už před
náklady. Revize vznikla z hodinového profilu výnosů na DEV (kapitola 8). Zlato v DEV rostlo
v asijských hodinách a klesalo v londýnské seanci, kdežto předregistrované okno C8 obě fáze míchalo.
Protože okna byla vybrána podle DEV dat, je C8b v DEV **optimisticky zkreslená** (data-mining
riziko). Do validace šla transparentně jako jediná ne-momentum anomálie se silným hrubým efektem,
„podmíněná náklady“. Podle zadání se strategie, která funguje jen před náklady, zamítá.

### Rekapitulace pravidel

- **Data a timeframe:** H1 bary, serverový čas NY+7, žádné parametry laděné na výnos (pevné hodiny).
- **Long noha:** nákup na open serverové hodiny 02 (19:00 NY, po normalizaci spreadu po denním
  znovuotevření), prodej na open hodiny 09 (02:00 NY, před otevřením Londýna).
- **Short noha:** prodej na open hodiny 09, krytí na open hodiny 15 (08:00 NY, před otevřením COMEX).
  V 09:00 nastává exit-and-reverse (nejdřív zavřít long, pak otevřít short).
- **Signál** vzniká na close H1 baru před cílovou hodinou, takže market příkaz se plní na open cílové
  hodiny. Vstupy jen pondělí až pátek.
- **Katastrofický stop:** 1,0 × průměrné denní rozpětí (klouzavé 23hodinové high − low, průměr
  za 20 dní). Maximální držení 20 hodin.
- **Swap:** žádný, obě nohy končí před rolloverem v 17:00 NY.

Jak strategie fakticky vystupuje [E, vlastní dopočet, DEV+OOS]: 7 104 ze 7 149 obchodů skončilo
plánovaně koncem okna s průměrem +0,0019 R. Jen 45 obchodů (0,6 %) zasáhlo katastrofický stop
s průměrem −0,99 R. I bez těchto stopů je čistý edge běžného obchodu zhruba 0,002 R, tedy
zanedbatelný proti typickému pohybu ±0,2 R za okno.

### Segmenty

| Segment | Obchody | Obch./rok | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF |
|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 2 757 | 501,1 | 49,7 | 0,22 | −0,23 | −0,005 | −0,86 | 0,95 |
| DEV 2010–2018 | 4 569 | 508,2 | 51,1 | 0,20 | −0,20 | 0,003 | 0,62 | 1,02 |
| OOS 2019–2023 | 2 580 | 516,9 | 46,3 | 0,20 | −0,20 | −0,017 | −3,11 | 0,84 |
| DEV+OOS 2010–2023 | 7 149 | 511,2 | 49,4 | 0,20 | −0,20 | −0,004 | −1,32 | 0,96 |

Jak číst tabulku: stejné segmenty jako výše. Při 510 obchodech ročně má t-statistika mnohem větší
sílu než u trendových strategií. Co z toho plyne: po nákladech je C8b kladná **jen v DEV, ze kterého
byla odvozena** (+0,003 R, PF 1,02, ani to nestačí na bránu 1). V nezávislém PRE i v OOS je záporná
a OOS **statisticky významně** (t −3,11) [E]. Průměrný zisk i ztráta jsou ±0,20 R. Typický pohyb za
6–7 hodin je tedy pětina katastrofického stopu a o výsledku rozhoduje malá asymetrie win rate (51 %
v DEV, 46 % v OOS).

| Segment | Sharpe | Sortino | CAGR | MaxDD | Calmar | Expozice | Ø držení h | Medián h | Max. série ztrát | Pod vodou (dny) |
|---|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | −0,37 | −0,51 | −1,31 % | 10,6 % | −0,12 | 57 % | 7 | 6 | 9 | 1 973 |
| DEV 2010–2018 | 0,21 | 0,30 | 0,59 % | 14,9 % | 0,04 | 56 % | 7 | 6 | 12 | 707 |
| OOS 2019–2023 | −1,41 | −1,87 | −4,16 % | 21,1 % | −0,20 | 56 % | 6 | 6 | 14 | 1 803 |
| DEV+OOS 2010–2023 | −0,35 | −0,50 | −1,14 % | 31,9 % | −0,04 | 56 % | 6 | 6 | 14 | 2 531 |

Jak číst tabulku: rizikové a časové charakteristiky. Co z toho plyne: OOS Sharpe −1,41 a MaxDD 31,9 %
za DEV+OOS jsou nejhorší čísla celé validace [E]. Expozice 56 % znamená, že strategie je v trhu každý
pracovní den 13 hodin. Období pod vodou 2 531 dní (téměř 7 let) zabírá většinu DEV+OOS.

| Segment | Hrubý PnL | Spread | Skluz | Swap | Čistý PnL | Náklady / hrubý | Obch. L / S | Long PnL | Short PnL |
|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–2009 (B) | 12 849 | 15 052 | 4 765 | −17 | −6 986 | 154 % | 1 366 / 1 391 | 3 404 | −10 390 |
| DEV 2010–2018 | 53 414 | 36 612 | 11 352 | −4 | 5 446 | 90 % | 2 262 / 2 307 | −3 115 | 8 560 |
| OOS 2019–2023 | 5 079 | 18 862 | 5 335 | 0 | −19 118 | 476 % | 1 290 / 1 290 | −6 366 | −12 751 |
| DEV+OOS 2010–2023 | 58 612 | 56 497 | 16 974 | −4 | −14 863 | 125 % | 3 552 / 3 597 | −9 909 | −4 954 |

Jak číst tabulku: PnL v USD. Co z toho plyne: **hrubý zisk je kladný ve všech segmentech** (v DEV
53 414 USD), ale spread a skluz ho převyšují všude kromě DEV. I tam z něj zbývá jen 10 % [E].
Anomálie je tedy skutečná v hrubém smyslu, ale velikostí odpovídá nákladům na její obchodování.
Swap je nulový (obchody nepřecházejí přes rollover), takže jediným nákladem je spread a skluz.

### Long vs. short

| Strana / segment | Obchody | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF | Sharpe | Čistě % kapitálu | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|---|
| long DEV | 2 263 | 49,9 | 0,18 | −0,18 | −0,002 | −0,44 | 0,97 | −0,15 | −2,8 % | 7 |
| long OOS | 1 290 | 47,2 | 0,18 | −0,19 | −0,011 | −1,64 | 0,88 | −0,75 | −7,0 % | 7 |
| long DEV+OOS | 3 553 | 48,9 | 0,18 | −0,18 | −0,006 | −1,32 | 0,94 | −0,35 | −9,4 % | 7 |
| short DEV | 2 307 | 52,2 | 0,22 | −0,23 | 0,007 | 1,15 | 1,06 | 0,39 | 8,3 % | 6 |
| short OOS | 1 290 | 45,4 | 0,21 | −0,22 | −0,022 | −2,70 | 0,81 | −1,20 | −13,1 % | 6 |
| short DEV+OOS | 3 597 | 49,8 | 0,22 | −0,22 | −0,003 | −0,64 | 0,97 | −0,16 | −5,9 % | 6 |

Jak číst tabulku: samostatné běhy jedné nohy. Co z toho plyne: po nákladech byla v DEV kladná jen
short (londýnská) noha (+0,007 R, PF 1,06, pod prahem brány 1). Asijská long noha byla po nákladech
záporná i v DEV [E]. V OOS jsou obě nohy záporné a short noha významně (t −2,70). Žádná noha samostatně
neprošla branami 1 a 2.

### Nákladový stres

| Scénář | D+O obch. | D+O exp. R | D+O PF | D+O Sharpe | D+O CAGR | D+O MaxDD | OOS exp. R | OOS PF | OOS Sharpe | OOS CAGR | OOS MaxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | 7 149 | 0,016 | 1,15 | 1,26 | 4,02 % | 9,9 % | 0,005 | 1,05 | 0,40 | 1,22 % | 9,2 % |
| baseline ×1,0 | 7 149 | −0,004 | 0,96 | −0,35 | −1,14 % | 31,9 % | −0,017 | 0,84 | −1,41 | −4,16 % | 21,1 % |
| stres ×1,5 | 7 149 | −0,014 | 0,88 | −1,15 | −3,56 % | 43,6 % | −0,027 | 0,76 | −2,30 | −6,67 % | 30,5 % |
| stres ×2,0 | 7 149 | −0,024 | 0,81 | −1,96 | −5,93 % | 57,8 % | −0,038 | 0,68 | −3,21 | −9,15 % | 39,0 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | 7 149 | 0,002 | 1,02 | 0,16 | 0,43 % | 23,4 % | −0,009 | 0,91 | −0,79 | −2,36 % | 14,6 % |

Jak číst tabulku: stejná struktura jako výše. Co z toho plyne: **bezfrikčně má C8b nejvyšší Sharpe
celé validace (1,26)**, po baseline nákladech je ale záporná. Rozdíl mezi ×0 a ×1 odpovídá asi
0,020 R nákladů na obchod, přičemž hrubý edge je 0,016 R [E, vlastní dopočet]. Ani optimistický ECN
scénář nedává kladné OOS (−0,009 R). Při ×2 by MaxDD dosáhl 57,8 %. Podle zadání („strategie, která
funguje jen před náklady, se zamítá“) je to zamítavý důvod sám o sobě.

| Scénář | Období | Hrubý PnL | Spread | Skluz | Komise | Swap | Čistý PnL | Náklady / hrubý |
|---|---|---|---|---|---|---|---|---|
| hrubě ×0 | DEV+OOS | 73 546 | 0 | 0 | 0 | 0 | 73 546 | 0 % |
| hrubě ×0 | OOS | 6 255 | 0 | 0 | 0 | 0 | 6 255 | 0 % |
| baseline ×1,0 | DEV+OOS | 58 612 | 56 497 | 16 974 | 0 | −4 | −14 863 | 125 % |
| baseline ×1,0 | OOS | 5 079 | 18 862 | 5 335 | 0 | 0 | −19 118 | 476 % |
| stres ×1,5 | DEV+OOS | 52 786 | 71 122 | 21 452 | 0 | −5 | −39 795 | 175 % |
| stres ×1,5 | OOS | 4 725 | 26 409 | 7 459 | 0 | 0 | −29 143 | 717 % |
| stres ×2,0 | DEV+OOS | 47 404 | 80 463 | 24 371 | 0 | −7 | −57 437 | 221 % |
| stres ×2,0 | OOS | 4 088 | 32 866 | 9 275 | 0 | 0 | −38 053 | 1 031 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | DEV+OOS | 62 684 | 31 530 | 9 452 | 15 455 | −2 | 6 244 | 90 % |
| ECN (×0,5 + 3,5 USD/lot/strana) | OOS | 5 368 | 9 905 | 2 803 | 3 879 | 0 | −11 219 | 309 % |

Jak číst tabulku: rozklad v USD. Co z toho plyne: spread je u C8b řádově větší položka než
u trendových strategií (56 497 USD proti 1 806–6 309 USD), protože strategie obchoduje 510krát ročně.
Bezfrikční čistý PnL 73 546 USD se v baseline změní na −14 863 USD. Z rozdílu 88 409 USD je 73 475 USD
explicitních nákladů a asi 14 930 USD nepřímý vliv [E, vlastní dopočet].

### Zpoždění vstupu

| Varianta | Obchody | Exp. R | Změna R | Změna % | PF | Sharpe | CAGR | MaxDD |
|---|---|---|---|---|---|---|---|---|
| baseline (fill na open dalšího baru) | 7 149 | −0,0044 | — | — | 0,96 | −0,35 | −1,14 % | 31,9 % |
| zpoždění +1 H1 bar | 7 147 | −0,0105 | −0,0062 | — | 0,92 | −0,75 | −2,68 % | 39,0 % |
| zpoždění +1 H1 bar a skluz ×3 | 7 147 | −0,0199 | −0,0155 | — | 0,86 | −1,41 | −4,90 % | 53,7 % |

Jak číst tabulku: procentní změna se u záporné výchozí hodnoty neuvádí. Co z toho plyne: hodinové
zpoždění stojí 0,0062 R na obchod, což je **asi 39 % celého hrubého edge** (0,0159 R) [E, vlastní
dopočet]. Session strategie je na načasování kritická. Výpadek, pozdní plnění nebo rozšířený spread
v hodinách vstupu ji v praxi zničí. U trendových strategií je to naopak.

### Perturbace parametrů

| Ukazatel | Hodnota |
|---|---|
| Počet bodů mřížky | 18 |
| Podíl bodů s exp. R > 0 (brána 4) | 0,0 % |
| Podíl bodů s PF > 1 | 0,0 % |
| Sharpe p10 / medián / p90 | −0,59 / −0,38 / −0,19 |
| Exp. R min / p10 / medián / p90 / max | −0,014 / −0,008 / −0,005 / −0,003 / −0,003 |
| Podíl bodů se Sharpe > 0,3 | 0,0 % |
| Počet obchodů min / max | 3 597 / 7 183 |
| MaxDD min / medián / max | 16,2 % / 29,9 % / 33,8 % |
| PBO (CSCV, roční bloky) | 0,68 |
| Počet rozdělení CSCV / medián logitu | 3 432 / −0,61 |

Jak číst tabulku: mřížka má dvě části po 9 bodech. Long okno vstup {01, 02, 03} × výstup {08, 09, 10}
při short okně 09→15, a short okno vstup {08, 09, 10} × výstup {14, 15, 16} při long okně 02→09. Stop
se testuje zvlášť (OAT). Co z toho plyne: **všech 18 variant je po nákladech záporných** (brána 4:
0 %) [E]. Nejde tedy o smůlu jednoho okna, ale o celou oblast. PBO 0,68 je u mřížky, kde je všechno
záporné, jen doplňková informace.

| Varianta (serverový čas) | Obchody | Exp. R | PF | Sharpe | CAGR | MaxDD |
|---|---|---|---|---|---|---|
| long 01→08, short 09→15 | 3 638 | −0,0034 | 0,970 | −0,17 | −0,46 % | 21,5 % |
| long 01→09, short 09→15 | 3 638 | −0,0033 | 0,971 | −0,17 | −0,46 % | 21,4 % |
| long 01→10, short 09→15 | 3 597 | −0,0040 | 0,965 | −0,20 | −0,53 % | 22,3 % |
| long 02→08, short 09→15 | 7 115 | −0,0052 | 0,951 | −0,43 | −1,34 % | 29,3 % |
| long 02→09, short 09→15 | 7 149 | −0,0044 | 0,960 | −0,35 | −1,14 % | 31,9 % |
| long 02→10, short 09→15 | 3 618 | −0,0100 | 0,909 | −0,56 | −1,28 % | 21,4 % |
| long 03→08, short 09→15 | 7 151 | −0,0064 | 0,939 | −0,54 | −1,65 % | 31,2 % |
| long 03→09, short 09→15 | 7 183 | −0,0055 | 0,951 | −0,44 | −1,41 % | 33,2 % |
| long 03→10, short 09→15 | 3 616 | −0,0135 | 0,873 | −0,79 | −1,72 % | 24,1 % |
| long 02→09, short 08→14 | 3 608 | −0,0041 | 0,956 | −0,26 | −0,54 % | 16,5 % |
| long 02→09, short 08→15 | 3 608 | −0,0043 | 0,955 | −0,27 | −0,56 % | 16,5 % |
| long 02→09, short 08→16 | 3 608 | −0,0031 | 0,966 | −0,20 | −0,42 % | 16,2 % |
| long 02→09, short 09→14 | 7 149 | −0,0048 | 0,954 | −0,41 | −1,25 % | 33,8 % |
| long 02→09, short 09→15 | 7 149 | −0,0044 | 0,960 | −0,35 | −1,14 % | 31,9 % |
| long 02→09, short 09→16 | 7 148 | −0,0037 | 0,971 | −0,25 | −0,98 % | 33,2 % |
| long 02→09, short 10→14 | 7 118 | −0,0072 | 0,927 | −0,66 | −1,83 % | 32,9 % |
| long 02→09, short 10→15 | 7 118 | −0,0066 | 0,937 | −0,56 | −1,68 % | 30,5 % |
| long 02→09, short 10→16 | 7 116 | −0,0060 | 0,951 | −0,43 | −1,55 % | 32,6 % |

Jak číst tabulku: všech 18 bodů z `grid_C8b.csv` (default 02→09 / 09→15 je v obou částech).
Expectancy na čtyři desetinná místa. **Důležité upozornění, nový nález [E, vlastní dopočet]:** osm
variant má jen asi 3 600 obchodů místo asi 7 150 a fakticky obchoduje **jen jedna noha**. Ověřil jsem
to přepočtem počtu obchodů podle směru:

- long vstup v 01 (tři varianty): long noha má jen 41 obchodů a obchoduje fakticky jen short.
  Signál pro vstup v 01:00 by vznikl na close baru 00:00–01:00, který připadá na denní přestávku
  (17:00–18:00 NY) a v datech většinou chybí [I];
- long výstup v 10 při short vstupu v 09 (varianty 02→10 a 03→10): long je ještě otevřený, short
  nemůže vzniknout (65, resp. 29 shortů), obchoduje jen long;
- short vstup v 08 při long výstupu v 09 (tři varianty): short nevznikne (55 shortů), obchoduje jen long.

I tyto jednonohé varianty jsou záporné, závěr o C8b se tedy nemění. Mřížka ale není „čistá“
perturbace oken, jak by se z protokolu mohlo zdát, a její vypovídací hodnota je menší. Z pohledu
navazujícího vývoje jde o konstrukční vlastnost: strategie s jednou pozicí neumí překrývající se
okna.

| Osa | Hodnota | Medián exp. R | Medián PF | Medián Sharpe | Medián MaxDD | Medián obchodů |
|---|---|---|---|---|---|---|
| long_entry_hour | 1 | −0,003 | 0,97 | −0,17 | 21,5 % | 3 638 |
| long_entry_hour | 2 | −0,005 | 0,95 | −0,43 | 29,3 % | 7 115 |
| long_entry_hour | 3 | −0,006 | 0,94 | −0,54 | 31,2 % | 7 151 |
| long_exit_hour | 8 | −0,005 | 0,95 | −0,43 | 29,3 % | 7 115 |
| long_exit_hour | 9 | −0,004 | 0,96 | −0,35 | 31,9 % | 7 149 |
| long_exit_hour | 10 | −0,010 | 0,91 | −0,56 | 22,3 % | 3 616 |
| short_entry_hour | 8 | −0,004 | 0,96 | −0,26 | 16,5 % | 3 608 |
| short_entry_hour | 9 | −0,004 | 0,96 | −0,35 | 33,2 % | 7 149 |
| short_entry_hour | 10 | −0,007 | 0,94 | −0,56 | 32,6 % | 7 118 |
| short_exit_hour | 14 | −0,005 | 0,95 | −0,41 | 32,9 % | 7 118 |
| short_exit_hour | 15 | −0,004 | 0,95 | −0,35 | 30,5 % | 7 118 |
| short_exit_hour | 16 | −0,004 | 0,97 | −0,25 | 32,6 % | 7 116 |

Jak číst tabulku: mediány přes tři body s danou hodnotou osy. Co z toho plyne: všechny mediány jsou
záporné. Nejméně záporné jsou hodnoty spojené s jednonohými variantami, protože poloviční počet
obchodů znamená poloviční náklady. Nejde o známku lepšího okna.

| Parametr | Hodnota | Obchody | Exp. R | PF | Sharpe | CAGR | MaxDD |
|---|---|---|---|---|---|---|---|
| stop_atr | 0,75 | 7 149 | −0,007 | 0,96 | −0,41 | −1,79 % | 40,9 % |
| stop_atr | 1 | 7 149 | −0,004 | 0,96 | −0,35 | −1,14 % | 31,9 % |
| stop_atr | 1,25 | 7 149 | −0,003 | 0,96 | −0,34 | −0,88 % | 26,4 % |
| stop_atr | 1,5 | 7 149 | −0,003 | 0,96 | −0,32 | −0,68 % | 21,8 % |

Jak číst tabulku: jednorozměrný řez velikostí katastrofického stopu v násobcích průměrného denního
rozpětí. Co z toho plyne: širší stop mírně zlepšuje expectancy a výrazně snižuje MaxDD (40,9 % →
21,8 %). Menší pozice při stejném riziku znamená menší dopad nákladů v USD [I]. Žádná varianta ale
není kladná.

### Timeframe

| TF | Parametry | Obchody | Exp. R | t | PF | Sharpe | CAGR | MaxDD | Ø držení h |
|---|---|---|---|---|---|---|---|---|---|
| M30 (A) | hranice 02, 09, 15 | 3 757 | −0,017 | −3,64 | 0,85 | −1,30 | −4,10 % | 31,7 % | 6 |
| M30 (A) | hranice posunuty o −30 min | 3 758 | −0,020 | −4,48 | 0,82 | −1,60 | −4,84 % | 34,9 % | 6 |
| M30 (A) | hranice posunuty o +30 min | 3 759 | −0,020 | −4,16 | 0,83 | −1,52 | −4,95 % | 35,0 % | 6 |
| H1 (A) | hranice 02, 09, 15 (default) | 3 759 | −0,017 | −3,65 | 0,85 | −1,30 | −4,10 % | 31,6 % | 6 |

Jak číst tabulku: u session strategie se místo škálování délek testuje jemnější báze (M30) a posun
všech hranic o ±30 minut. Vše jen na datech A za 2016-09 – 2023-12 s reálným bid/ask. Co z toho plyne:
všechny čtyři varianty jsou **silně záporné** (t −3,6 až −4,5) a posun oken o půl hodiny výsledek
ještě zhorší [E]. Shoda M30 a H1 se stejnými hranicemi (−0,017 R) potvrzuje, že výsledek není
artefakt agregace barů.

### Walk-forward

Walk-forward se u C8b neprovádí (brána 5 = N/A). Strategie nemá parametry, které by se daly
rekalibrovat (pevné hodiny), a protokol pro ni deklaroval jen roční řez (`DEV_SELECTION.md`). Ten je
v části „Roky a bloky“ níže.

### Bootstrap

| Metrika (trade bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| CAGR | −2,54 % | −1,13 % | 0,23 % |
| Expectancy R | −0,010 | −0,004 | 0,001 |
| Profit factor | 0,91 | 0,96 | 1,01 |
| Max drawdown | 10,0 % | 20,3 % | 32,7 % |
| Nejdelší série ztrát (obchody) | 10 | 12 | 16 |
| Nejdelší úsek pod maximem (obchody) | 2 947 | 6 614 | 7 146 |

Jak číst tabulku: kvůli počtu obchodů (≥ 2 000) se převzorkovává jen 2 000×. P(expectancy > 0) =
**10,4 %**. Co z toho plyne: s pravděpodobností kolem 90 % je čistá expectancy záporná. Úsek pod
maximem v mediánu 6 614 obchodů z 7 149 znamená, že simulovaná equity je téměř celou dobu pod
počátečním maximem [E].

| Metrika (blokový bootstrap) | p05 | p50 | p95 |
|---|---|---|---|
| Sharpe | −0,84 | −0,36 | 0,11 |
| CAGR | −2,55 % | −1,15 % | 0,29 % |
| Max drawdown | 10,3 % | 20,9 % | 33,3 % |

Jak číst tabulku: blokový bootstrap denních výnosů. P(Sharpe > 0) = **11,1 %**. Co z toho plyne:
shodný závěr, záporný Sharpe je zhruba osmkrát pravděpodobnější než kladný.

### Režimy

| Dimenze | Stav | Obchody | Exp. R | Win % | PF | Long exp. R | Short exp. R | Denní Sharpe |
|---|---|---|---|---|---|---|---|---|
| trend | range (bez trendu) | 4 902 | −0,001 | 49,7 | 0,99 | 0,000 | −0,001 | −0,06 |
| trend | trending | 2 247 | −0,012 | 48,7 | 0,90 | −0,017 | −0,008 | −0,92 |
| volatilita | vysoká | 3 237 | −0,001 | 50,0 | 0,99 | −0,003 | 0,000 | −0,13 |
| volatilita | nízká | 3 912 | −0,007 | 48,8 | 0,94 | −0,008 | −0,006 | −0,53 |
| USD (60 d) | silný USD | 4 057 | −0,002 | 50,2 | 0,99 | −0,003 | 0,000 | −0,15 |
| USD (60 d) | slabý USD | 3 092 | −0,008 | 48,4 | 0,92 | −0,008 | −0,007 | −0,63 |
| výnosy 10Y (60 d) | klesající | 3 570 | −0,010 | 48,8 | 0,91 | −0,006 | −0,014 | −0,80 |
| výnosy 10Y (60 d) | rostoucí | 3 579 | 0,001 | 50,0 | 1,02 | −0,005 | 0,008 | 0,11 |
| VIX | krize (VIX > 25) | 1 062 | −0,019 | 47,4 | 0,85 | −0,020 | −0,018 | −1,37 |
| VIX | normál | 6 087 | −0,002 | 49,7 | 0,98 | −0,003 | −0,001 | −0,15 |

Jak číst tabulku: stejné štítky jako výše. Co z toho plyne: kladný (a jen nepatrně) je jediný stav,
rostoucí výnosy 10Y (+0,001 R). Nejhorší jsou krize (−0,019 R) a silný trend (−0,012 R). Na rozdíl od
trendových strategií je C8b v nízké volatilitě horší než ve vysoké, protože v klidném trhu je hrubý
pohyb za okno malý proti fixnímu spreadu [I]. Režimový filtr by C8b nezachránil, žádný stav nemá
expectancy, která by po nákladech dávala smysl.

### Roky a bloky

| Rok | Segment | Obchody | Exp. R | Čistý PnL | Long PnL | Short PnL | Kumulativně |
|---|---|---|---|---|---|---|---|
| 2010 | DEV | 498 | 0,003 | 798 | 1 017 | −219 | 798 |
| 2011 | DEV | 496 | −0,002 | −344 | 318 | −662 | 454 |
| 2012 | DEV | 498 | 0,012 | 3 097 | −38 | 3 134 | 3 551 |
| 2013 | DEV | 514 | 0,032 | 8 760 | −1 477 | 10 238 | 12 311 |
| 2014 | DEV | 511 | −0,007 | −2 106 | −965 | −1 141 | 10 205 |
| 2015 | DEV | 509 | 0,033 | 9 318 | 2 583 | 6 735 | 19 524 |
| 2016 | DEV | 514 | 0,006 | 1 670 | 3 859 | −2 189 | 21 193 |
| 2017 | DEV | 513 | −0,020 | −6 073 | −2 437 | −3 636 | 15 121 |
| 2018 | DEV | 516 | −0,034 | −9 675 | −5 975 | −3 700 | 5 446 |
| 2019 | OOS | 516 | −0,021 | −5 419 | −790 | −4 629 | 27 |
| 2020 | OOS | 518 | −0,043 | −10 340 | −3 733 | −6 606 | −10 313 |
| 2021 | OOS | 516 | 0,016 | 3 604 | 2 332 | 1 272 | −6 709 |
| 2022 | OOS | 516 | −0,017 | −3 914 | −3 397 | −517 | −10 623 |
| 2023 | OOS | 514 | −0,019 | −4 240 | −1 205 | −3 035 | −14 863 |

Jak číst tabulku: rok výstupu obchodu, USD, baseline náklady. Co z toho plyne: zisk po nákladech
vznikl jen v letech 2010–2016 (kumulativně 21 193 USD) a od roku 2017 se ztrácí. Kumulativní výsledek
klesl na −14 863 USD [E]. Brána 6 má hodnotu „nekonečno“, protože celkový zisk je záporný. Jediný
kladný rok po roce 2016 je 2021.

| Rok | Obchody | Hrubá exp. R | Hrubý PnL | Long hrubá exp. R | Short hrubá exp. R |
|---|---|---|---|---|---|
| 2010 | 498 | 0,0203 | 5 009 | 0,0262 | 0,0147 |
| 2011 | 496 | 0,0139 | 3 532 | 0,0180 | 0,0100 |
| 2012 | 498 | 0,0312 | 8 433 | 0,0194 | 0,0424 |
| 2013 | 514 | 0,0477 | 14 820 | 0,0047 | 0,0907 |
| 2014 | 511 | 0,0126 | 4 196 | 0,0134 | 0,0117 |
| 2015 | 509 | 0,0511 | 18 464 | 0,0368 | 0,0652 |
| 2016 | 514 | 0,0251 | 9 985 | 0,0466 | 0,0038 |
| 2017 | 513 | 0,0054 | 2 181 | 0,0107 | 0,0001 |
| 2018 | 516 | −0,0077 | −3 296 | −0,0144 | −0,0010 |
| 2019 | 516 | 0,0059 | 2 432 | 0,0212 | −0,0094 |
| 2020 | 518 | −0,0229 | −9 528 | −0,0105 | −0,0354 |
| 2021 | 516 | 0,0363 | 14 999 | 0,0417 | 0,0309 |
| 2022 | 516 | 0,0033 | 1 401 | −0,0086 | 0,0153 |
| 2023 | 514 | 0,0023 | 919 | 0,0122 | −0,0076 |

Jak číst tabulku: **vlastní dopočet pro tento dokument** [E]. Bezfrikční běh C8b (`research/common.py`
`run`, `CostModel(multiplier=0, swap_enabled=False)`) za 2010–2023 rozdělený podle roku výstupu.
Součet hrubého PnL (73 546 USD) odpovídá řádku „hrubě ×0“ v `s02_C8b.json`. Co z toho plyne:
hrubá anomálie byla v letech 2010–2016 kladná každý rok, v průměru **+0,0289 R na obchod** (3 540
obchodů, hrubě 64 438 USD). V letech 2017–2023 klesla na **+0,0032 R** (3 609 obchodů, hrubě 9 108 USD)
se dvěma zápornými roky. Náklady baseline jsou asi 0,020 R na obchod. Do roku 2016 tedy hrubý edge
náklady převyšoval (čistě +0,0112 R), od roku 2017 je zhruba šestkrát menší než náklady (čistě −0,0196 R)
[E, vlastní dopočet]. Rok 2021 je výjimka.

Mohl by pokles být artefaktem přechodu z dat B na A v září 2016? Křížová kontrola za 2016-09 –
2018-12 (`s01_dev_screen.md`, kapitola 7) dává pro C8b na datech A i B **shodně −0,016 R**, takže
pokles není způsoben zdrojem dat [E]. Anomálie zeslábla v trhu, ne v datech. Je to v souladu se
skepsí k publikovaným a prakticky známým kalendářním anomáliím, které po zveřejnění slábnou
(kapitola 5) [I].

| Blok | Obchody | Exp. R | PF | Čistý PnL |
|---|---|---|---|---|
| 2010–2012 | 1 492 | 0,005 | 1,05 | 3 551 |
| 2013–2015 | 1 534 | 0,019 | 1,21 | 15 972 |
| 2016–2018 | 1 543 | −0,016 | 0,86 | −14 078 |
| 2019–2021 | 1 550 | −0,016 | 0,85 | −12 155 |
| 2022–2023 | 1 030 | −0,018 | 0,83 | −8 154 |

Jak číst tabulku: tříleté bloky, baseline náklady. Co z toho plyne: dva kladné bloky na začátku,
potom tři záporné, které jsou si nápadně podobné (−0,016 až −0,018 R). To je obraz trvalé změny,
ne výkyvu [I].

### Deflated Sharpe a PSR

| Varianta | N | T (dní) | SR (anual.) | SR0 (anual.) | PSR (SR > 0) | DSR |
|---|---|---|---|---|---|---|
| DEV+OOS, N = 60 (konzervativní) | 60 | 3 605 | −0,35 | 1,46 | 0,09 | 0,00 |
| jen OOS, N = 60 | 60 | 1 290 | −1,40 | 1,46 | 0,00 | 0,00 |

Jak číst tabulku: varianta v rámci mřížky se pro C8b nepočítala (`dsr_within_grid.json` obsahuje jen
C3, C2, C5, C9). Co z toho plyne: PSR 0,09 za DEV+OOS a 0,00 za OOS. U strategie se záporným Sharpe je
deflace formalita, protože korekce na počet testů výsledek jen dál zhoršuje.

### Brány

| Brána | Podmínka | Hodnota | Splněno |
|---|---|---|---|
| 1 | DEV: exp. R > 0 a PF > 1,10 | exp. 0,003 R, PF 1,022 | NE |
| 2 | OOS: exp. R > 0, PF > 1,05, Sharpe > 0,3 | exp. −0,017 R, PF 0,84, Sharpe −1,41 | NE |
| 3 | náklady ×1,5: exp. R DEV+OOS > 0 | −0,014 R | NE |
| 4 | ≥ 70 % bodů mřížky s exp. R > 0 | 0 % | NE |
| 5 | walk-forward spojený výsledek > 0 | netestováno (bez parametrů) | N/A |
| 6 | žádný rok > 50 % čistého zisku | nekonečno (celkový zisk záporný) | NE |
| 7 | bootstrap P(exp. R > 0) ≥ 90 % | 10,4 % | NE |
| Vše | brány 1–7 současně | splněno 0 ze 7 | NE |

Jak číst tabulku: hodnoty z `s02_C8b.json`. Co z toho plyne: C8b nesplnila žádnou z bran, které se
na ni daly použít. Je to nejjednoznačnější zamítnutí ve validaci.

### Celkové hodnocení C8b

> **Závěr:** Asijsko-londýnský intradenní vzor zlata je **skutečná hrubá anomálie** (bezfrikční Sharpe
> 1,26 za 2010–2023, kladná hrubá expectancy ve 12 ze 14 let). Je ale velká zhruba jako náklady na
> její obchodování (hrubě 0,016 R proti nákladům 0,020 R na obchod) a od roku 2017 výrazně zeslábla
> (hrubě 0,003 R na obchod). Po nákladech je záporná v PRE, OOS, ve všech 18 variantách oken, na M30
> i H1 a při posunu oken. Je extrémně citlivá na načasování (hodina zpoždění = 39 % hrubého edge).
> Splnila 0 ze 7 bran. **Zamítnuta** podle explicitního pravidla zadání: funguje jen před náklady.

Typ důkazu: čísla jsou [E]; ekonomické zdůvodnění (asijská fyzická poptávka vs. západní prodeje
a cenotvorba v londýnské a newyorské seanci, Blose et al. 2018) je [R/E literatura]; vysvětlení
poklesu po roce 2016 jako arbitráže známé anomálie je [I]. Pro další výzkum by C8b dávala smysl jen
u brokera s výrazně nižšími náklady (ECN s celkovými náklady pod polovinou baseline) a jen jako
samostatně ověřená hypotéza na nových datech [I].

## 10.6 Srovnání všech pěti strategií

### Klíčové metriky

| Metrika | C3 EMA | C2 Donchian | C5 Squeeze | C9 USD-Donchian | C8b Session |
|---|---|---|---|---|---|
| PRE 2004–2009 exp. R | 0,064 | 0,316 | 0,122 | 0,123 | −0,005 |
| DEV exp. R / PF | 0,074 / 1,22 | 0,064 / 1,09 | 0,109 / 1,24 | 0,192 / 1,31 | 0,003 / 1,02 |
| OOS exp. R / PF | 0,038 / 1,12 | 0,094 / 1,14 | −0,092 / 0,82 | −0,013 / 0,96 | −0,017 / 0,84 |
| OOS Sharpe | 0,16 | 0,26 | −0,41 | 0,00 | −1,41 |
| DEV+OOS obchody (za rok) | 256 (18,3) | 373 (26,7) | 510 (36,5) | 228 (16,3) | 7 149 (511,2) |
| DEV+OOS exp. R (t) | 0,061 (0,93) | 0,081 (0,79) | 0,038 (0,63) | 0,117 (0,80) | −0,004 (−1,32) |
| DEV+OOS PF | 1,18 | 1,13 | 1,07 | 1,17 | 0,96 |
| DEV+OOS Sharpe | 0,25 | 0,22 | 0,17 | 0,24 | −0,35 |
| DEV+OOS CAGR / MaxDD | 0,53 % / 7,4 % | 1,00 % / 13,4 % | 0,62 % / 16,9 % | 0,88 % / 12,5 % | −1,14 % / 31,9 % |
| DEV+OOS čistý PnL (USD) | 7 743 | 14 437 | 9 075 | 12 683 | −14 863 |
| Ø držení (h) | 128 | 149 | 78 | 147 | 6 |
| Long / short exp. R (DEV+OOS) | −0,017 / 0,109 | 0,151 / −0,003 | 0,001 / 0,076 | 0,208 / 0,030 | −0,006 / −0,003 |
| Exp. R hrubě / ×1,5 / ×2 | 0,108 / 0,041 / 0,021 | 0,207 / 0,047 / 0,007 | 0,095 / 0,013 / −0,013 | 0,282 / 0,083 / 0,049 | 0,016 / −0,014 / −0,024 |
| Exp. R ECN | 0,084 | 0,121 | 0,060 | 0,171 | 0,002 |
| Exp. R zpoždění +1 bar | 0,056 | 0,061 | 0,037 | 0,096 | −0,011 |
| Mřížka: podíl exp. R > 0 | 90 % | 96 % | 100 % | 100 % | 0 % |
| PBO | 0,47 | 0,70 | 0,24 | 0,55 | 0,68 |
| Timeframy s exp. R > 0 | 5 z 5 | 5 z 5 | 4 z 4 | 5 z 5 | 0 z 4 |
| Walk-forward spojený výnos | 7,4 % | 5,4 % | 30,9 % | −0,2 % | — |
| Bootstrap P(exp. R > 0) | 82,2 % | 78,2 % | 73,0 % | 78,3 % | 10,4 % |
| Blokový bootstrap P(Sharpe > 0) | 80,7 % | 79,4 % | 75,1 % | 78,9 % | 11,1 % |
| Největší rok / podíl | 2023 / 70 % | 2020 / 68 % | 2016 / 74 % | 2020 / 70 % | n/a (zisk < 0) |
| Krize VIX > 25 exp. R | −0,158 | −0,311 | −0,229 | −0,234 | −0,019 |
| Vysoká vol. exp. R | −0,114 | −0,088 | −0,148 | −0,229 | −0,001 |
| PSR (SR > 0) | 0,83 | 0,80 | 0,74 | 0,82 | 0,09 |
| DSR N = 60 / N = 125 | 0,00 / 0,39 | 0,00 / 0,53 | 0,00 / 0,30 | 0,00 / 0,55 | 0,00 / — |
| Pooled 2004–2026 exp. R (t) | 0,067 (1,25) | 0,149 (1,71) | 0,074 (1,46) | 0,125 (1,12) | −0,006 (−2,15) |
| Holdout 2024–2026 exp. R (jen report) | 0,106 | 0,197 | 0,162 | 0,180 | −0,015 |

Jak číst tabulku: všechny řádky kromě posledních dvou jsou z `s02_<K>.json` a `dsr_within_grid.json`
za 2010–2023 (PRE 2004–2009). Poslední dva řádky jsou ze `s05_pooled.json` a slouží jen pro orientaci:
pooled souhrn je v kapitole 13, holdout v kapitole 12 a na pořadí neměl vliv. Co z toho plyne: čtyři
trendové varianty mají velmi podobný profil. Kladná je expectancy za DEV+OOS (0,04–0,12 R), stejně tak
plato parametrů i všechny timeframy, Sharpe je 0,17–0,25, bootstrap 73–82 %, koncentrace 68–74 % a všechny
selhávají ve stejných režimech (krize, vysoká volatilita). C8b je ve všech ohledech mimo: hrubě
nejsilnější, po nákladech nejhorší.

### Brány

| Brána | C3 | C2 | C5 | C9 | C8b |
|---|---|---|---|---|---|
| 1 DEV exp. R > 0 a PF > 1,10 | ANO | NE | ANO | ANO | NE |
| 2 OOS exp. R > 0, PF > 1,05, Sharpe > 0,3 | NE | NE | NE | NE | NE |
| 3 náklady ×1,5 exp. R > 0 | ANO | ANO | ANO | ANO | NE |
| 4 ≥ 70 % mřížky kladných | ANO | ANO | ANO | ANO | NE |
| 5 walk-forward > 0 | ANO | ANO | ANO | NE | N/A |
| 6 žádný rok > 50 % zisku | NE | NE | NE | NE | NE |
| 7 bootstrap P ≥ 90 % | NE | NE | NE | NE | NE |
| Splněno bran (ze 7) | 4 | 3 | 4 | 3 | 0 |
| Všech 7 (robustní kandidát) | NE | NE | NE | NE | NE |

Jak číst tabulku: souhrn tabulek „Brány“ z podkapitol 10.1–10.5. Co z toho plyne: **žádná strategie
neprošla všemi sedmi branami** [E]. Selhání má společný vzor: brány 2, 6 a 7, které měří stabilitu
v čase a statistickou jistotu, neprošel nikdo. Brány 3 a 4, které měří odolnost vůči nákladům
a parametrům, prošly všechny čtyři trendové varianty. Pozitivní zjištění tedy zní: **trendový efekt
na H4 není křehký artefakt jedné konfigurace ani jednoho brokera**. Negativní: **je příliš malý
a příliš nerovnoměrně rozložený v čase, než aby ho 14 let dat statisticky potvrdilo.** Počet splněných
bran (4, 3, 4, 3) sám pořadí neurčuje, protože brány nemají stejnou váhu a kvalita splnění se liší
(C5 brána 3 o 0,013 R, brána 5 jen díky rekalibraci).

### Pravidlo pro směr

| Strategie | Strana | DEV exp. R / PF | Brána 1 | OOS exp. R / PF / Sharpe | Brána 2 | Obě |
|---|---|---|---|---|---|---|
| C3 | long | −0,015 / 0,95 | NE | −0,020 / 0,95 / −0,04 | NE | NE |
| C3 | short | 0,131 / 1,40 | ANO | 0,070 / 1,24 / 0,22 | NE | NE |
| C2 | long | 0,014 / 1,01 | NE | 0,362 / 1,57 / 0,60 | ANO | NE |
| C2 | short | 0,124 / 1,19 | ANO | −0,238 / 0,61 / −0,51 | NE | NE |
| C5 | long | 0,110 / 1,25 | ANO | −0,187 / 0,66 / −0,59 | NE | NE |
| C5 | short | 0,107 / 1,22 | ANO | 0,013 / 1,01 / 0,04 | NE | NE |
| C9 | long | 0,091 / 1,13 | ANO | 0,453 / 1,67 / 0,51 | ANO | ANO |
| C9 | short | 0,302 / 1,53 | ANO | −0,362 / 0,42 / −0,77 | NE | NE |
| C8b | long | −0,002 / 0,97 | NE | −0,011 / 0,88 / −0,75 | NE | NE |
| C8b | short | 0,007 / 1,06 | NE | −0,022 / 0,81 / −1,20 | NE | NE |

Jak číst tabulku: vlastní dopočet, prahy bran 1 a 2 aplikované na samostatné long a short běhy
(`PROTOCOL.md`: „směr, který samostatně neprojde body 1–2, se označí jako bez edge a v produkci se
vypne“). Co z toho plyne: z deseti směrů prošel oběma branami jen long C9 (36 OOS obchodů, t 0,78).
U C2 a C9 se mezi DEV a OOS směrové znaménko otočilo, u C5 selhal OOS long [E]. Doslovné uplatnění
pravidla by vypnulo prakticky všechno. Protože neprošla žádná strategie jako celek, pravidlo se do
zmrazené specifikace nepromítlo a obě strany zůstaly zapnuté. Směrové výsledky na 36–169 obchodech na směr
a segment sledují režim zlata (medvědí trh 2013–2015 pro shorty, býčí 2019–2020 pro longy), ne vlastnost
pravidel [I]. Doporučení je proto ponechat symetrická pravidla.

### Křížová kontrola zdrojů dat (2016-09 – 2018-12)

| Strategie | Exp. R data A | Exp. R data B | PF A | PF B | Obchody A / B |
|---|---|---|---|---|---|
| C3 | 0,200 | 0,189 | 1,62 | 1,57 | 42 / 45 |
| C2 | 0,056 | 0,115 | 1,09 | 1,21 | 60 / 59 |
| C5 | 0,014 | 0,093 | 1,02 | 1,19 | 83 / 92 |
| C9 | 0,031 | 0,142 | 1,04 | 1,27 | 37 / 36 |
| C8b | −0,016 | −0,016 | 0,86 | 0,86 | 1 179 / 1 197 |

Jak číst tabulku: stejné období 28 měsíců běží jednou na datech A (Dukascopy bid/ask) a jednou na
datech B (MT4 bid + modelový ask). Převzato ze `s01_dev_screen.md`, detail v kapitole 7. Co z toho
plyne: u C3 a C8b dávají oba zdroje prakticky stejný výsledek. U tří breakout variant (C2, C5, C9) jsou
data B výrazně optimističtější [E]. Pravděpodobným důvodem je modelový spread B (medián podle hodiny),
který nezachytí rozšíření spreadu v rušných chvílích, kdy breakout vstupuje [I]. Pro výklad DEV
(2010–2016-08 na datech B) to znamená, že DEV výsledky C2, C5 a C9 jsou spíš horním odhadem, kdežto
u C3 tento problém nevidíme. Je to další argument pro C3 na prvním místě.

### Co z validace plyne pro pořadí

1. **C3 EMA trend H4 (#1).** Nejméně slabých míst: kladná ve všech nezávislých obdobích, default
   uprostřed plata, nejmenší citlivost na zpoždění a nepřímé náklady, shodný výsledek na obou zdrojích
   dat, nejnižší MaxDD. Slabiny: malý efekt, závislost na roce 2023 a short straně v letech 2010–2023.
2. **C2 Donchian H4 (#2).** Nejvyšší hrubý efekt, nejrovnější tříleté bloky a nejlepší dlouhodobá
   historie (PRE, pooled). Slabiny: výsledek nese 5 % obchodů, velký nepřímý dopad bid/ask exekuce na
   stopy, citlivost na zpoždění a náklady ×2, PBO 0,70, optimismus dat B.
3. **C5 Squeeze H4 (#3).** Formálně 4 brány a nejlepší walk-forward, ale OOS záporné už hrubě, šest
   záporných let po sobě, nejvyšší citlivost na náklady, default i timeframe ve slabší části prostoru.
   Ve trojici zůstává kvůli odlišnému časování vstupů, ne kvůli síle důkazů.
4. **C9 (vyřazena).** Filtr fungoval jen v DEV. OOS ≈ 0, walk-forward −0,2 %, korelace s C2 0,79
   a závislost na živém USD indexu.
5. **C8b (zamítnuta).** Skutečná hrubá anomálie, ale menší než náklady a od roku 2017 téměř zaniklá.

> **Závěr kapitoly:** Plná validace potvrdila, že střednědobý trend na H4 je jediná rodina
> s konzistentně kladnou čistou expectancy na XAUUSD 2010–2023 a že tento výsledek je odolný vůči
> volbě parametrů, timeframu a nákladům ×1,5. Neprokázala ale, že je statisticky odlišný od nuly,
> stabilní v čase nebo rozložený mezi roky a směry. Všechny čtyři trendové varianty jsou jedna
> podkladová sázka se stejnými režimy selhání (korelace a překryvy v kapitole 11). Session anomálie
> C8b je hrubě reálná, ale po nákladech neobchodovatelná. Důvěra ve všechny závěry o kladném edge je
> **nízká**. Proto byla doporučena jen pozorovací PAPER fáze (kapitoly 15 a 16).

*Zdrojové soubory: `research/results/s02_C3.json`, `s02_C3.md`, `s02_C2.json`, `s02_C2.md`,
`s02_C5.json`, `s02_C5.md`, `s02_C9.json`, `s02_C9.md`, `s02_C8b.json`, `s02_C8b.md`, `grid_C3.csv`,
`grid_C2.csv`, `grid_C5.csv`, `grid_C9.csv`, `grid_C8b.csv`, `dsr_within_grid.json`,
`s03_portfolio_C2_C3_C5_C9.md` (korelace C2/C9), `s01_dev_screen.md` (křížová kontrola zdrojů),
`s05_pooled.json` (pooled a holdout řádky srovnávací tabulky), obrázky
`research/results/figures/grid_C3.png`, `grid_C2.png`, `grid_C5.png`; protokol a rozhodnutí
`research/PROTOCOL.md`, `research/DEV_SELECTION.md`, `research/frozen_spec.json`; kód
`research/s02_validate.py`, `research/stats.py`, `research/registry.py`, `research/common.py`,
`tradingsystem/strategies/trend.py`, `tradingsystem/strategies/breakout.py`,
`tradingsystem/strategies/session.py`. Vlastní dopočty pro tento dokument (bez zápisu do repozitáře):
kontext ceny zlata po letech z `data/processed` (spojená D1 řada); rozklad výstupů podle důvodu
(stop / signál) pro C3, C2, C5, C9, C8b; rozklad dopadu nákladů na přímou a nepřímou část; mediány
MaxDD a počtu obchodů po osách mřížek, percentil defaultu, 26 sousedů defaultu, pivot mřížky C9
a porovnání mřížek C9 a C2 bod po bodu; překryv krizových dní a dní vysoké volatility (`regime_frame`);
spojený výnos defaultu ve walk-forward; doby zotavení v letech; počet let potřebných pro t = 2;
směrové brány; počty obchodů podle směru u osmi jednonohých variant mřížky C8b; hrubý (bezfrikční)
výsledek C8b po letech.*
