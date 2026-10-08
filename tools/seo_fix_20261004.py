"""SEO監査(2026-10-04)の指摘を一括修正する(一度だけ実行)。
1. 見出し階層: メリット/デメリット/FAQ の h4 → h3
2. 記事に公開日・更新日を表示 (JSON-LDのdatePublished/dateModifiedを利用)
3. about/privacy に OG タグ補完
4. sitemap に lastmod を補完 (記事はdateModified、一覧は配下の最新日)"""
import os, re, glob
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))
BASE = 'https://takuhaishoku-navi.net/'


def rd(f):
    return open(f, encoding='utf8').read()


def wr(f, t):
    open(f, 'w', encoding='utf8', newline='\n').write(t)


mod = {}
for f in sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)):
    rel = os.path.relpath(f, ROOT).replace('\\', '/')
    t = rd(f)
    # 1. h4 -> h3
    t = t.replace('<h4>', '<h3>').replace('</h4>', '</h3>')
    # 2. 公開日・更新日
    pub = re.search(r'"datePublished": "(\d{4})-(\d\d)-(\d\d)', t)
    upd = re.search(r'"dateModified": "(\d{4})-(\d\d)-(\d\d)', t)
    if rel.count('/') == 2 and pub and upd and 'post-meta' not in t:
        fmt = lambda m: (f'{m.group(1)}-{m.group(2)}-{m.group(3)}', f'{m.group(1)}年{int(m.group(2))}月{int(m.group(3))}日')
        (pd, pj), (ud, uj) = fmt(pub), fmt(upd)
        meta = f'<p class="post-meta"><span>公開日 <time datetime="{pd}">{pj}</time></span>'
        if ud != pd:
            meta += f'<span>更新日 <time datetime="{ud}">{uj}</time></span>'
        meta += '</p>'
        t = re.sub(r'(<div class="hero-inner">\s*<h1>.*?</h1>)', lambda m: m.group(1) + '\n      ' + meta, t, count=1, flags=re.S)
        mod[rel] = ud
    # 3. about/privacy のOG補完
    if rel in ('about/index.html', 'privacy/index.html') and 'og:title' not in t:
        ttl = re.search(r'<title>(.*?)</title>', t).group(1)
        desc = re.search(r'<meta name="description" content="(.*?)">', t).group(1)
        og = (f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="宅配食ナビ">\n'
              f'<meta property="og:title" content="{ttl}">\n<meta property="og:description" content="{desc}">\n'
              f'<meta property="og:url" content="{BASE}{rel[:-10]}">\n<meta property="og:locale" content="ja_JP">\n'
              f'<meta name="twitter:card" content="summary">\n')
        t = re.sub(r'(<link rel="canonical"[^>]*>\n)', lambda m: m.group(1) + og, t, count=1)
    wr(f, t)

# 4. sitemap lastmod
sm_path = os.path.join(ROOT, 'sitemap.xml')
sm = rd(sm_path)
cat_latest = {}
for rel, d in mod.items():
    c = rel.split('/')[0]
    cat_latest[c] = max(cat_latest.get(c, ''), d)


def lm(m):
    loc = m.group(1)
    if m.group(2):
        return m.group(0)
    path = loc.replace(BASE, '')
    rel = path + 'index.html'
    if rel in mod:
        d = mod[rel]
    elif path == '':
        d = max(mod.values())
    elif path.count('/') == 1 and path.rstrip('/') in cat_latest:
        d = cat_latest[path.rstrip('/')]
    else:
        return m.group(0)
    return f'<url><loc>{loc}</loc><lastmod>{d}</lastmod></url>'


sm = re.sub(r'<url><loc>(.*?)</loc>(<lastmod>.*?</lastmod>)?</url>', lm, sm)
wr(sm_path, sm)

# CSS
css_path = os.path.join(ROOT, 'assets', 'style.css')
css = rd(css_path)
css = css.replace('.merit-demerit .merit-box h4', '.merit-demerit .merit-box h3').replace('.merit-demerit .demerit-box h4', '.merit-demerit .demerit-box h3')
css = css.replace('.faq-item h4', '.faq-item h3')
if '.post-meta' not in css:
    css += '''
/* 記事の公開日・更新日 */
.post-meta { display: flex; flex-wrap: wrap; gap: 4px 16px; margin: 12px 0 0 !important; padding-right: 0 !important; font-size: 0.78rem; color: var(--color-text-muted); }
.post-meta span::before { content: ""; display: inline-block; width: 7px; height: 7px; margin-right: 6px; border-radius: 50%; background: var(--color-warm); border: 1.5px solid var(--ink); vertical-align: 1px; }
'''
wr(css_path, css)
print('articles with dates:', len(mod))
