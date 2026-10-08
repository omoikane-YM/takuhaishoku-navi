"""2026-10-04 新規4記事を、カテゴリ一覧・ItemList・sitemap・トップ新着に登録する(一度だけ実行)。"""
import re, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
B = 'https://takuhaishoku-navi.net/'


def rd(p):
    return open(os.path.join(ROOT, p), encoding='utf8').read()


def wr(p, t):
    open(os.path.join(ROOT, p), 'w', encoding='utf8', newline='\n').write(t)


rows = {
    'baby-food/mogumodeli': ('モグモデリ', '成長期の小学生・中学生向け、無添加の冷凍ワンプレートが電子レンジ約4分で完成', '部活・塾で夕食が不規則な子どもの保護者'),
    'coop-delivery/kinki-coop': ('コープの宅配（コープきんき）', '近畿5府県で毎週約4,000点以上から選べる生協の個人宅配、資料請求・おためしセットから始められる', '近畿にお住まいで食品も日用品もまとめて宅配したい方'),
    'otoriyose/hokkaido-gyoren': ('北海道ぎょれん', '北海道の漁協ネットワークから全商品送料無料で届く産地直送の海産物（常時200点以上）', 'ギフトや自宅用に北海道の海の幸を選びたい方'),
    'senior-meal/anshin-soudan': ('シニアのあんしん相談室（宅配ごはん案内）', '郵便番号から配達可能な宅配食を検索・比較し、複数サービスの資料を一括請求できる', '離れて暮らす親の食事を探すご家族'),
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
add = ''.join(f'  <url><loc>{B}{p}/</loc><lastmod>2026-10-04</lastmod></url>\n' for p in rows)
i = t.index(f'  <url><loc>{B}about/</loc>')
wr('sitemap.xml', t[:i] + add + t[i:])

chips = {'baby-food': '離乳食宅配', 'coop-delivery': '食材宅配(生協・産直系)', 'otoriyose': 'お取り寄せグルメ', 'senior-meal': '高齢者・介護食'}
desc = {
    'baby-food/mogumodeli': '成長期の小学生・中学生向けに栄養基準を設けた、無添加の冷凍ワンプレートを紹介します。',
    'coop-delivery/kinki-coop': '滋賀・京都・奈良・大阪・和歌山で利用できる、毎週約4,000点以上から選べる生協の個人宅配を紹介します。',
    'otoriyose/hokkaido-gyoren': '北海道の漁協ネットワークから全商品送料無料で届く、産地直送の海産物ショップを紹介します。',
    'senior-meal/anshin-soudan': '郵便番号から配達可能な宅配食を検索・比較し、複数サービスの資料をまとめて請求できる案内サービスを紹介します。'}
ttl = {
    'baby-food/mogumodeli': 'モグモデリの評判・メリット・デメリット',
    'coop-delivery/kinki-coop': 'コープの宅配（コープきんき）の評判・メリット・デメリット',
    'otoriyose/hokkaido-gyoren': '北海道ぎょれんの評判・メリット・デメリット',
    'senior-meal/anshin-soudan': 'シニアのあんしん相談室（宅配ごはん案内）の評判・メリット・デメリット'}
t = rd('index.html')
li = ''.join(f'      <li><span class="cat">{chips[p.split("/")[0]]}</span><a href="{p}/">{ttl[p]}</a><p>{desc[p]}</p></li>\n' for p in rows)
a = t.index('<ul class="new-list">') + len('<ul class="new-list">\n')
wr('index.html', t[:a] + li + t[a:])
print('registered', len(rows))
