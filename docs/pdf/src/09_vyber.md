# 9. Rozhodnutí po DEV: výběr k plné validaci

DEV screening (kapitola 7) skončil tak, že ani jeden ze tří předregistrovaných kandidátů neprošel
bránou 1. Tato kapitola popisuje, jak se s tím výzkum vypořádal: co přesně předepisoval protokol, jaké
rozhodnutí bylo zapsáno v `research/DEV_SELECTION.md`, proč do plné validace šli C5, C9 a C3 a navíc
C2 a C8b, jaké testy byly k tomu deklarovány předem, jak vzniklo číslo N = 60 pro deflated Sharpe a –
hlavně – zda je taková náhrada metodicky legitimní a co znamená pro interpretaci výsledků OOS.

**Chronologie (git):** protokol `PROTOCOL.md` byl commitnut před prvním během jakékoli strategie
(6a151db); DEV screening, oprava dvou chyb enginu, revize C8b a rozhodnutí `DEV_SELECTION.md` jsou
v commitu 41ce7b8, **před jakýmkoli během na OOS 2019–2023**; specifikace a pořadí byly zmrazeny
v `frozen_spec.json` (cfe78c3) před holdoutem; holdout byl spuštěn jednou (87cd6b6). Rozhodnutí
popsaná v této kapitole tedy nemohla být ovlivněna výsledky OOS ani holdoutu [E].

## 9.1 Výchozí stav: co předepisoval protokol

Protokol (`research/PROTOCOL.md`, kap. 3) vybral pro plné testování tři strategie z literaturního
scorecardu – nejvyšší skóre s horizontem držení v mandátu a s **preferencí komplementarity**:

1. **C2 Donchian H4** – trend / breakout;
2. **C8 Session drift H1** – časová anomálie;
3. **C6 RSI(2) pullback D1** – podmíněná mean reversion.

Protokol výslovně uvádí, že C3 (třetí nejvyšší skóre) byla nahrazena C6, protože „C3 je stejná sázka
jako C2“. Ostatní kandidáti (C1, C3, C4, C5, C7, C9) se měli na DEV spustit jako **kontrolní skupina**
se stejnými náklady. Pro případ selhání protokol obsahuje pravidlo:

> „Výměna vybrané strategie za kontrolní je povolena jen tehdy, když vybraná selže na DEV branách —
> a musí být v reportu označena (zvyšuje počet testů pro deflated Sharpe).“ (`PROTOCOL.md`, kap. 3)

Brána 1 (`PROTOCOL.md`, kap. 6): na DEV čistá expectancy > 0 a PF > 1,10 při baseline nákladech.

Co protokol **nestanovil**: kolik kontrolních kandidátů smí nastoupit, podle jakého kritéria se mezi
nimi vybírá a zda smí být přidána revize kandidáta, který selhal. Tyto mezery vyplnil až dokument
`DEV_SELECTION.md` – po zhlédnutí DEV výsledků, ale před OOS [E]. To je podstatné pro hodnocení
legitimity (kapitola 9.8).

## 9.2 Co se stalo s předregistrovaným výběrem

| Kandidát | DEV exp. R | PF | t | Hrubá exp. R | Brána 1 | Rozhodnutí v `DEV_SELECTION.md` |
|---|---|---|---|---|---|---|
| C2 Donchian H4 | 0,064 | 1,094 | 0,56 | 0,183 | NE (těsně) | ponechána jako referenční člen trendové rodiny, nezpůsobilá pro označení „robustní“ |
| C6 RSI(2) pullback D1 | −0,018 | 0,882 | −0,68 | −0,004 | NE | zamítnuta (literatura ji podporuje, XAUUSD ne) |
| C8 Session drift H1 | −0,018 | 0,886 | −2,90 | 0,001 | NE | zamítnuta v předregistrované podobě |

*Jak číst:* čísla z `s01_dev_screen.json` (DEV 2010–2018, baseline náklady); „Hrubá exp. R“ je
z bezfrikčního běhu. *Co z toho plyne:* dvě ze tří předregistrovaných strategií selhaly **už před
náklady** (C6 hrubě záporná, C8 hrubě nulová), takže je nemohla zachránit ani lepší exekuce. C2 má
hrubý efekt, ale náklady ji stáhly těsně pod hranici PF. Podle protokolu tím vznikl nárok na náhradu
všech tří pozic. Rozbor jednotlivých selhání je v kapitolách 7.9 a 8.6.

## 9.3 Pravidlo náhrady a pořadí podle DEV t-statistiky

`DEV_SELECTION.md` (sekce „Pravidlo náhrady (stanoveno teď, před OOS)“) určil: do plné validace jdou
kontrolní kandidáti, kteří splnili DEV bránu 1, seřazení podle t-statistiky čisté expectancy v DEV.
Bránu 1 splnili právě tři:

| Pořadí | Kandidát | Rodina | DEV exp. R | PF | t | Sharpe | Hrubá exp. R | Obch. DEV |
|---|---|---|---|---|---|---|---|---|
| 1 | C5 Squeeze H4 | momentum po konsolidaci | 0,109 | 1,236 | 1,40 | 0,48 | 0,165 | 331 |
| 2 | C9 USD-filtr. Donchian H4 | trend + makro filtr | 0,192 | 1,310 | 1,15 | 0,37 | 0,353 | 144 |
| 3 | C3 EMA trend H4 | trend (klouzavé průměry) | 0,074 | 1,221 | 0,86 | 0,31 | 0,116 | 163 |

*Jak číst:* „Pořadí“ je pořadí v `DEV_SELECTION.md`; všechna ostatní čísla jsou z
`s01_dev_screen.json`. *Co z toho plyne:*

- **Proč t-statistika:** t kombinuje velikost expectancy s počtem obchodů a jejich rozptylem, je to tedy
  přirozená míra síly důkazu. Samotná expectancy nebo PF by favorizovaly C9, která má nejméně obchodů
  a tím i nejvíc nejistý odhad [I].
- **Na volbě kritéria nezáleželo:** bránu prošli přesně tři kandidáti, takže **množina** validovaných
  náhradníků by byla stejná při řazení podle t, PF (C9 > C5 > C3) i expectancy (C9 > C5 > C3) [E].
  Pořadí 1–3 bylo jen pracovní; finální pořadí (C3, C2, C5) určila až plná validace a bylo zmrazeno
  před holdoutem (`frozen_spec.json`).
- **Síla důkazu je i u náhradníků nízká**: nejvyšší t je 1,40. Brána 1 je filtr, ne potvrzení.

## 9.4 Proč navíc C2 a C8b

`DEV_SELECTION.md` přidal do plné validace ještě dva kandidáty, „transparentně, bez nároku na označení
robustní, pokud nesplní všechny brány“:

**C2 Donchian H4 – předregistrovaná reference.** C2 neprošla bránou 1 jen o 0,006 v PF a měla
nejsilnější apriorní evidenci z trendové rodiny (scorecard 71,7, Turtle pravidla). Její zařazení má dva
důvody: (a) jde o původní předregistrovanou volbu, kterou je fér sledovat dál, a (b) slouží jako
**kontrola výběrového zkreslení** – C2 nebyla do validace vybrána podle DEV výkonu, takže srovnání jejího
vývoje DEV → OOS s náhradníky ukazuje, jak velkou roli hrál výběr (kapitola 9.8) [I]. Formálně je od
začátku nezpůsobilá pro označení „robustní“, protože bránu 1 nesplnila.

**C8b Asie long / Londýn short – jediná ne-momentum anomálie.** C8b je datově odvozená revize C8
(kapitola 8). Bránu 1 nesplnila (PF 1,022), ale měla nejsilnější hrubý efekt celého screeningu (hrubý
Sharpe 1,72, hrubá t 5,26) a byla **jediným kandidátem, který mohl obsadit slot ne-trendového,
komplementárního zdroje edge**. `DEV_SELECTION.md` ji označuje jako „cost-conditional“ a výslovně
přiznává, že je „odvozena z DEV dat (data-mining riziko, mnoho možných oken) → v DEV je optimisticky
zkreslená“. Jako jediný doplňující nezávislý doklad uvádí kladnou asijskou nohu v pre-sample 2004–2009.

*Co z toho plyne:* do plné validace šlo pět strategií – tři náhradníci vybraní pravidlem, jedna
předregistrovaná reference a jedna data-driven anomálie. Pouze první tři mohly formálně získat
označení „robustní“; v praxi nesplnil všech sedm bran nikdo (kapitola 19 `REPORT.md`).

## 9.5 Náhradníci jsou stejná sázka

`DEV_SELECTION.md` to zapsal přímo a před OOS: **„Všichni tři jsou stejná ekonomická sázka
(momentum/trend).“** Žádný kandidát z rodin mean reversion ani session bránu 1 nesplnil.

Proč jde o stejnou sázku [E/R]:

- C3 (křížení EMA 20/100), C2 (proražení 55barového kanálu) a C9 (C2 s filtrem USD) jsou lineární
  trendové filtry nad stejnou cenou; Levine & Pedersen (2016) ukazují, že TSMOM a křížení klouzavých
  průměrů jsou ekvivalentní třídy filtrů. C5 (proražení Bollingerova pásma po kompresi volatility)
  vstupuje také ve směru pohybu.
- Všechny tři obchodují H4 se stejným horizontem (3–7 dní) a v DEV vydělaly hlavně na krátké straně
  v medvědím trhu 2013–2015 (kapitola 7.7).
- Pozdější analýza to potvrdila kvantitativně: pokud jsou dvě strategie z trojice C3/C2/C5 v trhu
  současně, jsou ve stejném směru v 98,7–100 % společného času, korelace denních výnosů 0,34–0,45,
  korelace drawdownů 0,67–0,70; C2 a C9 mají korelaci denních výnosů 0,79 (`s03_portfolio*.json`,
  kapitola 18 `REPORT.md`).

*Co z toho plyne:* náhrada **obětovala požadavek komplementarity**, kvůli kterému protokol původně
vyřadil C3. Ironií je, že všichni tři náhradníci patří přesně do kategorie, které se předregistrace
chtěla vyhnout. Zadání („3 nejrobustnější strategie“) tím nemohlo být splněno ve smyslu tří nezávislých
zdrojů edge – a výzkum to říká otevřeně od DEV fáze, ne až po výsledcích.

## 9.6 Doplňkové mřížky a testy deklarované před OOS

Protokol obsahoval perturbační mřížky, timeframy a walk-forward jen pro předregistrované C2, C8 a C6.
Pro náhradníky a C8b je proto `DEV_SELECTION.md` deklaroval **před OOS** (implementace v
`research/registry.py`, hodnoty se shodují):

| Strategie | Plná mřížka (DEV+OOS) | Bodů | One-at-a-time | Walk-forward 3 × 3 | Timeframy |
|---|---|---|---|---|---|
| C3 | fast {15, 17, 20, 23, 25} × slow {75, 85, 100, 115, 125} × stop_atr {2,25; 2,625; 3,0; 3,375; 3,75} | 125 | — | fast {15, 20, 25} × slow {75, 100, 125} | H2, H3, H4, H6, D1 |
| C5 | bb_n {15, 17, 20, 23, 25} × squeeze_pct {0,15; 0,175; 0,2; 0,225; 0,25} × stop_atr {1,5; 1,75; 2,0; 2,25; 2,5} | 125 | rank_n {90, 105, 120, 135, 150}; max_hold {22, 26, 30, 34, 38} | bb_n {15, 20, 25} × squeeze_pct {0,15; 0,2; 0,25} | H2, H3, H4, H6 |
| C9 | mřížka C2: entry_n {41, 47, 55, 63, 69} × exit_n {15, 17, 20, 23, 25} × stop_atr {1,5; 1,75; 2,0; 2,25; 2,5} | 125 | usd_ma {38, 44, 50, 56, 63} | entry_n {41, 55, 69} × exit_n {15, 20, 25} | H2, H3, H4, H6, D1 |
| C2 | z protokolu: entry_n × exit_n × stop_atr jako u C9 | 125 | — | entry_n {41, 55, 69} × exit_n {15, 20, 25} | H2, H3, H4, H6, D1 |
| C8b | long_entry {1, 2, 3} × long_exit {8, 9, 10}; short_entry {8, 9, 10} × short_exit {14, 15, 16} | 18 | stop {0,75; 1,0; 1,25; 1,5} | — (pevná pravidla, jen roční řez) | báze M30 a posun hranic ± 30 min |

*Jak číst:* mřížky pokrývají zhruba ±25 % kolem výchozí (literaturní) hodnoty každého parametru;
„one-at-a-time“ mění jeden další parametr při ostatních výchozích; walk-forward vybírá z mřížky 3 × 3
podle Sharpe v tréninku (4 roky trénink, 1 rok test, 2014–2023); u timeframů se délky indikátorů
škálují na stejný reálný čas. *Co z toho plyne:*

- **Deklarace před OOS brání „ladění robustnosti“**: kdyby se rozsah mřížky volil po zhlédnutí
  výsledků, šlo by podíl kladných sousedů (brána 4) nastavit téměř libovolně [I].
- Náklady ×1,5 / ×2, ECN scénář, zpoždění vstupu, bootstrap, režimy, subperiody a long/short byly
  stanoveny už v protokolu pro všechny strategie stejně.
- Jedinou zjištěnou mezerou je, že pro C5 nebyl deklarován timeframe D1 (odchylka 12 v kapitole 4.10);
  dopad je malý, C5 je kladná na všech čtyřech testovaných timeframech.
- U C8b je mřížka fakticky menší, než vypadá – některé kombinace obchodují jen jednu nohu
  (kapitola 8.10).

## 9.7 Počet testů N = 60 pro deflated Sharpe

**Jak bylo N odvozeno.** `DEV_SELECTION.md`: „Počet testovaných konfigurací pro deflated Sharpe:
10 kandidátů v DEV screenu + C8b revize (~50 implicitně zvažovaných oken) → konzervativně N = 60.“
Hodnota je zapsána v `research/s02_validate.py` (`N_TRIALS = 60`) a použita pro všech pět validovaných
strategií.

**Jak se N použije.** Deflated Sharpe ratio (Bailey & López de Prado 2014) porovnává pozorovaný Sharpe
s prahem SR0 = očekávaným maximem Sharpe z N bezcenných pokusů:

```
SR0 = sqrt(V) * [ (1 - g) * Phi^-1(1 - 1/N) + g * Phi^-1(1 - 1/(N*e)) ]
g   = 0,5772 (Eulerova-Mascheroniho konstanta), Phi^-1 = kvantilová funkce N(0,1)
V   = rozptyl denních Sharpe ratio 10 variant DEV screeningu
DSR = Phi( (SR - SR0) * sqrt(T - 1) / sqrt(1 - skew*SR + (kurt - 1)/4 * SR^2) )
```

S rozptylem Sharpe z DEV screeningu vychází **SR0 = 1,465 ročně** (vlastní ověření výpočtem shodné
s `s02_<K>.json`). Pozorované Sharpe DEV+OOS jsou 0,169 (C5), 0,221 (C2), 0,238 (C9) a 0,249 (C3),
C8b −0,350 → **DSR je u všech prakticky 0**, PSR(Sharpe > 0) 0,74–0,83 u trendových variant a 0,09
u C8b (`s02_<K>.json`).

**Citlivost prahu SR0 na volbu N** (vlastní dopočet stejným vzorcem a stejným V):

| N | SR0 (roční) |
|---|---|
| 5 | 0,74 |
| 10 | 0,98 |
| 20 | 1,19 |
| 60 | 1,46 |
| 125 | 1,63 |
| 253 | 1,77 |
| 1 771 | 2,13 |

*Jak číst:* N = 253 a 1 771 odpovídají počtu jednoduchých resp. dvounohých oken, ze kterých šlo C8b
vybrat (kapitola 8.7); N = 125 je velikost plné perturbační mřížky. *Co z toho plyne:*

- **Na přesné hodnotě N závěr nezávisí**: i při N = 5 je práh 0,74, tedy třikrát nad nejlepším
  pozorovaným Sharpe 0,25. Přesnější počítání pokusů by závěr jen zpřísnilo.
- **Práh je vysoký hlavně kvůli rozptylu V**, ne kvůli N: Sharpe deseti variant DEV screeningu se
  liší od −1,41 (C7) po +0,48 (C5), směrodatná odchylka ročního Sharpe je 0,62. Bez C7 a C8 by SR0 při
  N = 60 bylo 0,72 (vlastní dopočet) – stále téměř trojnásobek pozorovaných hodnot.
- **Je N = 60 „konzervativní“?** Jen částečně [I]. Započítává 10 variant screeningu a velkoryse volbu
  oken C8b, ale nezapočítává: druhý pohled na DEV po opravě chyby (kapitola 7.2), výběr literaturních
  parametrů a samotného univerza, walk-forward výběry, timeframové varianty a nákladové scénáře. Ty
  ovšem většinou slouží jako testy robustnosti, ne jako výběr, takže jejich započítání by bylo
  přehnané. Naopak kombinatorický prostor oken C8b (253 / 1 771) je větší než odhad „~50“, okna se ale
  silně překrývají. Rozumný rozsah efektivního N je tedy zhruba desítky až nízké stovky – a v celém
  tomto rozsahu je DSR ≈ 0.

**Mírnější varianta** (doplňková, **nepředregistrovaná**, spočtená po holdoutu v commitu 87cd6b6;
`dsr_within_grid.json`): N = 125 a rozptyl Sharpe uvnitř perturbační mřížky každé strategie. Tato
varianta měří jen riziko „vybrali jsme nejlepší parametry z mřížky“, ne riziko výběru rodiny:

| Strategie | N (mřížka) | Sharpe DEV+OOS | SR0 | PSR | DSR |
|---|---|---|---|---|---|
| C3 | 125 | 0,249 | 0,319 | 0,830 | 0,393 |
| C2 | 125 | 0,221 | 0,203 | 0,801 | 0,527 |
| C5 | 125 | 0,169 | 0,304 | 0,740 | 0,304 |
| C9 | 125 | 0,238 | 0,206 | 0,819 | 0,549 |

*Jak číst:* DSR je pravděpodobnost, že skutečný Sharpe převyšuje práh SR0; za přesvědčivé se považuje
DSR ≥ 0,95. *Co z toho plyne:* ani v této mírné variantě se žádná strategie nepřiblížila 0,95 (nejvýše
0,55). Výsledek trendové rodiny je slučitelný s tím, že jde o nejlepší z řady bezcenných pokusů
(kapitola 17 `REPORT.md`).

## 9.8 Je tato náhrada legitimní?

**Argumenty pro legitimitu:**

1. **Možnost náhrady byla předregistrovaná** – pravidlo stojí v protokolu, který byl commitnut před
   prvním během strategie (6a151db). Nejde o improvizaci po zhlédnutí výsledků [E].
2. **Konkrétní volba byla zapsána před OOS** (41ce7b8): množina, pořadí, doplňkové mřížky i N pro
   deflated Sharpe. OOS 2019–2023 tedy zůstal čistým testem právě těchto rozhodnutí [E].
3. **Výběr byl mechanický**, podle předem dané brány 1; množina náhradníků nezávisí na tom, zda se
   řadí podle t, PF nebo expectancy (kapitola 9.3).
4. **Transparentnost:** stejná sázka, data-driven původ C8b i zvýšený počet testů jsou přiznány
   v `DEV_SELECTION.md`, odchylky jsou vyjmenovány v reportu (kapitola 4.10).
5. **Alternativa by byla méně informativní:** striktní čtení („nic neprošlo, konec“) by bylo poctivé,
   ale neodpovědělo by na otázku, zda nejlepší DEV rodina přežije mimo DEV. Náhrada tuto otázku
   umožnila položit a OOS na ni odpověděl.

**Rizika a slabiny:**

1. **Výběrové zkreslení („prokletí vítěze“):** náhradníci byli vybráni *proto*, že v DEV vyšli dobře.
   Jejich DEV čísla jsou proto nadhodnocená a nemají důkazní váhu; důkazem mohou být až data mimo DEV.
2. **Mnohonásobné testování:** pět strategií v OOS zvyšuje šanci, že alespoň jedna projde OOS branou
   náhodou [I]. Částečně to kompenzuje DSR s N = 60 (kapitola 9.7).
3. **Ztráta komplementarity:** původní cíl tří odlišných sázek byl opuštěn (kapitola 9.5).
4. **Mezery protokolu vyplněné až po DEV:** počet náhradníků, kritérium řazení a přidání C2 a C8b
   určil `DEV_SELECTION.md` po zhlédnutí DEV (byť před OOS) – to je „zahrada rozvětvených cest“ v malém
   [I]. Výzkumník navíc viděl DEV výsledky dvakrát (oprava chyby) a z DEV odvodil C8b.
5. **Riziko kontaminace výzkumníka [U]:** autor zná obecný vývoj trhu zlata do roku 2026; zmrazení
   pravidel chrání parametry, ne volbu rodiny strategií (kapitola 17 `REPORT.md`).

**Dopad na interpretaci OOS – co se stalo s náhradníky mimo DEV** (`s02_<K>.json`):

| Kandidát | Jak se dostal do validace | PRE exp. R | DEV exp. R | OOS exp. R | OOS − DEV | DEV Sharpe | OOS Sharpe | OOS PF |
|---|---|---|---|---|---|---|---|---|
| C5 Squeeze H4 | náhrada (DEV t 1,40) | 0,122 | 0,109 | −0,092 | −0,200 | 0,48 | −0,41 | 0,824 |
| C9 USD-filtr. Donchian H4 | náhrada (DEV t 1,15) | 0,123 | 0,192 | −0,013 | −0,205 | 0,37 | 0,00 | 0,965 |
| C3 EMA trend H4 | náhrada (DEV t 0,86) | 0,064 | 0,074 | 0,038 | −0,036 | 0,31 | 0,16 | 1,122 |
| C2 Donchian H4 | předregistrovaná reference | 0,316 | 0,064 | 0,094 | 0,030 | 0,19 | 0,26 | 1,140 |
| C8b Asie/Londýn H1 | z DEV hodinového profilu | −0,005 | 0,003 | −0,017 | −0,019 | 0,21 | −1,41 | 0,843 |

*Jak číst:* PRE = pre-sample 2004–2009 (data B, k výběru nepoužit), DEV = 2010–2018 (období výběru),
OOS = 2019–2023 (data A). „OOS − DEV“ je změna expectancy v R. *Co z toho plyne:*

- **Všichni tři náhradníci se v OOS zhoršili** (průměrně o 0,147 R, vlastní dopočet) a **nejvíc ti,
  kteří byli v DEV nejlepší**: C5 (DEV t 1,40) a C9 (nejvyšší DEV expectancy) klesli o 0,20 R na
  zápornou expectancy, C3 jen o 0,036 R. Pořadí se úplně obrátilo – v DEV C5 > C9 > C3, v OOS
  C3 > C9 > C5 [E].
- **C2, která do validace nebyla vybrána podle DEV výkonu, se v OOS mírně zlepšila** (+0,030 R). To je
  přesně vzorec, který výběrové zkreslení předpovídá: co bylo vybráno jako nejlepší, regreduje; co
  vybráno nebylo, se chová „normálně“ [I]. Při 84–179 OOS obchodech na strategii jsou ale rozdíly
  statisticky slabé, takže jde o indicii, ne důkaz.
- **Ani jeden náhradník nesplnil OOS bránu 2** (expectancy > 0, PF > 1,05, Sharpe > 0,3): náhrada tedy
  „nevyrobila“ vítěze, jen umožnila test.
- **Pre-sample 2004–2009 je kladný u všech čtyř trendových variant** (0,064–0,316 R) a záporný u C8b.
  Protože pre-sample nebyl k výběru použit, je spolu s OOS a holdoutem hlavním nezávislým důkazem pro
  trendovou rodinu – ten je ale slabý (kapitoly 8 a 19 `REPORT.md`).

**Hodnocení [I]:** náhrada je **procedurálně legitimní** – byla předem povolená, provedená mechanicky,
zapsaná před OOS a otevřeně přiznaná. **Důkazní hodnotu ale nepřidává**: mění otázku z „funguje
předregistrovaná komplementární trojice?“ (odpověď: ne) na „přežije nejlepší rodina z DEV mimo DEV?“
(odpověď: slabě a ne podle bran). Pro správnou interpretaci z toho plynou tři pravidla:

1. DEV výsledky náhradníků se nesmí citovat jako důkaz; relevantní jsou PRE, OOS a holdout.
2. Statistická významnost se musí posuzovat po korekci na výběr (DSR s N = 60) – a ta je nulová.
3. Úsudek o trendové rodině má stát na konzistenci napříč nezávislými obdobími a na robustnostním
   profilu (perturbace, timeframe, náklady), ne na výsledku jednoho období.

## 9.9 Shrnutí

- Předregistrovaná trojice C2 + C8 + C6 na DEV selhala (C2 těsně na PF, C6 a C8 už před náklady).
- Podle předem povoleného pravidla nastoupili kontrolní kandidáti, kteří prošli bránou 1 – **C5, C9,
  C3** (pořadí podle DEV t-statistiky; množina by byla stejná při jakémkoli rozumném kritériu) –
  a transparentně navíc **C2** (předregistrovaná reference) a **C8b** (jediná ne-momentum anomálie).
- **Všichni tři náhradníci jsou jedna sázka** (trend/momentum na H4) – zapsáno před OOS.
- Mřížky, walk-forward a timeframy pro náhradníky a C8b byly deklarovány před OOS; N = 60 pro deflated
  Sharpe vzniklo jako 10 variant screeningu + odhad ~50 oken C8b. Závěr DSR ≈ 0 na volbě N nezávisí.
- V OOS se náhradníci vybraní podle DEV výkonu zhoršili tím víc, čím lepší byli v DEV, kdežto
  nevybraná C2 se mírně zlepšila – typický otisk výběrového zkreslení.

> **Závěr:** Náhrada předregistrovaných strategií kontrolními kandidáty byla předem povolená, provedená
> podle mechanického pravidla a zapsaná před OOS, takže OOS zůstal čistým testem. Za cenu toho byla
> opuštěna komplementarita – do validace postoupily tři varianty téže trendové sázky – a vzrostl počet
> testů. Výsledky OOS ukázaly klasický efekt „prokletí vítěze“ a žádná náhrada nesplnila OOS bránu.
> Náhrada je proto legitimní jako postup, ale neposiluje důkaz: hodnocení trendové rodiny musí stát
> na nezávislých obdobích (PRE, OOS, holdout) a na korekci na výběr, která statistickou významnost
> nepotvrzuje.

*Zdrojové soubory: `research/DEV_SELECTION.md` (rozhodnutí, pravidlo náhrady, doplňkové mřížky, N = 60);
`research/PROTOCOL.md` (předregistrovaný výběr, pravidlo náhrady, brány); `research/frozen_spec.json`
(zmrazené pořadí); `research/registry.py` (implementace mřížek, walk-forward a timeframů);
`research/s02_validate.py` (`N_TRIALS = 60`, výpočet rozptylu Sharpe z DEV screeningu);
`research/stats.py` (`deflated_sharpe`); `research/results/s01_dev_screen.json` (DEV výsledky);
`research/results/s02_C3.json`, `s02_C2.json`, `s02_C5.json`, `s02_C9.json`, `s02_C8b.json` (segmenty
PRE/DEV/OOS, DSR, brány); `research/results/dsr_within_grid.json`; `research/results/s03_portfolio.json`
a `s03_portfolio_C2_C3_C5_C9.json` (korelace); `REPORT.md` (kap. 2, 6, 17, 18, 19);
`docs/pdf/src/04_metodika.md` (chronologie commitů, odchylky); vlastní dopočty: citlivost SR0 na N
a na vyřazení C7/C8 (vzorec z `stats.py`, rozptyl z `s01_dev_screen.json`), ověření SR0 = 1,465,
průměrná změna expectancy DEV → OOS náhradníků, invariance množiny náhradníků vůči kritériu řazení.*
