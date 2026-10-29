"""2026-10-29 新規1記事を、カテゴリ一覧・ItemList・sitemap・トップ新着に登録する(一度だけ実行)。"""
import re, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
B = 'https://takuhaishoku-navi.net/'


def rd(p):
    return open(os.path.join(ROOT, p), encoding='utf8').read()


def wr(p, t):
    open(os.path.join(ROOT, p), 'w', encoding='utf8', newline='\n').write(t)


rows = {
    'senior-meal/wellness-dining': ('ウェルネスダイニング', '目的別の制限食とやわらか宅配食を選べ、管理栄養士に無料で相談できる冷凍宅配食', '食事の制限や噛む力が気になる方、そのご家族'),
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
add = ''.join(f'  <url><loc>{B}{p}/</loc><lastmod>2026-10-29</lastmod></url>\n' for p in rows)
i = t.index(f'  <url><loc>{B}about/</loc>')
wr('sitemap.xml', t[:i] + add + t[i:])

chips = {'senior-meal': '高齢者・介護食'}
desc = {'senior-meal/wellness-dining': '塩分・糖質・たんぱく質などの制限に配慮した宅配食とやわらか宅配食を、管理栄養士の無料相談とあわせて紹介します。'}
ttl = {'senior-meal/wellness-dining': 'ウェルネスダイニングの評判・メリット・デメリット'}
t = rd('index.html')
li = ''.join(f'      <li><span class="cat">{chips[p.split("/")[0]]}</span><a href="{p}/">{ttl[p]}</a><p>{desc[p]}</p></li>' + chr(10) for p in rows)
a = t.index('<ul class="new-list">') + len('<ul class="new-list">' + chr(10))
wr('index.html', t[:a] + li + t[a:])
print('registered', len(rows))
