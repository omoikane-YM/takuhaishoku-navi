"""選び方ガイド (docs/guide/) を生成する。内容は guide_data.py。再実行可 (上書き)。
ヘッダー/フッターは docs/privacy/index.html から流用し、sitemap にも登録する (重複登録なし)。"""
import os, re, json, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guide_data import GUIDES

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
BASE = 'https://takuhaishoku-navi.net/'
DATE = '2026-10-06'
NOW = DATE + 'T12:00:00+09:00'
SLUGS = {g['slug'] for g in GUIDES}


def esc(s):
    return html.escape(s, quote=False)


def read(p):
    return open(os.path.join(ROOT, p), encoding='utf8').read()


priv = read('privacy/index.html')
HEADER = re.search(r'<header class="site-header">.*?</header>', priv, re.S).group(0)
FOOTER = re.search(r'<footer class="site-footer">.*?</footer>', priv, re.S).group(0)
# privacy は depth1 ("../") → guide記事は depth2 ("../../")
HEADER = HEADER.replace('href="../', 'href="../../')
FOOTER = FOOTER.replace('href="../', 'href="../../').replace('href="./"', 'href="../../privacy/"')
HEADER_HUB = HEADER.replace('href="../../', 'href="../')
FOOTER_HUB = FOOTER.replace('href="../../', 'href="../')
mark = lambda h: h.replace('<a href="../../guide/">', '<a href="../../guide/" aria-current="page">')
HEADER = HEADER.replace('<a href="../../guide/">', '<a href="../" aria-current="page">')
HEADER_HUB = HEADER_HUB.replace('<a href="../guide/">', '<a href="./" aria-current="page">')


def links(s, depth=2):
    pre = '../' * depth
    return re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', lambda m: f'<a href="{pre}{m.group(1)}/">{m.group(2)}</a>' if not m.group(1).endswith('/') else f'<a href="{pre}{m.group(1)}">{m.group(2)}</a>', s)


def plain(s):
    return re.sub(r'\[\[[^|\]]+\|([^\]]+)\]\]', r'\1', s)


GA = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-9SNYF19K6S"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-9SNYF19K6S');
</script>'''


def head(title, desc, url, rel, extra=''):
    t = esc(title)
    d = html.escape(desc, quote=True)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="{rel}assets/favicon-32.png" sizes="32x32">
<link rel="icon" href="{rel}favicon.ico">
<link rel="apple-touch-icon" href="{rel}assets/apple-touch-icon.png">
<title>{t}｜宅配食ナビ</title>
<meta name="description" content="{d}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700&amp;display=swap">
<link rel="stylesheet" href="{rel}assets/style.css?v=8">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="宅配食ナビ">
<meta property="og:title" content="{t}｜宅配食ナビ">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
{extra}{GA}
</head>
<body>
'''


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + '\n</script>\n'


def breadcrumb_ld(items):
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]})


def build(g):
    url = f"{BASE}guide/{g['slug']}/"
    faq = g['faq']
    extra = breadcrumb_ld([('トップ', BASE), ('選び方ガイド', BASE + 'guide/'), (g['short'], url)])
    extra += ld({"@context": "https://schema.org", "@type": "Article", "headline": g['title'], "description": g['desc'],
                 "author": {"@type": "Organization", "name": "宅配食ナビ"},
                 "publisher": {"@type": "Organization", "name": "宅配食ナビ", "url": BASE},
                 "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "datePublished": NOW, "dateModified": NOW})
    extra += ld({"@context": "https://schema.org", "@type": "FAQPage",
                 "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in faq]})
    toc = '\n'.join(f'      <li><a href="#{i}">{esc(t)}</a></li>' for i, t, _ in g['sections'])
    toc += '\n      <li><a href="#faq">よくある質問</a></li>'
    secs = ''
    has_diag = any(i == 'diagnosis' for i, _, _ in g['sections'])
    for i, t, body in g['sections']:
        hint = '\n    <p class="diag-hint">いちばん当てはまるものを選ぶと、おすすめの選び方が表示されます。</p>' if i == 'diagnosis' else ''
        secs += f'  <section class="intro-block" id="{i}">\n    <h2>{esc(t)}</h2>{hint}\n{links(body.strip())}\n  </section>\n\n'
    faq_html = '\n'.join(f'      <div class="faq-item">\n        <h3>Q. {esc(q)}</h3>\n        <p>A. {links(esc(a))}</p>\n      </div>' for q, a in faq)
    rel = ''
    for p, label in g['related']:
        h = ('../' if p.rstrip('/') in SLUGS or p.split('/')[0] in SLUGS else '../../') + p
        rel += f'      <li><a href="{h}">{esc(label)}</a></li>\n'
    return head(g['title'], g['desc'], url, '../../', extra) + HEADER + f'''
<p class="breadcrumb"><a href="/">トップ</a> &gt; <a href="../">選び方ガイド</a> &gt; {esc(g['short'])}</p>

<main>
  <section class="hero">
    <div class="hero-inner">
      <h1>{esc(g['title'])}</h1>
      <p class="post-meta"><span>公開日 <time datetime="{DATE}">2026年10月6日</time></span></p>
      <p>{esc(g['lead'])}</p>
    </div>
  </section>

  <p class="affiliate-notice">本サイトはアフィリエイトプログラム(A8.net等)による収益を得ています。紹介内容は公開情報をもとに第三者視点で構成しており、運営者自身の体験談ではありません。価格・条件は変更されることがあるため、最新情報は各公式サイトでご確認ください。</p>

  <nav class="toc" aria-label="目次">
    <p>目次</p>
    <ol>
{toc}
    </ol>
  </nav>

{secs}  <section id="faq">
    <h2>よくある質問</h2>
    <div class="faq-list">
{faq_html}
    </div>
  </section>

  <section class="intro-block">
    <h2>あわせて読みたい</h2>
    <ul>
{rel}    </ul>
  </section>
</main>

''' + FOOTER + ('\n<script src="../../assets/diagnosis.js" defer></script>' if has_diag else '') + '\n</body>\n</html>\n'


def build_hub():
    url = BASE + 'guide/'
    title = '宅配食・食材宅配の選び方ガイド一覧'
    desc = '冷凍宅配弁当・ミールキット・高齢者向け宅配食・離乳食宅配・食材宅配(生協・産直)について、選び方のポイント、費用の考え方、注意点をまとめたガイド記事の一覧です。'
    extra = breadcrumb_ld([('トップ', BASE), ('選び方ガイド', url)])
    items = ''
    for g in GUIDES:
        items += f'''    <div class="intro-block">
      <h3><a href="{g['slug']}/">{esc(g['title'])}</a></h3>
      <p>{esc(g['desc'])}</p>
      <p><a href="../{g['cat']}/">{esc(g['cat_name'])}のサービス比較を見る</a></p>
    </div>
'''
    return head(title, desc, url, '../', extra).replace('og:type" content="article"', 'og:type" content="website"') + HEADER_HUB + f'''
<p class="breadcrumb"><a href="/">トップ</a> &gt; 選び方ガイド</p>

<main>
  <section class="hero">
    <div class="hero-inner">
      <h1>{esc(title)}</h1>
      <p>サービスを比べる前に読んでおきたい、選び方の基本をカテゴリごとにまとめました。費用の考え方、確認すべき項目、よくある失敗とその対策を、公開情報と公的なガイドラインをもとに整理しています。</p>
    </div>
  </section>

  <section id="guides">
    <h2>ガイド一覧</h2>
{items}  </section>

  <section class="intro-block">
    <h2>ガイドの使い方</h2>
    <ol>
      <li>気になるカテゴリのガイドを読み、自分に必要な条件を整理します。</li>
      <li>ガイド内の比較表から、候補のサービスを2〜3件に絞ります。</li>
      <li>各サービスの個別記事と公式サイトで、最新の価格・条件を確認します。</li>
    </ol>
    <p>当サイトの記事は、公開情報にもとづく第三者視点の情報提供です。健康・医療に関する判断は、医師・管理栄養士などの専門家にご相談ください。</p>
  </section>
</main>

''' + FOOTER_HUB + '\n</body>\n</html>\n'


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf8', newline='\n').write(text)


write('guide/index.html', build_hub())
for g in GUIDES:
    write(f"guide/{g['slug']}/index.html", build(g))

# sitemap
for name in ('sitemap.xml', 'sitemap-main.xml'):
    p = os.path.join(ROOT, name)
    t = open(p, encoding='utf8').read()
    add = [BASE + 'guide/'] + [f"{BASE}guide/{g['slug']}/" for g in GUIDES]
    for u in add:
        if f'<loc>{u}</loc>' not in t:
            t = t.replace('</urlset>', f'  <url><loc>{u}</loc><lastmod>{DATE}</lastmod></url>\n</urlset>')
    open(p, 'w', encoding='utf8', newline='\n').write(t)
print('guides:', len(GUIDES) + 1)
