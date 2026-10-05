# 1. Manažerské shrnutí

## 1.1 Odpověď na otázku „které strategie jsou nejlepší a proč“

> **Verdikt:** Žádná z deseti testovaných rodin strategií pro XAUUSD neprošla všemi sedmi
> předem stanovenými branami robustnosti. Data 2010–2023 s realistickými náklady nepodporují
> označení „robustní“ pro žádnou strategii. Nejsilnějšími kandidáty pro **další zkoumání** (ne pro
> obchodování) jsou tři varianty střednědobého trendu na H4: **#1 C3 EMA trend H4, #2 C2 Donchian
> breakout H4, #3 C5 Squeeze breakout H4**. Všechny tři jsou ve skutečnosti **jedna podkladová sázka**.
> Důvěra: **NÍZKÁ**.

Proč právě tyto tři:

1. **Jsou to jediné strategie s kladnou čistou expectancy v každém nezávislém období.** C3 a C2 byly
   kladné ve všech čtyřech segmentech: pre-sample 2004–2009, DEV 2010–2018, OOS 2019–2023
   a holdout 2024–2026. Pre-sample a holdout nebyly použity k vývoji. C5 byla kladná ve třech ze
   čtyř segmentů, v OOS ztrácela.
2. **Nezávisí na jedné hodnotě parametru.** V mřížce 125 kombinací (±25 % kolem defaultu) mělo
   kladnou čistou expectancy 90 % (C3), 96 % (C2) a 100 % (C5) sousedních nastavení. Kladné byly i
   na všech testovaných timeframech od H2 po D1.
3. **Přežijí realistické a zvýšené náklady.** Při 1,5× nákladech zůstávají kladné. Při 2× nákladech je
   C3 stále kladná (+0,021 R), C2 je na nule a C5 záporná.
4. **Mají ekonomické zdůvodnění a oporu v literatuře.** Jde o time-series momentum / trend
   following (Moskowitz, Ooi, Pedersen 2012; Hurst, Ooi, Pedersen 2017; Han, Hu, Yang 2016)
   v konzervativní podobě. Má pevná literaturní pravidla, ATR stopy a symetrický long/short.

Proč důvěra zůstává nízká:

- **Efekt je malý.** Čistá expectancy je +0,06 až +0,15 R na obchod, Sharpe 0,27–0,40 a
  t-statistika 1,25–1,71 za 22 let.
- **Po korekci na počet testů nejde o statisticky významný výsledek.** Deflated Sharpe je 0,30–0,53
  v mírnější variantě a ≈ 0 v konzervativní variantě, cíl by byl ≥ 0,95.
- **Zisky jsou soustředěné do několika let.** Největší rok přináší 68–74 % čistého zisku za DEV+OOS.
  Pravděpodobnost kladné expectancy z bootstrapu je jen 73–82 % (brána vyžadovala 90 %).
- **OOS 2019–2023 nesplnilo bránu Sharpe > 0,3.** C3 dosáhla 0,16, C2 0,26 a C5 −0,41.
- **Kladný holdout 2024–2026 je slabý důkaz.** Připadl na mimořádný býčí trh zlata a vydělávala jen
  long strana.

## 1.2 Proč ne ostatní

| Kandidát | Kde vypadl | Hlavní důvod |
|---|---|---|
| C1 TSMOM D1 | DEV | plochý výsledek (exp. −0,002 R), držení týdny–měsíce mimo mandát |
| C4 Volatility breakout D1 | DEV | záporná čistá expectancy (−0,036 R), hrubě téměř nula |
| C6 RSI(2) pullback D1 | DEV | záporná expectancy už **před náklady** – mean reversion na zlatě nefungovala |
| C7 Z-score MR H1 | DEV | silně záporná (−0,117 R, t −4,35), náklady i hrubá ztráta |
| C8 Session drift H1 | DEV | hrubě nulová, čistě záporná – předregistrované okno smíchalo opačné fáze dne |
| C8b Asie long / Londýn short | validace | hrubá anomálie existuje (hrubý Sharpe 1,27), ale náklady ji zcela pohltí; od 2016 slábne |
| C9 Donchian + USD filtr | validace | prakticky totožná s C2 (korelace 0,79), OOS ≈ 0, walk-forward −0,2 %, potřebuje živý USD index |
| C10 Podzimní sezónnost | scorecard | ~2 obchody ročně – statisticky netestovatelné, držení měsíc |
| C11 ML klasifikátor | scorecard | mandát: ML jen nad robustní deterministickou baseline, která neexistuje |

## 1.3 Klíčová čísla

| Ukazatel | C3 EMA trend | C2 Donchian | C5 Squeeze | Portfolio C3+C2+C5 (1/3) |
|---|---|---|---|---|
| Exp. R DEV 2010–2018 | 0,074 | 0,064 | 0,109 | — |
| Exp. R OOS 2019–2023 | 0,038 | 0,094 | −0,092 | — |
| Exp. R DEV+OOS | 0,061 | 0,081 | 0,038 | 0,052 |
| Exp. R holdout 2024–2026 | 0,106 | 0,197 | 0,162 | 0,171 |
| Sharpe DEV+OOS / holdout | 0,25 / 0,37 | 0,22 / 0,51 | 0,17 / 0,65 | 0,24 / 0,72 |
| Pooled 2004–2026: obchody, exp. R, t | 412; 0,067; 1,25 | 595; 0,149; 1,71 | 810; 0,074; 1,46 | — |
| Kladní sousedé v perturbaci | 90 % | 96 % | 100 % | — |
| Bootstrap P(exp. > 0) DEV+OOS | 82 % | 78 % | 73 % | — |
| Max DD DEV+OOS (0,5 % riziko) | 7,4 % | 13,4 % | 16,9 % | 7,5 % (riziko 1/3) |
| Průměrné držení | 128 h | 149 h | 78 h | 113 h |

Portfolio s jedním společným rizikovým rozpočtem dosáhlo v DEV+OOS CAGR jen 0,65 % při max DD
7,5 %. **Od ledna 2018 do konce roku 2023 nedosáhlo nového maxima.** I v případě úspěchu je realistické očekávání
nízký jednociferný výnos s dlouhými obdobími pod vodou.

## 1.4 Co z toho plyne pro další zpracování

1. **Nenasazovat reálný kapitál.** Žádná strategie nesplnila brány pro obchodování.
2. **Jako jeden „trendový ensemble“ zpracovávat C3 + C2 + C5** se sdíleným rizikovým rozpočtem.
   Celkem je to 0,5 % na obchod, tedy 1/3 na každou strategii. Pravidla jsou symetrická a bez
   vypínání směrů. Přesná konfigurace je v `config/paper.toml` (příloha D).
3. **Nejdřív re-validovat na datech vlastního brokera** (spready, swapy, časová zóna). Potom
   provést integrační testy MT5 na demu.
4. **Spustit pouze pozorovací PAPER fázi.** Cílem je změřit skutečné náklady a ověřit
   implementační věrnost, ne prokázat edge – statisticky to při Sharpe ~0,3 v rozumném čase nejde.
5. **Paralelně hledat nezávislý zdroj edge** pomocí nových předregistrovaných hypotéz (kapitola 16).
   Dnešní tři kandidáti diverzifikaci nepřinášejí, protože jde o jednu sázku.

## 1.5 Jak vznikly závěry a proč jim lze věřit

- **Pravidla, splity a brány byly zapsány a commitnuty před prvním během.** Výběr po DEV byl zapsán
  před OOS a pořadí bylo zmrazeno před holdoutem (commity 6a151db, 41ce7b8, cfe78c3, 87cd6b6).
  Odchylky od protokolu jsou vyjmenované v kapitole 4.
- **Exekuce probíhala na reálném bid/ask.** Simulace počítala se skluzem a se swapy podle historických
  sazeb, přes gapy plnila na horší ceně a při zásahu stopu i cíle v jednom baru předpokládala nejdřív
  stop.
- **Stejný kód strategie běží v backtestu i živém režimu.** Test parity ukazuje identické obchody
  (165/165).
- **Hlavní omezení:** data pocházejí z veřejných mirrorů a tick data chybějí. MT5 adaptér nebyl
  spuštěn proti skutečnému terminálu. Výzkumník znal obecný vývoj trhu zlata do roku 2026.
  Podrobnosti jsou v kapitole 19.

*Zdrojové soubory: research/results/s01_dev_screen.json, s02_C3.json, s02_C2.json, s02_C5.json,
s02_C9.json, s02_C8b.json, s03_portfolio.json, s03_portfolio_C2_C3_C5_C9.json, s04_holdout.json,
s05_pooled.json, dsr_within_grid.json, research/frozen_spec.json, config/paper.toml.*
