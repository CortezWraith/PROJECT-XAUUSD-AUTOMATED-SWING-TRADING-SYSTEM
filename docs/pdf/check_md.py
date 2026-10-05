"""Lint the chapter sources for things the PDF build cannot render well."""
from __future__ import annotations

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
problems = 0
for fp in sorted(glob.glob(os.path.join(ROOT, "docs", "pdf", "src", "*.md"))):
    name = os.path.basename(fp)
    lines = open(fp, encoding="utf-8").read().splitlines()
    h1 = [i for i, l in enumerate(lines) if re.match(r"^# ", l)]
    issues = []
    if len(h1) != 1 or h1[0] != 0:
        issues.append(f"h1 count/position {h1}")
    fence = False
    table_cols = None
    for i, l in enumerate(lines, 1):
        if l.strip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if re.match(r"^#{4,} ", l):
            issues.append(f"L{i} heading level >3")
        if re.search(r"<(div|span|br|table|img|sup|sub|b|i)\b", l):
            issues.append(f"L{i} raw HTML")
        if re.search(r"[✅❌\U0001F300-\U0001FAFF]", l):
            issues.append(f"L{i} emoji")
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", l):
            if not os.path.exists(os.path.join(ROOT, m.group(1))):
                issues.append(f"L{i} missing image {m.group(1)}")
        if l.startswith("|"):
            n = l.count("|") - l.count("\\|")
            if table_cols is None:
                table_cols = n
            elif n != table_cols:
                issues.append(f"L{i} table columns {n} != {table_cols}")
        else:
            table_cols = None
    words = sum(len(l.split()) for l in lines)
    print(f"{name}: {words} words, {len(issues)} issues")
    for x in issues[:20]:
        print("   ", x)
    problems += len(issues)
sys.exit(1 if problems else 0)
