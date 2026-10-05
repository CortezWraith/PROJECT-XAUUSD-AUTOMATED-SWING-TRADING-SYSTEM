# 3. Data

Tato kapitola popisuje, z jakých dat výzkum vychází, jak byla ověřena a jaká mají omezení. Kvalita
dat určuje, nakolik lze věřit všem dalším číslům. U strategií s expectancy kolem +0,06 R může i malá
chyba v datech (posunutá časová zóna, podhodnocený spread) změnit znaménko výsledku.

## 3.1 Přehled datových sad a proč GitHub mirrory

| Sada | Zdroj (URL) | Období | Typ ceny | Časová zóna | Použití |
|---|---|---|---|---|---|
| A | Dukascopy-format M1 bid/ask, github.com/Dypoi/XAUUSD_Dataset | 2016-09-01 – 2026-09-01 | bid i ask OHLC po minutách | UTC → převedeno na server NY+7 | DEV od 2016-09, OOS, HOLDOUT; exekuce na reálném bid/ask |
| B | export MT4 brokera (skript nvn01), github.com/FeziweMelvin/XAUUSD-Gold-Price | 2004-06-11 – 2025-06-06 | jen bid OHLC po hodinách; ask syntetizován | server GMT+2/+3 (≈ NY+7) | PRE-SAMPLE 2004–2009, DEV 2010-01 – 2016-08 |
| C | MT5 broker H1, github.com/ejtraderLabs/historical-data | 2012-05-17 – 2022-03-04 | jen bid, ceny ×100 jako celá čísla | server | deklarována jen pro křížovou kontrolu, ve výsledcích nepoužita |
| Makro | VIX: github.com/datasets/finance-vix; FX H.10: github.com/datasets/exchange-rates; US Treasury: github.com/fujiapple852/yield | 2000-01-03 – 2026-10-02 | denní hodnoty | americké datum | swapy (3M), režimy (VIX, USD, 10Y), filtr C9 (USD index) |

Jak číst tabulku: A je hlavní a nejkvalitnější sada (skutečný bid i ask po minutách), B prodlužuje
historii zpět do roku 2004, ale má jen bid. Co z toho plyne: výsledky OOS a holdoutu (2019–2026)
stojí výhradně na A s reálnými spready. DEV 2010–2018 je ze 74 % (podle počtu H4 barů) na B se
syntetickým askem a PRE-SAMPLE 2004–2009 celý na B.

**Proč GitHub mirrory.** Síťová politika výzkumného sandboxu blokovala přímý přístup k primárním
zdrojům (Dukascopy datafeed, FRED, Yahoo Finance) i k plným textům literatury. Přístupný byl GitHub,
proto byla data stažena z veřejných repozitářů, které primární zdroje zrcadlí (`research/fetch_data.sh`,
klonování s `--depth 1`). Surová data nejsou kvůli velikosti a licencím součástí repozitáře, skript
je stáhne do `data/raw/`. Důsledek: **původ dat nelze ověřit přímo u poskytovatele** [U]. Proto byla
každá sada ověřena nepřímo, z vnitřní konzistence a vzájemným srovnáním (kapitoly 3.2–3.4).

## 3.2 Datová sada A – Dukascopy-format M1 bid/ask

**Obsah.** Deset ročních CSV souborů (`XAUUSD_M1_20160901_20170901.csv` … `XAUUSD_M1_20250901_20260901.csv`)
se sloupci timestamp, open/high/low/close bid, open/high/low/close ask a objemy bid/ask. Po sloučení
bylo 3 550 079 minutových řádků, po odstranění duplicit 3 541 952. První minuta je 2016-09-01 00:00,
poslední 2026-09-01 23:59 (UTC).

### Ověření časové zóny

Formát Dukascopy používá UTC, ale mirror to nedokumentuje. Ověření vychází z otevírací a zavírací doby
spotového zlata: trh otevírá v neděli v 18:00 New York a zavírá v pátek v 17:00 New York. V UTC to
znamená otevření ve 22:00 (letní čas, EDT) nebo ve 23:00 (zimní čas, EST) a uzavření ve 21:00 nebo
ve 22:00. Pro tento dokument byla v datech znovu nalezena všechna víkendová přerušení delší než 40 hodin
(dopočet z `data/raw/dukascopy_m1`):

| Událost | Hodina UTC v datech | Počet týdnů | Interpretace |
|---|---|---|---|
| první minuta po víkendu | 22:00 | 340 | 18:00 NY v letním čase |
| první minuta po víkendu | 23:00 | 182 | 18:00 NY v zimním čase |
| z toho prosinec–únor | 23:00 | 129 ze 129 | zima: vždy 23:00 UTC |
| z toho červen–srpen | 22:00 | 131 ze 131 | léto: vždy 22:00 UTC |
| poslední minuta před víkendem | začátek 20:59 (konec 21:00) | 337 | 17:00 NY v létě |
| poslední minuta před víkendem | začátek 21:59 (konec 22:00) | 170 | 17:00 NY v zimě |
| poslední minuta před víkendem | jiná hodina (16–19 UTC) | 15 | zkrácené obchodování o svátcích |

Jak číst tabulku: kdyby data byla v jiné zóně (například GMT+2), otevření by se objevilo v 00:00 nebo
v 01:00. Co z toho plyne: data jsou v **UTC** se střídáním letního času přesně podle New Yorku, což
odpovídá záznamu v `data_quality.json` („Sunday open 22:00/23:00 UTC, Friday close 21:00/22:00 UTC“) [E].
Otevření v pondělí (8×) a uzavření ve čtvrtek (13×) připadají na svátky.

### Duplicity, díry a záporné spready

- **Duplicity:** 8 127 řádků. Všechny jsou přesné kopie (shoduje se čas i všechny ceny) a leží na
  1. září, tedy na hranicích ročních souborů, které se o několik hodin překrývají. Odstraněny
  (`drop_duplicates` podle času) [E, dopočet].
- **Záporné spready:** 0. Nulové spready (ask = bid): 0 [E, dopočet].
- **Díry v pracovní dny delší než 2 hodiny** (mimo denní přestávku a víkend): 69. Příklady jsou 2. ledna
  a 26. prosince různých let, tedy svátky se zkráceným obchodováním. Jiné díry delší než 2 hodiny
  v datech nejsou [E].

### Spread po letech

| Rok | Medián spreadu (USD) | Medián spreadu (bp) |
|---|---|---|
| 2016 | 0,283 | 2,26 |
| 2017 | 0,241 | 1,92 |
| 2018 | 0,239 | 1,87 |
| 2019 | 0,294 | 2,12 |
| 2020 | 0,397 | 2,17 |
| 2021 | 0,354 | 1,98 |
| 2022 | 0,368 | 2,04 |
| 2023 | 0,330 | 1,69 |
| 2024 | 0,380 | 1,59 |
| 2025 | 0,580 | 1,73 |
| 2026 | 0,690 | 1,50 |

Jak číst tabulku: medián spreadu close ask − close bid přes všechny minuty roku, v dolarech za unci
a v bazických bodech ceny (1 bp = 0,01 %). Rok 2016 obsahuje jen září až prosinec, 2026 leden až
1. září. Co z toho plyne: v dolarech spread od roku 2017 vzrostl skoro trojnásobně (0,24 → 0,69 USD),
v relativním vyjádření ale klesl (1,92 → 1,50 bp), protože cena zlata vzrostla zhruba 3,5×. **Náklady
je proto správné modelovat v bp, ne v pevných dolarech.** Typický dnešní spread kolem 1,5–1,7 bp
odpovídá při ceně 4 000 USD zhruba 0,6–0,7 USD na unci, tedy 60–70 USD na lot za celý obchod
(polovina při vstupu, polovina při výstupu).

## 3.3 Datová sada B – MT4 broker H1 (bid)

**Obsah.** Soubor `XAU_1h_data.csv` (oddělovač středník, formát data `2004.06.11 07:00`) se sloupci
Open, High, Low, Close a Volume. Jde o export z MetaTrader 4 neznámého brokera přes skript „nvn01“.
Má 122 028 hodinových řádků od 2004-06-11 07:00 do 2025-06-06 06:00. Duplicitní časy: 0. Řádky
o víkendu: 0 [E, dopočet].

### Ověření serverového času (NY+7)

MT4 data jsou v serverovém čase brokera, který není v souboru uveden. Na překryvu s A
(2016-09-01 – 2018-12-31, tedy uvnitř DEV) byla spočítána korelace hodinových log-výnosů close bid
B a A pro různé posuny B vůči UTC. Správný posun má dávat korelaci blízkou 1.

| Předpoklad: čas B = UTC + | Korelace H1 výnosů s A | Počet párů hodin |
|---|---|---|
| 0 h | 0,015 | 12 927 |
| 1 h | 0,007 | 13 063 |
| 2 h | 0,497 | 13 348 |
| 3 h | 0,517 | 13 517 |
| 4 h | −0,006 | 13 084 |
| 2 h, jen prosinec–únor | 0,990 | — |
| 3 h, jen červen–srpen | 0,992 | — |
| **server NY+7 (střídá +2 a +3 h)** | **0,938** | 13 691 |

Jak číst tabulku: posuny +2 h i +3 h dávají každý korelaci kolem 0,5, protože každý sedí přesně jen
zhruba polovinu roku. V zimě sedí +2 h (0,990), v létě +3 h (0,992). Co z toho plyne: B je v čase
GMT+2 v zimě a GMT+3 v létě, tedy prakticky NY+7. Po převodu A do serverového času NY+7 je korelace
0,9377 a medián absolutního rozdílu cen B − A je 0,041 USD (`data_quality.json`). Proto se B používá
v serverovém čase bez další úpravy (`research/prepare_data.py`) [E].

### Nový nález: posun o hodinu v týdnech změny času

Proč je celková korelace 0,94, když zima i léto dávají 0,99? Pro tento dokument byla korelace
rozložena po měsících. Většina měsíců má 0,93–0,999, výrazně nižší jsou jen březen (2017: 0,530; 2018:
0,542) a říjen–listopad (2017-11: 0,763; 2018-10: 0,879; 2018-11: 0,858). Kontrola v přesných týdnech:

| Týden | Korelace při posunu 0 h | Korelace při B + 1 h | Výklad |
|---|---|---|---|
| 2017-03-13 – 2017-03-24 | 0,046 | 0,984 | USA už na letním čase, EU ještě ne |
| 2017-03-27 – 2017-04-07 | 0,985 | 0,064 | obě zóny na letním čase (kontrola) |
| 2017-10-30 – 2017-11-03 | −0,076 | 0,993 | EU už na zimním čase, USA ještě ne |
| 2018-03-12 – 2018-03-23 | −0,003 | 0,992 | USA už na letním čase, EU ještě ne |
| 2018-10-29 – 2018-11-02 | −0,095 | 0,996 | EU už na zimním čase, USA ještě ne |

Jak číst tabulku: v týdnech, kdy Evropa a USA ještě nebo už nemají stejný čas, sedí B až po posunu
o +1 hodinu. Co z toho plyne: **broker B přepínal letní čas podle evropského kalendáře** (poslední
neděle v březnu a v říjnu), zatímco NY+7 se řídí americkým (druhá neděle v březnu, první neděle
v listopadu). Na překryvu 2016–2018 jsou tedy časové značky B přibližně 3 týdny v roce o hodinu
pozadu oproti NY+7 [E, dopočet]. `prepare_data.py` to nekoriguje. Pro roky před 2007 platila v USA
jiná pravidla změny času, takže rozsah posunu tam nelze z A ověřit [I]. Dopad [I]: pro H4 a D1 trendové
strategie je posun hranice svíčky o hodinu během několika týdnů ročně zanedbatelný. Pro hodinové
session strategie (C8, C8b) v období B (PRE-SAMPLE a DEV do 2016-08) mírně rozmazává hodinový profil.
Na zamítnutí C8/C8b to vliv nemá, protože ty selhaly i na čistých datech A (OOS 2019–2023).

### Další vlastnosti B

- **Díry:** 494 přerušení delších než 2 hodiny v pracovní dny, z toho 151 v roce 2010 a 76 v roce 2011.
  V letech 2010–2011 broker pravidelně vynechával serverové hodiny 23 a 00 (137 případů v roce 2010),
  měl tedy delší denní přestávku. Celkem v dírách kratších než 20 hodin chybí 1 263 hodin, zhruba 1 %
  řádků [E, dopočet]. Dvě díry přes 4 dny (2005-11, 2006-11) připadají na americké svátky.
- **Ask je syntetický:** ask = bid × (1 + s(h) / 10 000), kde s(h) je medián spreadu A v bp pro
  serverovou hodinu h, odhadnutý **jen na 2016-09-01 – 2018-12-31** (uvnitř DEV, aby do vývojových dat
  neprosákla informace z OOS). Stejné s(h) se použije na open, high, low i close daného baru. Tabulka
  s(h) je v kapitole 3.5 (sloupec „Model B“).
- **Důsledek syntetického asku [I]:** B nemá spready rozšířené při zprávách ani nárazové skoky, takže
  náklady v období 2004–2016 jsou spíš podhodnocené. Opačně u serverové hodiny 23, kde model
  přiřazuje 6,21 bp celé svíčce včetně open, jsou mírně nadhodnocené.

## 3.4 Datová sada C – deklarovaná, ale nepoužitá

Protokol (`research/PROTOCOL.md`) uvádí sadu C (MT5 broker H1, 2012-05 – 2022-03) jako „jen křížovou
kontrolu“. Žádný skript v `research/` ji ale nenačítá. Ve výsledcích tedy C nefiguruje [E]. Pro tento
dokument byla kontrola dodatečně provedena: soubor `XAUUSD/XAUUSDh1.csv` má 57 600 hodinových řádků
od 2012-05-17 do 2022-03-04, ceny jsou celá čísla ×100. Korelace hodinových výnosů C s A
(2016-09 – 2022-03) je 0,874 při nulovém posunu vůči serverovému času NY+7, −0,015 při posunu −1 h
a 0,116 při +1 h [E, dopočet]. C je tedy rovněž ve zhruba stejném serverovém čase a hrubě konzistentní
s A. Na závěrech výzkumu to nic nemění, je to jen další nezávislé potvrzení časové konvence.

## 3.5 Spread podle serverové hodiny, denní přestávka a spread guard

Dopočet z `data/processed/A_H1.parquet` (celé období A, 2016-09 – 2026-09): relativní spread na open
a na close každého H1 baru podle serverové hodiny. Pro srovnání je přidán modelový spread použitý
pro syntetický ask sady B.

| Serverová hodina | Hodina NY | Počet H1 barů (A) | Medián na open (bp) | p90 na open (bp) | Podíl open > 4 bp | Medián na close (bp) | Model B (bp) |
|---|---|---|---|---|---|---|---|
| 00 | 17 | 41 | 19,08 | 21,78 | 100,0 % | 19,08 | 19,08 |
| 01 | 18 | 2 579 | 5,97 | 11,46 | 77,7 % | 2,29 | 2,31 |
| 02 | 19 | 2 580 | 2,30 | 3,31 | 5,3 % | 1,94 | 2,04 |
| 03 | 20 | 2 580 | 1,93 | 2,58 | 1,7 % | 1,92 | 1,97 |
| 04 | 21 | 2 580 | 1,90 | 2,51 | 1,8 % | 1,89 | 1,95 |
| 05 | 22 | 2 580 | 1,89 | 2,48 | 1,7 % | 1,90 | 1,94 |
| 06 | 23 | 2 580 | 1,88 | 2,45 | 1,6 % | 1,89 | 1,96 |
| 07 | 00 | 2 580 | 1,88 | 2,40 | 1,4 % | 1,89 | 1,96 |
| 08 | 01 | 2 580 | 1,89 | 2,44 | 1,4 % | 1,92 | 1,99 |
| 09 | 02 | 2 580 | 1,93 | 2,54 | 1,5 % | 1,84 | 1,89 |
| 10 | 03 | 2 580 | 1,82 | 2,37 | 1,2 % | 1,82 | 1,87 |
| 11 | 04 | 2 580 | 1,80 | 2,35 | 1,1 % | 1,80 | 1,88 |
| 12 | 05 | 2 580 | 1,79 | 2,34 | 1,2 % | 1,80 | 1,88 |
| 13 | 06 | 2 580 | 1,80 | 2,30 | 1,0 % | 1,82 | 1,89 |
| 14 | 07 | 2 580 | 1,79 | 2,32 | 1,0 % | 1,82 | 1,87 |
| 15 | 08 | 2 579 | 1,78 | 2,32 | 1,0 % | 1,83 | 1,86 |
| 16 | 09 | 2 580 | 1,81 | 2,36 | 1,1 % | 2,02 | 1,97 |
| 17 | 10 | 2 580 | 1,97 | 2,93 | 4,1 % | 1,80 | 1,85 |
| 18 | 11 | 2 580 | 1,78 | 2,32 | 1,1 % | 1,79 | 1,86 |
| 19 | 12 | 2 580 | 1,79 | 2,28 | 1,0 % | 1,82 | 1,92 |
| 20 | 13 | 2 551 | 1,81 | 2,34 | 1,1 % | 1,86 | 1,96 |
| 21 | 14 | 2 530 | 1,83 | 2,53 | 3,0 % | 1,84 | 1,97 |
| 22 | 15 | 2 501 | 1,83 | 2,41 | 1,2 % | 1,84 | 2,00 |
| 23 | 16 | 2 501 | 1,86 | 2,48 | 1,5 % | 4,93 | 6,21 |

Jak číst tabulku: řádek „01“ je H1 bar 01:00–02:00 serveru, tedy 18:00–19:00 v New Yorku. Medián na
open je spread v první minutě baru, na close v poslední. „Model B“ je medián spreadu na close A
v kalibračním období 2016-09 – 2018-12 (`data_quality.json`). Celkově je medián spreadu na open
1,88 bp, p90 2,72 bp a 5,1 % hodinových openů má spread nad 4 bp. Po segmentech: DEV-část A
1,93 / 2,56 bp (3,7 % nad 4 bp), OOS 1,98 / 2,91 bp (5,8 %), HOLDOUT 1,62 / 2,44 bp (4,9 %).

Co z toho plyne:

1. **Denní přestávka 17:00–18:00 New York (server 00–01).** Spotové zlato se hodinu denně neobchoduje
   (navazuje na denní přestávku futures na CME Globex [I]). V datech A je v serverové hodině 00 jen 41 barů ze
   zhruba 2 580 dní (svátky a nepravidelnosti) a jejich spread je kolem 19 bp. Denní svíčka proto
   končí v 17:00 NY a v tento čas se účtuje swap.
2. **Hodina po znovuotevření (server 01, 18:00 NY) je drahá.** Medián spreadu na open je 5,97 bp,
   tedy 3× víc než přes den, a 77,7 % openů je nad 4 bp. Během hodiny se spread normalizuje: na close
   baru je 2,29 bp. Od 02:00 serveru je spread na open zhruba normální (2,30 bp, p90 3,31 bp).
3. **Proč se v hodinách 0–1 neobchoduje: spread guard.** Simulátor (`SimBroker`) i živý driver
   (`LiveRunner`) odkládají market příkazy, dokud je spread na open baru vyšší než 4 bp. Simulátor
   odkládá maximálně o 3 H1 bary (pak vyplní za jakoukoli cenu), živý driver maximálně o 180 minut.
   (`TradingSession` má navíc parametr pro vynechání prvních 15 minut po otevření, současný kód ho ale
   nevyužívá.) Prakticky: signál z H4 svíčky 20:00–24:00 (close v 17:00 NY) se nevyplní v 01:00 při
   spreadu ~6 bp, ale typicky ve 02:00 při ~2,3 bp. Protože vstup platí polovinu spreadu, ušetří se
   zhruba (5,97 − 2,30) / 2 ≈ 1,8 bp, tedy přibližně jeden celý běžný spread.
4. **Hodina 23 serveru (16:00–17:00 NY):** spread na open je normální (1,86 bp), ale ke close se
   rozšiřuje (4,93 bp) před denní přestávkou. Model B přiřazuje celé svíčce 6,21 bp, takže v období B
   je vstup na open této hodiny dražší, než by ve skutečnosti byl.
5. **Nesoulad A a B v hodině 01 [I]:** model B dává hodině 01 spread 2,31 bp na všech cenách včetně
   open. Spread guard v období B proto v 18:00 NY téměř nikdy nezasáhne a příkaz se vyplní za „normální“
   spread. V období B (do 2016-08) jsou tak vstupy po denní přestávce mírně optimistické. Efekt je malý
   (týká se jen příkazů z poslední H4 svíčky dne), ale je to systematický rozdíl mezi zdroji.

## 3.6 Konstrukce barů

Všechny timeframy vznikají agregací z nejjemnějších dostupných dat (`tradingsystem/data/bars.py::resample_bidask`):

- **A:** M1 (UTC) → převod do serverového času NY+7 (`utc_to_server`: UTC → New York včetně letního času
  → +7 h) → agregace na M30, H1, H2, H3, H4, H6 a D1.
- **B:** H1 je nativní (už v serverovém čase), vyšší timeframy H2, H3, H4, H6 a D1 se agregují z H1.
- **Pravidla agregace:** open = první, high = maximum, low = minimum, close = poslední hodnota,
  zvlášť pro bid a pro ask; objem = součet; interval [začátek, konec), označený časem začátku
  (`label="left", closed="left"`). Koše jsou **ukotveny na serverovou půlnoc** (`origin="start_day"`),
  takže H4 začínají v 00, 04, …, 20 a D1 pokrývá 17:00–17:00 NY. Prázdné koše (víkend, přestávka) se
  zahodí, víkendové pahýly (serverová sobota a neděle) také.
- **Mid ceny pro strategie:** open/high/low/close = průměr bid a ask (`add_mid`). Signály se počítají
  z mid, exekuce probíhá na bid/ask.

| Timeframe | Sada A (2016-09 – 2026-09) | Sada B (2004-06 – 2025-06) |
|---|---|---|
| M1 | 3 541 952 | — |
| M30 | 118 200 | — |
| H1 | 59 142 | 122 028 |
| H2 | 30 852 | 64 065 |
| H3 | 20 592 | 42 822 |
| H4 | 15 452 | 32 126 |
| H6 | 10 321 | 21 492 |
| D1 | 2 581 | 5 391 |

Jak číst tabulku: počty barů ze `data_quality.json`. A má 2 581 denních svíček za 10 let, tedy
258 ročně, což odpovídá 5 svíčkám týdně (víkend ani nedělní pahýl se nepočítají). H4 svíček je
5,99 na den. Co z toho plyne: konstrukce barů odpovídá konvenci MT5 brokerů s časem NY+7, takže
indikátory ve výzkumu se budou shodovat s indikátory na brokerově grafu, pokud broker tuto konvenci
používá (ověřit `server_offset_hours`, kapitola 17). M30 existuje jen pro A a slouží pro timeframe test C8b.

Kontrola zarovnání (dopočet): všechny H4 bary A i B začínají v hodinách 00, 04, 08, 12, 16, 20 a všechny
D1 bary v 00:00 serveru, rozložené rovnoměrně na pondělí až pátek (A: 509–520 barů na každý den v týdnu).

## 3.7 Spojení B → A (stitching)

Výzkumná řada (`research/common.py::stitched`) je **B před 2016-09-01 00:00 serverového času a A od
tohoto okamžiku**. Každý bar nese sloupec `source` („A“ nebo „B“), takže je vždy dohledatelné, z jakého
zdroje pochází. Nic dalšího se nemíchá: OOS a holdout jsou čistě A. Datum spoje je dané začátkem sady A.

Detaily spoje (dopočet): poslední bar B je 2016-08-31 23:00 (close bid 1 308,81), první bar A je
2016-09-01 03:00 serveru (= 2016-09-01 00:00 UTC, close bid 1 309,998). Ve spojené řadě tedy chybějí
serverové hodiny 01 a 02 dne 2016-09-01. Na trendové strategie s držením dní to vliv nemá [I]. V DEV
(2010–2018) pochází 10 230 H4 barů (74 %) z B a 3 598 (26 %) z A.

**Křížová kontrola zdrojů.** Aby bylo vidět, zda B dává jiné výsledky než A, spustil DEV screening
(`research/results/s01_dev_screen.md`) všechny kandidáty na překryvu 2016-09-01 – 2018-12-31 zvlášť
na A a zvlášť na B (baseline náklady):

| Kandidát | Obchody A | Obchody B | Exp. R A | Exp. R B | PF A | PF B |
|---|---|---|---|---|---|---|
| C1 TSMOM D1 | 19 | 24 | −0,050 | 0,067 | 0,77 | 1,32 |
| C2 Donchian H4 | 60 | 59 | 0,056 | 0,115 | 1,09 | 1,21 |
| C3 EMA trend H4 | 42 | 45 | 0,200 | 0,189 | 1,62 | 1,57 |
| C4 Volatility breakout D1 | 185 | 189 | −0,033 | −0,017 | 0,90 | 0,94 |
| C5 Squeeze H4 | 83 | 92 | 0,014 | 0,093 | 1,02 | 1,19 |
| C6 RSI(2) pullback D1 | 46 | 68 | −0,051 | −0,152 | 0,74 | 0,44 |
| C7 Z-score MR H1 | 379 | 375 | −0,040 | −0,066 | 0,91 | 0,86 |
| C8 Session drift H1 | 1 160 | 1 171 | −0,018 | −0,014 | 0,89 | 0,92 |
| C9 USD-filtr Donchian H4 | 37 | 36 | 0,031 | 0,142 | 1,04 | 1,27 |
| C8b Asie/Londýn H1 | 1 179 | 1 197 | −0,016 | −0,016 | 0,86 | 0,86 |

Jak číst tabulku: stejné strategie, stejné období (2,3 roku), jen jiný zdroj dat. Co z toho plyne:
znaménko expectancy se shoduje u 9 z 10 kandidátů (liší se jen C1 s 19–24 obchody), takže kvalitativní
závěry nezávisí na zdroji [E]. Breakoutové strategie (C2, C5, C9) ale na B vycházejí systematicky
lépe (+0,06 až +0,11 R). Je to konzistentní s tím, že syntetický ask B nemá nárazově rozšířené spready
[I]. DEV výsledky breakoutů z období 2010–2016 (na B) mohou být proto mírně optimistické. Malý vzorek
(36–92 obchodů) ale nedovoluje rozdíl přesně kvantifikovat.

## 3.8 Segmenty a cenový kontext

| Segment | Období | Zdroj | Délka (roky) | Podíl 2010–2026 | H1 barů | H4 barů | D1 barů |
|---|---|---|---|---|---|---|---|
| PRE-SAMPLE | 2004-07-01 – 2009-12-31 | B | 5,50 | — | 31 361 | 8 292 | 1 401 |
| DEV | 2010-01-01 – 2018-12-31 | B do 2016-08-31, pak A | 9,00 | 54,0 % | 52 509 | 13 828 | 2 316 |
| OOS | 2019-01-01 – 2023-12-31 | A | 5,00 | 30,0 % | 29 549 | 7 722 | 1 290 |
| HOLDOUT | 2024-01-01 – 2026-08-31 | A | 2,67 | 16,0 % | 15 770 | 4 125 | 688 |

Jak číst tabulku: podíly jsou počítány z kalendářní délky období 2010-01-01 – 2026-09-01 (dopočet),
počty barů ze spojené řady (holdout čistě z A). Co z toho plyne: rozdělení 54 / 30 / 16 % odpovídá
doporučení zadání (vývoj 50–60 %, OOS 20–25 %, holdout 20–25 %). Holdout je kratší, protože zadání
preferuje zachovat jako holdout právě roky 2024–2026 a data A končí 2026-09-01.

| Segment | První close D1 | Poslední close D1 | Změna | Minimum (datum) | Maximum (datum) |
|---|---|---|---|---|---|
| PRE-SAMPLE | 395,12 | 1 097,61 | 177,8 % | 386,72 (2004-07-27) | 1 215,48 (2009-12-02) |
| DEV | 1 121,40 | 1 282,55 | 14,4 % | 1 051,88 (2015-12-17) | 1 900,13 (2011-09-05) |
| OOS | 1 284,58 | 2 062,90 | 60,6 % | 1 270,91 (2019-05-02) | 2 077,82 (2023-12-27) |
| HOLDOUT | 2 058,82 | 4 447,74 | 116,0 % | 1 992,36 (2024-02-14) | 5 415,14 (2026-01-28) |

Jak číst tabulku: mid close denních svíček na začátku a konci segmentu a extrémy uvnitř (dopočet ze
spojené řady). Co z toho plyne: segmenty mají velmi odlišný charakter. PRE-SAMPLE je souvislý býčí
trh. DEV obsahuje vrchol 2011, propad 2013 a dno 2015, je to jediný segment s výrazným medvědím
obdobím. OOS je mírně býčí. HOLDOUT je extrémní býčí trh s ročním růstem 64,6 % v roce 2025, ale
také s prudkým poklesem v roce 2026 z maxima 5 415 na zhruba 4 000 USD (měsíční close 2026-06:
4 007,7). Trendové strategie testované v holdoutu tedy zažily nejen růst, ale i vysoce volatilní obrat.

![Vývoj XAUUSD 2004–2026](research/results/figures/xauusd.png)

Graf ukazuje denní close výzkumné řady (B → A) v logaritmickém měřítku. Logaritmická osa znamená, že
stejná svislá vzdálenost odpovídá stejné procentní změně, takže růst ze 400 na 800 USD vypadá stejně
velký jako ze 2 000 na 4 000 USD.

| Rok | Zdroj | D1 barů | Close na konci roku | Roční změna | Min | Max | Realizovaná volatilita p.a. |
|---|---|---|---|---|---|---|---|
| 2004 | B | 140 | 437,04 | — | 382,92 | 453,94 | 13,5 % |
| 2005 | B | 252 | 514,65 | 17,8 % | 412,43 | 527,36 | 12,4 % |
| 2006 | B | 251 | 636,26 | 23,6 % | 516,35 | 714,27 | 24,2 % |
| 2007 | B | 257 | 831,88 | 30,7 % | 606,76 | 839,18 | 17,2 % |
| 2008 | B | 258 | 866,88 | 4,2 % | 710,82 | 1 004,41 | 31,4 % |
| 2009 | B | 257 | 1 097,61 | 26,6 % | 811,25 | 1 215,48 | 20,1 % |
| 2010 | B | 256 | 1 408,27 | 28,3 % | 1 062,74 | 1 423,19 | 16,1 % |
| 2011 | B | 256 | 1 564,60 | 11,1 % | 1 313,58 | 1 900,13 | 20,1 % |
| 2012 | B | 257 | 1 675,03 | 7,1 % | 1 538,61 | 1 790,65 | 14,6 % |
| 2013 | B | 258 | 1 208,37 | −27,9 % | 1 190,07 | 1 692,46 | 21,5 % |
| 2014 | B | 258 | 1 186,94 | −1,8 % | 1 141,60 | 1 382,41 | 14,3 % |
| 2015 | B | 258 | 1 060,91 | −10,6 % | 1 051,88 | 1 301,78 | 13,7 % |
| 2016 | B+A | 258 | 1 151,44 | 8,5 % | 1 074,76 | 1 365,35 | 15,6 % |
| 2017 | A | 257 | 1 302,86 | 13,1 % | 1 158,95 | 1 349,21 | 10,0 % |
| 2018 | A | 258 | 1 282,55 | −1,6 % | 1 174,15 | 1 358,39 | 9,7 % |
| 2019 | A | 258 | 1 517,47 | 18,3 % | 1 270,91 | 1 552,25 | 11,3 % |
| 2020 | A | 259 | 1 898,41 | 25,1 % | 1 471,18 | 2 063,49 | 19,1 % |
| 2021 | A | 258 | 1 829,51 | −3,6 % | 1 683,66 | 1 950,06 | 13,3 % |
| 2022 | A | 258 | 1 823,86 | −0,3 % | 1 622,45 | 2 050,29 | 14,9 % |
| 2023 | A | 257 | 2 062,90 | 13,1 % | 1 811,08 | 2 077,82 | 13,2 % |
| 2024 | A | 259 | 2 624,53 | 27,2 % | 1 992,36 | 2 787,56 | 15,0 % |
| 2025 | A | 258 | 4 319,19 | 64,6 % | 2 636,45 | 4 533,61 | 19,0 % |
| 2026 | A | 173 | 4 324,70 | 0,1 % | 3 975,68 | 5 415,14 | 30,9 % |

Jak číst tabulku: dopočet z denních mid close spojené řady. Rok 2004 začíná 2004-06-11, rok 2026 končí
1. září (neúplný rok, „close na konci roku“ je poslední dostupný close). Realizovaná volatilita je
směrodatná odchylka denních log-výnosů × √252. Co z toho plyne: (a) z 22 ročních změn (2005–2026) bylo jen 6
záporných, dlouhodobý drift zlata je výrazně kladný, a long strana trendových strategií z něj profituje
(kapitola 13) [E]; (b) volatilita kolísá mezi 9,7 % (2018) a 31,4 % (2008), v roce 2026 je 30,9 %. Protože
stop-loss je v násobcích ATR, objem pozice se automaticky zmenšuje, když volatilita roste; (c) roky
2017–2018 s nízkou volatilitou a 2013–2015 s medvědím trendem jsou pro trendové strategie velmi odlišné
režimy (kapitola 10).

## 3.9 Makro řady

Makro data jsou v `data/processed/macro_daily.parquet` (denní, 2000-01-03 – 2026-10-02). Sestavuje je
`research/prepare_data.py::build_macro`.

**VIX.** Denní close indexu CBOE VIX z repozitáře datasets/finance-vix (DataHub mirror). Poslední
hodnota 2026-09-22. Použití: režim „crisis“ (VIX > 25).

**USD index.** Vlastní rekonstrukce indexu dolaru s vahami ICE DXY z denních poledních kurzů Federal
Reserve H.10 (repozitář datasets/exchange-rates). Kurzy v tomto souboru jsou všechny kótované jako
jednotky cizí měny za 1 USD (u eura a libry tedy obráceně oproti obvyklé kotaci EURUSD a GBPUSD),
proto mají všechny váhy kladné znaménko:

```
USD index = 50,14348112 × EUR^0,576 × JPY^0,136 × GBP^0,119 × CAD^0,091 × SEK^0,042 × CHF^0,036
(každá měna = počet jednotek dané měny za 1 USD; váhy: EUR 57,6 %, JPY 13,6 %, GBP 11,9 %,
 CAD 9,1 %, SEK 4,2 %, CHF 3,6 %)
```

Konstanta 50,14348112 a váhy jsou standardní definice DXY. Kontrola: hodnota rekonstrukce k 2024-12-31
je 108,51, což odpovídá úrovni oficiálního DXY koncem roku 2024 [I]. Poslední hodnota je 2026-09-25.
Použití: režim silný/slabý USD (60denní log změna) a filtr strategie C9 (index nad/pod svým 50denním
průměrem).

**US Treasury 3M / 2Y / 10Y.** Denní par yield curve amerického ministerstva financí (repozitář
fujiapple852/yield), převedeno z procent na desetinná čísla (0,0437 = 4,37 %). Poslední hodnota je
2026-10-02. Použití: **3M** pro výpočet swapů, **10Y** pro režim rostoucích/klesajících výnosů.
**2Y** je načten, ale v žádném výsledku se nepoužívá.

**Zpoždění o jeden den.** Makro hodnota daného dne (například close VIX) je v reálném čase známa až
po zavření amerického trhu, tedy kolem 16:00–17:00 NY. Aby simulace nepoužila informaci, kterou by
obchodník ještě neměl, posouvá se každá makro hodnota před použitím o jeden den:

- swapy: sazba pro rollover dne D je poslední známá hodnota 3M k datu D − 1 den (`RateCurve`, dopředné
  doplnění, nikdy nehledí dopředu),
- režimy: index makro řady se posune o +1 kalendářní den a doplní poslední známou hodnotou
  (`research/stats.py::regime_frame`),
- C9: příznak „USD nad 50denním průměrem“ se posune o +1 den a přiřadí se k datu H4 baru
  (`MacroFilteredDonchian.features`).

| Segment | Ø 3M výnos | Ø long swap p.a. | Ø short swap p.a. | Dny s r > 2,25 % | Dny s VIX > 25 | USD index začátek → konec | 10Y začátek → konec |
|---|---|---|---|---|---|---|---|
| PRE-SAMPLE | 2,73 % | −4,98 % | +0,48 % | 56,4 % | 23,4 % | 88,90 → 77,86 | 4,57 % → 3,85 % |
| DEV | 0,41 % | −2,66 % | −1,84 % | 2,4 % | 9,2 % | 77,45 → 96,14 | 3,85 % → 2,69 % |
| OOS | 1,97 % | −4,22 % | −0,28 % | 38,4 % | 24,6 % | 96,75 → 101,17 | 2,66 % → 3,88 % |
| HOLDOUT | 4,46 % | −6,71 % | +2,21 % | 100,0 % | 5,5 % | 102,10 → 99,42 | 3,95 % → 4,75 % |

Jak číst tabulku: dopočet z `macro_daily.parquet`. Long swap p.a. = −(r + 2,25 %), short swap =
r − 2,25 % (kladné = short dostává). Sloupec „dny s r > 2,25 %“ ukazuje, jak často short swap
přinášel. Co z toho plyne: **náklad držení longu se mezi segmenty mění 2,5×** (2,66 % p.a. v DEV vs.
6,71 % p.a. v holdoutu). V holdoutu short dostával 2,21 % p.a., ale long platil 6,71 % p.a. To je pro
vícedenní trendové pozice významná asymetrie (příklad v kapitole 4.4). Režim „krize“ (VIX > 25) byl
častý v PRE-SAMPLE (2008) a v OOS (2020, 2022), vzácný v holdoutu, který je tedy pro trendové
strategie spíš příznivý režim (kapitoly 10 a 12).

Chybějící hodnoty (`data_quality.json`, podíl dní v kalendáři sloučené řady): VIX 0,66 %, USD index
1,41 %, 3M 1,62 %, 2Y 1,57 %, 10Y 1,57 %. Jsou to převážně dny, kdy jeden z trhů měl svátek. Všechna
místa použití (swapy, režimy, filtr C9) je doplňují poslední známou hodnotou.

## 3.10 Omezení dat

1. **Žádná tick data.** Výzkum je bar-level (nejjemněji M1 pro A, H1 pro B). Stopy se vyhodnocují na
   H1 barech s konzervativními pravidly (kapitola 4.5). Tick-level validace exekuce nebyla možná [E].
2. **Původ mirrorů nelze ověřit u poskytovatele** [U]. Konzistence je ověřena nepřímo: časová zóna A
   z otevírací doby, B korelací 0,94 s A, C korelací 0,87 s A, nulové záporné spready, rozumné spready.
3. **B nemá skutečný ask.** 2004-06 – 2016-08 je se syntetickým spreadem kalibrovaným na 2016–2018.
   Nárazová rozšíření (zprávy, krize 2008, 2013) chybí, náklady v té době jsou spíš podhodnocené [I].
4. **B používá evropská data změny času** (nový nález, kapitola 3.3), několik týdnů v roce je o hodinu
   posunutých. Nekorigováno, dopad na H4/D1 zanedbatelný [I].
5. **Spready Dukascopy nejsou spready vašeho brokera.** Dukascopy je ECN/agregátor. Retail MT5 broker
   může mít spread vyšší i nižší a jinou dynamiku kolem přestávky. Re-validace na datech brokera je
   první krok další fáze (kapitola 16 a 18).
6. **Swapy nejsou historická řada.** Přirážka 2,25 % p.a. je kalibrace na typický retail swap 2024–2025.
   Pro dřívější roky jde o předpoklad [U].
7. **Reálné výnosy (TIPS) nebyly dostupné**, režim „sazby“ používá nominální 10Y. Vztah zlata k reálným
   sazbám se navíc po roce 2022 rozpadl (kapitola 5), takže ani dostupná řada by nemusela pomoci [I].
8. **Spoj 2016-09-01** má dvouhodinovou mezeru a v DEV je 74 % H4 barů z B. Křížová kontrola ukazuje
   shodu znamének, ale breakouty vycházejí na B lépe (kapitola 3.7).
9. **Sada C byla v protokolu deklarována, ale ve výzkumu nepoužita.** Dodatečná kontrola (korelace
   0,87) závěry nemění.

> **Závěr:** Data jsou pro bar-level výzkum swing strategií na H1–D1 dostatečná a jejich časová
> konvence (server NY+7, D1 = 17:00–17:00 NY) je ověřená. Nejslabším místem je období 2004–2016
> se syntetickým askem a nejistota, jak se budou lišit náklady konkrétního brokera. Obojí spíše
> nadhodnocuje výsledky breakoutových strategií, žádné z omezení ale nemůže proměnit zamítnuté
> strategie v robustní.

*Zdrojové soubory: `research/results/data_quality.json`, `data/processed/data_quality.json`,
`research/prepare_data.py`, `research/fetch_data.sh`, `research/common.py` (`stitched`, `load`, `macro`,
`rate_curve`), `research/stats.py`, `research/PROTOCOL.md`, `research/results/s01_dev_screen.md`,
`research/s05_summary.py` (graf), `research/results/figures/xauusd.png`, `tradingsystem/data/bars.py`,
`tradingsystem/data/instrument.py`, `tradingsystem/costs/model.py`, `tradingsystem/brokers/simulated.py`,
`tradingsystem/live/runner.py`, `tradingsystem/strategies/trend.py`; dopočty z `data/raw/dukascopy_m1/*.csv`,
`data/raw/mt4_h1/XAU_1h_data.csv`, `data/raw/mt5_ejtrader/XAUUSD/XAUUSDh1.csv`,
`data/processed/A_H1.parquet`, `A_M30.parquet`, `A_H4.parquet`, `A_D1.parquet`, `B_H1.parquet`, `B_H4.parquet`,
`B_D1.parquet` a `macro_daily.parquet`.*
