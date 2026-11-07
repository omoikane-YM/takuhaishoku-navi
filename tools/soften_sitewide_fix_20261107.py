"""soften_sitewide_20261107.py の機械置換で不自然になった文を直す (2026-11-07)。docs の HTML と tools の py に適用。"""
import re
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
DOCS = TOOLS.parent / "docs"

PAIRS = [
    ("注意が書かれています", "注意が必要です"),
    ("試せるセットが書かれています", "試せるセットがあります"),
    ("モデルが公式サイトで書かれています", "モデルが公式サイトで紹介されています"),
    ("ベースやフリーウェイトによる転倒防止・固定補助が書かれています", "ベースやフリーウェイトで、転倒防止や固定の補助もできます"),
    ("キャンペーンも書かれています", "キャンペーンもあります"),
    ("提案するとも書かれています", "提案してくれるとのことです"),
    ("利用の仕方が書かれています", "使い方も紹介されています"),
    ("購入手段として書かれています", "購入手段になっています"),
    ("解凍しないようにとも書かれています", "解凍しないようにとのことです"),
    ("食べきる手順が書かれています", "食べきる手順が紹介されています"),
    ("商品も書かれています", "商品も並んでいます"),
    ("公式サイトで書かれています", "公式サイトで確認できます"),
]
REGEX = [
    (r"(Pay|d払い|楽天ペイ|PayPay)が書かれています", r"\1が使えます"),
    (r"と記載されています", "とのことです"),
    (r"と案内されており、", "とのことで、"),
    (r"と案内されており", "とのことで"),
]


def fix(t):
    for a, b in PAIRS:
        t = t.replace(a, b)
    for a, b in REGEX:
        t = re.sub(a, b, t)
    return t


n = 0
files = sorted(DOCS.rglob("*.html")) + [p for p in TOOLS.rglob("*.py") if not p.name.startswith("soften_")]
for p in files:
    t = p.read_text(encoding="utf-8")
    s = fix(t)
    if s != t:
        p.write_text(s, encoding="utf-8", newline="\n")
        n += 1
print("fixed files:", n)
