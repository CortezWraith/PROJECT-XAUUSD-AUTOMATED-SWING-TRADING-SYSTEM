# 7. Vývojové období (DEV 2010–2018): screening všech kandidátů

Tato kapitola rozebírá první kontakt kandidátů s daty: **DEV screening** na období 2010-01-01 až
2018-12-31. Je to jediné období, na jehož základě se podle protokolu smělo cokoli rozhodovat (OOS
2019–2023 i holdout 2024–2026 zůstaly v této fázi nedotčené). Kapitola uvádí všechny výstupy
screeningu – výkonnost, rizikový profil, rozklad nákladů, bezfrikční („hrubý“) běh, samostatné běhy
long-only a short-only a křížovou kontrolu dvou datových zdrojů – a u každého kandidáta vysvětluje,
proč prošel nebo neprošel bránou 1. Rozhodnutí, které ze screeningu vzešlo (co šlo do plné validace),
je v kapitole 9; diagnostika časového (session) efektu, ze které vznikla revize C8b, je v kapitole 8.

Všechna čísla v tabulkách pocházejí z `research/results/s01_dev_screen.json` (skript
`research/s01_dev_screen.py`, commit 41ce7b8), pokud není uvedeno jinak. Vlastní dopočty (podíl
nákladů na hrubém zisku, struktura nákladů, rozpad short strany podle roků, rekonstrukce chybného
prvního běhu, roční změny ceny zlata) jsou výslovně označeny.

## 7.1 Co přesně DEV screening testoval

**Kandidáti.** Spuštěno bylo devět předregistrovaných kandidátů C1–C9 s literaturními parametry
přesně podle `research/PROTOCOL.md` a navíc C8b – datově odvozená revize C8, která vznikla až po
prvním průchodu screeningu (kapitola 8). C10 (podzimní sezónnost, dva obchody ročně) a C11 (ML) se
nespouštěly (kapitola 6). Hvězdička u názvu v tabulkách označuje **předregistrovanou volbu** pro plné
testování (C2, C6, C8).

**Data.** Výzkumná („stitched“) řada: data B (MT4 broker, bid + modelový ask) do 2016-08-31, data A
(Dukascopy-format bid/ask) od 2016-09-01. Indikátory mají 400denní zahřívací okno před začátkem
období; obchody vznikají až od 2010-01-01. Délka období je 8,99 roku.

**Nastavení simulace.** Počáteční kapitál 100 000 USD, riziko 0,5 % equity (rebasované na začátku
měsíce) na obchod ke stop-lossu odvozenému z ATR, každá strategie běží samostatně, limity denní a
týdenní ztráty risk manageru jsou ve výzkumných bězích vypnuté (`research/common.py`, funkce `run`).
Exekuce na bid/ask, skluz 0,3 bp na market a 1,0 bp na stop příkaz, swap podle 3M T-billu ± 2,25 % p.a.
(kapitola 4).

Každý kandidát byl spuštěn v šesti bězích:

| Běh | Náklady | Období | Data | Účel |
|---|---|---|---|---|
| baseline | ×1,0 (spread, skluz, swap) | DEV 2010–2018 | stitched B → A | brána 1, hlavní výsledek |
| bezfrikční | ×0, swap vypnut | DEV 2010–2018 | stitched B → A | existuje efekt před náklady? |
| long-only | ×1,0 | DEV 2010–2018 | stitched B → A | síla dlouhé strany samostatně |
| short-only | ×1,0 | DEV 2010–2018 | stitched B → A | síla krátké strany samostatně |
| zdroj A | ×1,0 | 2016-09 – 2018-12 | jen A | křížová kontrola zdrojů |
| zdroj B | ×1,0 | 2016-09 – 2018-12 | jen B | křížová kontrola zdrojů |

*Jak číst:* jediný běh, podle kterého se rozhodovalo, je „baseline“; ostatní jsou diagnostické.
*Co z toho plyne:* díky bezfrikčnímu běhu lze u každého kandidáta oddělit dvě různé příčiny selhání –
„efekt neexistuje“ (záporný nebo nulový výsledek už před náklady) a „efekt existuje, ale náklady ho
sežerou“. Tento rozdíl je pro interpretaci zásadní (kapitola 7.6).

**Metriky** (definice v kapitole 4.7): *Exp. R* = průměrný čistý výsledek obchodu v násobcích rizika
ke stopu; *t* = Exp. R / (směrodatná odchylka R / √počet obchodů); *PF* (profit factor) = součet
čistých zisků / součet čistých ztrát v USD; *Sharpe* a *Sortino* z denních výnosů equity, anualizováno
√252; *Max DD* = maximální pokles equity od vrcholu; *Calmar* = CAGR / Max DD; *expozice* = podíl času
s otevřenou pozicí; *hrubá exp. R* = Exp. R z bezfrikčního běhu.

**Brána 1** (předregistrovaná, `PROTOCOL.md` kap. 6): čistá expectancy > 0 **a** PF > 1,10 při baseline
nákladech na DEV. Je to záměrně mírná brána – filtr „stojí za to testovat dál“, ne důkaz edge.

## 7.2 Oprava chyby exit-and-reverse a opakování screeningu

První průchod DEV screeningem odhalil dvě chyby enginu (`REPORT.md`, kapitola 2, odchylka 2):

1. **Exit-and-reverse nefungoval.** Když strategie na jednom baru vyslala zároveň výstup ze stávající
   pozice a vstup opačným směrem, `ExecutionEngine` vstup odmítl s důvodem „already in position“,
   protože pozice v okamžiku zpracování vstupu formálně ještě existovala. U C8 se to dělo každý den
   v 15:00 serverového času (konec long nohy = začátek short nohy), takže **krátká noha C8 se otevřela
   jen ve dnech, kdy dlouhou pozici předtím vyrazil stop**. Oprava: engine si pamatuje pozice, pro které
   už odeslal výstup (množina `closing`), a vstup do nich pustí.
2. **Bezfrikční běh odmítal kotace s nulovým spreadem** (kontrola platnosti kotace vyžadovala ask > bid);
   oprava na ask ≥ bid.

Po opravě byl celý DEV screening spuštěn znovu; v repozitáři jsou jen výsledky opakovaného běhu. Aby
bylo vidět, co se opravou změnilo, chybné chování jsem pro tuto kapitolu **zrekonstruoval** (vlastní
dopočet: v paměti, bez změny souborů, byla metoda `ExecutionEngine._exit` nahrazena verzí, která pozici
nepřidává do `closing`; pak byly znovu spuštěny všechny kandidáty na DEV s baseline náklady).

| Varianta | Obch. | Long | Short | Exp. R | t | PF | Sharpe | Čistý PnL USD |
|---|---|---|---|---|---|---|---|---|
| C8 – první běh s chybou (rekonstrukce) | 2 362 | 2 261 | 101 | −0,023 | −2,86 | 0,853 | −0,97 | −23 797 |
| C8 – opakovaný běh po opravě (`s01`) | 4 520 | 2 232 | 2 288 | −0,018 | −2,90 | 0,886 | −0,99 | −34 165 |
| C8b – s chybou (hypoteticky) | 2 322 | 2 263 | 59 | 0,0006 | 0,11 | 1,005 | 0,03 | 480 |
| C8b – po opravě (`s01`) | 4 569 | 2 262 | 2 307 | 0,003 | 0,62 | 1,022 | 0,21 | 5 446 |

*Jak číst:* první řádek reprodukuje první (chybný) DEV screening C8 – 2 362 obchodů, z toho jen 101
krátkých (dny, kdy long noha skončila stop-lossem před 15:00). Opakovaný běh má 4 520 obchodů, tedy
obě nohy. Řádek C8b s chybou je hypotetický – C8b vznikla až po opravě. *Co z toho plyne:* chyba
zasáhla **jen strategie s výstupem a novým vstupem na stejném baru**, tedy C8 a C8b. U všech ostatních
kandidátů (C1–C7, C9) dala rekonstrukce stejné výsledky jako opakovaný screening (stejný počet
obchodů, Exp. R, PF, Sharpe i čistý PnL). Závěr o C8 se opravou nezměnil – C8 byla záporná v obou
bězích [E]. Opakování však znamená, že výzkumník viděl DEV výsledky dvakrát; protože se změnila jen C8,
riziko z toho plynoucího ovlivnění je malé [I]. Pro trendové kandidáty je důležité, že jejich DEV čísla
na opravě nezávisí.

## 7.3 Výkonnost všech kandidátů (baseline náklady)

| Kandidát | Brána 1 | Obch. | Obch./rok | Win % | Ø zisk R | Ø ztráta R | Exp. R | t | PF | Sharpe | Sortino |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 TSMOM D1 | NE | 106 | 11,8 | 32,1 | 0,84 | −0,40 | −0,002 | −0,02 | 0,980 | 0,02 | 0,04 |
| C2 Donchian H4 * | NE | 241 | 26,8 | 32,4 | 1,99 | −0,86 | 0,064 | 0,56 | 1,094 | 0,19 | 0,31 |
| C3 EMA trend H4 | ANO | 163 | 18,1 | 35,0 | 1,16 | −0,51 | 0,074 | 0,85 | 1,221 | 0,31 | 0,51 |
| C4 Vol. breakout D1 | NE | 697 | 77,5 | 47,8 | 0,63 | −0,65 | −0,036 | −1,21 | 0,889 | −0,39 | −0,57 |
| C5 Squeeze H4 | ANO | 331 | 36,8 | 38,4 | 1,44 | −0,72 | 0,109 | 1,40 | 1,236 | 0,48 | 0,81 |
| C6 RSI(2) pullback D1 * | NE | 260 | 28,9 | 64,6 | 0,24 | −0,48 | −0,018 | −0,68 | 0,882 | −0,27 | −0,37 |
| C7 Z-score MR H1 | NE | 1 494 | 166,2 | 42,2 | 0,98 | −0,91 | −0,117 | −4,35 | 0,751 | −1,41 | −1,82 |
| C8 Session drift H1 * | NE | 4 520 | 502,7 | 47,6 | 0,31 | −0,32 | −0,018 | −2,90 | 0,886 | −0,99 | −1,34 |
| C9 USD-filtr. Donchian H4 | ANO | 144 | 16,0 | 34,0 | 2,23 | −0,86 | 0,192 | 1,15 | 1,310 | 0,37 | 0,61 |
| C8b Asie/Londýn H1 (z DEV) | NE | 4 569 | 508,2 | 51,1 | 0,20 | −0,20 | 0,003 | 0,62 | 1,022 | 0,21 | 0,30 |

*Jak číst:* „Win %“ je podíl obchodů s kladným čistým výsledkem; „Ø zisk R“ a „Ø ztráta R“ jsou průměry
R ziskových a ztrátových obchodů. Exp. R ≈ Win % × Ø zisk R + (1 − Win %) × Ø ztráta R. Hvězdička =
předregistrovaná volba. *Co z toho plyne:*

- **Bránu 1 prošli jen tři kandidáti – C3, C5 a C9 – a všichni patří do rodiny trend/momentum na H4.**
  Ani jeden ze tří předregistrovaných kandidátů neprošel: C2 těsně (PF 1,094 < 1,10), C6 a C8 jasně.
- I u kandidátů, kteří prošli, je **statistická síla nízká**: nejvyšší t-statistika čisté expectancy je
  1,40 (C5); žádný kandidát nemá t > 2. Brána 1 je proto jen filtr pro další testování, ne doklad edge [E].
- Trendové varianty mají typický profil „málo výher, velké výhry“: win rate 32–38 %, průměrná výhra
  1,2–2,2 R proti průměrné ztrátě 0,5–0,9 R. C6 má opačný profil mean reversion – 64,6 % výher, ale
  průměrná výhra 0,24 R proti ztrátě 0,48 R (negativní šikmost) [E].
- Vysokofrekvenční kandidáti C7, C8, C8b (166–508 obchodů ročně) mají kvůli velkému počtu obchodů
  nejvyšší absolutní t-statistiky – u C7 a C8 ovšem **záporné** (−4,35 a −2,90): výsledek je spolehlivě
  horší než nula, ne jen nevýrazný.

## 7.4 Rizikový profil a časování

| Kandidát | CAGR % | Max DD % | Calmar | Nejdelší pod vodou (dny) | Expozice % | Ø držení h | Medián držení h | Max. série ztrát | Čistý výnos % ze 100 tis. |
|---|---|---|---|---|---|---|---|---|---|
| C1 TSMOM D1 | 0,03 | 6,9 | 0,00 | 2 012 | 95,6 | 693 | 196 | 8 | −0,3 |
| C2 Donchian H4 * | 0,83 | 8,5 | 0,10 | 1 489 | 46,1 | 152 | 132 | 8 | 6,7 |
| C3 EMA trend H4 | 0,65 | 3,7 | 0,18 | 1 045 | 27,7 | 133 | 110 | 12 | 6,0 |
| C4 Vol. breakout D1 | −1,41 | 15,0 | −0,09 | 3 260 | 39,3 | 49 | 38 | 10 | −12,0 |
| C5 Squeeze H4 | 1,92 | 6,4 | 0,30 | 1 455 | 34,3 | 82 | 76 | 7 | 18,7 |
| C6 RSI(2) pullback D1 * | −0,28 | 6,0 | −0,05 | 1 545 | 38,2 | 114 | 96 | 6 | −2,5 |
| C7 Z-score MR H1 | −9,31 | 60,4 | −0,15 | 3 267 | 36,6 | 19 | 15 | 16 | −58,5 |
| C8 Session drift H1 * | −4,54 | 35,8 | −0,13 | 3 274 | 81,0 | 10 | 9 | 10 | −34,2 |
| C9 USD-filtr. Donchian H4 | 1,44 | 5,7 | 0,25 | 940 | 28,3 | 156 | 126 | 7 | 13,7 |
| C8b Asie/Londýn H1 (z DEV) | 0,59 | 14,9 | 0,04 | 707 | 56,3 | 7 | 6 | 12 | 5,4 |

*Jak číst:* CAGR a Max DD platí pro riziko 0,5 % na obchod a jednu strategii; při jiném riziku se
škálují přibližně lineárně, poměrové ukazatele (Calmar, Sharpe) se nemění. „Nejdelší pod vodou“ je
nejdelší úsek bez nového maxima equity. *Co z toho plyne:*

- **Absolutní výnosy jsou malé i u nejlepších kandidátů**: C5 1,92 % ročně, C9 1,44 %, C2 0,83 %,
  C3 0,65 % – a to v období, kde byly vybrány jako nejlepší. I u nich trvalo nejdelší období pod vodou
  940–1 489 dní (2,6–4,1 roku) [E].
- **C3 má nejmírnější drawdown** (3,7 %) díky nízké expozici (27,7 % času v trhu) a širokému trailing
  stopu; za to platí nejdelší sérií ztrát (12 obchodů za sebou).
- **C7 a C8 by účet vážně poškodily**: C7 ztratila 58,5 % počátečního kapitálu s drawdownem 60,4 %,
  C8 34,2 %. Obě byly pod vodou téměř celé období (3 267 a 3 274 dní z 3 283 dní mezi prvním a posledním
  dnem DEV).
- **C1 je mimo mandát i realizovaně**: průměrné držení 693 h (≈ 29 dní), v trhu 95,6 % času.
- Realizovaná doba držení odpovídá apriorním odhadům z kapitoly 6: C2, C3 a C9 v průměru 5,5–6,5 dne,
  C5 3,4 dne, C4 2 dny, C7 necelý den (19 h), C8 a C8b 6,5–10 hodin.

## 7.5 Náklady: kolik z hrubého zisku zbylo

Rozklad čistého výsledku baseline běhu na hrubý zisk a jednotlivé nákladové položky (USD, celé DEV).
Hrubý PnL je výsledek téhož běhu oceněný bez spreadu, skluzu a swapu (stejné obchody); „Náklady celkem“
= spread + skluz − swap. Dva sloupce vpravo ukazují podíl nákladů dvěma způsoby (vlastní dopočet):

- **v USD** ze stejného běhu: (hrubý PnL − čistý PnL) / hrubý PnL;
- **v R** z porovnání bezfrikčního a baseline běhu: (hrubá exp. R − čistá exp. R) / hrubá exp. R.
  „Náklad R/obchod“ je rozdíl obou expectancy, tedy průměrná cena obchodu v násobcích rizika.

| Kandidát | Hrubý PnL | Spread | Skluz | Swap | Čistý PnL | Náklady celkem | Náklady / hrubý PnL | Hrubá exp. R | Čistá exp. R | Náklad R/obchod | Náklady / hrubá exp. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 TSMOM D1 | 2 481 | 290 | 80 | −2 385 | −274 | 2 755 | 111,0 % | 0,055 | −0,002 | 0,056 | 102,8 % |
| C2 Donchian H4 * | 15 840 | 2 473 | 1 594 | −5 042 | 6 731 | 9 109 | 57,5 % | 0,183 | 0,064 | 0,119 | 64,9 % |
| C3 EMA trend H4 | 9 739 | 1 104 | 711 | −1 942 | 5 981 | 3 757 | 38,6 % | 0,116 | 0,074 | 0,041 | 35,7 % |
| C4 Vol. breakout D1 | 1 165 | 5 360 | 3 661 | −4 104 | −11 960 | 13 125 | 1 126,2 % | 0,010 | −0,036 | 0,046 | 450,0 % |
| C5 Squeeze H4 | 28 188 | 3 914 | 1 555 | −4 028 | 18 691 | 9 497 | 33,7 % | 0,165 | 0,109 | 0,056 | 34,0 % |
| C6 RSI(2) pullback D1 * | −664 | 736 | 211 | −895 | −2 506 | 1 842 | hrubě ztrátová | −0,004 | −0,018 | 0,014 | hrubě ztrátová |
| C7 Z-score MR H1 | −34 265 | 13 901 | 6 838 | −3 496 | −58 499 | 24 234 | hrubě ztrátová | −0,067 | −0,117 | 0,050 | hrubě ztrátová |
| C8 Session drift H1 * | 417 | 26 104 | 8 392 | −86 | −34 165 | 34 582 | 8 292,8 % | 0,001 | −0,018 | 0,020 | 1 487,2 % |
| C9 USD-filtr. Donchian H4 | 19 572 | 1 604 | 1 016 | −3 278 | 13 674 | 5 898 | 30,1 % | 0,353 | 0,192 | 0,161 | 45,5 % |
| C8b Asie/Londýn H1 (z DEV) | 53 414 | 36 612 | 11 352 | −4 | 5 446 | 47 968 | 89,8 % | 0,022 | 0,003 | 0,020 | 88,4 % |

*Jak číst:* swap je se znaménkem (záporný = náklad). Podíl nad 100 % znamená, že náklady převýšily
hrubý zisk a čistý výsledek je záporný; u C4 a C8 jsou procenta extrémní jen proto, že hrubý zisk je
téměř nulový – správné čtení je „náklady mnohonásobně převyšují téměř nulový hrubý efekt“. Oba způsoby
výpočtu se liší, protože bezfrikční běh má mírně jiné obchody (např. C2 237 místo 241: bez spreadu se
vstupy a stopy plní na jiných cenách a spread guard nic neodkládá) a jiné vážení obchodů v USD (equity
roste jinak); na závěrech to nic nemění.

**Podíl nákladů na hrubém zisku u kandidátů s kladným čistým výsledkem** (vlastní dopočet):

| Kandidát | Náklady / hrubý PnL (USD) | Náklady / hrubá exp. (R) | Hlavní nákladová položka |
|---|---|---|---|
| C9 USD-filtr. Donchian H4 | 30,1 % | 45,5 % | swap (56 % nákladů) |
| C5 Squeeze H4 | 33,7 % | 34,0 % | swap a spread (42 % a 41 %) |
| C3 EMA trend H4 | 38,6 % | 35,7 % | swap (52 %) |
| C2 Donchian H4 * | 57,5 % | 64,9 % | swap (55 %) |
| C8b Asie/Londýn H1 (z DEV) | 89,8 % | 88,4 % | spread (76 %) |

*Co z toho plyne:* trendové varianty na H4 odevzdají na nákladech zhruba **třetinu až dvě třetiny**
hrubého zisku; session strategie C8b přibližně **90 %** – a to v období, ze kterého byla odvozena.

Struktura nákladů podle položek (vlastní dopočet z téhož souboru; podíl na nákladech celkem a průměrný
náklad na obchod):

| Kandidát | Spread | Skluz | Swap | Náklad USD/obchod |
|---|---|---|---|---|
| C1 TSMOM D1 | 11 % | 3 % | 87 % | 26,0 |
| C2 Donchian H4 * | 27 % | 17 % | 55 % | 37,8 |
| C3 EMA trend H4 | 29 % | 19 % | 52 % | 23,1 |
| C4 Vol. breakout D1 | 41 % | 28 % | 31 % | 18,8 |
| C5 Squeeze H4 | 41 % | 16 % | 42 % | 28,7 |
| C6 RSI(2) pullback D1 * | 40 % | 11 % | 49 % | 7,1 |
| C7 Z-score MR H1 | 57 % | 28 % | 14 % | 16,2 |
| C8 Session drift H1 * | 75 % | 24 % | 0 % | 7,7 |
| C9 USD-filtr. Donchian H4 | 27 % | 17 % | 56 % | 41,0 |
| C8b Asie/Londýn H1 (z DEV) | 76 % | 24 % | 0 % | 10,5 |

*Jak číst:* procenta se sčítají na 100 % (zaokrouhlení). Náklad na obchod v USD závisí na velikosti
pozice (riziko 0,5 % ke stopu), proto je mezi strategiemi s různě širokými stopy srovnatelnější sloupec
„Náklad R/obchod“ v předchozí tabulce. *Co z toho plyne:*

- **U vícedenních strategií je největší položkou swap**, ne spread [E]. Swap model účtuje longu
  3M T-bill + 2,25 % p.a. a shortu připisuje 3M T-bill − 2,25 % p.a.; 3M sazba byla v DEV většinu času
  téměř nulová (roční průměry 2010–2015 mezi 0,03 % a 0,14 %, průměr celého DEV 0,41 %; vlastní
  dopočet z `macro_daily`), takže swap platily **oba** směry. Citlivost na swapovou přirážku je proto pro trend klíčová –
  a přirážka 2,25 % je kalibrace na retail podmínky 2024–25, ne historická řada [U].
- **U session strategií je swap nulový** (nepřecházejí rollover v 17:00 NY), ale spread a skluz se
  platí dvakrát denně; jeden obchod C8b stojí v průměru 0,020 R, což je téměř celá hrubá expectancy
  (0,022 R). Kapitola 8.9 tento poměr převádí na body (bp) a počítá break-even náklad.
- **C1 ztrácí prakticky jen kvůli swapu** (87 % nákladů): drží pozici 96 % času.

## 7.6 Bezfrikční (gross) screening: existuje efekt vůbec?

Stejné strategie bez spreadu, skluzu, komise a swapu. Tento běh nemá obchodní význam – slouží jen
k rozlišení „efekt chybí“ vs. „efekt je, ale je dražší, než kolik vynese“.

| Kandidát | Obch. | Win % | Exp. R | t | PF | Sharpe | CAGR % | Max DD % | Long exp. R | Short exp. R |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 TSMOM D1 | 106 | 33,0 | 0,055 | 0,53 | 1,206 | 0,20 | 0,37 | 6,3 | 0,042 | 0,070 |
| C2 Donchian H4 * | 237 | 35,4 | 0,183 | 1,50 | 1,324 | 0,49 | 2,41 | 6,1 | 0,142 | 0,232 |
| C3 EMA trend H4 | 163 | 35,0 | 0,116 | 1,30 | 1,363 | 0,46 | 1,01 | 3,4 | 0,043 | 0,184 |
| C4 Vol. breakout D1 | 685 | 49,6 | 0,010 | 0,34 | 1,028 | 0,11 | 0,33 | 9,2 | 0,003 | 0,016 |
| C5 Squeeze H4 | 331 | 39,6 | 0,165 | 2,07 | 1,382 | 0,71 | 2,97 | 5,5 | 0,172 | 0,158 |
| C6 RSI(2) pullback D1 * | 260 | 66,5 | −0,004 | −0,17 | 0,961 | −0,08 | −0,09 | 5,6 | 0,000 | −0,009 |
| C7 Z-score MR H1 | 1 485 | 42,8 | −0,067 | −2,44 | 0,846 | −0,80 | −5,53 | 45,7 | −0,087 | −0,047 |
| C8 Session drift H1 * | 4 520 | 49,9 | 0,001 | 0,21 | 1,005 | 0,05 | 0,18 | 12,8 | −0,004 | 0,007 |
| C9 USD-filtr. Donchian H4 | 140 | 37,9 | 0,353 | 1,98 | 1,653 | 0,64 | 2,67 | 4,1 | 0,265 | 0,449 |
| C8b Asie/Londýn H1 (z DEV) | 4 569 | 54,5 | 0,022 | 5,26 | 1,227 | 1,72 | 5,61 | 3,9 | 0,018 | 0,026 |

*Jak číst:* sloupce mají stejný význam jako v kapitole 7.3, jen pro běh bez nákladů. Počet obchodů se
může mírně lišit (C2, C4, C7, C9), protože bez spreadu se neuplatní spread guard a stopy a vstupní
úrovně jsou zasaženy na jiných cenách [I]. *Co z toho plyne* – kandidáti se dělí do tří skupin:

1. **Žádný efekt už před náklady:** C6 (−0,004 R, t −0,17), C7 (−0,067 R, t −2,44 – významně
   *záporný*), C8 (0,001 R, t 0,21), C4 (0,010 R, t 0,34). Tady selhání **není problém nákladů**:
   ani dokonalá exekuce by z těchto pravidel na XAUUSD 2010–2018 zisk neudělala [E].
2. **Slabý hrubý efekt, který náklady zmenší, ale nezničí:** trendové varianty C2 (0,183 R), C3
   (0,116 R), C5 (0,165 R), C9 (0,353 R); t-statistiky 1,30–2,07. C1 (0,055 R, t 0,53) je na hraně
   nuly – plochý.
3. **Silný hrubý efekt, který náklady téměř celý pohltí:** C8b – hrubá t-statistika 5,26 a hrubý
   Sharpe 1,72 jsou nejvyšší ze všech kandidátů, ale (a) okna byla zvolena na týchž datech, takže číslo
   je optimisticky zkreslené, a (b) čistá expectancy je jen 0,003 R. Kapitola 8 ukazuje, co se s tímto
   efektem stalo mimo DEV.

## 7.7 Long-only a short-only

Samostatné běhy s povoleným jen jedním směrem (baseline náklady). Nejsou totožné s rozpadem
obousměrného běhu podle směru: v obousměrném běhu může otevřená pozice jednoho směru zablokovat signál
opačného směru (jedna pozice na strategii), v jednosměrném běhu ne – proto se počty obchodů liší
(např. C3 má v obousměrném běhu 79 long obchodů, v long-only běhu 88).

| Kandidát | Long obch. | Long exp. R | Long t | Long PF | Long čistý PnL | Short obch. | Short exp. R | Short t | Short PF | Short čistý PnL |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 TSMOM D1 | 67 | 0,002 | 0,02 | 1,019 | 156 | 64 | −0,032 | −0,28 | 0,879 | −925 |
| C2 Donchian H4 * | 131 | 0,014 | 0,09 | 1,010 | 361 | 110 | 0,124 | 0,70 | 1,195 | 6 439 |
| C3 EMA trend H4 | 88 | −0,015 | −0,15 | 0,951 | −694 | 87 | 0,131 | 1,00 | 1,397 | 5 623 |
| C4 Vol. breakout D1 | 476 | −0,011 | −0,31 | 0,961 | −2 989 | 500 | −0,060 | −1,62 | 0,832 | −14 330 |
| C5 Squeeze H4 | 162 | 0,110 | 1,10 | 1,253 | 8 846 | 169 | 0,107 | 0,91 | 1,219 | 9 004 |
| C6 RSI(2) pullback D1 * | 131 | −0,025 | −0,62 | 0,848 | −1 720 | 136 | −0,019 | −0,52 | 0,882 | −1 239 |
| C7 Z-score MR H1 | 751 | −0,135 | −3,56 | 0,735 | −40 116 | 749 | −0,099 | −2,62 | 0,792 | −31 431 |
| C8 Session drift H1 * | 2 263 | −0,025 | −3,05 | 0,841 | −24 159 | 2 288 | −0,013 | −1,33 | 0,923 | −14 106 |
| C9 USD-filtr. Donchian H4 | 75 | 0,091 | 0,39 | 1,131 | 2 909 | 69 | 0,302 | 1,26 | 1,528 | 10 458 |
| C8b Asie/Londýn H1 (z DEV) | 2 263 | −0,002 | −0,44 | 0,973 | −2 777 | 2 307 | 0,007 | 1,15 | 1,062 | 8 332 |

*Jak číst:* každý řádek obsahuje dva nezávislé běhy (long-only vlevo, short-only vpravo). *Co z toho
plyne:*

- **U trendových variant C2, C3 a C9 nesla DEV výsledek krátká strana**: short 0,124 / 0,131 /
  0,302 R proti long 0,014 / −0,015 / 0,091 R. C5 je jako jediná symetrická (0,110 vs. 0,107 R).
- **Mean reversion (C6, C7) a C4 jsou záporné v obou směrech** – selhání není asymetrií trhu, ale
  vlastností pravidel.
- **C8 je záporná v obou nohách**, dlouhá noha výrazněji (t −3,05). C8b má po nákladech kladnou jen
  krátkou (londýnskou) nohu.

Proč byla v DEV silnější krátká strana trendu, vysvětluje průběh ceny zlata (vlastní dopočet z denních
mid close výzkumné řady):

| Rok | Close konec roku (USD) | Změna za rok % | Max. denní close | Min. denní close |
|---|---|---|---|---|
| 2010 | 1 408 | 28,3 | 1 423 | 1 063 |
| 2011 | 1 565 | 11,1 | 1 900 | 1 314 |
| 2012 | 1 675 | 7,1 | 1 791 | 1 539 |
| 2013 | 1 208 | −27,9 | 1 692 | 1 190 |
| 2014 | 1 187 | −1,8 | 1 382 | 1 142 |
| 2015 | 1 061 | −10,6 | 1 302 | 1 052 |
| 2016 | 1 151 | 8,5 | 1 365 | 1 075 |
| 2017 | 1 303 | 13,1 | 1 349 | 1 159 |
| 2018 | 1 283 | −1,6 | 1 358 | 1 174 |

*Jak číst:* změna je mezi posledními denními close po sobě jdoucích let (konec 2009: 1 098 USD).
*Co z toho plyne:* DEV obsahuje vrchol býčího trhu (nejvyšší denní close 1 900 USD 2011-09-05),
**pád o 27,9 % v roce 2013** a pokračující medvědí trh do konce 2015; od konce 2009 do konce 2018
zlato vzrostlo celkem jen o 17 %. Pro trendové systémy to bylo období bez trvalého růstu, kde
nejsilnější a nejčistší trend byl směrem dolů.

Rozpad čistého PnL krátké strany trendových variant podle let (vlastní dopočet z ročních tabulek
`s02_<K>.json`; obchody 2010–2018 jsou v běhu DEV+OOS totožné s DEV během – součty long a short
odpovídají `s01` na dolar):

| Kandidát | Long PnL DEV | Short PnL DEV | Short 2013 | 2013 / short DEV | Short 2013–2015 | 2013–2015 / short DEV | Long 2010–2012 |
|---|---|---|---|---|---|---|---|
| C3 EMA trend H4 | −70 | 6 051 | 2 150 | 36 % | 4 683 | 77 % | −114 |
| C2 Donchian H4 | −251 | 6 983 | 5 944 | 85 % | 9 430 | 135 % | 6 048 |
| C5 Squeeze H4 | 9 967 | 8 724 | 5 069 | 58 % | 9 466 | 109 % | 194 |
| C9 USD-filtr. Donchian H4 | 2 481 | 11 193 | 5 380 | 48 % | 10 734 | 96 % | 7 800 |

*Jak číst:* hodnoty v USD, rok podle data výstupu z obchodu; podíl nad 100 % znamená, že krátká strana
mimo 2013–2015 v součtu ztrácela. *Co z toho plyne:* **převaha short strany v DEV je z velké části jeden
režim – medvědí trh 2013–2015, s těžištěm v roce 2013** (u C2 85 % celého short zisku DEV z jediného
roku) [E]. Nejde tedy o strukturální asymetrii („short je u zlata lepší“), ale o to, kudy se trh
v DEV zrovna pohnul. Kapitoly o OOS a holdoutu tento výklad potvrzují: v býčích letech 2019–2020
a 2024–2026 se asymetrie obrátila ve prospěch long strany (kapitola 16 `REPORT.md`). Proto
předregistrované pravidlo „směr, který samostatně neprojde, vypnout“ nebylo vhodné aplikovat na DEV
rozpad [I].

## 7.8 Křížová kontrola zdrojů A vs. B (2016-09 – 2018-12)

Na 28 měsících, kde se oba zdroje překrývají a které leží uvnitř DEV, byl každý kandidát spuštěn zvlášť
na datech A (Dukascopy-format, reálný bid i ask) a na datech B (MT4 broker, reálný bid, ask syntetizovaný
mediánovým spreadem A podle serverové hodiny). Cílem je ověřit, že výzkumná řada, která v DEV
z větší části (2010-01 – 2016-08) stojí na datech B, nedává systematicky jiné závěry.

| Kandidát | Obch. A | Obch. B | Win % A | Win % B | Exp. R A | Exp. R B | Rozdíl B − A | PF A | PF B | Shoda znaménka |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 TSMOM D1 | 19 | 24 | 31,6 | 33,3 | −0,050 | 0,067 | 0,117 | 0,769 | 1,315 | NE |
| C2 Donchian H4 * | 60 | 59 | 35,0 | 39,0 | 0,056 | 0,115 | 0,059 | 1,091 | 1,209 | ANO |
| C3 EMA trend H4 | 42 | 45 | 45,2 | 44,4 | 0,200 | 0,189 | −0,011 | 1,619 | 1,566 | ANO |
| C4 Vol. breakout D1 | 185 | 189 | 47,6 | 47,6 | −0,033 | −0,017 | 0,015 | 0,903 | 0,943 | ANO |
| C5 Squeeze H4 | 83 | 92 | 34,9 | 35,9 | 0,014 | 0,093 | 0,079 | 1,019 | 1,188 | ANO |
| C6 RSI(2) pullback D1 * | 46 | 68 | 67,4 | 58,8 | −0,051 | −0,152 | −0,101 | 0,738 | 0,437 | ANO |
| C7 Z-score MR H1 | 379 | 375 | 47,2 | 46,1 | −0,040 | −0,066 | −0,027 | 0,913 | 0,857 | ANO |
| C8 Session drift H1 * | 1 160 | 1 171 | 47,8 | 47,8 | −0,018 | −0,014 | 0,005 | 0,888 | 0,916 | ANO |
| C9 USD-filtr. Donchian H4 | 37 | 36 | 35,1 | 41,7 | 0,031 | 0,142 | 0,111 | 1,041 | 1,273 | ANO |
| C8b Asie/Londýn H1 (z DEV) | 1 179 | 1 197 | 47,5 | 47,1 | −0,016 | −0,016 | 0,000 | 0,858 | 0,858 | ANO |

Čistý PnL (USD) v témže srovnání: C1 −516 / +677, C2 1 489 / 3 237, C3 4 162 / 4 212, C4 −3 018 / −1 780,
C5 366 / 4 096, C6 −1 098 / −4 926, C7 −7 487 / −12 008, C8 −10 306 / −7 809, C9 417 / 2 467,
C8b −9 212 / −9 258 (vždy A / B).

*Jak číst:* „Rozdíl B − A“ je rozdíl Exp. R (kladný = na datech B vychází kandidát lépe); „Shoda
znaménka“ říká, zda oba zdroje dávají stejný směr výsledku. *Co z toho plyne:*

- **Kvalitativní závěr je stejný u 9 z 10 kandidátů** [E]. Jediná neshoda je C1 – denní strategie
  s 19 resp. 24 obchody, u které pár odlišných denních svíček změní znaménko; při takovém počtu obchodů
  je to v mezích šumu [I].
- **Session strategie C8 a C8b vycházejí na obou zdrojích téměř identicky** (C8b −0,016 R na obou,
  PF 0,858 na obou). Intradenní struktura cen je tedy v datech B zachycena dobře – to je důležité pro
  kapitolu 8, protože silný DEV efekt C8b pochází hlavně z let 2010–2016, kdy výzkumná řada stojí na B.
- **Trendové varianty vycházejí na B systematicky o něco lépe**: průměrný rozdíl B − A u C2, C3, C5, C9
  je +0,059 R (vlastní dopočet; medián přes všech 10 kandidátů +0,010 R, průměr +0,025 R). Rozdíl
  **nepochází z nákladů**: spread a skluz jsou na obou zdrojích téměř stejné (např. C2 1 237 vs. 1 221 USD,
  C9 777 vs. 742 USD), liší se hrubý výsledek (C5 3 030 vs. 7 091 USD, C9 2 151 vs. 4 236 USD).
  Příčinou jsou drobné rozdíly v OHLC barů dvou různých cenových feedů (korelace H1 výnosů A a B je
  0,9377, medián absolutního rozdílu ceny 0,041 USD; `data_quality.json`), které u breakout pravidel
  posunou okamžik proražení [I].
- **Důsledek pro interpretaci:** DEV výsledky trendových variant z období na datech B (2010–2016-08)
  mohou být mírně příznivější, než by byly na „reálném“ bid/ask feedu [I]. Čistší test je OOS
  2019–2023, který stojí výhradně na datech A. Rozdíly velikosti ±0,1 R na 36–92 obchodech jsou ale
  zároveň v mezích statistického šumu, takže z nich nelze vyvozovat víc než opatrnost.

## 7.9 Kandidát po kandidátovi: proč prošel / neprošel

### C1 – TSMOM D1 (benchmark): neprošel, plochý

Čistě −0,002 R (t −0,02, PF 0,980), hrubě 0,055 R (t 0,53). Long-only 0,002 R, short-only −0,032 R.
**Strategie je plochá už před náklady** a náklady – z 87 % swap, protože pozice je otevřená 95,6 % času –
srazí slabý hrubý výsledek na nulu. Důvod je v konstrukci [I]: literatura o TSMOM (Moskowitz, Ooi,
Pedersen 2012; Hurst, Ooi, Pedersen 2017) pracuje s desítkami trhů, měsíčním rebalancováním a
diverzifikací napříč třídami aktiv; jediný trh s 60denním signálem a 106 obchody za 9 let má malou
statistickou sílu. C1 navíc drží v průměru 29 dní, tedy mimo mandát 4 h – 10 dní, a sloužila jen jako
benchmark. **Verdikt:** neprošla bránou 1; na rozhodnutí by to nic neměnilo.

### C2 – Donchian H4 (předregistrovaná): neprošla těsně

Čistě 0,064 R (t 0,56), **PF 1,094 – o 0,006 pod hranicí 1,10**; Sharpe 0,19, CAGR 0,83 %, max DD 8,5 %.
Hrubě 0,183 R (t 1,50, PF 1,324) – **efekt před náklady existuje**, ale náklady odeberou 57,5 % hrubého
zisku v USD (64,9 % v R), z toho 55 % swap: C2 drží pozici v průměru 6,3 dne a je v trhu 46 % času.
Výsledek nese short strana (0,124 R vs. 0,014 R), a to z 85 % díky roku 2013 (kapitola 7.7).
Na zdroji A v letech 2016–2018 je slabší (0,056 R) než na B (0,115 R). **Verdikt:** formálně neprošla.
Rozdíl 0,006 v PF je statisticky bezvýznamný, ale pravidlo je pravidlo – C2 proto pokračovala jen
jako „předregistrovaná reference“ bez nároku na označení robustní (kapitola 9).

### C3 – EMA trend H4: prošla

Čistě 0,074 R (t 0,85, PF 1,221), Sharpe 0,31, **nejnižší max DD ze všech (3,7 %)**, CAGR 0,65 %.
Hrubě 0,116 R (t 1,30); náklady berou 38,6 % hrubého zisku (35,7 % v R, 0,041 R na obchod – nejlevnější
z trendových variant díky nízké frekvenci 18 obchodů ročně a expozici 28 %). Long-only −0,015 R,
short-only 0,131 R: DEV zisk je téměř celý z krátké strany a ze 77 % z let 2013–2015. Na obou zdrojích
v letech 2016–2018 prakticky stejná (0,200 vs. 0,189 R) – nejstabilnější vůči volbě dat. **Verdikt:**
prošla bránou 1; slabá, ale nejvyrovnanější.

### C4 – Volatility breakout D1: neprošel, edge ≈ 0 hrubě a náklady ho zničí

Čistě −0,036 R (t −1,21, PF 0,889), max DD 15,0 %, pod vodou 3 260 dní. Hrubě 0,010 R (t 0,34,
PF 1,028) – **hrubý edge je prakticky nulový**. Strategie obchoduje 77,5krát ročně s těsným stopem
(1 ATR) a výstupem po 2 dnech, takže náklady 0,046 R na obchod jsou čtyřapůlnásobkem hrubé expectancy.
Obě strany záporné, short výrazněji (−0,060 R). Výsledek odpovídá slabé literatuře (opening-range
breakout doložen pro ropu, pro zlato jen diplomové práce; kapitola 5). **Verdikt:** zamítnuta – chybí
hrubý efekt, ne jen levná exekuce.

### C5 – Squeeze breakout H4: prošla s nejvyšší t-statistikou

Čistě 0,109 R (**t 1,40 – nejvyšší z kandidátů**, PF 1,236), Sharpe 0,48, CAGR 1,92 %, max DD 6,4 %.
Hrubě 0,165 R (t 2,07 – jediná trendová varianta s hrubým t > 2). Náklady 33,7 % hrubého zisku.
**Jako jediná trendová varianta je symetrická** (long 0,110 R, short 0,107 R). Na zdroji A v letech
2016–2018 výrazně slabší (0,014 R) než na B (0,093 R) – první varování, že DEV výsledek může být
nadhodnocený. **Verdikt:** prošla bránou 1 a v pořadí podle t-statistiky byla první (kapitola 9).
Pozdější vývoj (OOS −0,092 R) ukázal, že DEV výsledek byl nejvíc „nafouknutý“ ze všech.

### C6 – RSI(2) pullback D1 (předregistrovaná): neprošla, záporná už před náklady

Čistě −0,018 R (t −0,68, PF 0,882); **hrubě −0,004 R (t −0,17, PF 0,961) – záporná i bez nákladů**.
Typický profil mean reversion: 64,6 % výher, ale průměrná výhra 0,24 R proti průměrné ztrátě 0,48 R.
Obě strany záporné (long −0,025, short −0,019 R), na obou datových zdrojích záporná. **Nejde o problém
nákladů, ale o neexistenci efektu v daném tvaru** [E]: Connorsova pravidla (SMA200 + RSI(2) < 10 / > 90)
pocházejí z akciových indexů, kde je krátkodobá reverze dobře zdokumentovaná; u zlata literatura
nabízela jen smíšenou evidenci (kontrariánský efekt i „inertia“, Caporale & Plastun) [I]. **Verdikt:**
zamítnuta.

### C7 – Z-score mean reversion H1: neprošla, významně záporná i hrubě

Čistě −0,117 R (t −4,35, PF 0,751), **ztráta 58,5 % kapitálu, max DD 60,4 %**. Hrubě −0,067 R
(t −2,44) – **statisticky významně záporná už před náklady**. Znamená to, že po odchylce o 2σ od
48hodinového průměru v „netrendovém“ režimu (efficiency ratio < 0,3) cena na H1 spíše pokračovala, než
se vracela [E]; náklady (166 obchodů ročně, 0,050 R na obchod) ztrátu jen prohloubily. Obě strany
silně záporné. **Verdikt:** zamítnuta; nejhorší kandidát screeningu. Opačná sázka (sledovat odchylku)
nebyla testována a nebyla předregistrovaná – její vyhodnocení by bylo nové data-mining [I].

### C8 – Session drift H1 (předregistrovaná): neprošla, hrubý efekt nulový

Čistě −0,018 R (t −2,90, PF 0,886), ztráta 34,2 % kapitálu. **Hrubě 0,001 R (t 0,21) – efekt v
předregistrovaném tvaru neexistuje.** Při 503 obchodech ročně stojí náklady 34,6 tis. USD a čistý
výsledek je proto spolehlivě záporný. Ve hrubém běhu je long noha (02→15 serverového času) mírně záporná
(−0,004 R) a short noha (15→21) mírně kladná (0,007 R). Diagnostika hodinového profilu (kapitola 8)
ukázala proč: dlouhé okno 19:00 → 08:00 NY smíchalo **rostoucí asijskou fázi a klesající londýnskou
fázi**, které se v DEV téměř přesně vyrušily. Opakovaný screening po opravě chyby exit-and-reverse
(kapitola 7.2) závěr nezměnil. **Verdikt:** zamítnuta v předregistrované podobě – a z ní odvozená
revize C8b je samostatný, data-driven kandidát.

### C9 – Donchian filtrovaný trendem USD (H4): prošla s nejvyšší expectancy

Čistě 0,192 R (t 1,15, PF 1,310 – nejvyšší expectancy i PF), Sharpe 0,37, CAGR 1,44 %, max DD 5,7 %,
nejkratší období pod vodou z trendových variant (940 dní). Hrubě 0,353 R (t 1,98). Náklady 30,1 % hrubého zisku. Filtr
(long breakout jen při USD indexu pod jeho 50denním průměrem, short jen nad ním, s jednodenním
zpožděním makrodat) obchoduje méně často než C2 – 144 místo 241 obchodů – s vyšší expectancy. Short strana 0,302 R vs. long 0,091 R. Na zdroji A v letech 2016–2018 jen 0,031 R
(B 0,142 R). **Verdikt:** prošla bránou 1. Už v DEV ale bylo zřejmé, že je to C2 s filtrem, tedy
stejná sázka – a filtr vyžaduje živý USD index (Fed H.10 s denním zpožděním).

### C8b – Asie long / Londýn short H1 (odvozeno z DEV): neprošla

Čistě 0,003 R (t 0,62), **PF 1,022 < 1,10** → brána 1 nesplněna, přestože čistý PnL je kladný
(+5 446 USD). Hrubě 0,022 R s t-statistikou 5,26 a Sharpe 1,72 – nejsilnější hrubý efekt screeningu,
ale **naměřený na týchž datech, ze kterých byla okna vybrána**, takže je optimisticky zkreslený.
Náklady pohltí 89,8 % hrubého zisku. Kladná je po nákladech jen krátká (londýnská) noha. **Verdikt:**
nesplnila bránu 1; přesto byla transparentně zařazena do plné validace jako jediná ne-momentum
anomálie s výrazným hrubým efektem (kapitoly 8 a 9).

## 7.10 Co DEV screening ukázal

- **Prošli jen tři kandidáti, všichni z jedné rodiny** (C3, C5, C9 – trend/momentum na H4). Ze tří
  předregistrovaných volb neprošla žádná: C2 o 0,006 v PF, C6 a C8 jasně.
- **Dvě celé rodiny selhaly už před náklady**: krátkodobá mean reversion (C6, C7) a čas v dni
  v předregistrovaném tvaru (C8). Stejně tak volatility breakout (C4). To je informativní negativní
  výsledek, ne nákladový artefakt [E].
- **Trend na H4 je slabě kladný** (čistě 0,06–0,19 R, t 0,56–1,40) a náklady mu berou zhruba třetinu
  až dvě třetiny hrubého zisku, hlavně swapem. DEV zisk krátké strany je z velké části jediný režim
  (2013–2015).
- **Vysokofrekvenční strategie potřebují hrubý efekt větší než náklady obchodu**, což na retail
  nákladech (spread ≈ 2 bp) nesplnila žádná – u C8b DEV efekt sotva, mimo DEV vůbec (kapitola 8).
- **Data A a B dávají kvalitativně stejné závěry** (shoda znaménka 9/10); breakout strategie jsou na B
  mírně příznivější, session strategie identické.
- **Statistická síla DEV je nízká**: žádná čistá t-statistika nepřesáhla 1,40. DEV screening proto
  mohl kandidáty vyřadit, ale nemohl žádný potvrdit.

> **Závěr:** DEV screening zamítl předregistrovanou trojici (C2 těsně na PF, C6 a C8 už před náklady) a
> bránu 1 propustil jen tři varianty téže sázky – trend/momentum na H4 – se slabým, nevýznamným čistým
> výsledkem, jehož velká část pochází z medvědího trhu 2013–2015. Jediný silný hrubý efekt (C8b) byl
> odvozen z týchž dat a po nákladech byl téměř nulový. Výsledek screeningu je proto filtr pro další
> testování, nikoli důkaz edge.

*Zdrojové soubory: `research/results/s01_dev_screen.json` a `research/results/s01_dev_screen.md`
(baseline, frictionless, sides, cross_source); `research/s01_dev_screen.py` (definice běhů);
`research/common.py` (funkce `run`, období DEV, nastavení risk configu); `research/PROTOCOL.md`
(brána 1, předregistrovaný výběr); `research/DEV_SELECTION.md`; `research/results/s02_C2.json`,
`s02_C3.json`, `s02_C5.json`, `s02_C9.json` (roční rozpad long/short PnL 2010–2018);
`research/results/data_quality.json` (korelace A/B, modelový spread); `tradingsystem/execution/engine.py`
(množina `closing`, exit-and-reverse); `tradingsystem/strategies/*.py` (pravidla kandidátů);
`REPORT.md` (kap. 2 – odchylka 2, oprava chyb enginu; kap. 6 a 16); vlastní dopočty: podíl nákladů na
hrubém zisku a struktura nákladů (z `s01_dev_screen.json`), rekonstrukce prvního chybného běhu
(dočasné nahrazení `ExecutionEngine._exit` v paměti, `research/common.py::run` na DEV), roční změny
ceny zlata (`stitched('D1')`, mid close), podíl roku 2013 a let 2013–2015 na short PnL.*
