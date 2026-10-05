"""Build the detailed Czech PDF report from docs/pdf/src/*.md (+ generated appendices).

    python docs/pdf/build_pdf.py            -> docs/XAUUSD_vyzkum_swing_strategii.pdf

Markdown subset: headings (#, ##, ###), paragraphs, lists, GFM tables, blockquotes (callouts),
fenced code, images (paths relative to the repo root).
"""
from __future__ import annotations

import datetime as dt
import glob
import html
import json
import os
import re
import subprocess
import sys

import markdown
from weasyprint import HTML

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "docs", "pdf", "src")
OUT = os.path.join(ROOT, "docs", "XAUUSD_vyzkum_swing_strategii.pdf")
TITLE = "XAUUSD – automatizovaný swing trading"
SUBTITLE = "Nezávislý výzkum, kvantitativní ověření a odůvodnění výběru strategií"

CSS = r"""
@page {
  size: A4; margin: 20mm 17mm 20mm 17mm;
  @top-left { content: string(chapter); font-size: 7.5pt; color: #7a7a7a; }
  @top-right { content: "XAUUSD – výzkum swing strategií"; font-size: 7.5pt; color: #7a7a7a; }
  @bottom-center { content: "Strana " counter(page) " z " counter(pages); font-size: 7.5pt; color: #7a7a7a; }
}
@page cover { margin: 0; @top-left { content: none } @top-right { content: none } @bottom-center { content: none } }
@page wide { size: A4 landscape; margin: 15mm 14mm 15mm 14mm; }
html { font-family: "Liberation Sans", "DejaVu Sans", sans-serif; font-size: 9.6pt; line-height: 1.42; color: #1d1d1f; }
body { margin: 0; }
h1 { string-set: chapter content(); page-break-before: always; font-size: 19pt; color: #14365d; margin: 0 0 10pt 0;
     padding-bottom: 5pt; border-bottom: 2.2pt solid #c9a227; bookmark-level: 1; }
h2 { font-size: 13.2pt; color: #14365d; margin: 15pt 0 6pt 0; bookmark-level: 2; page-break-after: avoid; }
h3 { font-size: 11pt; color: #2b4f7a; margin: 11pt 0 4pt 0; bookmark-level: 3; page-break-after: avoid; }
p { margin: 0 0 6pt 0; text-align: justify; hyphens: auto; orphans: 3; widows: 3; }
ul, ol { margin: 0 0 6pt 0; padding-left: 15pt; }
li { margin: 0 0 2.5pt 0; }
strong { color: #0f2a48; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; background: #f2f4f7; padding: 0 2pt; border-radius: 2pt; }
pre { font-family: "DejaVu Sans Mono", monospace; font-size: 7.4pt; line-height: 1.3; background: #f6f7f9;
      border: 0.6pt solid #d9dde3; border-left: 2.5pt solid #14365d; padding: 6pt 8pt; white-space: pre-wrap;
      page-break-inside: auto; margin: 4pt 0 8pt 0; }
pre code { background: none; padding: 0; font-size: 7.4pt; }
blockquote { margin: 6pt 0 9pt 0; padding: 6pt 10pt; background: #fbf6e6; border-left: 3pt solid #c9a227;
             page-break-inside: avoid; }
blockquote p { margin: 0 0 3pt 0; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 10pt 0; font-size: 7.8pt; page-break-inside: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #14365d; color: #fff; font-weight: bold; text-align: left; padding: 3pt 4pt; border: 0.4pt solid #14365d; }
td { padding: 2.4pt 4pt; border: 0.4pt solid #d5d9df; vertical-align: top; }
tbody tr:nth-child(even) td { background: #f5f7fa; }
table.small { font-size: 6.9pt; }
table.small td, table.small th { padding: 2pt 2.6pt; }
table.xsmall { font-size: 6.1pt; }
table.xsmall td, table.xsmall th { padding: 1.6pt 2pt; }
.widewrap { page: wide; }
figure { margin: 6pt 0 10pt 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; max-height: 120mm; }
figcaption { font-size: 8pt; color: #555; margin-top: 3pt; font-style: italic; }
/* cover */
.cover { page: cover; height: 297mm; width: 210mm; background: #14365d; color: #fff; position: relative; }
.cover .band { position: absolute; top: 0; left: 0; width: 210mm; height: 9mm; background: #c9a227; }
.cover .inner { position: absolute; top: 62mm; left: 22mm; right: 22mm; }
.cover h1.ct { string-set: none; page-break-before: avoid; border: none; color: #fff; font-size: 30pt; margin: 0 0 8pt 0; bookmark-level: none; }
.cover .sub { font-size: 14pt; color: #e6d48f; margin-bottom: 26pt; }
.cover .meta { font-size: 9.5pt; color: #d4dbe6; line-height: 1.7; }
.cover .verdict { margin-top: 26pt; padding: 10pt 12pt; border: 1pt solid #c9a227; font-size: 10pt; color: #fff; line-height: 1.5; }
.cover .verdict b { color: #e6d48f; }
/* toc */
.toc h1 { page-break-before: always; }
.toc ul { list-style: none; padding-left: 0; }
.toc li.l1 { font-weight: bold; margin-top: 4pt; font-size: 9.6pt; }
.toc li.l2 { padding-left: 12pt; font-size: 8.6pt; color: #333; }
.toc a { color: inherit; text-decoration: none; }
.toc a::after { content: leader('.') target-counter(attr(href), page); }
a { color: #1f5fa8; text-decoration: none; }
"""


def git_hash() -> str:
    try:
        return subprocess.check_output(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "?"


def appendices() -> str:
    parts = []

    def demote(md: str, prefix: str) -> str:
        out = []
        for line in md.splitlines():
            m = re.match(r"^(#{1,3}) (.*)$", line)
            if m:
                lvl = len(m.group(1))
                line = "#" * min(lvl + 1, 3) + " " + m.group(2)
            out.append(line)
        return "\n".join(out)

    with open(os.path.join(ROOT, "research", "PROTOCOL.md")) as f:
        parts.append("# Příloha A – Předregistrovaný výzkumný protokol\n\nDoslovné znění `research/PROTOCOL.md` "
                     "(commit 6a151db, zapsáno před prvním během strategií).\n\n" + demote(f.read(), "A"))
    with open(os.path.join(ROOT, "research", "DEV_SELECTION.md")) as f:
        parts.append("# Příloha B – Rozhodnutí po DEV\n\nDoslovné znění `research/DEV_SELECTION.md` "
                     "(commit 41ce7b8, zapsáno před prvním během na OOS).\n\n" + demote(f.read(), "B"))
    with open(os.path.join(ROOT, "research", "frozen_spec.json")) as f:
        parts.append("# Příloha C – Zmrazená specifikace před holdoutem\n\n`research/frozen_spec.json` "
                     "(commit cfe78c3).\n\n```\n" + f.read() + "\n```\n")
    with open(os.path.join(ROOT, "config", "paper.toml")) as f:
        parts.append("# Příloha D – Konfigurace PAPER fáze\n\n`config/paper.toml` – přesné parametry pro další "
                     "zpracování.\n\n```\n" + f.read() + "\n```\n")
    with open(os.path.join(ROOT, "research", "results", "data_quality.json")) as f:
        dq = json.load(f)
    parts.append("# Příloha E – Protokol kvality dat\n\n`research/results/data_quality.json`.\n\n```\n"
                 + json.dumps(dq, indent=1, ensure_ascii=False) + "\n```\n")
    files = subprocess.check_output(["git", "-C", ROOT, "ls-files"], text=True).splitlines()
    files = [x for x in files if not x.startswith("docs/pdf/src/")]
    parts.append("# Příloha F – Obsah repozitáře a reprodukce\n\n## F.1 Reprodukce výsledků\n\n```\n"
                 "pip install -r requirements.txt\nbash research/fetch_data.sh\npython research/prepare_data.py\n"
                 "python research/scorecard.py\npython research/s01_dev_screen.py\npython research/s02_validate.py\n"
                 "python research/s03_portfolio.py C3 C2 C5\npython research/s04_holdout.py\npython research/s05_summary.py\n"
                 "python -m pytest -q tests\npython docs/pdf/build_pdf.py\n```\n\n## F.2 Soubory v repozitáři\n\n```\n"
                 + "\n".join(files) + "\n```\n")
    return "\n\n".join(parts)


LIST_RE = re.compile(r"^\s*([-*+]|\d+\.)\s+")


def normalize(md_text: str) -> str:
    """python-markdown needs a blank line before lists and tables (GFM does not); add them,
    outside fenced code blocks only."""
    out, fence, prev = [], False, ""
    for line in md_text.splitlines():
        if line.strip().startswith("```"):
            fence = not fence
            out.append(line)
            prev = line
            continue
        if not fence and prev.strip():
            starts_list = bool(LIST_RE.match(line)) and not LIST_RE.match(prev) and not prev.startswith((" ", "\t"))
            starts_table = line.startswith("|") and not prev.startswith("|")
            if starts_list or starts_table:
                out.append("")
        out.append(line)
        prev = line
    return "\n".join(out) + "\n"


def md_to_html(md_text: str) -> str:
    return markdown.markdown(normalize(md_text), extensions=["tables", "fenced_code", "sane_lists", "toc"],
                             extension_configs={"toc": {"slugify": slug}})


def slug(value: str, separator: str = "-") -> str:
    import unicodedata
    v = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    v = re.sub(r"[^\w\s-]", "", v).strip().lower()
    return re.sub(r"[\s_-]+", separator, v)


def postprocess(h: str) -> str:
    # images -> figures with captions
    h = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" ?/?></p>',
               lambda m: f'<figure><img src="{m.group(2)}" alt="{m.group(1)}"/><figcaption>{m.group(1)}</figcaption></figure>', h)

    # table sizing by column count; very wide tables on landscape pages
    def fix_table(m):
        t = m.group(0)
        head = re.search(r"<tr>(.*?)</tr>", t, re.S)
        n = len(re.findall(r"<th", head.group(1))) if head else 0
        if n >= 16:
            return '<div class="widewrap">' + t.replace("<table>", '<table class="small">', 1) + "</div>"
        if n >= 13:
            return t.replace("<table>", '<table class="xsmall">', 1)
        if n >= 9:
            return t.replace("<table>", '<table class="small">', 1)
        return t
    h = re.sub(r"<table>.*?</table>", fix_table, h, flags=re.S)
    return h


def unique_ids(h: str, counter: dict) -> str:
    def fix(m):
        tag, ident = m.group(1), m.group(2)
        counter[ident] = counter.get(ident, 0) + 1
        if counter[ident] > 1:
            ident = f"{ident}-{counter[ident]}"
        return f'<{tag} id="{ident}"'
    return re.sub(r'<(h[123]) id="([^"]+)"', fix, h)


def build() -> str:
    files = sorted(glob.glob(os.path.join(SRC, "*.md")))
    if not files:
        sys.exit("no chapters in docs/pdf/src")
    bodies, counter = [], {}
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            bodies.append(unique_ids(postprocess(md_to_html(f.read())), counter))
    bodies.append(unique_ids(postprocess(md_to_html(appendices())), counter))
    body = "\n".join(bodies)
    # table of contents from h1/h2
    toc_items = []
    for m in re.finditer(r'<(h[12]) id="([^"]+)">(.*?)</h[12]>', body, re.S):
        lvl = "l1" if m.group(1) == "h1" else "l2"
        text = re.sub(r"<[^>]+>", "", m.group(3))
        toc_items.append(f'<li class="{lvl}"><a href="#{m.group(2)}">{text}</a></li>')
    today = dt.date.today().isoformat()
    cover = f"""
<section class="cover"><div class="band"></div><div class="inner">
<h1 class="ct">{html.escape(TITLE)}</h1>
<div class="sub">{html.escape(SUBTITLE)}</div>
<div class="meta">Podklad pro další zpracování · zpracováno {today} · verze repozitáře {git_hash()}<br/>
Instrument: XAUUSD (spot zlato) · timeframe H1 / H4 / D1 · data 2004–2026<br/>
Repozitář: CortezWraith/PROJECT-XAUUSD-AUTOMATED-SWING-TRADING-SYSTEM</div>
<div class="verdict"><b>Verdikt:</b> žádná z 10 testovaných rodin strategií neprošla všemi předem stanovenými
branami robustnosti. Jediná konzistentně (slabě) kladná rodina je střednědobý trend na H4.
Pořadí kandidátů pro další zkoumání: <b>1. C3 EMA trend H4</b>, <b>2. C2 Donchian H4</b>,
<b>3. C5 Squeeze H4</b> – jedna podkladová sázka, důvěra <b>NÍZKÁ</b>; doporučena pouze pozorovací PAPER fáze.</div>
</div></section>"""
    toc = '<section class="toc"><h1 id="obsah">Obsah</h1><ul>' + "".join(toc_items) + "</ul></section>"
    return f"<html lang='cs'><head><meta charset='utf-8'><title>{html.escape(TITLE)}</title></head><body>{cover}{toc}{body}</body></html>"


def main() -> None:
    from weasyprint import CSS as _CSS
    doc = build()
    with open(os.path.join(ROOT, "docs", "pdf", "report.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    HTML(string=doc, base_url=ROOT).write_pdf(OUT, stylesheets=[_CSS(string=CSS)])
    print("written", OUT)


if __name__ == "__main__":
    main()
