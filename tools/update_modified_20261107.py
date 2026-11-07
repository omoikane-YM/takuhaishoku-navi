"""加筆済み記事(id="details"を持つページ)の更新日を 2026-11-07 に揃える。
表示の「更新日」、JSON-LD の dateModified、sitemap の lastmod を更新。カテゴリ一覧の lastmod は配下の最新日(既存ルール)。
冪等。実行: python tools/update_modified_20261107.py"""
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
D = "2026-11-07"
DJ = "2026年11月7日"

updated = []
for p in sorted(DOCS.glob("*/*/index.html")):
    t = p.read_text(encoding="utf-8")
    if 'id="details"' not in t:
        continue
    o = t
    # 1. JSON-LD
    t, n1 = re.subn(r'"dateModified": "\d{4}-\d\d-\d\d(T[^"]*)?"', f'"dateModified": "{D}T00:00:00+09:00"', t)
    # 2. 表示
    if "更新日" in t:
        t = re.sub(r'(<span>更新日 <time datetime=")\d{4}-\d\d-\d\d(">)[^<]*(</time></span>)', rf"\g<1>{D}\g<2>{DJ}\g<3>", t)
    else:
        t = re.sub(
            r'(<span>公開日 <time datetime="[^"]*">[^<]*</time></span>)',
            rf'\1<span>更新日 <time datetime="{D}">{DJ}</time></span>',
            t,
            count=1,
        )
    if t != o:
        p.write_text(t, encoding="utf-8")
    updated.append(p.parent.relative_to(DOCS).as_posix())
    assert n1 >= 1, f"dateModified not found: {p}"

# 3. sitemap
sm_path = DOCS / "sitemap.xml"
sm = sm_path.read_text(encoding="utf-8")
cats = set()
for slug in updated:
    cats.add(slug.split("/")[0])
    sm = re.sub(
        rf"(<url><loc>https://takuhaishoku-navi\.net/{re.escape(slug)}/</loc><lastmod>)[^<]*(</lastmod></url>)",
        rf"\g<1>{D}\g<2>",
        sm,
    )
for c in cats:  # 一覧ページは配下の最新日
    sm = re.sub(
        rf"(<url><loc>https://takuhaishoku-navi\.net/{re.escape(c)}/</loc><lastmod>)[^<]*(</lastmod></url>)",
        rf"\g<1>{D}\g<2>",
        sm,
    )
sm_path.write_text(sm, encoding="utf-8")
print(len(updated), "articles;", sorted(cats))
