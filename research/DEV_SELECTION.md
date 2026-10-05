# Rozhodnutí po DEV (zapsáno a commitnuto před jakýmkoli během na OOS 2019–2023)

Zdroj čísel: `results/s01_dev_screen.md` (DEV 2010-01-01 – 2018-12-31, baseline náklady).

## Co se stalo s předregistrovaným výběrem

| Předvybraná | DEV výsledek | Brána 1 (exp > 0, PF > 1,10) | Rozhodnutí |
|---|---|---|---|
| C2 donchian_h4 | exp 0,064 R, PF 1,094, t 0,56 | **ne** (těsně) | ponechána jako referenční člen trendové rodiny, nezpůsobilá pro označení „robustní“ |
| C6 rsi2_pullback_d1 | exp −0,018 R, PF 0,88; záporné i před náklady | **ne** | **zamítnuta** (literatura ji podporuje, XAUUSD ne) |
| C8 session_drift_h1 | exp −0,018 R, PF 0,89; hrubě ≈ 0 | **ne** | **zamítnuta** v předregistrované podobě |

Diagnostika na DEV (hodinový profil výnosů): zlato rostlo v asijských hodinách (server 01–09 =
18:00–02:00 NY, +3,3 bp/den, t≈4) a klesalo v londýnské seanci (server 09–15, −3,9 bp/den, t≈−4,2).
Předregistrované okno obě fáze smíchalo. Revize **C8b session_asia_london_h1** (long 02→09, short 09→15)
je **odvozena z DEV dat** (data-mining riziko, mnoho možných oken) → v DEV je optimisticky zkreslená.
DEV: hrubě +53 tis. USD, net jen +5,4 tis. (PF 1,02) → **nesplňuje bránu 1 při baseline nákladech**.
Asijská noha byla kladná i v nezávislém pre-sample 2004–2009 (+3,5 bp/den, t 2,7; data B, předtím nepoužita).

## Pravidlo náhrady (stanoveno teď, před OOS)

Kandidáti splňující DEV bránu 1: C3 ema_trend_h4 (PF 1,22, t 0,86), C5 squeeze_h4 (PF 1,24, t 1,40),
C9 donchian_usd_h4 (PF 1,31, t 1,15). **Všichni tři jsou stejná ekonomická sázka (momentum/trend).**
Žádný kandidát z rodin mean-reversion ani session nesplnil bránu 1.

**Plné backend testování (OOS, WF, perturbace, TF, zpoždění, náklady, režimy, bootstrap, long/short):**

1. C5 squeeze_h4 (DEV t 1,40)
2. C9 donchian_usd_h4 (DEV t 1,15)
3. C3 ema_trend_h4 (DEV t 0,86)

Navíc (transparentně, bez nároku na označení „robustní“, pokud nesplní všechny brány):
C2 donchian_h4 (předregistrovaná reference) a C8b session_asia_london_h1 (jediná ne-momentum
anomálie se silným hrubým efektem; „cost-conditional“).

Počet testovaných konfigurací pro deflated Sharpe: 10 kandidátů v DEV screenu + C8b revize
(~50 implicitně zvažovaných oken) → konzervativně N = 60.

## Doplňkové mřížky (deklarovány teď, před OOS)

* C3: fast {15, 17, 20, 23, 25} × slow {75, 85, 100, 115, 125} × stop_atr {2.25, 2.625, 3.0, 3.375, 3.75}
* C5: bb_n {15, 17, 20, 23, 25} × squeeze_pct {0.15, 0.175, 0.2, 0.225, 0.25} × stop_atr {1.5, 1.75, 2.0, 2.25, 2.5};
  OAT: rank_n {90, 105, 120, 135, 150}, max_hold {22, 26, 30, 34, 38}
* C9: mřížka C2 + OAT usd_ma {38, 44, 50, 56, 63}
* C8b: long_entry {1, 2, 3} × long_exit {8, 9, 10}; short_entry {8, 9, 10} × short_exit {14, 15, 16}; stop {0.75, 1.0, 1.25, 1.5}
* Timeframe: C3/C5/C9/C2 na H2, H3, H4, H6 (+ D1 pro C3, C9, C2) se škálováním délek v hodinách; C8b báze M30 a posun ±30 min.
* Walk-forward 3×3: C3 fast {15, 20, 25} × slow {75, 100, 125}; C5 bb_n {15, 20, 25} × squeeze_pct {0.15, 0.2, 0.25};
  C9 a C2 entry_n {41, 55, 69} × exit_n {15, 20, 25}; C8b bez parametrů (pevná pravidla, jen roční řez).
