# 8. Diagnostika intradenního (session) efektu

Předregistrovaná session strategie C8 byla na DEV záporná už před náklady (kapitola 7). Tato kapitola
vysvětluje proč: rozkládá výnosy XAUUSD podle hodiny dne, ukazuje, z jakého pozorování vznikla revize
C8b (asijská long noha, londýnská short noha), kvantifikuje, jak velké je u takové revize riziko
data-miningu, a uvádí všechny výsledky C8b – DEV, OOS, holdout, pre-sample, náklady, break-even,
long/short, roky, timeframe, zpoždění, perturbace, bootstrap a režimy. Na konci je vysvětleno, proč byla
C8b zamítnuta a co by muselo platit, aby se dala obchodovat.

Výsledky C8b pocházejí z `research/results/s02_C8b.json`, `s04_holdout.json` a `s05_pooled.json`.
Hodinový profil, součty oken, spready podle hodiny, analýza počtu možných oken, rozklad obchodů na body
(bp) a citlivost na násobek nákladů jsou **vlastní dopočty** z `data/processed` přes `research/common.py`
(`stitched('H1')`, `load('A','H1')`, `load('B','H1')`, `run`); u každé tabulky je to uvedeno.

## 8.1 Výchozí hypotéza: proč C8 vypadala ex ante slibně

**Literatura [E]:** Blose, Gondhalekar a Kort (2018) na futures COMEX, londýnském fixingu, zlatých ETF
i těžařích v letech 1985–2012 našli kladné „overnight“ výnosy zlata a záporné výnosy během denní seance
COMEX, ekonomicky významné i po nákladech. Praktici popisují „London bias“: zlato roste v asijských
hodinách a klesá během Londýna a New Yorku [I/U]. Ekonomické zdůvodnění [R]: asijská fyzická a
retailová poptávka proti západní cenotvorbě a prodejům během denní seance.

**Operacionalizace C8** (pevné hodiny, nula laděných parametrů): long od open serverové hodiny 02
(19:00 NY) do open hodiny 15 (08:00 NY), short od 15 do 21 (14:00 NY), katastrofický stop 1 × průměrné
denní rozpětí. Zhruba 500 obchodů ročně dává vysokou statistickou sílu, ale extrémní citlivost na
náklady – scorecard to věděl (skóre nákladů 40/100).

Orientační převod klíčových hodin (serverový čas = New York + 7 h; Londýn je většinu roku NY + 5 h,
v USA a Evropě se letní čas přepíná v rozdílných týdnech, takže 2–3 týdny ročně se vztah liší o hodinu):

| Server | NY | Londýn (obvykle) | Co se v té době děje |
|---|---|---|---|
| 00 | 17:00 | 22:00 | denní přestávka a rollover (swap) |
| 01 | 18:00 | 23:00 | znovuotevření trhu, široký spread |
| 02 | 19:00 | 00:00 | vstup long C8 i C8b; ráno v Tokiu (08:00–09:00 místního času) |
| 09 | 02:00 | 07:00 | konec long a vstup short C8b; začátek londýnského obchodování |
| 12:30 | 05:30 | 10:30 | LBMA ranní aukce (orientačně) |
| 15 | 08:00 | 13:00 | konec long C8 a short C8b, vstup short C8; před otevřením denní seance COMEX (08:20 NY) |
| 17 | 10:00 | 15:00 | LBMA odpolední aukce (orientačně) |
| 21 | 14:00 | 19:00 | konec short C8 (denní seance COMEX končí 13:30 NY) |

*Jak číst:* převod je orientační [I]; strategie pracují výhradně se serverovými hodinami. *Co z toho
plyne:* C8 dlouhá noha (02 → 15) pokrývá celou asijskou seanci **i** londýnské dopoledne; to se ukáže
jako klíčový problém.

## 8.2 Metodika diagnostiky: proč bid open-to-open výnosy

**Definice.** Hodinový výnos baru = ln(open_bid následujícího baru) − ln(open_bid tohoto baru), v bp,
přiřazený serverové hodině baru. Pro každou hodinu a období: průměr, počet pozorování a t-statistika
(průměr / (směrodatná odchylka / √n)). **Denní výnos okna a → b** = ln(open_bid v hodině b) −
ln(open_bid v hodině a) téhož serverového dne (jen dny, kdy existují oba bary). Okno „02 → 09“ tak
odpovídá přesně držení long nohy C8b od open 02 do open 09. Stejnou definici používá graf
`session_profile.png` (`research/s05_summary.py`, funkce `fig_session_profile`).

**Proč bid a ne mid.** V datech B je reálný jen bid; ask je syntetický: bid × (1 + medián *close*
spreadu A pro danou serverovou hodinu, odhadnutý na 2016-09 – 2018-12), a tatáž hodnota se použije na
open, high, low i close baru (`research/prepare_data.py`). Modelový spread proto neodpovídá spreadu na
open baru v hodinách kolem denní přestávky:

| Server | NY | A 2016-09 – 2018 | A 2019–2023 | A 2024–2026 | B model (z close) |
|---|---|---|---|---|---|
| 00 | 17 | 19,07 | — | — | 19,08 |
| 01 | 18 | 5,36 | 6,24 | 6,05 | 2,31 |
| 02 | 19 | 2,30 | 2,35 | 2,15 | 2,04 |
| 03 | 20 | 2,01 | 2,05 | 1,67 | 1,97 |
| 08 | 01 | 1,94 | 2,00 | 1,66 | 1,99 |
| 09 | 02 | 1,95 | 2,08 | 1,62 | 1,89 |
| 14 | 07 | 1,87 | 1,90 | 1,53 | 1,87 |
| 15 | 08 | 1,82 | 1,89 | 1,54 | 1,86 |
| 20 | 13 | 1,91 | 1,89 | 1,53 | 1,96 |
| 21 | 14 | 1,93 | 1,92 | 1,56 | 1,97 |
| 22 | 15 | 1,95 | 1,93 | 1,50 | 2,00 |
| 23 | 16 | 1,98 | 2,00 | 1,47 | 6,21 |

*Jak číst:* mediány spreadu (ask − bid) na open H1 baru v bp ceny; sloupce A jsou reálné kotace
(vlastní dopočet z `A_H1`), poslední sloupec je modelový spread přiřazený barům B
(`data_quality.json`). *Co z toho plyne:* v hodině 23 má B na open baru modelový spread 6,21 bp, ač
reálný je kolem 2 bp; v hodině 01 naopak 2,31 bp proti reálným 5,4–6,2 bp. **Mid (nebo ask) výnosy
v datech B by proto kolem denní přestávky obsahovaly umělé skoky zhruba ±2 bp** – stejně velké jako
zkoumaný efekt. Bid je jediná cena, která je v obou zdrojích skutečně pozorovaná, a proto se diagnostika
dělá na bid výnosech [E].

**Ani bid ale není bez mikrostrukturních vlivů.** Po znovuotevření trhu (hodina 01) je reálný spread
široký a bid je stlačen dolů; jak se spread během první hodiny zužuje, bid mechanicky roste. Ověření na
datech A (vlastní dopočet): hodina 01 v OOS 2019–2023 má bid výnos +2,37 bp (t 4,56), ale mid výnos 0,00
a ask výnos −2,37 bp (t −4,61); v A 2016-09 – 2018 bid +3,53 bp (t 8,66), mid +1,21, ask −1,11. **Kladný
bid výnos v hodině 01 je tedy převážně artefakt normalizace spreadu, ne pohyb ceny.** C8 i C8b proto
vstupují až v 02, kdy je spread téměř normální (2,15–2,35 bp proti zhruba 1,5–2,0 bp ve zbytku dne).
Pro okna C8b je rozdíl bid vs. mid malý: OOS Asie 02 → 09 bid 0,85 / mid 0,67 bp, Londýn 09 → 15
bid −0,12 / mid −0,21 bp.

Další technické poznámky: výnos hodiny 23 v DEV v 97,8 % případů přesahuje denní přestávku nebo víkend
(další bar přichází za ≥ 2 h) a hodiny 22 v 15,5 % případů – tyto hodiny obsahují noční a víkendové
gapy. Hodina 00 má v DEV jen 41 pozorování (sporadické bary v datech A kolem denní přestávky); její
průměr je statisticky bezcenný.

## 8.3 Intradenní profil

![Intradenní profil XAUUSD](research/results/figures/session_profile.png)

*Jak číst:* graf ukazuje **kumulovaný součet průměrných hodinových bid výnosů** podle serverové hodiny
pro tři období (šedě 2004–2009, modře DEV 2010–2018, oranžově OOS 2019–2023). Důležitý je **sklon**
křivky v daném úseku, ne její úroveň: rostoucí úsek znamená, že zlato v těch hodinách v průměru rostlo.
Zelené pole (02–09) je asijská long noha C8b, červené (09–15) londýnská short noha. Počáteční úroveň
modré křivky (≈ 3,2 bp v hodině 00) je dána 41 pozorováními a nemá význam; vzestup v hodině 01 je
z velké části artefakt spreadu (kapitola 8.2).

*Co z toho plyne:*

- **DEV (modře):** zřetelný vzestup 02 → 09 (součet průměrů hodin 02–08: +3,07 bp) a pak pokles
  09 → 15 (hodiny 09–14: −3,92 bp); zbytek dne zhruba ploše. To je vzor „Asie nahoru, Londýn dolů“,
  ze kterého vznikla C8b.
- **2004–2009 (šedě, data B, nepoužita k návrhu):** vzestup v asijských hodinách je přítomen (hodiny
  02–08: +3,57 bp), ale **londýnský pokles chybí** (hodiny 09–14: −0,14 bp); místo toho roste pozdní
  americká seance (hodiny 21–23: +3,15 bp).
- **OOS 2019–2023 (oranžově):** profil je kromě hodiny 01 (artefakt) téměř plochý – hodiny 02–08
  +0,85 bp, hodiny 09–14 +0,11 bp. **Vzor z DEV v OOS nepokračuje.**

## 8.4 Průměrný výnos podle serverové hodiny

Vlastní dopočet (`stitched('H1')`, bid open-to-open, bp). „n DEV“ je počet hodinových pozorování
v DEV; pro ostatní období je n přibližně úměrné délce (PRE ≈ 1 370, OOS ≈ 1 290, HOLDOUT ≈ 688 na
hodinu, hodiny 20–23 o něco méně).

| Server | NY | n DEV | DEV bp | DEV t | PRE bp | PRE t | OOS bp | OOS t | HOLDOUT bp | HOLDOUT t |
|---|---|---|---|---|---|---|---|---|---|---|
| 00 | 17 | 41 | 3,23 | 4,05 | — | — | — | — | — | — |
| 01 | 18 | 2 264 | 1,02 | 3,52 | −0,05 | −0,08 | 2,37 | 4,56 | 5,32 | 5,01 |
| 02 | 19 | 2 299 | 0,48 | 1,78 | 0,10 | 0,16 | 0,94 | 2,68 | 1,16 | 1,41 |
| 03 | 20 | 2 301 | 0,18 | 0,49 | −0,03 | −0,07 | −0,01 | −0,02 | 1,69 | 1,51 |
| 04 | 21 | 2 301 | 0,73 | 1,99 | 0,33 | 0,82 | 0,30 | 0,58 | 0,20 | 0,15 |
| 05 | 22 | 2 302 | 0,39 | 1,37 | 0,60 | 1,38 | −0,03 | −0,08 | −0,54 | −0,61 |
| 06 | 23 | 2 302 | 0,15 | 0,59 | 1,03 | 2,63 | −0,38 | −1,33 | 0,58 | 0,96 |
| 07 | 00 | 2 301 | 0,38 | 1,51 | 1,30 | 2,73 | 0,01 | 0,03 | 0,40 | 0,47 |
| 08 | 01 | 2 308 | 0,76 | 2,42 | 0,24 | 0,37 | 0,01 | 0,02 | −1,19 | −1,22 |
| 09 | 02 | 2 312 | −1,41 | −3,77 | −0,36 | −0,48 | 0,58 | 1,14 | 2,11 | 2,26 |
| 10 | 03 | 2 313 | −0,44 | −0,97 | −0,47 | −0,71 | 0,37 | 0,70 | 0,07 | 0,08 |
| 11 | 04 | 2 314 | −1,12 | −2,94 | −0,52 | −0,86 | −0,10 | −0,22 | 0,11 | 0,11 |
| 12 | 05 | 2 313 | −0,90 | −2,70 | −0,05 | −0,07 | 0,04 | 0,09 | −0,12 | −0,18 |
| 13 | 06 | 2 313 | −0,12 | −0,31 | −0,30 | −0,43 | −0,51 | −1,02 | 1,04 | 1,27 |
| 14 | 07 | 2 313 | 0,07 | 0,16 | 1,57 | 1,23 | −0,28 | −0,58 | 1,19 | 1,25 |
| 15 | 08 | 2 312 | −0,83 | −1,19 | −1,00 | −0,82 | 0,19 | 0,21 | −0,12 | −0,08 |
| 16 | 09 | 2 309 | −0,91 | −1,43 | −1,47 | −1,20 | −0,68 | −0,76 | −1,47 | −1,03 |
| 17 | 10 | 2 310 | 0,89 | 1,39 | 1,77 | 1,66 | 0,84 | 0,91 | 0,47 | 0,28 |
| 18 | 11 | 2 308 | 0,55 | 1,12 | 1,47 | 1,60 | 0,31 | 0,49 | 0,20 | 0,18 |
| 19 | 12 | 2 303 | −0,02 | −0,05 | 0,69 | 0,74 | −0,64 | −1,28 | −0,60 | −0,64 |
| 20 | 13 | 2 280 | −0,38 | −0,87 | −0,29 | −0,41 | 0,37 | 0,81 | −0,03 | −0,04 |
| 21 | 14 | 2 255 | −0,24 | −0,53 | 0,74 | 1,00 | 0,47 | 0,82 | 0,15 | 0,16 |
| 22 | 15 | 2 239 | 0,86 | 2,12 | 1,82 | 3,16 | −0,34 | −0,76 | 1,16 | 1,19 |
| 23 | 16 | 1 896 | 0,72 | 2,00 | 0,59 | 0,86 | −0,17 | −0,33 | −0,59 | −0,54 |

*Jak číst:* každý řádek je jedna serverová hodina (sloupec NY = hodina v New Yorku na začátku baru);
„bp“ = průměrný výnos od open této hodiny do open další, „t“ jeho t-statistika. PRE = 2004-07 – 2009
(data B), HOLDOUT = 2024-01 – 2026-08 (data A). *Co z toho plyne:*

- **V DEV má |t| ≥ 2 (po zaokrouhlení) osm hodin z 24**: 00 (41 pozorování), 01 (artefakt spreadu),
  08 (+0,76), **09 (−1,41, t −3,77)**, 11 (−1,12), 12 (−0,90), 22 (+0,86) a 23 (+0,72; obsahuje noční
  a víkendové gapy). Nejsilnější je pokles v hodině 09 (02:00 NY, začátek londýnského obchodování).
- **Tabulka obsahuje 93 hodinových testů** (24 v DEV, po 23 v dalších obdobích); i bez jakéhokoli
  efektu by se čekaly zhruba čtyři až pět s |t| > 2 [I]. Jednotlivé hodiny proto samy o sobě nic nedokazují – rozhodující je, zda se vzor
  opakuje v nezávislých obdobích.
- **Londýnský pokles se neopakuje:** hodina 09 je v PRE −0,36 (t −0,48), v OOS **+0,58** a v holdoutu
  **+2,11 (t 2,26)** – znaménko se obrátilo. Hodiny 11 a 12 jsou mimo DEV prakticky nulové.
- **Asijské hodiny jsou v DEV i PRE mírně kladné**, ale v OOS se kromě hodiny 02 (+0,94, t 2,68)
  nedrží; v holdoutu jsou smíšené.

## 8.5 Součty oken podle období a zdroje dat

Vlastní dopočet: průměrný denní výnos oken v bp (bid, open → open) a jeho t-statistika přes dny.
„C8 long“ je dlouhá noha předregistrované C8; „C8b hrubě“ je denní hrubý výsledek obou noh C8b
(výnos Asie minus výnos Londýna), tedy součet výsledků dvou obchodů. Řádky s označením zdroje počítají
okna zvlášť na datech A a B.

| Období / zdroj | Dní | Asie 02→09 bp | t | Londýn 09→15 bp | t | NY 15→21 bp | t | C8 long 02→15 bp | t | C8b hrubě bp | t |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PRE 2004-07 – 2009 (B) | 1 364 | 3,53 | 2,64 | −0,31 | −0,15 | −0,51 | −0,19 | 3,15 | 1,34 | 3,92 | 1,54 |
| DEV 2010–2018 | 2 296 | 2,96 | 3,79 | −3,86 | −4,12 | −0,81 | −0,55 | −0,91 | −0,74 | 6,78 | 5,54 |
| 2010–2012 | 758 | 3,35 | 2,32 | −3,00 | −1,64 | 0,61 | 0,21 | 0,31 | 0,14 | 6,29 | 2,62 |
| 2013–2015 | 767 | 3,50 | 2,68 | −8,47 | −4,78 | −2,81 | −1,06 | −4,97 | −2,21 | 11,98 | 5,58 |
| 2016–2018 | 771 | 2,02 | 1,56 | −0,12 | −0,10 | −0,23 | −0,12 | 1,94 | 1,11 | 2,10 | 1,19 |
| OOS 2019–2023 | 1 290 | 0,85 | 0,88 | −0,12 | −0,11 | 0,41 | 0,21 | 0,92 | 0,60 | 1,17 | 0,79 |
| HOLDOUT 2024-01 – 2026-08 (A) | 688 | 2,29 | 0,87 | 4,40 | 1,99 | −1,55 | −0,52 | 6,69 | 2,01 | −2,10 | −0,59 |
| B 2010-01 – 2016-08 | 1 696 | 3,43 | 3,54 | −4,69 | −3,94 | −0,51 | −0,27 | −1,28 | −0,82 | 8,09 | 5,31 |
| B 2016-09 – 2018-12 | 598 | 1,50 | 1,25 | −1,24 | −1,01 | −1,73 | −0,88 | 0,24 | 0,15 | 2,75 | 1,48 |
| A 2016-09 – 2018-12 | 600 | 1,62 | 1,37 | −1,50 | −1,22 | −1,67 | −0,85 | 0,15 | 0,10 | 3,09 | 1,67 |
| B 2019–2023 | 1 287 | 0,72 | 0,73 | 0,01 | 0,01 | 0,40 | 0,21 | 0,71 | 0,44 | 0,74 | 0,47 |
| A 2019–2023 | 1 290 | 0,85 | 0,88 | −0,12 | −0,11 | 0,41 | 0,21 | 0,92 | 0,60 | 1,17 | 0,79 |

*Jak číst:* „Dní“ je počet dní s oběma bary asijského okna (u ostatních oken se liší o jednotky dní).
Výzkumná řada je B do 2016-08 a A od 2016-09, takže řádek „2016–2018“ obsahuje oba zdroje a řádek
„A 2019–2023“ je totožný s OOS. Pre-sample 2004–2009 **nebyl použit k návrhu C8b** – je to jediný
nezávislý test z doby před výběrem oken. *Co z toho plyne:*

- **Z oken v tabulce je asijské jediné se stejným znaménkem ve všech čtyřech obdobích** (PRE +3,53, DEV +2,96,
  OOS +0,85, HOLDOUT +2,29 bp denně) a ve všech třech subperiodách DEV. Významné je ale jen v PRE a DEV
  (t 2,6–3,8); v OOS a holdoutu má t pod 1 [E].
- **Londýnský pokles je jev let 2010–2015**: −3,00 bp (2010–12), **−8,47 bp (2013–15, t −4,78)**, ale
  −0,12 bp v letech 2016–18, −0,31 bp v pre-sample, −0,12 bp v OOS a +4,40 bp (t 1,99) v holdoutu.
  Nejde o stabilní strukturu trhu, ale o vlastnost jednoho období – medvědího trhu 2013–2015 a jeho
  okolí [E/I].
- **Newyorské okno 15 → 21 (krátká noha C8) je všude nevýznamné** (|t| ≤ 1,06).
- **C8b hrubě slábne od roku 2016:** 6,29 → 11,98 → 2,10 bp denně v subperiodách DEV, 1,17 bp v OOS
  a −2,10 bp v holdoutu. Silný DEV výsledek pochází z let 2010–2016 (na datech B: +8,09 bp, t 5,31).
- **Zdroje A a B se v překryvu shodují:** 2016-09 – 2018-12 Asie 1,50 vs. 1,62 bp, Londýn −1,24 vs.
  −1,50 bp, C8b 2,75 vs. 3,09 bp; v letech 2019–2023 0,72 vs. 0,85 a 0,01 vs. −0,12 bp. Data B tedy
  intradenní strukturu reprodukují věrně a silný efekt 2010–2016 není zjevný artefakt zdroje B [I];
  přímo ho ale ověřit nelze, protože data A začínají až 2016-09.
- Hodnoty se řádově shodují s čísly v `DEV_SELECTION.md` (asijské hodiny server 01–09 „+3,3 bp/den,
  t ≈ 4“, Londýn 09–15 „−3,9 bp/den, t ≈ −4,2“, pre-sample asijská noha „+3,5 bp/den, t 2,7“). Drobné
  rozdíly plynou z přesné definice okna (začátek 01 vs. 02) a ceny (bid vs. mid); například okno 01 → 09
  na mid cenách v DEV dává +3,15 bp (t 3,81) a 09 → 15 na mid −3,89 bp (t −4,15) – vlastní dopočet.

## 8.6 Proč předregistrovaná C8 selhala

1. **Dlouhé okno smíchalo dvě opačné fáze.** Long noha C8 (02 → 15) = asijská fáze + londýnské
   dopoledne. V DEV: +2,96 bp (Asie) a −3,86 bp (Londýn) za den, dohromady **−0,91 bp (t −0,74)**.
   Kladná asijská fáze byla londýnským poklesem přesně vyrušena.
2. **Krátká noha neměla co vydělat.** Newyorské okno 15 → 21 bylo v DEV −0,81 bp denně (t −0,55);
   short tedy hrubě získal 0,81 bp – statisticky nula.
3. **Náklady dvou obchodů denně.** Každý obchod zaplatí spread a skluz na vstupu i výstupu; u obchodů
   C8b vychází v průměru 2,2–2,9 bp podle období a nohy (kapitola 8.9) a C8 obchoduje ve srovnatelných
   hodinách se srovnatelnými spready [I]. Při hrubém efektu blízkém nule to vede na
   čistou expectancy −0,018 R a t −2,90 (kapitola 7).
4. **Literatura měřila jinak a jinde.** Blose et al. dělí den na „overnight“ (od konce denní seance
   COMEX do jejího otevření) a „day“ (denní seance) na vzorku 1985–2012. V DEV 2010–2018 byla část jejich
   „overnight“ fáze – londýnské dopoledne – výrazně záporná, a denní seance COMEX klesala jen nepatrně [I].
5. **Ex ante to nebyla absurdní sázka:** v pre-sample 2004–2009 by dlouhé okno C8 vynášelo +3,15 bp
   denně (t 1,34), protože Londýn byl tehdy plochý. Hypotéza se rozpadla právě v období, kde byla
   testována [E].

Oprava chyby exit-and-reverse (kapitola 7.2) na závěru nic nezměnila: C8 byla záporná před opravou
(−0,023 R, 2 362 obchodů) i po ní (−0,018 R, 4 520 obchodů).

## 8.7 Vznik C8b a proč je to riziko data-miningu

**Jak C8b vznikla.** Po prvním DEV screeningu byl spočten hodinový profil DEV (kapitoly 8.3–8.4).
Z něj byla odvozena dvě okna: long 02 → 09 (Asie, vstup až po normalizaci spreadu) a short 09 → 15
(Londýn, výstup před otevřením COMEX); zbytek pravidel (stop 1 × denní rozpětí, exit-and-reverse v 09,
obchodní dny po–pá) zůstal jako u C8. Revize je jako data-driven výslovně označena v kódu
(`tradingsystem/strategies/session.py`, třída `AsiaLondonSession`), v `DEV_SELECTION.md` i v reportu a
byla zapsána **před** jakýmkoli během na OOS (commit 41ce7b8). DEV výsledek C8b je proto z definice
in-sample a nemá důkazní hodnotu.

**Kolik oken šlo zvolit.** `DEV_SELECTION.md` odhaduje „~50 implicitně zvažovaných oken“ a z toho
odvozuje N = 60 testů pro deflated Sharpe (kapitola 9.7). Kombinatorika ukazuje, že prostor možností byl
ve skutečnosti mnohem větší (vlastní dopočet; hranice oken na celých serverových hodinách 01–23, denní
výnosy DEV z bid open cen):

| Typ návrhu | Počet možností | DEV t > 2 (abs.) | DEV t > 3 (abs.) | DEV t > 5 (abs.) | Zvolená volba | Její DEV t | Pořadí volby |
|---|---|---|---|---|---|---|---|
| jedno souvislé okno a → b (směr dle znaménka) | 253 | 91 | 35 | 0 | Asie 02→09 | 3,79 | 12. |
| jedno souvislé okno a → b (směr dle znaménka) | 253 | 91 | 35 | 0 | Londýn 09→15 | −4,12 | 7. |
| dvě navazující nohy a → b long, b → c short (nebo obráceně) | 1 771 | 690 | 315 | 37 | 02→09→15 (C8b) | 5,54 | 16. |

*Jak číst:* „Pořadí“ je pořadí zvolené volby mezi všemi možnostmi seřazenými podle |t| v DEV. Okna se
silně překrývají (sdílejí tytéž silné hodiny 01, 09, 11, 12), takže nejde o nezávislé testy – efektivní
počet nezávislých pokusů je mnohem menší než 253 resp. 1 771, ale zároveň větší než jedna [I]. *Co z toho
plyne:* hodinový profil je „plný“ zdánlivě významných vzorů: v DEV má |t| > 2 přes třetinu všech
jednoduchých oken a 37 dvounohých návrhů má dokonce |t| > 5. Zvolená C8b není vůbec nejsilnější
(nejsilnější návrhy začínají v hodině 01, která je zatížená artefaktem spreadu). Zároveň je třeba být
přesný: t-statistika 5,54 je příliš vysoká na to, aby ji vysvětlil pouhý výběr z šumu – i po hrubé
Bonferroniho korekci na 1 771 návrhů by p-hodnota byla zhruba 0,00005 (u samotného asijského okna
po korekci na 253 oken ≈ 0,04, u londýnského ≈ 0,01; vlastní dopočet z normálního rozdělení) [I].
**Vzor v DEV tedy pravděpodobně skutečně existoval.** Výběr z velkého prostoru ale zaručuje, že jeho
v DEV naměřená velikost je nadhodnocená (efekt „prokletí vítěze“), a hlavně nic neříká o tom, zda vzor
vydrží – to ukazuje až následující tabulka.

**Co se s nejlepšími DEV okny stalo mimo DEV** (deset jednoduchých oken s nejvyšším |t| v DEV a obě
zvolená okna; bp denně):

| Pořadí | Okno (server) | NY čas | DEV bp/den | DEV t | PRE bp/den | PRE t | OOS bp/den | OOS t |
|---|---|---|---|---|---|---|---|---|
| 1 | 09→13 | 02:00→06:00 | −3,78 | −4,89 | −1,44 | −1,07 | 0,90 | 0,95 |
| 2 | 01→09 | 18:00→02:00 | 3,96 | 4,79 | 3,55 | 2,48 | 3,22 | 3,22 |
| 3 | 09→14 | 02:00→07:00 | −3,89 | −4,63 | −1,80 | −1,20 | 0,38 | 0,36 |
| 4 | 09→12 | 02:00→05:00 | −2,88 | −4,23 | −1,39 | −1,21 | 0,86 | 1,03 |
| 5 | 09→17 | 02:00→10:00 | −5,62 | −4,20 | −2,95 | −1,07 | −0,38 | −0,21 |
| 6 | 01→08 | 18:00→01:00 | 3,21 | 4,18 | 3,32 | 2,71 | 3,21 | 3,46 |
| 7 | 09→15 (zvoleno) | 02:00→08:00 | −3,86 | −4,12 | −0,31 | −0,15 | −0,12 | −0,11 |
| 8 | 09→16 | 02:00→09:00 | −4,72 | −4,09 | −1,33 | −0,57 | 0,30 | 0,20 |
| 9 | 01→03 | 18:00→20:00 | 1,50 | 3,97 | 0,01 | 0,01 | 3,32 | 6,18 |
| 10 | 01→06 | 18:00→23:00 | 2,67 | 3,95 | 1,01 | 0,90 | 3,58 | 4,16 |
| 12 | 02→09 (zvoleno) | 19:00→02:00 | 2,96 | 3,79 | 3,53 | 2,64 | 0,85 | 0,88 |

*Jak číst:* PRE (2004–2009) a OOS (2019–2023) jsou mimo období výběru. *Co z toho plyne:*

- **Londýnská okna (začínající v 09) se v OOS rozpadla úplně** – všechna mají v OOS výnos blízký nule
  nebo s obráceným znaménkem.
- **Okna začínající v 01 se v OOS zdánlivě drží** (01 → 03: +3,32 bp, t 6,18), ale to je artefakt
  normalizace spreadu na bid cenách (mid výnos hodiny 01 v OOS je 0,00 bp; kapitola 8.2). Obchodovat se
  na nich nedá: kdo koupí v 01, zaplatí ask při spreadu 5–6 bp.
- **Souhrnně** (vlastní dopočet): 20 jednoduchých oken s nejvyšším DEV |t| mělo v DEV průměrně 3,10 bp
  denně, v OOS ve směru DEV znaménka 0,98 bp. **Bez oken začínajících v 01** (tj. bez artefaktu) mělo
  20 nejlepších DEV oken v DEV 3,29 bp a **v OOS −0,12 bp** – úplná regrese k nule. V pre-sample si
  stejná okna udržela 1,7 bp: vzor tedy existoval v letech 2004–2015 v různé míře, ale po roce 2016
  zmizel. Vzhledem k velikosti DEV t-statistik je pravděpodobnějším výkladem skutečný, ale dočasný
  režim než čistý šum; pro obchodování to ale vede ke stejnému závěru – na vzor, který zmizel, nelze
  stavět [I].

## 8.8 Výsledky C8b ve všech segmentech

| Segment | Obch. | Win % | Exp. R | t | PF | Sharpe | CAGR % | Max DD % | Čistý PnL USD | Hrubá exp. R (×0) |
|---|---|---|---|---|---|---|---|---|---|---|
| PRE 2004-07 – 2009 (B) | 2 757 | 49,7 | −0,0051 | −0,86 | 0,953 | −0,37 | −1,31 | 10,6 | −6 986 | 0,0102 |
| DEV 2010–2018 | 4 569 | 51,1 | 0,0026 | 0,62 | 1,022 | 0,21 | 0,59 | 14,9 | 5 446 | 0,0221 |
| OOS 2019–2023 | 2 580 | 46,3 | −0,0167 | −3,11 | 0,843 | −1,41 | −4,16 | 21,1 | −19 118 | 0,0049 |
| DEV+OOS 2010–2023 | 7 149 | 49,4 | −0,0044 | −1,32 | 0,960 | −0,35 | −1,14 | 31,9 | −14 863 | 0,0159 |
| HOLDOUT 2024-01 – 2026-08 | 1 375 | 46,7 | −0,0150 | −1,86 | 0,868 | −1,25 | −3,73 | 10,3 | −9 624 | −0,0002 |
| Souhrn 2004-07 – 2026-08 | 11 281 | — | −0,0058 | −2,15 | 0,949 | −0,46 | — | — | — | — |

*Jak číst:* baseline náklady; zdroje: segmenty PRE, DEV, OOS a DEV+OOS z `s02_C8b.json`, holdout
z `s04_holdout.json`, souhrn 2004–2026 z `s05_pooled.json`. Sloupec „Hrubá exp. R (×0)“ je vlastní
dopočet bezfrikčním během (pro DEV+OOS a OOS se shoduje s `s02_C8b.json`). **Pozor na měřítko R:**
stop C8b je katastrofický (1 × denní rozpětí ≈ 1,3–1,7 % ceny), takže 1 R odpovídá zhruba 133–166 bp
pohybu a typický obchod má jen ±0,2 R. Expectancy v R proto vypadá řádově menší než u trendových
strategií; srozumitelnější je přepočet na bp v kapitole 8.9. *Co z toho plyne:*

- **Kladná je jen DEV** – období, ze kterého byla okna vybrána – a i tam jen s PF 1,022.
- **Pre-sample 2004–2009** (nezávislý, dříve nepoužitý): hrubě +0,0102 R (t 1,71 v bezfrikčním běhu),
  čistě −0,0051 R. Hrubý efekt tam nesla asijská noha, londýnská nebyla.
- **OOS 2019–2023:** čistě −0,0167 R s **t −3,11** – spolehlivě záporná; hrubě jen +0,0049 R (t 0,92).
- **Holdout 2024–2026:** čistě −0,0150 R, **hrubě −0,0002 R** – efekt zmizel i před náklady.
- **Souhrnně 2004–2026** (11 281 obchodů): −0,0058 R, t −2,15; kladný je 1 ze 4 segmentů.

## 8.9 Náklady a break-even

**Rozklad obchodu na body** (vlastní dopočet z obchodů baseline běhů přes `research/common.py::run`;
hrubý a čistý výsledek, náklad = spread + skluz, vše v bp nominální hodnoty pozice; „Stop“ = medián
vzdálenosti stopu):

| Segment | Noha | Obch. | Hrubě bp/obchod | t hrubě | Náklad bp/obchod | z toho spread bp | Čistě bp/obchod | Stop (medián) bp | Stop-outy % |
|---|---|---|---|---|---|---|---|---|---|
| PRE 2004–09 | long 02→09 | 1 366 | 3,57 | 2,66 | 2,57 | 1,96 | 0,99 | 166 | 0,6 |
| PRE 2004–09 | short 09→15 | 1 391 | 0,23 | 0,11 | 2,48 | 1,88 | −2,26 | 165 | 1,3 |
| PRE 2004–09 | obě nohy | 2 757 | 1,88 | 1,55 | 2,53 | 1,92 | −0,65 | 166 | 0,9 |
| DEV 2010–18 | long 02→09 | 2 262 | 2,70 | 3,39 | 2,62 | 2,01 | 0,09 | 133 | 0,6 |
| DEV 2010–18 | short 09→15 | 2 307 | 3,87 | 4,11 | 2,49 | 1,88 | 1,39 | 133 | 0,8 |
| DEV 2010–18 | obě nohy | 4 569 | 3,29 | 5,32 | 2,55 | 1,95 | 0,74 | 133 | 0,7 |
| OOS 2019–23 | long 02→09 | 1 290 | 0,91 | 0,97 | 2,92 | 2,32 | −2,01 | 134 | 0,5 |
| OOS 2019–23 | short 09→15 | 1 290 | −0,23 | −0,20 | 2,71 | 2,11 | −2,94 | 134 | 0,5 |
| OOS 2019–23 | obě nohy | 2 580 | 0,34 | 0,45 | 2,82 | 2,21 | −2,48 | 134 | 0,5 |
| HOLDOUT 2024–26 | long 02→09 | 688 | 2,70 | 1,09 | 2,57 | 1,96 | 0,12 | 155 | 1,5 |
| HOLDOUT 2024–26 | short 09→15 | 687 | −3,38 | −1,66 | 2,23 | 1,63 | −5,61 | 155 | 0,1 |
| HOLDOUT 2024–26 | obě nohy | 1 375 | −0,34 | −0,21 | 2,40 | 1,80 | −2,74 | 155 | 0,8 |

*Jak číst:* hrubý výsledek je ocenění téhož obchodu bez spreadu a skluzu; t hrubě je t-statistika
hrubých bp přes obchody. Náklad ≈ celý spread (vstup za ask, výstup za bid nebo naopak) + 2 × 0,3 bp
skluzu. Stop-loss zasáhne méně než 1,5 % obchodů – téměř všechny končí časovým výstupem. *Co z toho
plyne:*

- **Break-even podmínka je jednoduchá: hrubý pohyb musí v průměru překonat ≈ 2,4–2,8 bp na obchod**
  (průměrný náklad obou noh v jednotlivých obdobích).
  V DEV ji obě nohy dohromady splnily jen těsně (3,29 vs. 2,55 bp), v pre-sample, OOS ani holdoutu ne.
- **Jediná noha, která byla po nákladech nezáporná ve třech ze čtyř období, je asijský long** (PRE
  +0,99, DEV +0,09, HOLDOUT +0,12 bp; OOS −2,01 bp) – vždy ale jen o desetiny bodu, což je hluboko
  v šumu.
- **Londýnský short byl ziskový jen v DEV** (+1,39 bp čistě); v pre-sample, OOS i holdoutu ztrácel,
  v holdoutu výrazně (−5,61 bp na obchod).

**Citlivost na násobek nákladů a break-even** (vlastní dopočet: stejný běh s násobkem spreadu, skluzu
a swapové přirážky ×0 až ×1; řádky ×1,5 a ×2 pro OOS a DEV+OOS z `s02_C8b.json`, pro holdout
z `s04_holdout.json`; DEV při ×1,5 a ×2 nebyl počítán):

| Násobek nákladů | DEV exp. R | DEV PF | OOS exp. R | OOS PF | DEV+OOS exp. R | DEV+OOS PF | HOLDOUT exp. R | HOLDOUT PF |
|---|---|---|---|---|---|---|---|---|
| ×0,00 | 0,0221 | 1,227 | 0,0049 | 1,050 | 0,0159 | 1,151 | −0,0002 | 0,993 |
| ×0,25 | 0,0172 | 1,171 | −0,0005 | 0,994 | 0,0108 | 1,099 | −0,0039 | 0,959 |
| ×0,50 | 0,0123 | 1,118 | −0,0059 | 0,941 | 0,0057 | 1,050 | −0,0076 | 0,933 |
| ×0,60 | 0,0103 | 1,098 | −0,0081 | 0,918 | 0,0037 | 1,031 | −0,0091 | 0,920 |
| ×0,70 | 0,0084 | 1,078 | −0,0102 | 0,900 | 0,0017 | 1,012 | −0,0106 | 0,909 |
| ×0,75 | 0,0074 | 1,069 | −0,0113 | 0,891 | 0,0007 | 1,004 | −0,0113 | 0,901 |
| ×0,80 | 0,0065 | 1,058 | −0,0124 | 0,882 | −0,0003 | 0,995 | −0,0121 | 0,895 |
| ×0,90 | 0,0045 | 1,040 | −0,0145 | 0,863 | −0,0024 | 0,977 | −0,0136 | 0,881 |
| ×1,00 | 0,0026 | 1,022 | −0,0167 | 0,843 | −0,0044 | 0,960 | −0,0150 | 0,868 |
| ×1,50 | — | — | −0,0273 | 0,756 | −0,0144 | 0,880 | −0,0226 | 0,819 |
| ×2,00 | — | — | −0,0380 | 0,677 | −0,0244 | 0,807 | −0,0299 | 0,766 |

*Jak číst:* ×1,00 je baseline (shoduje se s `s02_C8b.json` a `s04_holdout.json`, což potvrzuje
reprodukovatelnost dopočtu); ×0 je bezfrikční běh. *Co z toho plyne* – **break-even násobek nákladů**
(lineární interpolace mezi sousedními řádky, vlastní dopočet):

- **DEV+OOS 2010–2023: ≈ ×0,78** baseline nákladů (mezi ×0,75 a ×0,80);
- **OOS 2019–2023: ≈ ×0,23** – náklady by musely klesnout zhruba na čtvrtinu;
- **DEV: nad ×1,0** (lineární extrapolace ≈ ×1,13) – to je období, ze kterého byla okna vybrána;
- **HOLDOUT: neexistuje** – už bezfrikční běh je záporný.

V bodech je obraz ještě přísnější: v OOS pokryl hrubý výsledek 0,34 bp jen 12 % průměrného nákladu
2,82 bp. Obě míry se liší váhováním (bp je prostý průměr přes obchody, R normalizuje šířkou stopu a
equity se v čase mění), řádově ale vycházejí stejně: **v OOS 2019–2023 by C8b potřebovala náklady na
desetině až čtvrtině retail úrovně a v holdoutu 2024–2026 by nepomohly ani nulové náklady**.

**Předem deklarované nákladové scénáře** (`s02_C8b.json`):

| Scénář | DEV+OOS exp. R | PF | Sharpe | Čistý PnL | Náklady USD | OOS exp. R | PF | Sharpe | Čistý PnL |
|---|---|---|---|---|---|---|---|---|---|
| ×0 (bez nákladů) | 0,0159 | 1,151 | 1,26 | 73 546 | 0 | 0,0049 | 1,050 | 0,40 | 6 255 |
| ×1,0 baseline | −0,0044 | 0,960 | −0,35 | −14 863 | 73 471 | −0,0167 | 0,843 | −1,41 | −19 118 |
| ×1,5 | −0,0144 | 0,880 | −1,15 | −39 795 | 92 575 | −0,0273 | 0,756 | −2,30 | −29 143 |
| ×2,0 | −0,0244 | 0,807 | −1,96 | −57 437 | 104 834 | −0,0380 | 0,677 | −3,21 | −38 053 |
| ECN: spread a skluz ×0,5 + 3,5 USD/lot/strana | 0,0019 | 1,016 | 0,16 | 6 244 | 56 438 | −0,0092 | 0,909 | −0,79 | −11 219 |

*Jak číst:* „Náklady USD“ = spread + skluz + komise v DEV+OOS (swap je u C8b zanedbatelný, −4 USD za
14 let). V holdoutu: ×1 −0,015 R, ×1,5 −0,023 R, ×2 −0,030 R. *Co z toho plyne:* **hrubý Sharpe 1,26
za 2010–2023 je skutečná hrubá anomálie**, ale baseline náklady (73,5 tis. USD) jsou vyšší než hrubý
zisk téhož baseline běhu (58,6 tis. USD) a prakticky stejně velké jako celý zisk bezfrikčního běhu
(73,5 tis. USD). I optimistický ECN scénář je v OOS záporný. Brána 3 (DEV+OOS
při ×1,5 > 0) jasně selhala.

## 8.10 Long/short, roky, timeframe, zpoždění, perturbace, bootstrap, režimy

**Long vs. short** (samostatné běhy; DEV, OOS a DEV+OOS z `s02_C8b.json`, holdout z `s04_holdout.json`):

| Strana | Segment | Obch. | Win % | Exp. R | t | PF | Sharpe | Čistý výnos % |
|---|---|---|---|---|---|---|---|---|
| long | DEV 2010–18 | 2 263 | 49,9 | −0,0024 | −0,44 | 0,973 | −0,15 | −2,8 |
| long | OOS 2019–23 | 1 290 | 47,2 | −0,0114 | −1,64 | 0,882 | −0,75 | −7,0 |
| long | DEV+OOS | 3 553 | 48,9 | −0,0056 | −1,32 | 0,941 | −0,35 | −9,4 |
| long | HOLDOUT 2024–26 | 688 | 50,9 | 0,0083 | 0,70 | 1,070 | 0,40 | 2,6 |
| short | DEV 2010–18 | 2 307 | 52,2 | 0,0073 | 1,15 | 1,062 | 0,39 | 8,3 |
| short | OOS 2019–23 | 1 290 | 45,4 | −0,0219 | −2,70 | 0,811 | −1,20 | −13,1 |
| short | DEV+OOS | 3 597 | 49,8 | −0,0032 | −0,64 | 0,972 | −0,16 | −5,9 |
| short | HOLDOUT 2024–26 | 687 | 42,5 | −0,0384 | −3,54 | 0,689 | −2,14 | −11,6 |

*Jak číst:* „Čistý výnos %“ je čistý PnL v % počátečních 100 000 USD. *Co z toho plyne:* po nákladech
byla v DEV kladná jen londýnská short noha a právě ta se v OOS (t −2,70) a holdoutu (t −3,54) obrátila
nejvýrazněji. Asijský long je v holdoutu mírně kladný (PF 1,070, t 0,70) – v býčím trhu 2024–2026 zlato
rostlo i v Asii – ale za 2004–2026 souhrnně je long −0,001 R a short −0,010 R (`s05_pooled.json`).

**Výsledky po letech** (`s02_C8b.json`, DEV+OOS, rok podle výstupu z obchodu):

| Rok | Obch. | Exp. R | Čistý PnL | Long PnL | Short PnL |
|---|---|---|---|---|---|
| 2010 | 498 | 0,0034 | 798 | 1 017 | −219 |
| 2011 | 496 | −0,0015 | −344 | 318 | −662 |
| 2012 | 498 | 0,0124 | 3 097 | −38 | 3 134 |
| 2013 | 514 | 0,0324 | 8 760 | −1 477 | 10 238 |
| 2014 | 511 | −0,0074 | −2 106 | −965 | −1 141 |
| 2015 | 509 | 0,0327 | 9 318 | 2 583 | 6 735 |
| 2016 | 514 | 0,0059 | 1 670 | 3 859 | −2 189 |
| 2017 | 513 | −0,0200 | −6 073 | −2 437 | −3 636 |
| 2018 | 516 | −0,0341 | −9 675 | −5 975 | −3 700 |
| 2019 | 516 | −0,0205 | −5 419 | −790 | −4 629 |
| 2020 | 518 | −0,0426 | −10 340 | −3 733 | −6 606 |
| 2021 | 516 | 0,0160 | 3 604 | 2 332 | 1 272 |
| 2022 | 516 | −0,0168 | −3 914 | −3 397 | −517 |
| 2023 | 514 | −0,0192 | −4 240 | −1 205 | −3 035 |

| Blok | Obch. | Exp. R | PF | Čistý PnL |
|---|---|---|---|---|
| 2010–2012 | 1 492 | 0,0048 | 1,049 | 3 551 |
| 2013–2015 | 1 534 | 0,0192 | 1,212 | 15 972 |
| 2016–2018 | 1 543 | −0,0161 | 0,857 | −14 078 |
| 2019–2021 | 1 550 | −0,0158 | 0,849 | −12 155 |
| 2022–2023 | 1 030 | −0,0180 | 0,829 | −8 154 |

*Jak číst:* hodnoty v USD při riziku 0,5 % na obchod. *Co z toho plyne:* **celý kladný přínos C8b
vznikl v letech 2012, 2013 a 2015** (dohromady 21 175 USD, vlastní součet), v DEV z velké části krátkou
nohou v medvědím trhu. Od roku 2016 je záporný každý blok (2016–2018, 2019–2021, 2022–2023) a ze sedmi let 2017–2023 byl
kladný jediný (2021). Brána 6 (žádný rok > 50 % zisku) je nesplnitelná, protože čistý zisk DEV+OOS je
záporný (`max_year_share` = nekonečno).

**Timeframe, posun hranic a zpoždění vstupu** (`s02_C8b.json`):

| Test | Obch. | Exp. R | t | PF | Sharpe | Max DD % |
|---|---|---|---|---|---|---|
| H1 baseline DEV+OOS (stitched) | 7 149 | −0,0044 | −1,32 | 0,960 | −0,35 | 31,9 |
| zpoždění +1 H1 bar | 7 147 | −0,0105 | −2,78 | 0,919 | −0,75 | 39,0 |
| zpoždění +1 bar a skluz ×3 | 7 147 | −0,0199 | −5,25 | 0,856 | −1,41 | 53,7 |
| M30 (A 2016-09 – 2023) | 3 757 | −0,0165 | −3,64 | 0,849 | −1,30 | 31,7 |
| M30, hranice −30 min (A) | 3 758 | −0,0196 | −4,48 | 0,823 | −1,60 | 34,9 |
| M30, hranice +30 min (A) | 3 759 | −0,0201 | −4,16 | 0,829 | −1,52 | 35,0 |
| H1 (A 2016-09 – 2023) | 3 759 | −0,0165 | −3,65 | 0,849 | −1,30 | 31,6 |

*Jak číst:* řádky M30 a „H1 (A …)“ běží jen na datech A (2016-09 – 2023-12), proto mají méně obchodů
a nejsou přímo srovnatelné s prvním řádkem. *Co z toho plyne:* jemnější báze M30 dává totéž co H1
(−0,0165 R) – výsledek tedy není artefakt hodinových barů; posun hranic o ±30 minut výsledek zhorší,
takže kolem zvolených hodin neexistuje kladné „plató“. Zpoždění vstupu o hodinu zhorší expectancy více
než dvojnásobně: session strategie je na přesném načasování závislá, trendové strategie ne (kapitola 13
`REPORT.md`).

**Perturbace oken a stopu** (`grid_C8b.csv`, DEV+OOS, předem deklarovaná mřížka z `DEV_SELECTION.md`):

| Varianta | Obch. | Exp. R | PF | Sharpe | Max DD % |
|---|---|---|---|---|---|
| long 01→08, short 09→15 | 3 638 | −0,0034 | 0,970 | −0,17 | 21,5 |
| long 01→09, short 09→15 | 3 638 | −0,0033 | 0,971 | −0,17 | 21,4 |
| long 01→10, short 09→15 | 3 597 | −0,0040 | 0,965 | −0,20 | 22,3 |
| long 02→08, short 09→15 | 7 115 | −0,0052 | 0,951 | −0,43 | 29,3 |
| long 02→09, short 09→15 (C8b) | 7 149 | −0,0044 | 0,960 | −0,35 | 31,9 |
| long 02→10, short 09→15 | 3 618 | −0,0100 | 0,909 | −0,56 | 21,4 |
| long 03→08, short 09→15 | 7 151 | −0,0064 | 0,939 | −0,54 | 31,2 |
| long 03→09, short 09→15 | 7 183 | −0,0055 | 0,951 | −0,44 | 33,2 |
| long 03→10, short 09→15 | 3 616 | −0,0135 | 0,873 | −0,79 | 24,1 |
| long 02→09, short 08→14 | 3 608 | −0,0041 | 0,956 | −0,26 | 16,5 |
| long 02→09, short 08→15 | 3 608 | −0,0043 | 0,955 | −0,27 | 16,5 |
| long 02→09, short 08→16 | 3 608 | −0,0031 | 0,966 | −0,20 | 16,2 |
| long 02→09, short 09→14 | 7 149 | −0,0048 | 0,954 | −0,41 | 33,8 |
| long 02→09, short 09→16 | 7 148 | −0,0037 | 0,971 | −0,25 | 33,2 |
| long 02→09, short 10→14 | 7 118 | −0,0072 | 0,927 | −0,66 | 32,9 |
| long 02→09, short 10→15 | 7 118 | −0,0066 | 0,937 | −0,56 | 30,5 |
| long 02→09, short 10→16 | 7 116 | −0,0060 | 0,951 | −0,43 | 32,6 |
| stop 0,75 × denní rozpětí | 7 149 | −0,0067 | 0,955 | −0,41 | 40,9 |
| stop 1,25 × denní rozpětí | 7 149 | −0,0034 | 0,961 | −0,34 | 26,4 |
| stop 1,50 × denní rozpětí | 7 149 | −0,0027 | 0,963 | −0,32 | 21,8 |

*Jak číst:* mřížka má 9 variant long okna (při short 09 → 15) a 9 variant short okna (při long
02 → 09) plus čtyři hodnoty stopu „one-at-a-time“ (výchozí 1,0 je řádek C8b). *Co z toho plyne:*
**všech 18 variant oken i všechny stopy jsou záporné** (podíl kladných 0 %, Sharpe p10 / medián / p90
−0,59 / −0,38 / −0,19, PBO 0,68). Pozor na technický detail (vlastní interpretace počtů obchodů [I]):
varianty s počtem ≈ 3 600 obchodů obchodují fakticky jen jednu nohu. Vstup v 01 se téměř nikdy nespustí,
protože signál se generuje na baru před cílovou hodinou a bar 00 v datech skoro neexistuje; a když se
okna překrývají (long do 10 a short od 09, nebo short od 08 a long do 09), otevřená pozice zablokuje
druhou nohu. Mřížka tedy testuje méně odlišných návrhů, než kolik má bodů – ani jeden ale není kladný.

**Bootstrap a deflated Sharpe** (`s02_C8b.json`, DEV+OOS): trade bootstrap (10 000×) dává
P(expectancy > 0) = **10,4 %**, expectancy p05 / p50 / p95 = −0,0099 / −0,0043 / 0,0011 R, max DD
p50 20,3 % a p95 32,7 %. Blokový bootstrap denních výnosů (bloky 20 dní, 5 000×): Sharpe −0,84 /
−0,36 / 0,11, P(Sharpe > 0) = 11,1 %. Deflated Sharpe s N = 60: Sharpe DEV+OOS −0,35 proti
prahu SR0 1,46 → PSR(> 0) 0,09, **DSR 0,00**; jen OOS: Sharpe −1,40, PSR 0,00, DSR 0,00.

**Režimy** (ex-ante štítky ke dni vstupu, DEV+OOS, `s02_C8b.json`):

| Režim | Stav | Obch. | Exp. R | PF | Long exp. R | Short exp. R | Denní Sharpe |
|---|---|---|---|---|---|---|---|
| trend | range | 4 902 | −0,0007 | 0,994 | −0,0005 | −0,0010 | −0,06 |
| trend | trend | 2 247 | −0,0123 | 0,899 | −0,0166 | −0,0080 | −0,92 |
| volatilita | vysoká | 3 237 | −0,0014 | 0,989 | −0,0027 | −0,0001 | −0,13 |
| volatilita | nízká | 3 912 | −0,0068 | 0,937 | −0,0079 | −0,0057 | −0,53 |
| USD (60 dní) | silný | 4 057 | −0,0019 | 0,989 | −0,0035 | −0,0003 | −0,15 |
| USD (60 dní) | slabý | 3 092 | −0,0076 | 0,924 | −0,0083 | −0,0070 | −0,63 |
| výnosy 10Y (60 dní) | klesající | 3 570 | −0,0102 | 0,908 | −0,0061 | −0,0142 | −0,80 |
| výnosy 10Y (60 dní) | rostoucí | 3 579 | 0,0014 | 1,019 | −0,0050 | 0,0078 | 0,11 |
| krize | VIX > 25 | 1 062 | −0,0186 | 0,851 | −0,0195 | −0,0177 | −1,37 |
| krize | normál | 6 087 | −0,0019 | 0,981 | −0,0031 | −0,0007 | −0,15 |

*Jak číst:* definice režimů jsou v kapitole 4 (data k předchozímu dni). *Co z toho plyne:* C8b nemá
režim, ve kterém by po nákladech přesvědčivě fungovala; jediný kladný stav (rostoucí výnosy 10Y,
+0,0014 R, PF 1,019) je v mezích šumu a nebyl předem hypotézou. Nejhůř vychází krize (VIX > 25) a
trendující trh. Výběr režimu ex post by byl další vrstva data-miningu [I].

**Předregistrované brány** (`s02_C8b.json`): 1 NE, 2 NE, 3 NE, 4 NE (0 % sousedů kladných),
5 neaplikovatelné (C8b nemá parametry pro walk-forward), 6 NE, 7 NE (10,4 %). **Celkově NE.**

## 8.11 Proč je C8b zamítnuta

1. **Funguje jen před náklady a jen v období, ze kterého byla odvozena.** Hrubý efekt v DEV (3,29 bp
   na obchod, t 5,32) je in-sample; v OOS klesl na 0,34 bp (t 0,45) a v holdoutu na −0,34 bp. Náklady
   ≈ 2,4–2,8 bp na obchod jsou v OOS zhruba 8× větší než hrubý efekt a v holdoutu je hrubý efekt
   dokonce záporný.
2. **Efekt slábne od roku 2016 a v holdoutu má londýnská noha obrácené znaménko.** Londýnský pokles
   je fenomén let 2010–2015; asijský růst má stabilní znaménko, ale po roce 2016 je pod úrovní nákladů.
3. **Riziko data-miningu je vysoké a doložené**: okna byla vybrána z prostoru stovek až tisíců možností
   a nejlepší DEV okna (bez artefaktu hodiny 01) v OOS regredovala na nulu.
4. **Žádná robustnost**: 0 % variant mřížky kladných, posun hranic o 30 minut zhoršuje, zpoždění
   o hodinu zdvojnásobí ztrátu, bootstrap P(exp > 0) 10 %, DSR 0,00.
5. **Zadání vyžaduje edge, který přežije realistické náklady** (×1,5 a ×2); C8b nepřežije ani ×1,0.

Zamítnutí C8b zároveň znamená, že **slot pro ne-trendový, komplementární zdroj edge zůstal neobsazený**
– C8b byla jediným kandidátem, který mohl diverzifikovat trendovou rodinu (kapitola 9).

## 8.12 Co by bylo potřeba, aby se session efekt dal obchodovat

Následující body jsou podmínky pro případný **nový** výzkum, ne doporučení k obchodování [I]:

1. **Výrazně nižší náklady.** Podle break-even analýzy by v OOS bylo nutné snížit náklady na zhruba
   10–25 % retail úrovně, tj. na desetiny bodu na obchod. To odpovídá spíše institucionální exekuci
   (futures s minimálním krokem ceny, pasivní limitní příkazy, nízké komise) než CFD účtu se spreadem
   ≈ 2 bp [I]. Pasivní exekuce ale přináší riziko nevyplnění, které by se muselo samostatně modelovat [U].
2. **Doklad stability na nových datech.** Všechna historická data 2004–2026 už byla viděna; jakákoli
   další úprava oken by byla nový data-mining. Poctivý test by vyžadoval předregistrovat pevná okna
   (např. jen asijský long 02 → 09, jediná noha se stabilním znaménkem) a vyhodnotit je výhradně na
   datech po 2026-08.
3. **Dostatečný vzorek.** Denní směrodatná odchylka asijského okna je v OOS ≈ 35 bp a v holdoutu ≈ 69 bp
   (vlastní dopočet z tabulky 8.5). K odlišení hrubého efektu velikosti jednoho nákladu (≈ 2,6 bp denně)
   od nuly s t ≈ 2 je třeba zhruba (2 × 34,7 / 2,6)² ≈ 712 obchodních dní, tedy necelé 3 roky při
   volatilitě OOS; při volatilitě holdoutu přibližně čtyřnásobek. Prokázat, že efekt je **větší** než
   náklady, by trvalo ještě déle [I].
4. **Ekonomický mechanismus testovatelný mimo cenu.** Pokud je příčinou asijská fyzická poptávka [R],
   měl by efekt souviset s ukazateli, jako je prémie Šanghajské burzy zlata nebo dovozy do Indie a Číny;
   takové podmíněné testy zde nebyly provedeny a data pro ně nejsou k dispozici [U].
5. **Odolnost vůči načasování.** Obchodovatelný efekt by měl přežít posun hranic o ±30 minut a zpoždění
   vstupu; C8b nepřežila ani jedno.

> **Závěr:** Předregistrovaná C8 selhala, protože její dlouhé okno smíchalo rostoucí asijskou a klesající
> londýnskou fázi, které se v DEV vyrušily, a krátká noha neměla co vydělat. Revize C8b tyto fáze
> oddělila a v DEV ukázala silnou hrubou anomálii (hrubý Sharpe 1,72, t 5,26), ta však byla vybrána
> z prostoru stovek možných oken, londýnská složka byla vlastností let 2010–2015 a od roku 2016 efekt
> nepokrývá ani retail náklady (OOS hrubě 0,34 bp proti nákladu 2,82 bp na obchod, holdout hrubě
> záporný). C8b je zamítnuta; jediným zbytkem, který by stál za nový, předregistrovaný test na budoucích
> datech, je slabá asijská long noha – a i ta jen při nákladech zlomkových proti retail úrovni.

*Zdrojové soubory: `research/results/figures/session_profile.png` a `research/s05_summary.py`
(`fig_session_profile`); `research/results/s02_C8b.json` a `.md` (segmenty, long/short, náklady,
zpoždění, timeframe, perturbace, bootstrap, režimy, roky, bloky, DSR, brány);
`research/results/grid_C8b.csv`; `research/results/s04_holdout.json` a `.md` (holdout C8b ×1, ×1,5, ×2,
long-only, short-only); `research/results/s05_pooled.json` (souhrn 2004–2026);
`research/results/s01_dev_screen.json` (C8 a C8b v DEV); `research/DEV_SELECTION.md` (vznik C8b,
odhad počtu oken, mřížka); `research/PROTOCOL.md` (C8); `research/prepare_data.py` a
`research/results/data_quality.json` (syntetický ask v datech B, modelový spread);
`tradingsystem/strategies/session.py` (`SessionDrift`, `AsiaLondonSession`); `REPORT.md` (kap. 3.3,
13, 14, 17); vlastní dopočty z `data/processed` přes `research/common.py`: hodinový profil a jeho
t-statistiky (`stitched('H1')`, bid open-to-open), denní součty oken pro subperiody a zdroje A/B
(`load('A','H1')`, `load('B','H1')`), bid vs. mid vs. ask v hodině 01, mediány spreadu podle hodiny,
kombinatorika oken a jejich OOS/PRE výsledky, rozklad obchodů C8b na bp (`run` s baseline a bezfrikčními
náklady), citlivost na násobek nákladů ×0 – ×1 a interpolace break-even, směrodatné odchylky oken
pro odhad potřebného vzorku.*
