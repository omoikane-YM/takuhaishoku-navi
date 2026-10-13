"""2026-10-13 SEO見直しの一括修正(冪等)。
- 全ページ: og:image / twitter:image 追加、twitter:card を summary_large_image に
- Article構造化データに image を追加
- 個別記事: h1 を「<名>の評判・メリット・デメリット」(titleと同形)に短縮し、元の長文は .hero-catch として直下に残す
- 楽天バナーの http 画像を https に(混在コンテンツ解消)
- トップ: Organization 構造化データ追加
- style.css に .hero-catch を追加し、?v=8 → ?v=9 に更新
- sitemap の lastmod を 2026-10-13 に更新
"""
import os, re, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
B = 'https://takuhaishoku-navi.net/'
OG = B + 'assets/og-image.jpg'
TODAY = '2026-10-13'
stat = dict(og=0, h1=0, ld=0, http=0, css=0)

# ---- CSS ----
p = os.path.join(ROOT, 'assets', 'style.css')
css = open(p, encoding='utf8').read()
if '.hero-catch' not in css:
    css = css.replace('.hero p { color: #4a3f35; max-width: 680px; margin: 0; padding-right: 40px; }',
                      '.hero p { color: #4a3f35; max-width: 680px; margin: 0; padding-right: 40px; }\n'
                      '.hero p.hero-catch { color: var(--ink); font-weight: 700; font-size: 1.02rem; line-height: 1.7; margin: 8px 0 10px; }')
    assert '.hero-catch' in css
    open(p, 'w', encoding='utf8', newline='\n').write(css)

for f in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
    rel = os.path.relpath(f, ROOT).replace(os.sep, '/')
    s = open(f, encoding='utf8').read()
    o = s

    s = s.replace('style.css?v=8', 'style.css?v=9')

    # og:image
    if rel != '404.html' and 'og:image' not in s:
        s = s.replace('<meta property="og:locale" content="ja_JP">',
                      '<meta property="og:locale" content="ja_JP">\n'
                      f'<meta property="og:image" content="{OG}">\n'
                      '<meta property="og:image:width" content="1200">\n'
                      '<meta property="og:image:height" content="630">', 1)
        s = s.replace('<meta name="twitter:card" content="summary">',
                      '<meta name="twitter:card" content="summary_large_image">\n'
                      f'<meta name="twitter:image" content="{OG}">', 1)
        assert 'og:image' in s, rel
        stat['og'] += 1

    # Article image
    if '"@type": "Article"' in s and '"image":' not in s:
        s = re.sub(r'(  "headline": [^\n]*,\n)', lambda m: m.group(1) + f'  "image": "{OG}",\n', s, count=1)
        if '"image":' in s:
            stat['ld'] += 1

    # 個別記事のh1
    parts = rel.split('/')
    if len(parts) == 3 and parts[0] != 'guide' and 'hero-catch' not in s:
        m = re.search(r'<h1>(.*?)</h1>', s, re.S)
        t = re.search(r'<title>(.*?)｜宅配食ナビ</title>', s)
        if m and t and m.group(1) != t.group(1):
            old_h1, new_h1 = m.group(1), t.group(1)
            block = f'<h1>{new_h1}</h1>'
            after = s[m.end():]
            pm = re.match(r'\s*<p class="post-meta">.*?</p>', after, re.S)
            catch = f'\n      <p class="hero-catch">{old_h1}</p>'
            if pm:
                s = s[:m.start()] + block + pm.group(0) + catch + after[pm.end():]
            else:
                s = s[:m.start()] + block + catch + after
            stat['h1'] += 1

    # http画像
    if 'http://hbb.afl.rakuten.co.jp' in s:
        s = s.replace('http://hbb.afl.rakuten.co.jp', 'https://hbb.afl.rakuten.co.jp')
        stat['http'] += 1

    # トップ: Organization
    if rel == 'index.html' and '"Organization"' not in s:
        org = ('<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "Organization",\n'
               '  "name": "宅配食ナビ",\n  "url": "%s",\n  "logo": "%sassets/favicon-512.png"\n}\n</script>\n' % (B, B))
        s = s.replace('<!-- Google tag (gtag.js) -->', org + '<!-- Google tag (gtag.js) -->', 1)

    if s != o:
        open(f, 'w', encoding='utf8', newline='\n').write(s)

# sitemap
p = os.path.join(ROOT, 'sitemap.xml')
t = open(p, encoding='utf8').read()
t = re.sub(r'<lastmod>[^<]*</lastmod>', f'<lastmod>{TODAY}</lastmod>', t)
open(p, 'w', encoding='utf8', newline='\n').write(t)
print(stat)
