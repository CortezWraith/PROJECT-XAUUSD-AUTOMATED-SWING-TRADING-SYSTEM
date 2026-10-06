# 12. Finální holdout 2024–2026

## 12.1 Postup a ochrana před laděním

Holdout je poslední, do té doby nedotčený úsek dat: 2024-01-01 až 2026-08-31, výhradně datová sada A
(reálný bid/ask Dukascopy). Ochrana proti tomu, aby výsledky holdoutu ovlivnily pravidla:

1. Specifikace všech pěti validovaných strategií, jejich parametry, rizikové váhy portfolia a pořadí
   kandidátů byly zapsány do `research/frozen_spec.json` a commitnuty (commit `cfe78c3`) **před**
   prvním během na holdoutu.
2. Skript `research/s04_holdout.py` před každým během kontroluje, že parametry strategie přesně
   odpovídají zmrazené specifikaci (`assert`); jakákoli změna by běh zastavila.
3. Holdout byl spuštěn jednou (commit `87cd6b6`). Po něm se v `tradingsystem/` ani v
   `research/registry.py` nezměnilo nic, co by ovlivnilo pravidla.
4. Výsledek holdoutu nemění pořadí. Pořadí je výsledkem DEV+OOS a bylo zmrazeno předem.

## 12.2 Kontext trhu

| Ukazatel (mid D1, sada A) | Hodnota |
|---|---|
| Cena 2024-01-02 | 2 058,8 USD |
| Cena 2026-08-31 | 4 447,7 USD |
| Změna za holdout | +116,0 % |
| Maximum (denní close) | 5 415,1 USD (2026-01-28) |
| Rok 2024 | +27,5 % |
| Rok 2025 | +62,5 % |
| Rok 2026 (do konce srpna) | přibližně beze změny, po propadu z maxima o ~18 % |
| Anualizovaná volatilita holdoutu | 21,4 % (OOS 2019–2023: 14,6 %) |

Jak číst: holdout zachytil jeden z nejsilnějších býčích trhů zlata v historii (cena se víc než
zdvojnásobila) a vyšší volatilitu než předchozí období. Takové prostředí systematicky prospívá
trendovým strategiím na long straně. Kladný výsledek proto není nezávislým důkazem robustnosti.
Dokládá spíš to, že strategie v prostředí, pro které jsou stavěné, fungovaly tak, jak mají.

## 12.3 Výsledky jednotlivých strategií (baseline náklady)

| Strategie | Obchody | Win % | Exp. R | PF | Sharpe | CAGR % | Max DD % |
|---|---|---|---|---|---|---|---|
| C3 EMA trend H4 | 49 | 34,7 | 0,106 | 1,27 | 0,37 | 0,88 | 4,7 |
| C2 Donchian H4 | 76 | 30,3 | 0,197 | 1,31 | 0,51 | 2,66 | 8,0 |
| C5 Squeeze H4 | 95 | 31,6 | 0,162 | 1,31 | 0,65 | 2,82 | 5,2 |
| C9 Donchian + USD filtr | 41 | 36,6 | 0,180 | 1,30 | 0,32 | 1,19 | 6,2 |
| C8b Session Asie/Londýn | 1 375 | 46,7 | −0,015 | 0,87 | −1,25 | −3,73 | 10,3 |
| Portfolio C3+C2+C5 (váhy 1/3, limity zapnuté) | 218 | 32,1 | 0,171 | 1,35 | 0,72 | 2,18 | 4,0 |

Co z toho plyne: všechny čtyři trendové varianty byly v holdoutu kladné, session strategie C8b
záporná. CAGR je nízký, protože výzkumné riziko je 0,5 % na obchod a v portfoliu jen 1/3 z toho.
Rozhodující je expectancy v R a Sharpe, ne absolutní výnos.

## 12.4 Nákladový stres v holdoutu (exp. R)

| Strategie | ×1,0 | ×1,5 | ×2,0 |
|---|---|---|---|
| C3 | 0,106 | 0,091 | 0,076 |
| C2 | 0,197 | 0,170 | 0,144 |
| C5 | 0,162 | 0,140 | 0,120 |
| C9 | 0,180 | 0,156 | 0,131 |
| C8b | −0,015 | −0,023 | −0,030 |

Trendové strategie zůstávají kladné i při dvojnásobných nákladech. Při velkých cenových pohybech
holdoutu jsou náklady relativně menší, protože jsou úměrné ceně, ale pohyby rostly rychleji.
C8b ztrácí při každé úrovni nákladů.

## 12.5 Long vs. short v holdoutu

| Strategie | Long obchody | Long exp. R | Long PF | Short obchody | Short exp. R | Short PF |
|---|---|---|---|---|---|---|
| C3 | 27 | 0,380 | 2,13 | 27 | −0,136 | 0,62 |
| C2 | 45 | 0,812 | 2,56 | 31 | −0,696 | 0,13 |
| C5 | 49 | 0,610 | 2,55 | 46 | −0,315 | 0,50 |
| C9 | 26 | 0,555 | 2,19 | 15 | −0,469 | 0,31 |
| C8b | 688 | 0,008 | 1,07 | 687 | −0,038 | 0,69 |

> **Klíčové zjištění:** celý zisk holdoutu přinesla long strana; short strana ztrácela u všech
> strategií (C2 short: 31 obchodů, úspěšnost 9,7 %, exp. −0,70 R). V DEV a OOS přitom byla u C3
> právě short strana ta ziskovější (DEV +0,131 R, OOS +0,070 R) a long strana záporná. Asymetrie
> směrů se mění s režimem trhu zlata. Pravidlo „vypni směr, který neprošel branami“ by před
> holdoutem vypnulo long stranu C3, tedy tu, která v holdoutu vydělávala. Proto doporučujeme
> symetrická pravidla a směr nevypínat bez mnohem většího vzorku (kapitola 16).

## 12.6 Byl holdout v očekávaném pásmu?

Porovnání expectancy holdoutu s 5–95% pásmem trade bootstrapu z DEV+OOS (kapitola 10):

| Strategie | Bootstrap exp. R p05 | p50 | p95 | Holdout exp. R | V pásmu? |
|---|---|---|---|---|---|
| C3 | −0,044 | 0,058 | 0,172 | 0,106 | ANO |
| C2 | −0,086 | 0,080 | 0,257 | 0,197 | ANO |
| C5 | −0,060 | 0,038 | 0,139 | 0,162 | NE (nad p95) |

C3 a C2 dopadly v holdoutu lépe než medián, ale uvnitř očekávaného rozpětí. C5 nad rozpětím:
po slabém OOS (−0,092 R) následoval velmi silný holdout. To je typický obraz strategie, jejíž výsledek
víc závisí na režimu trhu než na stabilním edge.

## 12.7 Portfolio po letech

| Rok | Výnos | Obchody | Win % | Exp. R | PF |
|---|---|---|---|---|---|
| 2024 | −0,5 % | 92 | 27,2 | −0,043 | 0,94 |
| 2025 | +4,0 % | 80 | 36,2 | 0,323 | 1,76 |
| 2026 (do 08/31) | +2,4 % | 46 | 34,8 | 0,334 | 1,83 |

I v roce, kdy zlato vzrostlo o 27,5 % (2024), bylo portfolio mírně záporné. Trend na H4 nesbírá
„betu“ trhu automaticky; zisk přišel až s plynulejšími trendovými úseky roku 2025 a s propadem
a odrazem v roce 2026.

## 12.8 Závěr kapitoly

- Holdout **nevyvrátil** trendovou rodinu: všechny čtyři varianty byly kladné i při 2× nákladech.
- Holdout **nepotvrdil robustnost**: období bylo pro trend mimořádně příznivé, zisk pochází jen
  z long strany a vzorek je malý (49–95 obchodů na strategii, t-statistiky 0,5–0,9).
- Session strategie C8b selhala i zde, což potvrzuje její zamítnutí.
- Zmrazené pořadí (C3, C2, C5) zůstává beze změny. Nejlepší výsledek v holdoutu měla C2, ale
  to je informace o historickém výsledku, ne o budoucí robustnosti (kapitola 15).

*Zdrojové soubory: research/results/s04_holdout.json, s04_holdout.md, research/frozen_spec.json,
research/s04_holdout.py, data/processed/A_D1.parquet (kontext trhu), research/results/s02_C3.json,
s02_C2.json, s02_C5.json (bootstrap pásma).*
