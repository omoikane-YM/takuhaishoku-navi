"""サイト全体(docs/**/*.html と生成スクリプト)の業務的な語尾を、加筆部分と同じルールでやわらかくする (2026-11-07)。
FAQ の JSON-LD と画面表示がずれないよう、HTML は全文に同じ置換を適用する。
実行: python tools/soften_sitewide_20261107.py   その後 python tools/touch_modified.py"""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from soften_phrasing_20261107 import soften  # noqa: E402

DOCS = TOOLS.parent / "docs"

targets = sorted(DOCS.rglob("*.html"))
gens = [p for p in TOOLS.rglob("*.py") if p.name.startswith(("make_", "guide_data", "enhance_", "add_article_faqs", "build_home")) or p.parent.name == "faq"]

changed = 0
for p in targets + gens:
    t = p.read_text(encoding="utf-8")
    s = soften(t)
    if s != t:
        p.write_text(s, encoding="utf-8", newline="\n")
        changed += 1
print("changed files:", changed)
