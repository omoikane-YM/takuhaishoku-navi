"""変更・追加した記事の更新日を「今日」に揃える(表示の更新日 / JSON-LD dateModified / sitemap lastmod)。

使い方(リポジトリ直下):
  python tools/touch_modified.py                # git で変更・追加された記事(docs/*/*/index.html)を自動検出して今日に更新
  python tools/touch_modified.py 2026-11-07     # 日付を指定
  python tools/touch_modified.py --all          # 全記事を対象
  python tools/touch_modified.py --slugs otoriyose/masuyone frozen-meal/delipicks   # 記事を明示

記事を変更・追加したらコミット前に必ず実行する(サイトが継続的に更新されていることを示すため)。
新規記事に更新日が無い場合は、公開日の隣に追加する。カテゴリ一覧の lastmod は配下の最新日(既存ルール)。
冪等。"""
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def changed_slugs():
    out = subprocess.run(
        ["git", "status", "--porcelain", "--", "docs"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    ).stdout
    slugs = set()
    for line in out.splitlines():
        path = line[3:].strip().strip('"')
        m = re.match(r"docs/([^/]+/[^/]+)/index\.html$", path)
        if m:
            slugs.add(m.group(1))
    return sorted(slugs)


def main():
    args = sys.argv[1:]
    d = None
    for a in list(args):
        if re.fullmatch(r"\d{4}-\d\d-\d\d", a):
            d = a
            args.remove(a)
    d = d or date.today().isoformat()
    y, mth, day = d.split("-")
    dj = f"{int(y)}年{int(mth)}月{int(day)}日"

    if "--all" in args:
        slugs = sorted(p.parent.relative_to(DOCS).as_posix() for p in DOCS.glob("*/*/index.html"))
    elif "--slugs" in args:
        slugs = args[args.index("--slugs") + 1 :]
    else:
        slugs = changed_slugs()
    if not slugs:
        print("対象の記事なし")
        return

    done = []
    for slug in slugs:
        p = DOCS / slug / "index.html"
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        o = t
        t = re.sub(r'"dateModified": "\d{4}-\d\d-\d\d(T[^"]*)?"', f'"dateModified": "{d}T00:00:00+09:00"', t)
        if "<span>更新日" in t:
            t = re.sub(
                r'(<span>更新日 <time datetime=")\d{4}-\d\d-\d\d(">)[^<]*(</time></span>)', rf"\g<1>{d}\g<2>{dj}\g<3>", t
            )
        else:
            t = re.sub(
                r'(<span>公開日 <time datetime="[^"]*">[^<]*</time></span>)',
                rf'\1<span>更新日 <time datetime="{d}">{dj}</time></span>',
                t,
                count=1,
            )
        if t != o:
            p.write_text(t, encoding="utf-8")
        done.append(slug)

    sm_path = DOCS / "sitemap.xml"
    sm = sm_path.read_text(encoding="utf-8")
    cats = {s.split("/")[0] for s in done}
    for loc in [f"{s}/" for s in done] + [f"{c}/" for c in cats]:
        sm = re.sub(
            rf"(<url><loc>https://takuhaishoku-navi\.net/{re.escape(loc)}</loc><lastmod>)[^<]*(</lastmod></url>)",
            rf"\g<1>{d}\g<2>",
            sm,
        )
    sm_path.write_text(sm, encoding="utf-8")
    print(f"{d}: {len(done)} 記事の更新日を更新 / カテゴリ一覧: {sorted(cats)}")


if __name__ == "__main__":
    main()
