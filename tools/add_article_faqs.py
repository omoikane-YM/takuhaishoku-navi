"""個別記事にFAQ(HTML + FAQPage JSON-LD + 目次)を追加する。
使い方: python tools/add_article_faqs.py <tools/faq/ 内のモジュール名>...   例: python tools/add_article_faqs.py frozen_meal
FAQPage がすでにある記事はスキップ(冪等)。FAQは記事本文・公式サイトで確認できた事実のみで作ること。"""
import os, re, sys, json, html, importlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faq'))
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
done = 0
for mod in sys.argv[1:]:
    FAQ = importlib.import_module(mod).FAQ
    for key, qa in FAQ.items():
        p = os.path.join(ROOT, key, 'index.html')
        t = open(p, encoding='utf8').read()
        if '"FAQPage"' in t:
            print('skip', key)
            continue
        assert 3 <= len(qa) <= 8, key
        faq_html = '\n'.join(
            f'      <div class="faq-item">\n        <h3>Q. {html.escape(q, quote=False)}</h3>\n        <p>A. {html.escape(a, quote=False)}</p>\n      </div>' for q, a in qa)
        sec = f'''  <section class="intro-block" id="faq">
    <h2>よくある質問</h2>
    <div class="faq-list">
{faq_html}
    </div>
  </section>

'''
        marker = '  <p class="affiliate-notice">'
        assert t.count(marker) == 1, (key, t.count(marker))
        t = t.replace(marker, sec + marker, 1)
        m = re.search(r'(<nav class="toc".*?)(\s*</ol>)', t, re.S)
        assert m, key
        t = t.replace(m.group(0), m.group(1) + '\n      <li><a href="#faq">よくある質問</a></li>' + m.group(2), 1)
        ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
        script = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=2) + '\n</script>\n'
        g = '<!-- Google tag (gtag.js) -->'
        assert t.count(g) == 1, key
        t = t.replace(g, script + g, 1)
        open(p, 'w', encoding='utf8', newline='\n').write(t)
        done += 1
        print('added', key, len(qa))
print('total', done)
