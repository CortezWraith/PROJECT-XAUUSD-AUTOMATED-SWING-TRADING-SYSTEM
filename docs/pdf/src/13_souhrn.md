# 13. Souhrn za celé období 2004–2026

## 13.1 Proč souhrn přes všechny segmenty

Jednotlivé segmenty mají jen 50–250 obchodů na strategii, takže každý z nich je statisticky slabý.
Spojení všech čtyř nezávislých úseků (PRE 2004–2009, DEV 2010–2018, OOS 2019–2023, HOLDOUT
2024–2026) dává nejdelší dostupný vzorek. Upozornění: souhrn se nepoužil k žádnému rozhodnutí
(pořadí bylo zmrazeno před holdoutem). Slouží jen k odhadu, jak velký a jak jistý efekt je.

## 13.2 Souhrnná tabulka (baseline náklady)

| Strategie | Obchody | Exp. R | t-stat | PF | Sharpe | Kladné segmenty |
|---|---|---|---|---|---|---|
| C3 EMA trend H4 | 412 | 0,067 | 1,25 | 1,20 | 0,27 | 4 ze 4 |
| C2 Donchian H4 | 595 | 0,149 | 1,71 | 1,25 | 0,40 | 4 ze 4 |
| C5 Squeeze H4 | 810 | 0,074 | 1,46 | 1,16 | 0,33 | 3 ze 4 |
| C9 Donchian + USD | 371 | 0,125 | 1,12 | 1,19 | 0,26 | 3 ze 4 |
| C8b Session | 11 281 | −0,006 | −2,15 | 0,95 | −0,46 | 1 ze 4 |

## 13.3 Expectancy po segmentech a podle směru

| Strategie | PRE | DEV | OOS | HOLDOUT | Long celkem | Short celkem |
|---|---|---|---|---|---|---|
| C3 | 0,064 | 0,074 | 0,038 | 0,106 | 0,101 | 0,035 |
| C2 | 0,316 | 0,064 | 0,094 | 0,197 | 0,384 | −0,147 |
| C5 | 0,122 | 0,109 | −0,092 | 0,162 | 0,136 | 0,009 |
| C9 | 0,123 | 0,192 | −0,013 | 0,180 | 0,335 | −0,120 |
| C8b | −0,005 | 0,003 | −0,017 | −0,015 | −0,001 | −0,010 |

Jak číst: C3 a C2 jsou jediné strategie kladné ve všech čtyřech obdobích, z nichž dvě (PRE a
HOLDOUT) nebyly použity k vývoji. U C2 je za 22 let long strana výrazně silnější než short. To
odpovídá dlouhodobému růstu ceny zlata z ~400 na ~4 400 USD a zároveň varuje, že část výsledku
může být jen beta k býčímu trhu [I].

![Equity křivky 2004–2026 (0,5 % riziko na obchod, baseline náklady)](research/results/figures/equity_segments.png)

## 13.4 Statistická síla: proč ani 22 let nestačí

Anualizovaný Sharpe a t-statistika střední hodnoty denních výnosů jsou přibližně svázány vztahem
**t ≈ SR · √(počet let)**. Aby byl výsledek významný na obvyklé hladině (t ≈ 2), je potřeba:

| Skutečný Sharpe | Potřebná délka historie pro t = 2 |
|---|---|
| 0,25 | 64 let |
| 0,30 | 44 let |
| 0,40 | 25 let |

Pozorovaný Sharpe trendových variant 0,26–0,40 za 22 let tedy dává t-statistiky 1,1–1,7. Pro
rozhodování to znamená:

1. Edge této velikosti **nelze prokázat** ani nejdelší dostupnou historií, natož několikaměsíčním
   paper tradingem. Nulovou hypotézu („edge neexistuje“) nelze zamítnout.
2. Rozhodnutí, zda pokračovat, musí stát na kombinaci **ekonomického zdůvodnění** (literatura
   o trend followingu), **robustnostního profilu** (perturbace, timeframy, náklady, nezávislé segmenty)
   a **ochoty nést riziko**, že edge je nulový.
3. Paper a demo fáze proto mají měřit implementační věrnost (náklady, skluz, paritu signálů), ne
   „potvrzovat edge“ (kapitola 18).

## 13.5 Závěr kapitoly

> **Závěr:** Trendová rodina na H4 je jediná, která má za 22 let a ve všech nezávislých úsecích
> konzistentně kladnou čistou expectancy. Efekt je ale malý (+0,07 až +0,15 R na obchod) a statisticky
> neprůkazný (t < 2). Session strategie C8b má za 22 let čistou expectancy statisticky záporně
> odlišnou od nuly (t = −2,15), tedy jasně ztrátovou.

*Zdrojové soubory: research/results/s05_pooled.json, s05_pooled.md, research/s05_summary.py,
research/results/figures/equity_segments.png.*
