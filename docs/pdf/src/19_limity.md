# 19. Rizika, neznámé a omezení

Každé omezení je ohodnoceno dopadem na závěry (vysoký, střední, nízký) a doplněno tím, co by ho
zmírnilo.

## 19.1 Data

| Omezení | Dopad | Zmírnění |
|---|---|---|
| Data pocházejí z veřejných GitHub mirrorů; původ nelze ověřit přímo u Dukascopy (síť sandboxu blokovala přímé zdroje) | střední | re-validace na datech vlastního brokera (16.1) |
| Chybí tick data; výzkum je na úrovni barů (M1 → H1/H4), stopy se řeší na H1 | nízký pro H4/D1, střední pro session strategie | tick data nebo M1 simulace pro finální ověření |
| Datová sada B (2004–2016) má jen bid; ask je syntetizován modelovým spreadem | střední pro PRE a část DEV | spready brokera z té doby nejsou k dispozici; výsledky B brát s rezervou |
| Broker B přepíná letní čas podle EU kalendáře → ~3 týdny ročně posun o 1 h vůči NY+7 | nízký (H4/D1), střední pro hodinový profil v B | session závěry stojí na OOS a holdoutu z A |
| Chybějí reálné výnosy (TIPS); použity nominální výnosy 10Y | nízký | doplnit DFII10 při dostupnosti |

## 19.2 Náklady

| Omezení | Dopad | Zmírnění |
|---|---|---|
| Spready Dukascopy (~1,9 bp) se liší od spreadů konkrétního brokera (ECN může být levnější, standardní účet dražší) | střední; trendové strategie přežijí ×1,5, C8b je na nákladech závislá zcela | měřit v paper fázi |
| Swapová přirážka 2,25 % p.a. je kalibrace na 2024–25, ne historická řada | střední (swap tvoří velkou část nákladů vícedenních longů) | použít skutečné swapy brokera |
| Někteří brokeři účtují trojitý swap u kovů v pátek, ne ve středu | nízký | nastavit podle `symbol_info` |
| Skluz stop příkazů v rychlém trhu (gapy, zprávy) | střední | konzervativní model (1 bp + gap na open); ověřit na demu |

## 19.3 Simulace

| Omezení | Dopad | Zmírnění |
|---|---|---|
| Konzervativní předpoklady (SL před TP, stop v témže baru) | nízký; spíš podhodnocují výsledek | — |
| Simulátor nemodeluje částečná plnění | nízký (retailové objemy) | demo fáze |
| Dopad na trh zanedbán | nízký (retail) | — |

## 19.4 Statistika a výzkumný proces

| Omezení | Dopad | Zmírnění |
|---|---|---|
| Malé vzorky (50–250 obchodů na segment), t < 2 i za 22 let | **vysoký** – edge nelze prokázat | rozhodovat podle robustnostního profilu a ekonomické logiky; neočekávat důkaz z paper fáze |
| Mnoho vyzkoušených konfigurací (deflated Sharpe 0–0,55) | vysoký | předregistrace nových hypotéz |
| C8b odvozena z DEV dat | vysoký pro C8b (zamítnuta) | — |
| Náhrada předvybraných kandidátů po DEV | střední | pravidlo zapsáno před OOS; OOS je pro C3/C5/C9 jediný čistý test |
| Výzkumník znal obecný vývoj trhu zlata do roku 2026 (hindsight bias při volbě rodiny) | střední | zmrazení pravidel před holdoutem; nezávislé ověření jinou osobou |

## 19.5 Režim trhu

| Omezení | Dopad | Zmírnění |
|---|---|---|
| Holdout 2024–2026 je mimořádný býčí trh poháněný poptávkou centrálních bank | vysoký pro interpretaci holdoutu | nepovažovat holdout za důkaz robustnosti |
| Strukturální změna driverů zlata (rozpad vztahu k reálným sazbám po 2022) | střední | nepoužívat makro filtry kalibrované na staré vztahy |
| Režim selhání trendu (krize, vysoká volatilita) se může opakovat | střední | DD stopy, kill switch, monitoring režimu |

## 19.6 Literatura a software

| Omezení | Dopad | Zmírnění |
|---|---|---|
| Plné texty části zdrojů nedostupné (arXiv, SSRN blokovány); použity abstrakty a souhrny | nízký až střední | ověřit klíčové práce v plném znění (zejména Kurth et al. 2026 pro zlato) |
| MT5 adaptér nebyl spuštěn proti terminálu | **vysoký pro provoz** | integrační testy na demu (16.2) |
| Posun časové zóny serveru brokera musí být nastaven ručně | střední | ověřit korelací s referenčními daty |

## 19.7 Netestované směry

ML modely, opční data (GVZ), pozicování (COT), toky ETF, intermarket (stříbro, AUD, těžaři),
časové stopy pro trend a kombinace trendu s režimovými filtry. Nic z toho nebylo předregistrováno,
proto to nebylo testováno.

## 19.8 Co nejvíc ohrožuje doporučení

1. **Edge může být nulový.** Při t < 2 je to reálná možnost. Proto jen pozorovací paper fáze, žádný kapitál.
2. **Náklady u konkrétního brokera** mohou být vyšší než model. Při 2× nákladech je C2 na nule a C5 záporná.
3. **Netestovaná MT5 integrace** a provozní chyby (duplicitní příkazy, časová zóna).

Ověření ve stejném pořadí: re-validace na datech brokera, integrační testy na demu, paper fáze
s měřením nákladů.

*Zdrojové soubory: research/results/data_quality.json, docs/pdf/src/03_data.md (posun DST v B),
research/results/s02_*.json, dsr_within_grid.json, s04_holdout.json, tradingsystem/brokers/mt5.py.*
