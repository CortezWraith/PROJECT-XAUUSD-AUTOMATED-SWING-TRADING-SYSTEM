# 6. Univerzum kandidátů a scorecard

Tato kapitola popisuje všech jedenáct kandidátů (C1–C11) a datově odvozenou revizi C8b tak podrobně,
aby je bylo možné znovu implementovat bez čtení kódu: hypotézu, ekonomický mechanismus, přesná pravidla
a parametry, timeframe, očekávané držení, oporu v literatuře a hlavní slabiny. Druhá polovina kapitoly
rozebírá literaturní scorecard (kritéria, váhy, skóre každého kandidáta a jejich zdůvodnění) a
předregistrovanou výběrovou logiku – včetně toho, proč byla volba C2 + C8 + C6 ex ante rozumná, přestože
dvě ze tří strategií pak na datech selhaly.

Všechna pravidla a parametry byly stanoveny **před prvním spuštěním jakékoli strategie** na datech
XAUUSD (protokol `research/PROTOCOL.md`, commit 6a151db). Kód tříd je v `tradingsystem/strategies/`;
scorecard v `research/scorecard.py` (výstup `research/results/scorecard.md`).

## 6.1 Jak bylo univerzum sestaveno

Zadání vyžaduje nejprve sestavit „rozumné univerzum kandidátů“ (ne začít se třemi předem vybranými
strategiemi), zhruba 6–10 rodin, a z nich vybrat tři pro backend testování. Univerzum bylo sestaveno
podle těchto principů:

1. **Jeden reprezentant na rodinu.** Každá ekonomicky odlišná myšlenka ze seznamu v zadání (trend,
   breakout, mean reversion, volatilitní expanze, makro filtr, sezónnost, čas v dni, ML) dostala jednoho
   kandidáta. Výjimkou je trend, kde jsou tři varianty (C2, C3, C5) a makro varianta C9 – trend má
   nejsilnější literaturu a různé implementace se liší obratem a chováním v režimech.
2. **Literaturní výchozí parametry**, žádná optimalizace (Turtle 55/20 a 2N, EMA 20/100, RSI(2) 10/90,
   Bollinger 20/2, 60denní TSMOM).
3. **Deterministická pravidla** počítaná z uzavřených barů, bez diskrece.
4. **Povinný ochranný stop** odvozený z ATR u každého vstupu, velikost pozice z rizika ke stopu.
5. **Přirozené držení v mandátu 4 h – 10 dní** jako tvrdá podmínka výběru (ne podmínka zařazení do
   univerza – C1 a C10 jsou v univerzu jako benchmark a kontrola).

Přehled univerza (realizované hodnoty jsou z DEV screenu 2010–2018, `s01_dev_screen.json`):

| ID | Rodina | Třída v kódu | TF | Počet parametrů | Apriorní držení | Ø držení DEV (h) | Obch./rok DEV | Stav |
|---|---|---|---|---|---|---|---|---|
| C1 | Time-series momentum | `TimeSeriesMomentum` | D1 | 3 | týdny až měsíce | 693 | 11,8 | benchmark, mimo mandát; DEV ≈ 0 |
| C2 | Cenový kanál (Donchian/Turtle) | `DonchianBreakout` | H4 | 5 | 3–10 dní | 152 | 26,8 | předregistrovaná; finální #2 |
| C3 | Klouzavé průměry (EMA cross) | `EmaTrend` | H4 | 4 | 2–8 dní | 133 | 18,1 | kontrolní; finální #1 |
| C4 | Volatility / range breakout | `VolatilityBreakout` | D1 | 4 | 1–3 dny | 49 | 77,5 | zamítnuta v DEV |
| C5 | Momentum po konsolidaci | `SqueezeBreakout` | H4 | 8 | 1–5 dní | 82 | 36,8 | kontrolní; finální #3 |
| C6 | Podmíněná mean reversion | `TrendPullbackRSI` | D1 | 8 | 2–7 dní | 114 | 28,9 | předregistrovaná; zamítnuta v DEV |
| C7 | Volatilitou podmíněná reverze | `RangeZScoreReversion` | H1 | 6 | 4–24 h | 19 | 166,2 | zamítnuta v DEV |
| C8 | Čas v dni (session drift) | `SessionDrift` | H1 | 6 (pevné hodiny) | 6–13 h | 10 | 502,7 | předregistrovaná; zamítnuta v DEV |
| C9 | Makro-podmíněný trend | `MacroFilteredDonchian` | H4 | 6 | 3–10 dní | 156 | 16,0 | kontrolní; vyřazena po validaci |
| C10 | Kalendářní sezónnost | neimplementováno | D1 | 0 | měsíc | — | — | netestováno |
| C11 | ML klasifikátor směru | neimplementováno | — | — | — | — | — | vyloučeno |
| C8b | Čas v dni, revize z DEV dat | `AsiaLondonSession` | H1 | 6 (pevné hodiny) | 6–7 h | 7 | 508,2 | zamítnuta po validaci |

*Jak číst:* „Počet parametrů“ nepočítá přepínače `allow_long` a `allow_short`; u C8 a C8b jsou čtyři
z parametrů hodiny daných hranicemi seancí, nikoli laděné hodnoty. *Co z toho plyne:* realizované
držení potvrdilo apriorní odhady – C1 drží v průměru 693 h (zhruba 29 kalendářních dní), tedy skutečně
mimo mandát; C7, C8 a C8b obchodují stovky krát ročně, což z nich dělá nákladově nejcitlivější
kandidáty; trendové varianty na H4 drží 3–7 dní, přesně uprostřed mandátu.

## 6.2 Společné prvky všech kandidátů

Tyto vlastnosti platí pro všechny implementované kandidáty a jsou součástí rozhraní `Strategy`
(`tradingsystem/strategies/base.py`):

- **Signál na uzavřeném baru** z cen střed (bid + ask) / 2. Strategie nevidí equity účtu a nikdy
  neposílá příkazy brokerovi – vrací jen signály ENTER, EXIT, UPDATE_STOP.
- **Exekuce:** market příkaz se plní na open dalšího baru (long za ask, short za bid) plus skluz;
  stop-entry (jen C4) se plní na horší z úrovně a open; ochranný stop se kontroluje na granularitě H1
  i pro H4/D1 strategie, při mezeře se plní na open.
- **Posun stopu jen ve směru snížení rizika:** UPDATE_STOP je exekučním enginem ignorován, pokud by stop
  povolil (`execution/engine.py::_update_stop`); pokud by nový stop byl už za trhem, pozice se místo
  toho zavře.
- **Jedna pozice na strategii**, žádné pyramidování ani průměrování.
- **Sizing:** riziko 0,5 % equity (rebasované na začátku měsíce) / (abs(vstup − stop) × 100 oz),
  zaokrouhleno dolů na 0,01 lotu.
- **Časová osa:** serverový čas = New York + 7 h; H4 bary ukotvené na serverovou půlnoc (00, 04, …, 20);
  D1 = obchodní den 17:00–17:00 NY.

Definice indikátorů (`tradingsystem/signals/indicators.py`; všechny kauzální, ověřeno unit testem):

| Indikátor | Definice v kódu | Poznámka |
|---|---|---|
| SMA(n) | prostý klouzavý průměr n hodnot | — |
| EMA(n) | exponenciální průměr se span = n, bez korekce startu | live okno ≥ 3 × n barů kvůli paritě |
| ATR(n) | prostý průměr true range za n barů | ne Wilderovo vyhlazení; konečná paměť |
| Donchian high/low(n) | max high / min low **předchozích** n barů | aktuální bar vyloučen |
| RSI(n) | Cutlerova varianta: prosté průměry zisků a ztrát | ne Wilderova RSI |
| z-score(n) | (close − SMA) / směrodatná odchylka (ddof 0) | — |
| Efficiency ratio(n) | abs(čistá změna za n) / součet abs(změn) | 0 = šum, 1 = přímka |
| Bollinger bandwidth | 2k × σ / SMA (σ s ddof 0) | — |
| Percentilové pořadí(n) | podíl předchozích n − 1 hodnot menších než aktuální | rozsah 0–1 |

*Jak číst:* tabulka je referenční pro reimplementaci. *Co z toho plyne:* drobné odchylky od „učebnicových“
definic (prostý ATR, Cutlerova RSI) jsou záměrné – konečná paměť zaručuje, že backtest a live běh
spočítají na stejných datech identickou hodnotu. Při převodu do jiné platformy (např. MQL5) je nutné
použít stejné definice, jinak se signály budou lišit.

## 6.3 C1 – Time-series momentum D1 (benchmark)

- **Hypotéza:** znaménko výnosu za poslední ~3 měsíce predikuje směr dalšího pohybu.
- **Ekonomický mechanismus [R]:** nedoreakce a pomalá difúze informací, hedging pressure, pomalý kapitál
  (kapitola 5.2).
- **Pravidla:** `mom` = log(close / close před 60 D1 bary). Požadovaný směr = long, je-li `mom` > 0,
  jinak short. Je-li pozice v opačném směru, vystup (EXIT na close, plnění na open dalšího dne); nový
  vstup v novém směru přijde na **následujícím** close (otočení tedy trvá jeden den bez pozice). Bez
  pozice vstup ve směru `mom`. Katastrofický stop close ∓ 3 × ATR(20) D1, bez trailingu. Po zásahu
  stopu strategie znovu vstoupí na dalším close, pokud `mom` stále ukazuje stejný směr.
- **Parametry:** lookback 60, atr_n 20, stop_atr 3,0.
- **TF a držení:** D1; apriorně týdny až měsíce; v DEV průměrně 693 h.
- **Literatura:** nejsilnější (Moskowitz et al. 2012, Hurst et al. 2017, Han et al. 2016) – ale pro
  měsíční rebalancování a portfolia trhů.
- **Rizika:** horizont mimo mandát; malý počet obchodů (DEV 106 za 9 let); na jednom instrumentu bez
  diverzifikace; trpí při obratech trendu.
- **Výsledek (orientačně):** DEV −0,002 R na obchod (hrubě 0,055 R), PF 0,98 – benchmark nic nepřidal.

## 6.4 C2 – Donchian channel breakout H4 (předregistrovaná volba #1)

- **Hypotéza:** proražení ~9,5denního maxima/minima signalizuje začátek trendu, který pokračuje dny.
- **Ekonomický mechanismus [R/I]:** trendové mechanismy jako C1 + koncentrace stop příkazů a breakout
  obchodníků za hranicemi kanálu, jejichž aktivace pohyb zesiluje.
- **Pravidla (Turtle System 2):**
  - HH55 / LL55 = nejvyšší high / nejnižší low **předchozích** 55 H4 barů; XH20 / XL20 totéž pro 20 barů.
  - Long: close > HH55. Short: close < LL55. Signál na close, plnění na open dalšího baru.
  - Počáteční stop: close − 2 × ATR(20) pro long, close + 2 × ATR(20) pro short (Turtle „2N“).
  - Trailing: každý bar se stop posune na XL20 (long) / XH20 (short), je-li těsnější.
  - Výstup: close pod XL20 (long) / nad XH20 (short), nebo time-stop po 90 H4 barech (15 obchodních dní).
  - Re-entry: kdykoli close znovu překoná HH55 / LL55.
- **Parametry:** entry_n 55, exit_n 20, atr_n 20, stop_atr 2,0, max_hold 90.
- **TF a držení:** H4; apriorně 3–10 dní; v DEV průměrně 152 h (zhruba 6 dní).
- **Literatura:** kanálové strategie ve futures (Szakmary et al. 2010), ekvivalence s TSMOM
  (Levine & Pedersen 2016); negativní apriorní signál z Kurth et al. 2026 pro rychlý trend na small-tick
  kontraktech.
- **Rizika:** whipsawy v range a ve vysoké volatilitě; nízký win rate (kolem 30 %), dlouhé série ztrát;
  swap u vícedenních longů; time-stop 15 dní mírně přesahuje mandát 10 dní.
- **Výsledek (orientačně):** DEV 0,064 R, PF 1,094 – těsně pod bránou 1 (PF > 1,10); plně validována
  jako reference; nejlepší historický výsledek 2004–2026 (souhrnně 0,149 R, t 1,71); finální pořadí #2.

## 6.5 C3 – EMA trend H4 (kontrolní k C2)

- **Hypotéza:** stejná jako C2 – střednědobá persistence trendu – měřená křížením klouzavých průměrů.
- **Ekonomický mechanismus [R]:** jako C2; podle Levine & Pedersen jde o tentýž lineární trendový filtr.
- **Pravidla:**
  - EMA(20) a EMA(100) z close; stav = znaménko (EMA20 − EMA100).
  - Long: stav +1 a předchozí stav ≤ 0 (čerstvé křížení nahoru). Short zrcadlově. Vstup **jen na
    čerstvém křížení** – po zásahu stopu se znovu nevstupuje, dokud nepřijde opačné křížení.
  - Počáteční stop: close ∓ 3 × ATR(20).
  - Trailing: long max(stávající stop, nejvyšší close za 20 barů − 3 × ATR20); short min(stávající,
    nejnižší close za 20 barů + 3 × ATR20).
  - Výstup: opačný stav EMA (signál na close) nebo zásah stopu; bez time-stopu.
- **Parametry:** fast 20, slow 100, atr_n 20, stop_atr 3,0.
- **TF a držení:** H4; apriorně 2–8 dní; v DEV průměrně 133 h.
- **Literatura:** MA timing v komoditách (Szakmary et al. 2010, Han et al. 2016).
- **Rizika:** stejná sázka jako C2 (proto nebyla v předregistrované trojici); bez time-stopu může
  držet déle než 10 dní; široký stop 3 ATR.
- **Výsledek (orientačně):** jediná ze tří trendových variant, která prošla DEV bránou 1 a měla kladnou
  expectancy i při dvojnásobných nákladech; finální pořadí #1 (nejvyrovnanější profil).

## 6.6 C4 – Volatility breakout D1

- **Hypotéza:** den s neobvyklým rozšířením rozsahu (cena se vzdálí od včerejšího close o víc než
  zlomek ATR) pokračuje v daném směru 1–2 dny.
- **Ekonomický mechanismus [I]:** příchod nové informace se projeví expanzí rozsahu; obchodníci
  reagující se zpožděním pohyb prodlužují (rodina Williams / ORB).
- **Pravidla:**
  - Po každém denním close, je-li strategie bez pozice, se zadají dva stop-entry příkazy platné jeden
    den: buy stop na close + 0,5 × ATR(14), sell stop na close − 0,5 × ATR(14).
  - OCO: vyplnění jednoho zruší druhý (`brokers/simulated.py`).
  - Ochranný stop 1 × ATR(14) od vstupní úrovně.
  - Výstup: na close druhého denního baru po vstupu (signál EXIT, plnění na open dalšího dne).
- **Parametry:** k 0,5, atr_n 14, stop_atr 1,0, hold_days 2.
- **TF a držení:** D1; apriorně 1–3 dny; v DEV průměrně 49 h.
- **Literatura:** ORB na ropě (Holmberg et al. 2013); pro zlato jen diplomové práce.
- **Rizika:** vysoký obrat (77,5 obchodu ročně v DEV), stop příkazy se skluzem, úzký stop vůči šumu.
- **Výsledek (orientačně):** DEV −0,036 R, hrubě jen 0,010 R – zamítnuta.

## 6.7 C5 – Squeeze breakout H4 (momentum po konsolidaci)

- **Hypotéza:** po období neobvykle nízké volatility přichází expanze a první proražení pásma ukazuje
  její směr.
- **Ekonomický mechanismus:** shlukování volatility je robustní fakt **[E]**; predikovatelnost směru
  expanze je slabě podložená **[I/U]**.
- **Pravidla:**
  - Bollinger(20, 2σ): střed SMA20, pásma ± 2σ; bandwidth = 4σ / SMA20.
  - Percentilové pořadí bandwidth ve 120 barech; „squeeze“ = pořadí < 0,20 kdykoli v posledních 5 barech.
  - Long: squeeze a close > horní pásmo. Short: squeeze a close < dolní pásmo.
  - Stop: close ∓ 2 × ATR(20), bez trailingu.
  - Výstup: close zpět přes střední pásmo (long pod SMA20, short nad SMA20) nebo po 30 barech (5 dní).
  - Re-entry: je možný opakovaně, dokud squeeze podmínka platí (5barové okno).
- **Parametry:** bb_n 20, bb_k 2,0, rank_n 120, squeeze_pct 0,2, lookback 5, atr_n 20, stop_atr 2,0,
  max_hold 30 – nejvíc stupňů volnosti z trendové rodiny.
- **TF a držení:** H4; apriorně 1–5 dní; v DEV průměrně 82 h.
- **Literatura:** jen praktici (Bollinger); kapitola 5.10.
- **Rizika:** 8 parametrů; výstup přes SMA20 je blízko vstupu → víc obchodů a vyšší náklady; nejistý směr.
- **Výsledek (orientačně):** nejlepší DEV t-statistika ze všech (1,40), v OOS 2019–2023 záporná
  (−0,092 R); finální pořadí #3 s nejnižší důvěrou.

## 6.8 C6 – RSI(2) pullback v trendu D1 (předregistrovaná volba #3)

- **Hypotéza:** krátkodobý přeprodaný pokles uvnitř dlouhodobého růstového trendu (a zrcadlově) se
  během několika dní vrací.
- **Ekonomický mechanismus [R]:** dočasné likviditní šoky a přehnané reakce; dlouhodobý trend určuje,
  kterým směrem je reverze „bezpečnější“.
- **Pravidla (rodina Connors):**
  - Trend: SMA(200) z close. RSI(2) Cutlerovou metodou. Výstupní průměr SMA(5).
  - Long: close > SMA200 a RSI(2) < 10. Short: close < SMA200 a RSI(2) > 90.
  - Katastrofický stop close ∓ 3 × ATR(20).
  - Výstup: close nad SMA5 (long) / pod SMA5 (short), nebo po 10 denních barech.
- **Parametry:** trend_n 200, rsi_n 2, lo 10, hi 90, exit_n 5, atr_n 20, stop_atr 3,0, max_hold 10.
- **TF a držení:** D1; apriorně 2–7 dní; v DEV průměrně 114 h.
- **Literatura:** kontrariánský efekt u zlata den po abnormálním pohybu (Caporale & Plastun 2020/2021);
  Connorsova pravidla jsou praktická literatura.
- **Rizika:** záporná šikmost (časté malé zisky, vzácné velké ztráty); 8 parametrů; přenos
  jednodenního efektu na vícedenní pravidlo je **[I]**.
- **Výsledek (orientačně):** DEV −0,018 R, hrubě −0,004 R (záporná už před náklady) při win rate
  64,6 % – zamítnuta.

## 6.9 C7 – Z-score mean reversion H1

- **Hypotéza:** v trhu bez trendu se 2σ výchylky od dvoudenního průměru vracejí k průměru během dne.
- **Ekonomický mechanismus [R]:** tvůrci trhu a obchodníci s rozsahem absorbují dočasné nerovnováhy
  toku příkazů.
- **Pravidla:**
  - z = (close − SMA48) / σ48 (σ s ddof 0); efficiency ratio ER48 (Kaufman).
  - Vstup jen při ER ≤ 0,3 („range“ režim): long při z < −2, short při z > 2.
  - Stop: close ∓ 2,5 × ATR(48) na H1.
  - Výstup: z ≥ 0 (long) / z ≤ 0 (short), nebo po 24 barech.
- **Parametry:** n 48, z_entry 2,0, er_max 0,3, atr_n 48, stop_atr 2,5, max_hold 24.
- **TF a držení:** H1; apriorně 4–24 h; v DEV průměrně 19 h.
- **Literatura:** žádná gold-specifická recenzovaná podpora; kapitola 5.9.
- **Rizika:** vysoký obrat (166 obchodů ročně v DEV), křehká definice režimu, obchod proti pohybu.
- **Výsledek (orientačně):** DEV −0,117 R (t −4,35), hrubě −0,067 R, max drawdown 60,4 % – nejhorší
  kandidát, zamítnuta.

## 6.10 C8 – Session drift H1 (předregistrovaná volba #2)

- **Hypotéza:** zlato v průměru roste mimo americkou denní seanci a klesá během ní (Blose, Gondhalekar,
  Kort 2018).
- **Ekonomický mechanismus [I]:** asijská fyzická a retailová poptávka vs. západní prodeje a cenotvorba
  během denní seance COMEX; autoři studie efekt vykládají tak, že cena je při otevření trhů „příliš
  vysoko“.
- **Pravidla (pevné hodiny serverového času = NY + 7 h):**
  - Long noha: nákup na open serverové hodiny 02 (19:00 NY, po normalizaci spreadu po denním znovuotevření),
    prodej na open hodiny 15 (08:00 NY, před denní seancí COMEX). Nepřechází rollover → bez swapu.
  - Short noha: prodej na open hodiny 15, krytí na open hodiny 21 (14:00 NY, po konci seance COMEX
    ve 13:30 NY). V 15:00 tedy exit-and-reverse.
  - Signál se generuje na close H1 baru **před** cílovou hodinou, takže market příkaz se plní na open
    cílové hodiny.
  - Katastrofický stop 1 × „denní ATR“ – průměr klouzavého 23barového rozsahu high–low za 20 dní z H1 dat.
  - Pojistka: výstup nejpozději po 20 hodinách; obchoduje se pondělí–pátek.
- **Parametry:** long_entry_hour 2, long_exit_hour 15, short_entry_hour 15, short_exit_hour 21,
  daily_atr_days 20, stop_atr 1,0. Hodiny jsou dané hranicemi seancí, ne laděné.
- **TF a držení:** H1; long noha 13 h, short noha 6 h; v DEV průměrně 10 h.
- **Literatura:** recenzovaná, specificky zlatá (Blose et al. 2018, vzorek 1985–2012) + praktici
  („London bias“); kapitola 5.8.
- **Rizika:** extrémní citlivost na náklady (dvě nohy denně, v DEV 502,7 obchodu ročně proti efektu
  v jednotkách bp); závislost na serverovém čase a spreadech brokera kolem rolloveru; efekt měřený na
  COMEX do roku 2012 nemusí platit pro spot po roce 2012.
- **Výsledek (orientačně):** DEV hrubě 0,001 R, čistě −0,018 R (t −2,90) – zamítnuta. Diagnostika
  hodinového profilu ukázala, že okno 02→15 smíchalo asijský růst s londýnským poklesem (kapitola 5.8).

## 6.11 C8b – datově odvozená revize C8 (poznámka)

C8b **není** součástí předregistrovaného univerza. Vznikla po DEV screenu, kdy diagnostika hodinového
profilu výnosů v DEV ukázala růst v asijských hodinách a pokles během Londýna (`DEV_SELECTION.md`:
server 01–09 +3,3 bp za den, t ≈ 4; server 09–15 −3,9 bp za den, t ≈ −4,2).

- **Pravidla:** jako C8, jen s jinými hodinami: long 02→09 serveru (19:00→02:00 NY), short 09→15
  (02:00→08:00 NY), exit-and-reverse v 09:00; stop 1 × denní ATR.
- **Parametry:** long_entry_hour 2, long_exit_hour 9, short_entry_hour 9, short_exit_hour 15,
  daily_atr_days 20, stop_atr 1,0.
- **Proč je to problematické:** okna byla vybrána **z DEV dat**, na kterých se pak vyhodnocuje DEV výkon –
  DEV výsledek je tím optimisticky zkreslený (data-mining; protokol to přiznává a počítá N = 60
  konfigurací pro deflated Sharpe). Jediný nezávislý doklad byl, že asijská noha byla kladná i v dříve
  nepoužitém pre-sample 2004–2009 (+3,5 bp za den, t 2,7).
- **Proč byla přesto testována:** byla to jediná ne-momentum anomálie se silným hrubým efektem (hrubý
  Sharpe v DEV 1,72) – tedy jediný kandidát na skutečně komplementární zdroj edge. Testována byla
  transparentně „bez nároku na označení robustní“.
- **Výsledek (orientačně):** DEV čistě 0,003 R (PF 1,02), OOS −0,017 R, souhrnně 2004–2026 −0,006 R
  (t −2,15); všech 18 variant oken v perturbační mřížce záporných; funguje jen před náklady → zamítnuta.

## 6.12 C9 – Donchian filtrovaný trendem USD (H4)

- **Hypotéza:** breakout zlata má vyšší šanci pokračovat, když mu „pomáhá“ dolar (zlato se oceňuje v USD).
- **Ekonomický mechanismus [R]:** slabší USD zvyšuje cenu zlata v USD mechanicky i přes poptávku ze
  zahraničí; stabilně záporná denní korelace zlata s USD indexem (kapitola 5.6).
- **Pravidla:** všechna pravidla C2 + filtr na vstupu: long jen tehdy, je-li USD index (váhy DXY, Fed
  H.10) **pod** svým 50denním průměrem; short jen tehdy, je-li **nad** ním. Makro hodnota je posunuta
  o 1 den (zveřejnění). Chybí-li hodnota filtru, nevstupuje se. Výstupy beze změny (filtr se na
  výstupy neuplatňuje).
- **Parametry:** jako C2 + usd_ma 50.
- **TF a držení:** H4; apriorně 3–10 dní; v DEV průměrně 156 h.
- **Literatura:** vazba zlato–USD je dobře známá, ale filtr jako obchodní pravidlo recenzovanou
  podporu nemá; vztah zlata k sazbám se po roce 2022 rozpadl.
- **Rizika:** potřeba živého makro feedu a jeho přesného časování; nestabilita makro vztahů; filtr
  jen ubírá obchody stejné trendové sázky.
- **Výsledek (orientačně):** nejvyšší DEV expectancy (0,192 R), ale OOS −0,013 R, walk-forward −0,2 %,
  denní korelace s C2 0,79 → vyřazena.

## 6.13 C10 – Podzimní sezónnost (netestováno)

- **Hypotéza:** zlato v září a listopadu v průměru roste (Baur 2013, vzorek 1981–2010).
- **Ekonomický mechanismus [I/U]:** podle autora souvislost se slabými akciemi v těchto měsících;
  jinak slabě podložené.
- **Pravidla (jen v scorecardu):** long v září a listopadu.
- **Proč netestováno:** přibližně 2 obchody ročně jsou na 16 letech statisticky netestovatelné; měsíční
  držení je mimo mandát (horizont NE).
- **Dodatečná kontrola (kapitola 5.8):** po roce 2010 bylo září v průměru −1,70 % a listopad −1,06 %
  – vyloučení nic neztratilo.

## 6.14 C11 – ML klasifikátor směru (vyloučeno)

- **Hypotéza:** model strojového učení nad technickými a makro příznaky predikuje směr.
- **Proč vyloučeno:** zadání připouští ML jen tehdy, když prokazatelně zlepšuje už robustní
  deterministický základ a dá se validovat bez úniku informací (leakage). Takový základ neexistoval
  (a po validaci existuje nanejvýš slabý trend H4). Nejnižší skóre ve všech „robustnostních“
  kritériích (odolnost vůči overfittingu 10).

## 6.15 Parametry všech implementovaných kandidátů

| Kandidát | Parametr | Hodnota | Význam | Původ |
|---|---|---|---|---|
| C1 | lookback | 60 D1 | délka momentum okna (~3 měsíce) | TSMOM literatura |
| C1 | atr_n / stop_atr | 20 / 3,0 | katastrofický stop | konvence |
| C2 | entry_n | 55 H4 | vstupní kanál (~9,5 dne) | Turtle System 2 |
| C2 | exit_n | 20 H4 | výstupní kanál a trailing (~3,5 dne) | Turtle |
| C2 | atr_n / stop_atr | 20 / 2,0 | počáteční stop „2N“ | Turtle |
| C2 | max_hold | 90 H4 | time-stop 15 dní | konvence |
| C3 | fast / slow | 20 / 100 | EMA křížení | běžný default |
| C3 | atr_n / stop_atr | 20 / 3,0 | počáteční i trailing stop | konvence |
| C4 | k | 0,5 | vzdálenost stop-entry v ATR | Williams / ORB |
| C4 | atr_n / stop_atr | 14 / 1,0 | ATR a stop | konvence |
| C4 | hold_days | 2 | časový výstup | konvence |
| C5 | bb_n / bb_k | 20 / 2,0 | Bollinger pásma | Bollinger |
| C5 | rank_n / squeeze_pct / lookback | 120 / 0,2 / 5 | definice squeeze | praxe |
| C5 | atr_n / stop_atr / max_hold | 20 / 2,0 / 30 | stop a časový výstup | konvence |
| C6 | trend_n | 200 D1 | dlouhodobý trend | Connors |
| C6 | rsi_n / lo / hi | 2 / 10 / 90 | přeprodanost / překoupenost | Connors |
| C6 | exit_n / max_hold | 5 / 10 | výstup přes SMA5, max 10 dní | Connors |
| C6 | atr_n / stop_atr | 20 / 3,0 | katastrofický stop | konvence |
| C7 | n / z_entry | 48 H1 / 2,0 | dvoudenní průměr, 2σ | konvence |
| C7 | er_max | 0,3 | filtr „range“ režimu | Kaufman |
| C7 | atr_n / stop_atr / max_hold | 48 / 2,5 / 24 | stop a časový výstup | konvence |
| C8 | long_entry / long_exit | 02 / 15 server | 19:00 → 08:00 NY | Blose et al. 2018 (hranice seancí) |
| C8 | short_entry / short_exit | 15 / 21 server | 08:00 → 14:00 NY | Blose et al. 2018 |
| C8 | daily_atr_days / stop_atr | 20 / 1,0 | katastrofický stop | konvence |
| C8b | long 02 → 09, short 09 → 15 | server | 19:00 → 02:00 a 02:00 → 08:00 NY | **odvozeno z DEV dat** |
| C9 | parametry C2 + usd_ma | 50 D1 | trend USD indexu | konvence |

*Jak číst:* sloupec „Původ“ říká, odkud hodnota pochází – „konvence“ znamená běžnou volbu bez konkrétní
studie. *Co z toho plyne:* jediné hodnoty odvozené z dat XAUUSD jsou hodiny C8b; všechny ostatní byly
převzaty předem. Pro C2, C3, C5, C9 a C8b byly perturbační mřížky (±25 %) deklarovány předem
(`PROTOCOL.md`, `DEV_SELECTION.md`) a vyhodnoceny v navazujících kapitolách.

## 6.16 Vyloučené přístupy a proč

### Vyloučeno zadáním (dokumentováno)

| Přístup | Důvod vyloučení |
|---|---|
| SMC / ICT, order blocks | subjektivní interpretace, nelze deterministicky definovat ani poctivě backtestovat |
| Ručně kreslené supporty a rezistence | diskrece; výsledek závisí na tom, kdo kreslí |
| Elliottovy vlny | nejednoznačné počítání vln, ex post přizpůsobitelné |
| Vzory bez přesné definice | nelze automatizovat ani testovat |
| Nadměrná optimalizace parametrů | overfitting (kapitola 5.3) |
| Neprůhledné neuronové sítě BUY/SELL | nelze ověřit mechanismus, vysoké riziko leakage |
| Martingale, grid, průměrování ztrát | záporná šikmost, riziko krachu, porušuje pravidlo „riziko nezávislé na předchozích ziscích“ |

*Jak číst:* jde o vyloučení **ze zadání**, převzaté do protokolu bez úprav. *Co z toho plyne:* všichni
kandidáti v univerzu jsou deterministické, plně specifikované systémy s pevným rizikem na obchod.

### Vyloučeno z ekonomických důvodů

- **Carry / swap jako zdroj edge [R/I].** Zlato nenese výnos; rozdíl mezi spotem a futures (contango)
  zhruba odpovídá financování. U retailového CFD long platí swap (v modelu 3M T-bill + 2,25 % p.a.),
  short dostává 3M T-bill − 2,25 % p.a. „Carry strategie“ by tedy znamenala držet short kvůli swapu,
  tj. sázet proti dlouhodobému růstovému driftu zlata – to je kompenzace za riziko, ne prediktivní edge.
  Swap se proto v projektu objevuje jen jako náklad.

### Rodiny ze zadání bez samostatného kandidáta

Zadání jmenuje i rodiny, které nedostaly vlastního kandidáta. Proč, protokol výslovně nedokumentuje;
níže je rekonstrukce důvodů **[I]**:

- **ATR-normalizovaný breakout** – je pokryt C4 (vstup close ± 0,5 × ATR) a ATR stopy C2/C5.
- **Multi-timeframe trend** – kombinace trendových filtrů různých délek je podle Levine & Pedersen opět
  lineární trendový filtr; přidala by parametry bez nového zdroje edge.
- **Režimově filtrovaný trend a přepínání volatilitních režimů** – zástupcem je makro filtr C9;
  volatilitní filtr nebyl zařazen (klasifikace režimu je další volný stupeň). Ex post je to citlivý
  bod: regimová analýza ukázala, že trend ztrácí ve vysoké volatilitě, ale zavést filtr až po zhlédnutí
  výsledků by byl data-snooping.
- **Hybridní systémy** – zvyšují složitost a počet parametrů; zadání preferuje jednoduché systémy.
- **Intermarket (stříbro, AUD, těžaři), opční data (GVZ), COT, toky ETF** – nebyla zařazena; vedena
  jako netestovaná oblast (kapitola 5.18).

## 6.17 Scorecard: kritéria a váhy

Scorecard byl sepsán **před prvním backtestem** (`research/scorecard.py`). Každý kandidát dostal
v každém z 11 kritérií ze zadání skóre 0–100 (vyšší = lepší). U „citlivosti na náklady“ a „overfittingu“
znamená vyšší skóre **menší** citlivost / **vyšší** odolnost; u „nároků na data“ vyšší skóre znamená
**menší** nároky. Vážené skóre = Σ(váha × skóre) / 100. Tvrdá podmínka mimo skóre: přirozené držení musí
odpovídat mandátu 4 h – 10 obchodních dní („Horizont OK“).

| Kritérium | Váha | Co měří | Proč tato váha (rekonstrukce [I]) |
|---|---|---|---|
| Důkazy | 15 % | síla a kvalita empirické evidence mimo jeden backtest | zadání výslovně žádá evidenci nad rámec jednoho optimalizovaného backtestu; nejvyšší váha |
| Ekonomické zdůvodnění | 12 % | existence věrohodného mechanismu | efekt bez mechanismu je spíše data-mining; zadání požaduje „plausible market structure or economic logic“ |
| Robustnost napříč režimy | 12 % | očekávané chování v různých režimech zlata | hlavní cíl zadání – přežít různé režimy |
| Odolnost vůči overfittingu | 12 % | počet parametrů, volnost konstrukce | zadání penalizuje stupně volnosti |
| Odolnost vůči nákladům | 10 % | obrat vůči velikosti efektu | strategie fungující jen před náklady se zamítá |
| Vhodnost pro XAUUSD | 10 % | specifické vlastnosti zlata, gold-specific evidence | jde o jeden konkrétní instrument |
| Potenciál velikosti vzorku | 8 % | počet obchodů pro statistický test | bez vzorku nelze nic ověřit |
| Srozumitelnost implementace | 6 % | jednoznačnost pravidel | všichni kandidáti jsou deterministické → malá diferenciace |
| Nízké nároky na data | 5 % | potřeba externích dat | praktické, sekundární |
| Přenositelnost mezi brokery | 5 % | závislost na serverovém čase, typech příkazů, spreadech | praktické, sekundární |
| Kompatibilita s risk managementem | 5 % | jasný stop, ATR sizing, omezené ztráty | praktické, sekundární |

*Jak číst:* váhy sčítají na 100 %; „robustnostní“ kritéria (důkazy, zdůvodnění, režimy, overfitting,
náklady) dohromady nesou 61 %. Skript obsahuje jen samotné váhy – sloupec „proč“ je zpětná rekonstrukce
logiky ze zadání, ne dokument vzniklý před backtestem. *Co z toho plyne:* scorecard je postaven tak,
aby upřednostnil doložené, jednoduché a levně obchodovatelné efekty před „zajímavými“, což odpovídá
pravidlu zadání „robustnost a opakovatelnost jsou důležitější než maximální historický výnos“.

## 6.18 Výsledky scorecardu

Kvůli šířce je tabulka rozdělena na dvě části; kandidáti jsou seřazeni podle váženého skóre. Číslo
v závorce v záhlaví je váha kritéria v procentech.

| Kandidát | Vážené skóre | Horizont OK | Důkazy (15) | Zdůvodnění (12) | Režimy (12) | Overfit (12) |
|---|---|---|---|---|---|---|
| C1 TSMOM D1 | 73,7 | NE | 85 | 75 | 55 | 80 |
| C2 Donchian H4 | 71,7 | ano | 65 | 70 | 50 | 75 |
| C8 Session drift H1 | 71,5 | ano | 65 | 60 | 55 | 85 |
| C3 EMA trend H4 | 68,5 | ano | 60 | 70 | 50 | 70 |
| C6 RSI(2) pullback D1 | 62,7 | ano | 50 | 60 | 55 | 60 |
| C9 USD-filtrovaný Donchian H4 | 59,0 | ano | 50 | 70 | 40 | 55 |
| C4 Volatility breakout D1 | 58,8 | ano | 45 | 50 | 40 | 55 |
| C10 Podzimní sezónnost | 55,7 | NE | 40 | 35 | 40 | 60 |
| C5 Squeeze H4 | 54,3 | ano | 30 | 45 | 45 | 45 |
| C7 Z-score MR H1 | 53,9 | ano | 35 | 50 | 35 | 45 |
| C11 ML klasifikátor | 34,7 | ano | 20 | 20 | 20 | 10 |

| Kandidát | Náklady (10) | Jasnost (6) | Vzorek (8) | Data (5) | Přenositelnost (5) | XAUUSD (10) | Risk (5) |
|---|---|---|---|---|---|---|---|
| C1 TSMOM D1 | 85 | 90 | 35 | 95 | 95 | 60 | 70 |
| C2 Donchian H4 | 70 | 95 | 70 | 95 | 95 | 65 | 85 |
| C8 Session drift H1 | 40 | 95 | 95 | 95 | 70 | 80 | 85 |
| C3 EMA trend H4 | 70 | 95 | 60 | 95 | 95 | 60 | 75 |
| C6 RSI(2) pullback D1 | 55 | 90 | 60 | 95 | 95 | 55 | 70 |
| C9 USD-filtrovaný Donchian H4 | 70 | 75 | 50 | 50 | 70 | 60 | 85 |
| C4 Volatility breakout D1 | 45 | 85 | 85 | 95 | 90 | 50 | 80 |
| C10 Podzimní sezónnost | 85 | 95 | 10 | 95 | 95 | 60 | 60 |
| C5 Squeeze H4 | 60 | 85 | 50 | 95 | 95 | 50 | 80 |
| C7 Z-score MR H1 | 35 | 85 | 90 | 95 | 95 | 45 | 65 |
| C11 ML klasifikátor | 40 | 30 | 80 | 60 | 80 | 40 | 50 |

*Jak číst:* první tabulka obsahuje „robustnostní“ kritéria a vážené skóre, druhá praktická kritéria.
*Co z toho plyne:* nejvyšší skóre má C1, ale nesplňuje horizont. Mezi kandidáty s horizontem „ano“ je
na čele **C2 (71,7) a C8 (71,5) prakticky nerozlišitelně**, následuje C3 (68,5) a s odstupem C6 (62,7).
Kandidáti s nejslabší literaturou (C5, C7, C11) jsou na konci – C5 se přesto později dostala do finální
trojice, což je důležitá lekce (6.22).

Rozpad váženého skóre na příspěvky jednotlivých kritérií (váha × skóre / 100) pro pět nejlépe
hodnocených kandidátů ukazuje, **čím** se liší:

| Kritérium | Váha | C1 | C2 | C8 | C3 | C6 |
|---|---|---|---|---|---|---|
| Důkazy | 15 % | 12,75 | 9,75 | 9,75 | 9,00 | 7,50 |
| Ekonomické zdůvodnění | 12 % | 9,00 | 8,40 | 7,20 | 8,40 | 7,20 |
| Robustnost napříč režimy | 12 % | 6,60 | 6,00 | 6,60 | 6,00 | 6,60 |
| Odolnost vůči overfittingu | 12 % | 9,60 | 9,00 | 10,20 | 8,40 | 7,20 |
| Odolnost vůči nákladům | 10 % | 8,50 | 7,00 | 4,00 | 7,00 | 5,50 |
| Srozumitelnost implementace | 6 % | 5,40 | 5,70 | 5,70 | 5,70 | 5,40 |
| Potenciál velikosti vzorku | 8 % | 2,80 | 5,60 | 7,60 | 4,80 | 4,80 |
| Nízké nároky na data | 5 % | 4,75 | 4,75 | 4,75 | 4,75 | 4,75 |
| Přenositelnost mezi brokery | 5 % | 4,75 | 4,75 | 3,50 | 4,75 | 4,75 |
| Vhodnost pro XAUUSD | 10 % | 6,00 | 6,50 | 8,00 | 6,00 | 5,50 |
| Kompatibilita s risk managementem | 5 % | 3,50 | 4,25 | 4,25 | 3,75 | 3,50 |
| Součet (vážené skóre) | 100 % | 73,7 | 71,7 | 71,5 | 68,5 | 62,7 |

*Jak číst:* každá buňka je počet bodů, které kritérium přispělo k váženému skóre. *Co z toho plyne:*
C8 doháněla C2 na odolnosti vůči overfittingu (+1,2 bodu), velikosti vzorku (+2,0) a vhodnosti pro
XAUUSD (+1,5) a ztrácela hlavně na nákladech (−3,0) a zdůvodnění (−1,2). Jinými slovy: scorecard
**věděl**, že C8 je nákladově nejrizikovější, a přesto ji kvůli silné gold-specifické evidenci a nule
laděných parametrů zařadil vysoko. C3 zaostává za C2 o 3,2 bodu hlavně kvůli důkazům, vzorku a risk
kompatibilitě – rozdíl je malý a odpovídá tomu, že jde o tutéž sázku.

## 6.19 Zdůvodnění skóre po kandidátech

Původní skript obsahuje k zdůvodnění jen souhrnné poznámky (`SCORE_NOTES`), citované u každého kandidáta
v uvozovkách. **Rozvedení po jednotlivých kritériích je zpětná rekonstrukce [I]** logiky z literatury
(kapitola 5) a z vlastností pravidel – není to dokument vzniklý před backtestem a neměl by být čten jako
nezávislé ex ante zdůvodnění.

### C1 TSMOM D1 – 73,7, horizont NE

Poznámka scorecardu: „nejsilnější akademická evidence (MOP 2012, HOP 2017, Han-Hu-Yang 2016), ale držení
týdny až měsíce: mimo swingový mandát → jen benchmark“.

- Důkazy 85: nejširší a nejstarší evidence napříč trhy; ne vyšší, protože jde o měsíční horizont
  a portfolia trhů.
- Zdůvodnění 75: standardní TSMOM mechanismy [R].
- Režimy 55: crisis alpha v literatuře, ale slabost při bodech obratu (Goulding et al.).
- Overfit 80: 3 parametry, lookback z literatury.
- Náklady 85: nízký obrat (v DEV 11,8 obchodu ročně).
- Jasnost 90, Data 95, Přenositelnost 95: jednoduché, jen ceny, standardní příkazy.
- Vzorek 35: málo obchodů (DEV 106 za 9 let).
- XAUUSD 60: zlato je ve studiích jen jedním z mnoha trhů.
- Risk 70: dlouhé držení, široký katastrofický stop, expozice vůči víkendovým gapům.

### C2 Donchian H4 – 71,7, horizont ano

Poznámka: „breakout = trendový filtr (Levine-Pedersen 2016). Negativně: krátkodobý trend po 2009
zeslábl na small-tick futures (Kurth-Eisler-Rej-Bouchaud 2026); zlato je small-tick.“

- Důkazy 65: kanálové strategie ve futures doložené (Szakmary et al.), ale sníženo kvůli Kurth et al.
  a kratšímu horizontu.
- Zdůvodnění 70: trend + koncentrace stop příkazů za hranicemi kanálu.
- Režimy 50: trend ztrácí v range a při obratech.
- Overfit 75: 5 parametrů, všechny klasické Turtle hodnoty.
- Náklady 70: vícedenní držení, desítky obchodů ročně; spread malý vůči cílovému pohybu, ale swap.
- Jasnost 95, Data 95, Přenositelnost 95.
- Vzorek 70: očekávaně 20–30 obchodů ročně (v DEV 26,8).
- XAUUSD 65: zlato má dlouhé makro trendy [I].
- Risk 85: jasný počáteční stop 2 ATR, trailing, time-stop.

### C8 Session drift H1 – 71,5, horizont ano

Poznámka: „recenzovaný gold-specific efekt overnight kladný / den záporný (Blose-Gondhalekar-Kort 2018)
+ nedávné komentáře k asijským vs. americkým hodinám; nula laděných parametrů, ale velmi citlivé na
náklady (~250 round-tripů ročně)“.

- Důkazy 65: recenzovaná a specificky zlatá studie, ale vzorek do 2012, COMEX, bez replikace.
- Zdůvodnění 60: mechanismus (asijská poptávka vs. západní prodeje) je spíše [I].
- Režimy 55: efekt měřený přes desetiletí, ale bez rozkladu podle režimů.
- Overfit 85: hodiny dané hranicemi seancí; nic se neladí.
- Náklady 40: obrat stovky obchodů ročně proti efektu v jednotkách bp. Poznámka scorecardu obrat
  podhodnotila – skutečně 502,7 obchodu ročně (dvě nohy denně), takže i 40 bylo spíše optimistické.
- Jasnost 95, Data 95.
- Vzorek 95: tisíce obchodů.
- Přenositelnost 70: závisí na serverovém čase brokera, spreadech kolem rolloveru a hodinách obchodování.
- XAUUSD 80: přímo zlatý efekt.
- Risk 85: krátké držení, bez swapu, malý stop.

### C3 EMA trend H4 – 68,5, horizont ano

Poznámka: „stejná ekonomická sázka jako C2 (MA cross ~ TSMOM); ponechána jen jako kontrola pro C2“.

- Důkazy 60: MA timing v komoditách (Szakmary et al., Han et al.); o stupeň níže než C2.
- Zdůvodnění 70: jako C2.
- Režimy 50: jako C2.
- Overfit 70: 4 parametry, ale neomezené držení a trailing z extrému close dávají víc volnosti v konstrukci.
- Náklady 70, Jasnost 95, Data 95, Přenositelnost 95.
- Vzorek 60: méně obchodů než C2 (v DEV 18,1 ročně).
- XAUUSD 60.
- Risk 75: širší stop 3 ATR, bez time-stopu.

### C6 RSI(2) pullback D1 – 62,7, horizont ano

Poznámka: „kontrariánský efekt u zlata po abnormálních pohybech (Caporale-Plastun 2019); krátkodobá
reverze ve futures dobře zdokumentovaná; zápornou šikmost je nutné kontrolovat stopem“.

- Důkazy 50: jednodenní kontrariánský efekt u zlata, Connors jako praktická literatura.
- Zdůvodnění 60: likviditní šoky a přehnané reakce [R].
- Režimy 55: podmínka SMA200 omezuje obchody proti hlavnímu trendu.
- Overfit 60: 8 parametrů, ale převážně standardní Connorsovy hodnoty.
- Náklady 55: kratší držení a menší cílový pohyb na obchod než u trendu.
- Jasnost 90, Data 95, Přenositelnost 95.
- Vzorek 60: desítky obchodů ročně (v DEV 28,9).
- XAUUSD 55: gold-specific evidence slabá a nepřímá.
- Risk 70: záporná šikmost, katastrofický stop 3 ATR.

### C9 USD-filtrovaný Donchian H4 – 59,0, horizont ano

Poznámka: „vazba USD–zlato je reálná, ale nestabilní (vztah zlata a reálných výnosů se rozpadl 2022–24);
přidává datovou závislost a parametr“.

- Důkazy 50: vztah zlato–USD doložen, filtr jako pravidlo ne.
- Zdůvodnění 70: oceňování v USD [R].
- Režimy 40: nestabilní makro vztahy.
- Overfit 55: další parametr a volba makro proměnné jako skrytý stupeň volnosti.
- Náklady 70: jako C2.
- Jasnost 75: závisí na časování makro dat.
- Vzorek 50: filtr ubírá obchody (v DEV 16,0 ročně).
- Data 50: potřeba živého USD indexu se zpožděním publikace.
- Přenositelnost 70: makro feed musí být u brokera nebo externě.
- XAUUSD 60, Risk 85 (jako C2).

### C4 Volatility breakout D1 – 58,8, horizont ano

Poznámka: „evidence pro ORB převážně z ropy a intradenních akciových indexů; málo gold-specific
recenzované podpory; vysoký obrat“.

- Důkazy 45, Zdůvodnění 50: nepřímá evidence, mechanismus [I].
- Režimy 40: expanze rozsahu se v range trzích často vrací.
- Overfit 55: 4 parametry, k a délka držení jsou volné volby.
- Náklady 45: téměř denní obchodování, stop příkazy se skluzem.
- Jasnost 85, Data 95, Přenositelnost 90 (vyžaduje stop-entry a OCO podporu).
- Vzorek 85: mnoho obchodů.
- XAUUSD 50, Risk 80 (stop 1 ATR, krátké držení).

### C10 Podzimní sezónnost – 55,7, horizont NE

Poznámka: „autumn effect (Baur 2013); ~2 obchody ročně → statisticky netestovatelné na 16 letech;
měsíční držení“.

- Důkazy 40: jedna studie, 30 pozorování na měsíc.
- Zdůvodnění 35: slabý mechanismus.
- Režimy 40, Overfit 60: dva měsíce vybrané z dvanácti jsou implicitní výběr z dat.
- Náklady 85: dva obchody ročně.
- Vzorek 10: netestovatelné.
- Jasnost 95, Data 95, Přenositelnost 95, XAUUSD 60, Risk 60 (měsíční expozice).

### C5 Squeeze H4 – 54,3, horizont ano

Poznámka: „praktická literatura; shlukování volatility je reálné, ale směr po squeeze doložen není“.

- Důkazy 30: jen praktici.
- Zdůvodnění 45: polovina mechanismu doložena (volatilita), druhá ne (směr).
- Režimy 45, Overfit 45: 8 parametrů.
- Náklady 60: kratší držení, víc obchodů než C2.
- Jasnost 85, Data 95, Přenositelnost 95.
- Vzorek 50, XAUUSD 50, Risk 80.

### C7 Z-score MR H1 – 53,9, horizont ano

Poznámka: „hodinová reverze v range: vysoký obrat, dominují náklady, křehká definice režimu“.

- Důkazy 35, Zdůvodnění 50.
- Režimy 35: závisí na filtru ER < 0,3.
- Overfit 45: 6 parametrů včetně režimového filtru.
- Náklady 35: stovky obchodů ročně na H1.
- Jasnost 85, Data 95, Přenositelnost 95.
- Vzorek 90, XAUUSD 45, Risk 65 (obchod proti pohybu, záporná šikmost).

### C11 ML klasifikátor – 34,7, horizont ano

Poznámka: „vyloučeno mandátem, dokud nezlepší robustní základ bez leakage; takový základ zatím neexistuje“.

- Důkazy 20, Zdůvodnění 20, Režimy 20, Overfit 10: černá skříňka s mnoha stupni volnosti.
- Náklady 40, Jasnost 30, Data 60, Přenositelnost 80, XAUUSD 40, Risk 50.
- Vzorek 80: model může generovat hodně obchodů.

## 6.20 Citlivost scorecardu na váhy [E, vlastní dopočet]

Váhy jsou subjektivní. Abychom ověřili, zda výběr na nich nezávisí, přepočítali jsme vážené skóre ze
`scorecard.py` pro tři alternativní sady vah.

| Varianta vah | Pořadí všech kandidátů (skóre) | Top 3 s horizontem „ano“ |
|---|---|---|
| Původní váhy | C1 73,7 > C2 71,7 > C8 71,5 > C3 68,5 > C6 62,7 > C9 59,0 > C4 58,8 > C10 55,7 > C5 54,3 > C7 53,9 > C11 34,7 | C2, C8, C3 |
| Rovné váhy (každé kritérium 1/11) | C2 75,9 > C1 75,0 = C8 75,0 > C3 72,7 > C6 67,7 > C4 65,5 > C5 61,8 > C7 = C9 = C10 61,4 > C11 40,9 | C2, C8, C3 |
| Bez kritéria „důkazy“ | C2 72,9 > C8 72,7 > C1 71,6 > C3 70,1 > C6 64,9 > C4 61,2 > C9 60,6 > C5 58,6 > C10 58,5 > C7 57,2 > C11 37,3 | C2, C8, C3 |
| Jen robustnostní kritéria (důkazy, zdůvodnění, režimy, overfitting, náklady) | C1 76,1 > C2 65,8 > C3 63,6 > C8 61,9 > C9 56,2 > C6 55,7 > C10 50,3 > C4 47,0 > C5 43,8 > C7 39,9 > C11 21,3 | C2, C3, C8 |

*Jak číst:* každý řádek je celé pořadí při jiné sadě vah; poslední sloupec ukazuje tři nejvýše
hodnocené kandidáty, kteří splňují horizont. *Co z toho plyne:* **C2, C8 a C3 jsou nejlepší trojicí
při všech čtyřech variantách vah.** Po uplatnění pravidla komplementarity (6.21: C3 a C9 jsou stejná
sázka jako C2) vychází ve všech variantách stejná předregistrovaná volba **C2 + C8 + C6**. Výběr tedy
nebyl artefaktem konkrétních vah. Pořadí na konci (C5, C7, C11) je také stabilní.

## 6.21 Výběrová logika předregistrace

Postup výběru tří strategií pro plné backend testování byl zapsán v `PROTOCOL.md` (oddíl 3) před prvním
během:

1. **Filtr horizontu:** vyřazeny C1 (týdny až měsíce) a C10 (měsíc). C1 zůstal jako benchmark v
   kontrolní skupině.
2. **Řazení podle váženého skóre** mezi kandidáty s horizontem „ano“: C2 71,7 → C8 71,5 → C3 68,5 →
   C6 62,7 → C9 59,0 → C4 58,8 → C5 54,3 → C7 53,9 → C11 34,7.
3. **Preference komplementarity:** zadání výslovně žádá „preferovat tři komplementární strategie před
   třemi variantami téhož momentum obchodu“. C3 je podle Levine & Pedersen tatáž sázka jako C2, proto
   byla přeskočena a třetí místo dostala nejlépe hodnocená strategie **z jiné rodiny** – C6 (mean
   reversion). C9 (trend s makro filtrem) by byla také stejná sázka.
4. **Výsledná trojice:** **C2** (trend / breakout), **C8** (časová anomálie), **C6** (podmíněná mean
   reversion) – tři ekonomicky odlišné mechanismy.
5. **Kontrolní skupina:** C1, C3, C4, C5, C7, C9 se na DEV spustí se stejnými náklady a výsledky se
   reportují.
6. **Pravidlo náhrady:** výměna vybrané strategie za kontrolní je povolena jen tehdy, když vybraná selže
   na DEV branách, a musí být v reportu označena (zvyšuje počet testů pro deflated Sharpe).
7. **Validace deklarovaná předem:** pro C2, C8 i C6 byly v protokolu předem stanoveny perturbační mřížky
   (125 bodů pro C2 a C6, 9 + 9 oken a 4 stopy pro C8) a timeframové testy (C2 H2–D1, C8 M30 vs. H1
   s posunem ± 30 min, C6 D1/H12/H8).

### Proč byla volba C2 + C8 + C6 ex ante rozumná

- **Tři nezávislé hypotézy místo jedné.** Kdyby se vybraly tři nejvýše hodnocené (C2, C8, C3), dvě by
  testovaly totéž. Při třech odlišných mechanismech se maximalizuje šance, že alespoň jeden nezávislý
  zdroj edge přežije – a portfolio by bylo skutečně diverzifikované, což je cíl zadání (kapitola 15
  zadání: komplementarita).
- **Každá volba měla nejlepší dostupnou oporu ve své rodině:** C2 klasickou trendovou literaturu
  ve futures; C8 jedinou recenzovanou gold-specific anomálii s nulou laděných parametrů; C6 jediný
  gold-specific doklad krátkodobé reverze (Caporale & Plastun).
- **Profilová komplementarita [I]:** trend má nízký win rate, dlouhé držení a kladnou šikmost; mean
  reversion vysoký win rate, krátké držení a zápornou šikmost; session drift je krátkodobý a tržně
  neutrální vůči dlouhodobému směru. Očekávaná korelace mezi nimi byla nízká.
- **Nízká složitost:** C2 5 parametrů, C8 žádný laděný parametr, C6 standardní Connorsovy hodnoty.
- **Rozhodnutí bylo zapsáno dřív, než byla známa jakákoli data** – a tím se chránilo před nejčastější
  chybou (výběr podle backtestu). Pravidlo náhrady bylo připraveno pro případ selhání.
- **Výběr nebyl citlivý na váhy** (6.20).

## 6.22 Co se s výběrem stalo a co z toho plyne

DEV screen všech kandidátů (2010-01 až 2018-12, baseline náklady; * = předregistrovaná volba;
brána 1 = expectancy > 0 a PF > 1,10):

| Kandidát | Obch. | Obch./rok | Win % | Exp. R | t | PF | Sharpe | Hrubá exp. R | Ø držení h | Brána 1 |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 TSMOM D1 | 106 | 11,8 | 32,1 | −0,002 | −0,02 | 0,980 | 0,02 | 0,055 | 693 | NE |
| C2 Donchian H4 * | 241 | 26,8 | 32,4 | 0,064 | 0,56 | 1,094 | 0,19 | 0,183 | 152 | NE |
| C3 EMA trend H4 | 163 | 18,1 | 35,0 | 0,074 | 0,85 | 1,221 | 0,31 | 0,116 | 133 | ano |
| C4 Vol. breakout D1 | 697 | 77,5 | 47,8 | −0,036 | −1,21 | 0,889 | −0,39 | 0,010 | 49 | NE |
| C5 Squeeze H4 | 331 | 36,8 | 38,4 | 0,109 | 1,40 | 1,236 | 0,48 | 0,165 | 82 | ano |
| C6 RSI(2) D1 * | 260 | 28,9 | 64,6 | −0,018 | −0,68 | 0,882 | −0,27 | −0,004 | 114 | NE |
| C7 Z-score MR H1 | 1494 | 166,2 | 42,2 | −0,117 | −4,35 | 0,751 | −1,41 | −0,067 | 19 | NE |
| C8 Session H1 * | 4520 | 502,7 | 47,6 | −0,018 | −2,90 | 0,886 | −0,99 | 0,001 | 10 | NE |
| C9 USD-Donchian H4 | 144 | 16,0 | 34,0 | 0,192 | 1,15 | 1,310 | 0,37 | 0,353 | 156 | ano |
| C8b Asie/Londýn H1 | 4569 | 508,2 | 51,1 | 0,003 | 0,62 | 1,022 | 0,21 | 0,022 | 7 | NE |

*Jak číst:* „Exp. R“ je čistá průměrná expectancy na obchod v násobcích rizika, „Hrubá exp. R“ totéž
bez nákladů (bezfrikční běh), „t“ t-statistika expectancy. *Co z toho plyne:* **C6 a C8 byly záporné
nebo nulové už před náklady** – nešlo o nákladový problém, efekt na XAUUSD 2010–2018 neexistoval. C2
minula bránu 1 o fous (PF 1,094 proti 1,10). Bránu prošly jen tři trendové varianty (C3, C5, C9) – podle
pravidla náhrady (zapsaného v `DEV_SELECTION.md` před OOS) šly do plné validace seřazené podle t:
C5, C9, C3, navíc transparentně C2 (předregistrovaná reference) a C8b. Křížová kontrola zdrojů A vs. B
na překryvu 2016-09 až 2018-12 dala kvalitativně stejné závěry (`s01_dev_screen.md`).

### Předpověděl scorecard výsledky? [E, vlastní dopočet]

| Kandidát | Vážené skóre | Pořadí podle skóre (z 9) | DEV t | Pořadí podle DEV t (z 9) | Osud |
|---|---|---|---|---|---|
| C1 TSMOM D1 | 73,7 | 1 | −0,02 | 5 | benchmark, DEV ≈ 0 |
| C2 Donchian H4 | 71,7 | 2 | 0,56 | 4 | brána 1 těsně ne; finální #2 |
| C8 Session drift H1 | 71,5 | 3 | −2,90 | 8 | zamítnuta (hrubě 0) |
| C3 EMA trend H4 | 68,5 | 4 | 0,85 | 3 | finální #1 |
| C6 RSI(2) pullback D1 | 62,7 | 5 | −0,68 | 6 | zamítnuta (záporná před náklady) |
| C9 USD-Donchian H4 | 59,0 | 6 | 1,15 | 2 | vyřazena po validaci |
| C4 Volatility breakout D1 | 58,8 | 7 | −1,21 | 7 | zamítnuta |
| C5 Squeeze H4 | 54,3 | 8 | 1,40 | 1 | finální #3, OOS záporná |
| C7 Z-score MR H1 | 53,9 | 9 | −4,35 | 9 | zamítnuta |

*Jak číst:* porovnáváme pořadí podle apriorního skóre s pořadím podle DEV t-statistiky u devíti
kandidátů, kteří byli skutečně spuštěni (C10, C11 a C8b mimo). *Co z toho plyne:* Spearmanova pořadová
korelace mezi váženým skóre a DEV výsledkem je **0,17** pro expectancy R (p = 0,67), **0,07** pro
t-statistiku i Sharpe (p = 0,86) a **0,23** pro hrubou expectancy (p = 0,55). **Scorecard pořadí
v DEV prakticky nepředpověděl.** Shoda je jen na okrajích (C7 poslední v obou pořadích, C4 sedmá
v obou). Nejvýrazněji se rozešel u C8 (3. vs. 8.) a C5 (8. vs. 1.) – přičemž u C5 se DEV výsledek
v OOS obrátil (−0,092 R), takže „chyba“ scorecardu u C5 byla spíše chybou DEV vzorku.

### Proč selhání dvou ze tří neznamená, že výběr byl ex ante špatný

1. **Kvalita rozhodnutí ≠ výsledek.** Rozhodnutí se hodnotí podle informací dostupných v okamžiku
   rozhodování. Ex ante měly C8 a C6 nejlepší dostupnou oporu ve svých rodinách a výběr byl robustní
   vůči vahám (6.20).
2. **Selhání bylo informativní.** Test zamítl dvě celé rodiny (session/čas v dni a krátkodobou mean
   reversion) na XAUUSD 2010–2018 – a to už před náklady. To je skutečný poznatek, který by výběr tří
   trendových variant nepřinesl.
3. **Literatura to připouštěla.** Kapitola 5.16 ukazuje, že gold-specific efekty měly kratší vzorky bez
   replikací a po konci původních vzorků se rozpadly – riziko selhání bylo známé (proto skóre 60–65,
   ne 80+ u důkazů).
4. **Pravidlo náhrady fungovalo**, jak bylo navrženo: místo ad hoc hledání nových strategií se do plné
   validace posunuli kontrolní kandidáti, kteří prošli předem danou bránou, a to s výslovným zápisem,
   že jde o stejnou ekonomickou sázku.
5. **Cena za to je přiznaná:** náhrada zvýšila počet testů (proto N = 60 pro deflated Sharpe) a
   výsledná trojice C3, C2, C5 porušuje požadavek komplementarity – což report výslovně uvádí: tři
   „nejsilnější kandidáti“ jsou fakticky jedna sázka.

> **Závěr:** Univerzum pokrylo všechny rodiny ze zadání jedním až čtyřmi deterministickými kandidáty
> s literaturními parametry. Scorecard seřadil kandidáty rozumně a stabilně vůči vahám a předregistrace
> zvolila tři ekonomicky odlišné strategie C2 + C8 + C6. Na datech XAUUSD se ale apriorní pořadí
> nepotvrdilo (pořadová korelace 0,17): obě ne-trendové volby selhaly už před náklady a jedinou slabě
> kladnou rodinou zůstal trend na H4. Scorecard se tak osvědčil jako nástroj k vymezení a zmrazení
> hypotéz, ne jako předpověď, která strategie projde.

*Zdrojové soubory: `research/scorecard.py` (váhy, skóre, `SCORE_NOTES`) a `research/results/scorecard.md`;
`research/PROTOCOL.md` (výběr, pravidlo náhrady, mřížky); `research/DEV_SELECTION.md` (rozhodnutí po DEV,
C8b); `research/frozen_spec.json` (zmrazené parametry C2, C3, C5, C9, C8b); `tradingsystem/strategies/base.py`,
`trend.py`, `breakout.py`, `meanrev.py`, `session.py` (třídy `Params` a `on_bar`);
`tradingsystem/signals/indicators.py`; `tradingsystem/execution/engine.py` (posun stopu);
`tradingsystem/brokers/simulated.py` (OCO); `research/registry.py`; `research/results/s01_dev_screen.json`
a `.md` (DEV screen, křížová kontrola zdrojů); `research/results/s02_C2.json`, `s02_C3.json`, `s02_C5.json`,
`s02_C9.json`, `s02_C8b.json`; `research/results/s05_pooled.json`; `research/results/s03_portfolio_C2_C3_C5_C9.md`;
`REPORT.md` (kap. 4–7); `Project XAUUSD.docx` (zadání); vlastní dopočty: citlivost scorecardu na váhy a
Spearmanova korelace skóre s DEV výsledky (`scorecard.py` + `s01_dev_screen.json`).*
