# Výzkumný protokol (předregistrace)

Tento soubor byl zapsán a commitnut **před prvním spuštěním jakékoli strategie na datech XAUUSD**.
Vše, co je zde uvedeno (splity, parametry, mřížky perturbací, brány přijetí), se po zhlédnutí
výsledků nemění. Jakákoli pozdější odchylka musí být v reportu výslovně označena jako odchylka.

## 1. Data

| Sada | Zdroj | Období | Typ ceny | Časová zóna | Použití |
|---|---|---|---|---|---|
| A | Dukascopy-format M1 bid/ask (github.com/Dypoi/XAUUSD_Dataset) | 2016-09-01 – 2026-09-01 | bid + ask OHLC | UTC → serverový čas NY+7 | DEV (od 2016-09), OOS, HOLDOUT, exekuce na bid/ask |
| B | MT4 broker H1 (github.com/FeziweMelvin/XAUUSD-Gold-Price) | 2004-06-11 – 2025-06-06 | bid OHLC, ask = bid + modelový spread | server GMT+2/+3 (= NY+7), ověřeno korelací s A | PRE-SAMPLE, DEV do 2016-08-31 |
| C | MT5 broker H1 (github.com/ejtraderLabs/historical-data) | 2012-05 – 2022-03 | bid | server | jen křížová kontrola |
| Makro | VIX (CBOE), USD index (DXY váhy, Fed H.10), US Treasury 3M/2Y/10Y | 1990/2000 – 2026 | denní | US datum | swapy (3M), režimy, filtr C9; vždy zpožděno o 1 obchodní den |

* Modelový spread pro B = medián spreadu A v bps podle serverové hodiny, odhadnutý **jen na 2016-09 – 2018-12** (uvnitř DEV).
* „Stitched“ výzkumná řada = B do 2016-08-31, A od 2016-09-01 (sloupec `source`). Nic dalšího se nemíchá.
* Serverový čas = New York + 7 h; denní svíčka = obchodní den 17:00–17:00 NY (5 denních svíček týdně).

## 2. Chronologické rozdělení (nikdy se nemíchá)

| Segment | Období | Podíl 2010–2026 | Pravidla |
|---|---|---|---|
| PRE-SAMPLE | 2004-07 – 2009-12 (B) | — | nepoužito k vývoji; zpětný out-of-sample test |
| DEVELOPMENT | 2010-01-01 – 2018-12-31 | ~54 % | jediné místo, kde se smí cokoli rozhodovat |
| OUT-OF-SAMPLE | 2019-01-01 – 2023-12-31 | ~30 % | jen vyhodnocení, žádné ladění |
| FINAL HOLDOUT | 2024-01-01 – 2026-08-31 | ~16 % | spuštěno jednou po zmrazení specifikace (`frozen_spec.json`) |

## 3. Kandidáti a výběr pro backend testování

Scorecard (literatura, před backtestem): `research/scorecard.py` → `results/scorecard.md`.
Tvrdá podmínka: přirozená doba držení musí odpovídat mandátu 4 h – 10 obchodních dní.

**Vybrané tři pro plné testování** (nejvyšší skóre s horizontem „yes“, s preferencí komplementarity —
C3 je stejná sázka jako C2, proto je nahrazena C6):

1. **C2 donchian_h4** – trend / breakout (H4, 55/20, stop 2×ATR20, time-stop 90 barů)
2. **C8 session_drift_h1** – časová (session) anomálie: long 02→15 server (19:00→08:00 NY), short 15→21 server (08:00→14:00 NY), katastrofický stop 1×denní rozpětí
3. **C6 rsi2_pullback_d1** – podmíněná mean reversion: SMA200 trend, RSI(2) <10 / >90, exit přes SMA5, max 10 dní, stop 3×ATR20

Ostatní (C1, C3, C4, C5, C7, C9) se na DEV spustí jako **kontrolní skupina** se stejnými náklady;
výsledky se reportují. Výměna vybrané strategie za kontrolní je povolena jen tehdy, když vybraná
selže na DEV branách — a musí být v reportu označena (zvyšuje počet testů pro deflated Sharpe).

## 4. Nákladový model (baseline)

* Spread: skutečný bid/ask z dat (A), modelový pro B; exekuce long na ask, short na bid.
* Skluz: 0,3 bp na market příkaz, 1,0 bp na stop příkaz; gapy se plní na horší ceně (open).
* Komise: 0 (spread-only účet; Dukascopy spread ~1,9 bp již obsahuje přirážku). Citlivost: 3,5 USD/lot/strana.
* Swap: long platí (3M T-bill + 2,25 % p.a.), short dostává (3M T-bill − 2,25 % p.a.), ACT/360, trojitý ve středu.
* Spread guard: market příkaz se odloží (max. 3 bary), když spread při otevření baru > 4 bp.
* Stres: náklady ×1,5 a ×2,0 (spread, skluz, komise, swapová přirážka). Bezfrikční běh jen pro rozklad gross/net.

## 5. Testy robustnosti (deklarované předem)

* **Perturbace parametrů** (plná mřížka, DEV+OOS 2010–2023):
  * C2: entry_n {41, 47, 55, 63, 69} × exit_n {15, 17, 20, 23, 25} × stop_atr {1.5, 1.75, 2.0, 2.25, 2.5}
  * C8: long_entry {1, 2, 3} × long_exit {14, 15, 16}; short_entry {14, 15, 16} × short_exit {20, 21, 22}; stop {0.75, 1.0, 1.25, 1.5}
  * C6: lo {5, 7.5, 10, 12.5, 15} × trend_n {150, 175, 200, 225, 250} × exit_n {3, 4, 5, 6, 7}
* **Timeframe**: C2 H2/H3/H4/H6/D1 se škálováním délek v hodinách; C8 báze M30 vs H1 (stejné hodiny, ± 30 min posun); C6 D1/H12/H8 (škálované délky).
* **Zpoždění vstupu**: +1 bar báze (H1) a skluz ×3.
* **Walk-forward**: klouzavě 4 roky trénink / 1 rok test, testy 2014–2023; výběr z 3×3 mřížky dvou hlavních parametrů podle Sharpe v tréninku.
* **Bootstrap**: obchody (10 000×) a blokový bootstrap denních výnosů (blok 20 dní, 5 000×).
* **Režimy (ex-ante, data k předchozímu dni)**: trend/range (|ret60|/(σ·√60) > 1), vysoká/nízká vol (σ20 vs. 252denní medián), silný/slabý USD (60denní změna indexu), rostoucí/klesající sazby (60denní změna 10Y), krize (VIX > 25) vs. normál.
* **Subperiody**: po letech a 3letých blocích; long a short odděleně.

## 6. Brány přijetí (předem stanovené)

Strategie je označena jako **robustní kandidát**, jen pokud splní všechny body:

1. DEV: net expectancy > 0 a PF > 1,10 při baseline nákladech.
2. OOS (2019–2023): net expectancy > 0, PF > 1,05, Sharpe > 0,3.
3. Náklady ×1,5: expectancy DEV+OOS > 0 (×2 se reportuje).
4. Perturbace: ≥ 70 % sousedních kombinací má kladnou net expectancy (DEV+OOS).
5. Walk-forward: spojený OOS výsledek kladný.
6. Koncentrace: žádný kalendářní rok nepřináší > 50 % celkového net zisku.
7. Bootstrap: P(expectancy > 0) ≥ 90 %.
8. Holdout se jen reportuje (žádné ladění); záporný holdout snižuje důvěru, ale nevede ke změně pravidel.

Směr (long/short), který samostatně neprojde body 1–2, se označí jako bez edge a v produkci se vypne.
