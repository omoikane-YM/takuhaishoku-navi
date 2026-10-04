"""全ページSEO監査。 python tools/seo_audit.py [--json out.json]
チェック: title/description長と重複、h1、canonical、OG、JSON-LD妥当性、画像alt、
内部リンク(孤立ページ・被リンク数)、リンク切れ、sitemap整合、広告リンクのrel、本文量、FAQ有無。"""
import os, re, sys, json, glob
from collections import defaultdict, Counter
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))
BASE = 'https://omoikane-ym.github.io/takuhaishoku-navi/'


class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.title = ''; s.in_title = False; s.meta = {}; s.canon = None; s.h = []
        s.cur_h = None; s.links = []; s.imgs = []; s.jsonld = []; s.in_ld = False
        s.ld_buf = ''; s.text = []; s.skip = 0; s.html_lang = None; s.in_main = False
        s.cur_a = None

    def handle_starttag(s, t, a):
        a = dict(a)
        if t == 'html': s.html_lang = a.get('lang')
        if t == 'title': s.in_title = True
        if t == 'meta':
            k = a.get('name') or a.get('property')
            if k: s.meta[k] = a.get('content', '')
        if t == 'link' and a.get('rel') == 'canonical': s.canon = a.get('href')
        if t in ('h1', 'h2', 'h3', 'h4'): s.cur_h = [t, '']
        if t == 'a' and a.get('href'):
            s.links.append(dict(href=a['href'], rel=a.get('rel', ''), main=s.in_main)); s.cur_a = s.links[-1]
        if t == 'img': s.imgs.append(a)
        if t == 'script':
            if a.get('type') == 'application/ld+json': s.in_ld = True; s.ld_buf = ''
            s.skip += 1
        if t == 'style': s.skip += 1
        if t == 'main': s.in_main = True

    def handle_endtag(s, t):
        if t == 'title': s.in_title = False
        if t in ('h1', 'h2', 'h3', 'h4') and s.cur_h: s.h.append(tuple(s.cur_h)); s.cur_h = None
        if t == 'script':
            if s.in_ld: s.jsonld.append(s.ld_buf); s.in_ld = False
            s.skip -= 1
        if t == 'style': s.skip -= 1
        if t == 'main': s.in_main = False
        if t == 'a': s.cur_a = None

    def handle_data(s, d):
        if s.in_title: s.title += d
        if s.in_ld: s.ld_buf += d
        if s.cur_h: s.cur_h[1] += d
        if s.in_main and not s.skip: s.text.append(d)


def url_of(rel):
    d = os.path.dirname(rel).replace('\\', '/')
    return BASE + (d + '/' if d else '')


def main():
    pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        rel = os.path.relpath(f, ROOT).replace('\\', '/')
        p = P(); p.feed(open(f, encoding='utf8').read())
        pages[rel] = p
    issues = defaultdict(list)
    inbound = defaultdict(set)
    sm = set(re.findall(r'<loc>(.*?)</loc>', open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf8').read()))
    titles = defaultdict(list); descs = defaultdict(list)

    for rel, p in pages.items():
        u = url_of(rel)
        is404 = rel == '404.html'
        t = p.title.strip(); d = p.meta.get('description', '')
        titles[t].append(rel); descs[d].append(rel)
        if not is404:
            if len(t) > 40: issues['title長すぎ(>40字)'].append(f'{rel} ({len(t)})')
            if len(t) < 15: issues['title短い(<15字)'].append(f'{rel} ({len(t)})')
            if not d: issues['description無し'].append(rel)
            elif len(d) > 120: issues['description長すぎ(>120字)'].append(f'{rel} ({len(d)})')
            elif len(d) < 50: issues['description短い(<50字)'].append(f'{rel} ({len(d)})')
            if p.canon != u: issues['canonical不一致'].append(f'{rel}: {p.canon}')
            if u not in sm: issues['sitemap未掲載'].append(rel)
            for k in ('og:title', 'og:description', 'og:url'):
                if k not in p.meta: issues[f'{k}無し'].append(rel)
        if p.html_lang != 'ja': issues['lang未指定'].append(rel)
        if 'viewport' not in p.meta: issues['viewport無し'].append(rel)
        if 'noindex' in p.meta.get('robots', ''): issues['noindex'].append(rel)
        h1 = [x for x in p.h if x[0] == 'h1']
        if len(h1) != 1: issues['h1が1個でない'].append(f'{rel} ({len(h1)})')
        else:
            if len(h1[0][1].strip()) > 70: issues['h1長すぎ(>70字)'].append(f'{rel} ({len(h1[0][1].strip())})')
        # 見出し階層(h2→h4飛びなど)
        prev = 1
        for lv, _ in p.h:
            n = int(lv[1])
            if n > prev + 1: issues['見出し階層の飛び'].append(f'{rel}: {lv} after h{prev}'); break
            prev = n
        for ld in p.jsonld:
            try: json.loads(ld)
            except Exception as e: issues['JSON-LD不正'].append(f'{rel}: {e}')
        for im in p.imgs:
            if 'alt' not in im: issues['img alt属性無し'].append(f'{rel}: {im.get("src", "")[:60]}')
            elif im['alt'].strip() == '' and im.get('width') not in ('1', None):
                issues['img alt空(装飾でない可能性)'].append(f'{rel}: {im.get("src", "")[:60]}')
        body = ''.join(p.text)
        n = len(re.sub(r'\s+', '', body))
        if n < 800 and not is404 and rel.count('/') >= 2: issues['記事本文が短い(<800字)'].append(f'{rel} ({n})')
        if rel.count('/') >= 2 and 'FAQPage' not in ''.join(p.jsonld): issues['記事にFAQPage無し'].append(rel)
        for l in p.links:
            h = l['href']
            if re.match(r'https?://', h):
                host = re.match(r'https?://([^/]+)', h).group(1)
                if ('a8.net' in host or 'rakuten' in host) and 'sponsored' not in l['rel'] and 'nofollow' not in l['rel']:
                    issues['広告リンクにrel=sponsored/nofollow無し'].append(f'{rel}: {h[:60]}')
                if h.startswith('http://') and 'hbb.afl.rakuten' not in h:
                    issues['http(非SSL)リンク'].append(f'{rel}: {h[:60]}')
                continue
            if re.match(r'(mailto:|tel:|#|javascript:|data:)', h): continue
            path = h.split('#')[0].split('?')[0]
            if not path: continue
            if path.startswith('/takuhaishoku-navi/'): tgt = path[len('/takuhaishoku-navi/'):]
            else: tgt = os.path.normpath(os.path.join(os.path.dirname(rel), path)).replace('\\', '/')
            if tgt in ('', '.'): tgt = 'index.html'
            full = os.path.join(ROOT, tgt)
            if os.path.isdir(full): tgt = tgt.rstrip('/') + '/index.html'
            if not os.path.exists(os.path.join(ROOT, tgt)):
                issues['リンク切れ'].append(f'{rel}: {h}')
            elif tgt != rel and l['main']:
                inbound[tgt].add(rel)
    for t, rs in titles.items():
        if len(rs) > 1: issues['title重複'].append(f'{t}: {rs}')
    for d, rs in descs.items():
        if d and len(rs) > 1: issues['description重複'].append(f'{d[:30]}...: {rs}')
    # 孤立ページ・被リンク
    for rel in pages:
        if rel in ('404.html', 'index.html'): continue
        c = len(inbound.get(rel, ()))
        if c == 0: issues['孤立ページ(本文内被リンク0)'].append(rel)
        elif c == 1 and rel.count('/') >= 2: issues['記事への本文内被リンクが1のみ'].append(rel)
    for u in sm:
        r = u.replace(BASE, '') + 'index.html'
        if not os.path.exists(os.path.join(ROOT, r)): issues['sitemapに存在しないページ'].append(u)

    print(f'ページ数: {len(pages)}  sitemap: {len(sm)}')
    for k in sorted(issues, key=lambda x: -len(issues[x])):
        v = issues[k]
        print(f'\n■ {k}: {len(v)}件')
        for x in v[:12]: print('   -', x)
        if len(v) > 12: print(f'   ... 他{len(v) - 12}件')
    if not issues: print('問題なし')
    if '--json' in sys.argv:
        json.dump(issues, open(sys.argv[sys.argv.index('--json') + 1], 'w', encoding='utf8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
