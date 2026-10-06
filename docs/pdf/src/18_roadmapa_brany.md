# 18. Implementační roadmapa a objektivní promotion gates

## 18.1 Princip

Úspěšný backtest **neautorizuje** další fázi. Každý přechod vyžaduje splnění všech číselných bran
a písemný záznam (commit s daty měření). Při Sharpe kolem 0,3 nelze edge v rozumném čase prokázat
(kapitola 13.4). Brány proto měří **implementační věrnost a nepřítomnost rozpadu**, ne existenci edge.

## 18.2 Fáze

| Fáze | Účel | Vstupní podmínka | Délka | Stav |
|---|---|---|---|---|
| RESEARCH | hypotézy, literatura, apriorní pravidla | — | — | hotovo |
| BACKTEST | DEV screening | předregistrace commitnuta | — | hotovo |
| OOS VALIDACE | OOS, WF, perturbace, náklady, režimy | DEV brána 1 | — | hotovo, žádná strategie neprošla všemi branami |
| PAPER (pozorovací) | měření nákladů a věrnosti, bez kapitálu | re-validace na datech brokera + MT5 integrační testy | ≥ 3 měsíce | další krok |
| DEMO | skutečná plnění a swapy brokera | brána PAPER → DEMO | ≥ 6 měsíců | |
| SMALL LIVE | malé reálné riziko | brána DEMO → SMALL LIVE | ≥ 12 měsíců | |
| PRODUCTION | cílové riziko | brána SMALL LIVE → PRODUCTION | průběžně | |

## 18.3 Brány

| Přechod | Objektivní brány (všechny musí platit) |
|---|---|
| RESEARCH → BACKTEST | hypotéza s ekonomickým zdůvodněním; apriorní pravidla, parametry, splity a brány commitnuté před prvním během |
| BACKTEST → OOS VALIDACE | DEV: exp > 0 a PF > 1,10 při baseline nákladech |
| OOS VALIDACE → PAPER (plnohodnotný kandidát) | všech 7 předregistrovaných bran; **dnes nesplňuje nikdo** |
| … → PAPER (jen pozorovací) | DEV+OOS exp > 0 při ×1,5 nákladech a ≥ 70 % kladných sousedů v mřížce; splňují C3, C2, C5 |
| PAPER → DEMO | ≥ 3 měsíce a ≥ 30 signálů za rodinu; 0 kritických chyb (duplicitní nebo ztracený příkaz, nesoulad pozic); parita signálů s offline replay ≥ 99 %; realizovaný spread + skluz ≤ 1,5× model; frekvence obchodů v pásmu 5–95 % |
| DEMO → SMALL LIVE | ≥ 6 měsíců a ≥ 60 obchodů za rodinu; realizované náklady včetně swapů ≤ 1,5× model; realizovaná exp. R v bootstrap pásmu 5–95 %; max DD < bootstrap p95; reconnect, restart a kill switch otestovány; re-validace na datech brokera se stejným závěrem; vyplněno `small_live_approved_on` |
| SMALL LIVE → PRODUCTION | ≥ 12 měsíců; statistiky v pásmech; žádné porušení limitů; tracking error live vs. replay ≤ 0,1 R na obchod; nezávislá revize kódu; navyšování rizika max. ×2 za čtvrtletí |

## 18.4 Demotion a kill pravidla

| Spouštěč | Akce |
|---|---|
| Portfolio DD > 13 % (bootstrap p90 při vahách 1/3) | zpět o fázi, manuální revize |
| Portfolio DD ≥ 15 % (≈ bootstrap p95 14,9 %) | automatický kill switch: zavřít vše, halt |
| Strategický DD > 10 % equity | strategie vypnuta, manuální revize |
| Exp. R posledních 100 obchodů < bootstrap p05 | zpět o fázi |
| Realizované náklady > 2× model | zastavit, re-validace nákladů |
| Chyba rekonciliace nebo duplicitní příkaz | okamžitý halt, oprava, opakování fáze |
| Denní ztráta 2 % / týdenní 4 % | do konce dne / týdne žádné nové vstupy |

## 18.5 Risk framework s odůvodněním

| Parametr | Hodnota | Odůvodnění |
|---|---|---|
| Riziko na obchod | 0,5 % za celou trendovou rodinu (1/3 na strategii, tj. 0,167 %) | jedna sázka = jeden rozpočet; při 0,5 % na každou strategii dosáhl DEV+OOS drawdown 15 % (kill switch v 11/2021), bez limitů 23 % |
| Max. otevřené riziko | 1,5 % equity | max. 3 současné pozice ve stejném směru |
| Hrubá expozice | ≤ 3× equity | ochrana proti příliš těsným stopům a pákovému efektu |
| Denní / týdenní ztráta | 2 % / 4 % | ~12 R / ~24 R při 0,167 %; zastaví provozní chyby dřív než strategický DD |
| Strategický DD stop | 10 % equity | ~60 R při 0,167 %, nad bootstrap p95 (C2: ~50 R) |
| Portfolio DD stop | 15 % | ≈ p95 blokového bootstrapu portfolia (14,9 %; medián 8,3 %) |
| Volatility sizing | stop v násobcích ATR → objem nepřímo úměrný volatilitě | Harvey et al. (2018): u komodit nezvyšuje Sharpe, ale snižuje chvosty |
| Sizing báze | equity na začátku měsíce | riziko nezávisí na nedávných ziscích |
| Zakázáno | martingale, dohánění ztrát, průměrování, pyramidování | požadavek zadání a ochrana kapitálu |

## 18.6 Roadmapa

| Krok | Délka | Výstup |
|---|---|---|
| 1. Re-validace na datech brokera | 1–2 týdny | zpráva o shodě (kapitola 16.1) |
| 2. MT5 integrační testy na demu | 1–2 týdny | splněný checklist (kapitola 16.2) |
| 3. PAPER | ≥ 3 měsíce | měsíční reporty KPI proti pásmům |
| 4. DEMO | ≥ 6 měsíců | reporty nákladů a plnění |
| 5. SMALL LIVE (0,05–0,1 % na obchod za rodinu) | ≥ 12 měsíců | tracking error, rozhodnutí o PRODUCTION |
| Paralelně: nový výzkumný cyklus | průběžně | předregistrované hypotézy nezávislého edge (kapitola 16.5) |

*Zdrojové soubory: REPORT.md kap. 20.4, 21, 22; research/results/s03_portfolio.json (portfolio
varianty, kill switch 2021-11); bootstrap portfolia (p50 8,3 %, p90 13,1 %, p95 14,9 %);
research/results/s02_C2.json (bootstrap max DD); config/paper.toml.*
