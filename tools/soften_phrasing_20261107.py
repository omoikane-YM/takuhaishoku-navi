"""加筆文の業務的な語尾(「〜と案内されています」等)をやわらかい言い回しに置き換える (2026-11-07)。
対象: tools/enrich_articles_20261107.py と enrich_batch*_20261107.py のデータ文字列。
その後 各バッチを再実行して HTML を作り直す。冪等(置換後は元の語尾が残らない)。"""
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
FILES = [TOOLS / "enrich_articles_20261107.py"] + sorted(TOOLS.glob("enrich_batch*_20261107.py"))

ROT = ["とのことです", "と書かれています"]


def soften(t: str) -> str:
    n = {"i": 0}

    def rot(_m):
        s = ROT[n["i"] % len(ROT)]
        n["i"] += 1
        return s

    # 「Aと、公式サイトで案内されています」「Aと案内されています」「Aと表示されています」
    t = re.sub(r"と、(?:公式[^、。\"]{0,12}で)案内されています", rot, t)
    t = re.sub(r"と(?:公式[^、。\"]{0,12}で)?案内されています", rot, t)
    t = re.sub(r"と(?:表示|紹介)されています", rot, t)
    t = re.sub(r"と(?:表示|紹介)されている(?=[。、\"])", "と書かれている", t)
    t = re.sub(r"と案内されている(?=[。、\"])", "と書かれている", t)
    # 修飾の「案内されている」
    t = re.sub(r"(公式[^、。\"「」]{0,12})で案内されている", r"\1に載っている", t)
    t = t.replace("案内されている", "載っている")
    # 残りの文末
    t = t.replace("案内されています", "書かれています")
    t = t.replace("掲載されています", "載っています")
    t = t.replace("掲載されている", "載っている")
    # 「整理しました」を一部「まとめました」に(同一文字列内で交互)
    k = {"i": 0}

    def seiri(m):
        k["i"] += 1
        return "まとめました" if k["i"] % 2 else m.group(0)

    t = re.sub(r"整理しました", seiri, t)
    return t


def main():
    for f in FILES:
        o = f.read_text(encoding="utf-8")
        s = soften(o)
        if s != o:
            f.write_text(s, encoding="utf-8", newline="\n")
    for f in FILES:
        r = subprocess.run([sys.executable, str(f)], capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            print("ERR", f.name, r.stderr[-300:])
    print("done")


if __name__ == "__main__":
    main()
