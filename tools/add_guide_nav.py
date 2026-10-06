"""全ページのヘッダーナビに「選び方ガイド」を追加 (一度だけ実行)。"""
import re, pathlib
DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"
pat = re.compile(r'( *)<li><a href="((?:\.\./)*|\./)health-food/"[^>]*>美容・健康食品</a></li>')
n = 0
for f in DOCS.rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    if "選び方ガイド</a>" in t:
        continue
    def rep(m):
        pre = m.group(2)
        pre = "" if pre == "./" else pre
        return m.group(0) + "\n" + m.group(1) + f'<li><a href="{pre}guide/">選び方ガイド</a></li>'
    t2, c = pat.subn(rep, t)
    if c:
        f.write_text(t2, encoding="utf-8"); n += 1
print("nav updated:", n)
