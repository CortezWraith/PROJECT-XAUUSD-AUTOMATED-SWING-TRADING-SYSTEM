# 14. Hodnocení rizika přeučení (overfitting)

## 14.1 Co tu znamená „přeučení“

Přeučení je situace, kdy backtest vypadá dobře proto, že pravidla nebo jejich výběr byly
(i nevědomky) přizpůsobeny náhodnému šumu v historii. Takový „edge“ v budoucnu zmizí. Rizika
hodnotíme po zdrojích a pro každou strategii zvlášť.

## 14.2 Matice zdrojů rizika

| Zdroj rizika | C3 EMA | C2 Donchian | C5 Squeeze | C9 USD filtr | C8b Session |
|---|---|---|---|---|---|
| Ladění parametrů | nízké | nízké | střední | střední | vysoké |
| Výběr režimu / období | střední | střední | vysoké | vysoké | vysoké |
| Survivorship | nízké | nízké | nízké | nízké | nízké |
| Data-snooping (výběr z kandidátů) | vysoké | vysoké | vysoké | vysoké | vysoké |
| Look-ahead | nízké | nízké | nízké | nízké | nízké |
| Nerealistické fills | nízké | nízké | nízké | nízké | střední |
| Malý vzorek | vysoké | vysoké | vysoké | vysoké | nízké |
| Jedno výjimečné období | střední | střední | vysoké | vysoké | vysoké |

Odůvodnění hlavních hodnocení:

- **Ladění parametrů.** C3 a C2 používají literaturní defaulty (EMA 20/100, Turtle 55/20, 2–3 ATR),
  nic nebylo optimalizováno. Perturbace ukazuje plató: 90 % (C3) a 96 % (C2) ze 125 sousedních
  kombinací má kladnou expectancy. C5 má 8 parametrů a walk-forward ukázal, že její výsledek v čase
  citlivě závisí na volbě bb_n/squeeze_pct (WF +30,9 % vs. default). C8b má okna obchodování vybraná
  z hodinového profilu DEV, tedy přímo z dat.
- **Výběr období.** U C3 přináší největší rok (2023) 70 % čistého zisku za DEV+OOS, u C2 rok 2020
  68 %, u C5 rok 2016 74 %. U C5 vznikl celý zisk 2013–2017, období 2018–2023 bylo záporné.
- **Data-snooping.** Trojice C3/C5/C9 byla vybrána po DEV screenu deseti kandidátů jako ta, která
  prošla bránou 1. To je selekce a OOS je pro tyto strategie jediným čistým testem: C3 a C2 v něm
  zůstaly kladné, C5 a C9 ne.
- **Look-ahead.** Indikátory jsou kauzální (unit test přepočítává na zkrácené historii), signály se
  počítají na uzavřeném baru, makro data jsou zpožděna o 1 den, plnění je na dalším baru.
- **Fills.** Exekuce na reálném bid/ask, gapy na horší ceně, při zásahu SL i TP v jednom baru se
  předpokládá nejdřív SL. U C8b (6h obchody kolem znovuotevření trhu) je citlivost na skutečné
  spready nejvyšší.

## 14.3 Formální statistiky přeučení

| Strategie | PBO (CSCV) | PSR (DEV+OOS) | DSR, N=60 kandidátů | DSR, N=125 mřížka | Kladní sousedé |
|---|---|---|---|---|---|
| C3 | 0,47 | 0,83 | 0,00 | 0,39 | 90 % |
| C2 | 0,70 | 0,80 | 0,00 | 0,53 | 96 % |
| C5 | 0,24 | 0,74 | 0,00 | 0,30 | 100 % |
| C9 | 0,55 | 0,82 | 0,00 | 0,55 | 100 % |
| C8b | 0,68 | 0,09 | 0,00 | — | 0 % |

Jak číst:

- **PBO** (pravděpodobnost přeučení výběru parametrů) říká, jak často je konfigurace nejlepší
  v tréninkové polovině let horší než medián v testovací polovině. Vysoké PBO u C2 (0,70) zde
  neznamená klasické přeučení: všechny konfigurace mřížky jsou si podobné, takže „nejlepší v tréninku“
  je v testu náhodně pod mediánem. Volba parametrů nemá hodnotu a literaturní default je stejně dobrý.
- **PSR** je pravděpodobnost, že skutečný Sharpe je větší než nula, bez korekce na počet testů.
  Hodnoty 0,74–0,83 nedosahují obvyklých 0,95.
- **DSR** (deflated Sharpe) koriguje na počet vyzkoušených variant. V konzervativní variantě
  (rozptyl Sharpe přes 10 kandidátů DEV screenu, N = 60) je práh SR0 = 1,46. To je mnohem víc než
  pozorovaných 0,17–0,25, proto DSR = 0. V mírnější variantě (rozptyl v rámci mřížky, N = 125) je
  DSR 0,30–0,55. Ani jedna varianta se neblíží 0,95.

## 14.4 Stupně volnosti výzkumníka

| Rozhodnutí | Počet zvažovaných variant |
|---|---|
| Kandidáti v DEV screenu | 10 + revize C8b |
| Okna session strategie (implicitně) | desítky až stovky (viz kapitola 8) |
| Body perturbačních mřížek | 125 na C3, C2, C5, C9; 18 + 4 u C8b |
| Timeframy | 4–5 na strategii |
| Walk-forward mřížky | 9 na strategii |
| Rozhodnutí po DEV (náhrada kandidátů) | 1 (pravidlo zapsané před OOS) |

Opatření, která riziko snižují: předregistrace protokolu (commit `6a151db`), rozhodnutí po DEV
zapsané před OOS (`41ce7b8`), zmrazení specifikace před holdoutem (`cfe78c3`), kauzální indikátory,
konzervativní simulace a úplný výčet odchylek (kapitola 4).

Zbytkové riziko, které opatření neodstraní: výzkumník znal obecný vývoj trhu zlata do roku 2026,
včetně býčího trhu 2024–2026. Zmrazení chrání pravidla, ale ne volbu rodiny strategií. Preference
trendu proto mohla být ovlivněna vědomím, jak trh dopadl (hindsight bias) [U].

## 14.5 Závěrečné skóre rizika přeučení (0 = žádné, 100 = jisté)

| Strategie | Skóre | Hlavní důvod |
|---|---|---|
| C3 EMA trend | 35 | literaturní parametry, plató, kladná ve 4 segmentech; ale výběr po DEV a malý vzorek |
| C2 Donchian | 35 | totéž; navíc předregistrovaná, takže selekce ji netýká |
| C5 Squeeze | 50 | 8 parametrů, citlivost v čase, OOS záporné |
| C9 USD filtr | 55 | extra parametr a datová závislost, OOS ≈ 0, WF −0,2 % |
| C8b Session | 85 | okna vybrána z dat DEV, mimo DEV záporná |

*Zdrojové soubory: research/results/s02_C3.json, s02_C2.json, s02_C5.json, s02_C9.json, s02_C8b.json
(perturbation, pbo, dsr_full, max_year_share, walk_forward), research/results/dsr_within_grid.json,
research/PROTOCOL.md, research/DEV_SELECTION.md, git log.*
