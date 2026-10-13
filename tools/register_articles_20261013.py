"""2026-10-13 新規2記事を、カテゴリ一覧・ItemList・sitemap・トップ新着に登録する(一度だけ実行)。"""
import re, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
B = 'https://takuhaishoku-navi.net/'


def rd(p):
    return open(os.path.join(ROOT, p), encoding='utf8').read()


def wr(p, t):
    open(os.path.join(ROOT, p), 'w', encoding='utf8', newline='\n').write(t)


rows = {
    'frozen-meal/muscle-deli': ('Muscle Deli（マッスルデリ）', '目的別4プランの栄養基準を公開、メニュー50種類以上のボディメイク向け冷凍宅配食', '食事管理の目安を確認しながら続けたい方'),
    'kitchen-goods/takuhai-box-meihinkan': ('宅配ボックス名品館（ルスネコボックス）', '工事不要の置き型宅配ボックス。ロック方式や容量の違うモデルから選べる', '再配達を減らし荷物を安全に受け取りたい方'),
}
for path, (name, strength, who) in rows.items():
    cat, slug = path.split('/')
    f = cat + '/index.html'
    t = rd(f)
    assert slug not in t, f
    row = (f'          <tr class="clickable-row" onclick="location.href=\'{slug}/\'">\n'
           f'            <td>{name}</td>\n            <td>{strength}</td>\n            <td>{who}</td>\n'
           f'            <td><a href="{slug}/">記事を読む</a></td>\n          </tr>\n')
    i = t.index('</tbody>')
    i = t.rfind('\n', 0, i) + 1
    t = t[:i] + row + t[i:]
    m = list(re.finditer(r'    \{"@type": "ListItem", "position": (\d+), "url": "[^"]*"\}\n  \]', t))
    last = m[-1]
    n = int(last.group(1)) + 1
    seg = last.group(0)
    seg2 = seg.replace('}\n  ]', '},\n' + f'    {{"@type": "ListItem", "position": {n}, "url": "{B}{cat}/{slug}/"}}\n  ]')
    t = t.replace(seg, seg2, 1)
    wr(f, t)

t = rd('sitemap.xml')
add = ''.join(f'  <url><loc>{B}{p}/</loc><lastmod>2026-10-13</lastmod></url>\n' for p in rows)
i = t.index(f'  <url><loc>{B}about/</loc>')
wr('sitemap.xml', t[:i] + add + t[i:])

chips = {'frozen-meal': '冷凍宅配弁当', 'kitchen-goods': 'キッチン用品'}
desc = {
    'frozen-meal/muscle-deli': '目的別4プランの栄養基準を公開している、ボディメイク向けの冷凍宅配食を紹介します。',
    'kitchen-goods/takuhai-box-meihinkan': '工事不要の置き型宅配ボックス「ルスネコボックス」を扱う専門店を紹介します。'}
ttl = {
    'frozen-meal/muscle-deli': 'Muscle Deli（マッスルデリ）の評判・メリット・デメリット',
    'kitchen-goods/takuhai-box-meihinkan': '宅配ボックス名品館（ルスネコボックス）の評判・メリット・デメリット'}
t = rd('index.html')
li = ''.join(f'      <li><span class="cat">{chips[p.split("/")[0]]}</span><a href="{p}/">{ttl[p]}</a><p>{desc[p]}</p></li>\n' for p in rows)
a = t.index('<ul class="new-list">') + len('<ul class="new-list">\n')
wr('index.html', t[:a] + li + t[a:])
print('registered', len(rows))
