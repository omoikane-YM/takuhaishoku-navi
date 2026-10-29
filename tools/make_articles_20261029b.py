"""2026-10-29 新規承認4件(ウェルネスダイニング系)の記事生成 (docs/<cat>/<slug>/index.html)。"""
import os, re, json, html

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
BASE = 'https://takuhaishoku-navi.net/'
NOW = '2026-10-29T20:00:00+09:00'
SPONSOR = None


def read(p):
    return open(os.path.join(ROOT, p), encoding='utf8').read()


def esc(s):
    return html.escape(s, quote=False)


def title_of(path):
    t = re.search(r'<title>(.*?)｜宅配食ナビ', read(path + '/index.html')).group(1)
    return t


def build(a):
    sib = read(a['sibling'] + '/index.html')
    header = re.search(r'<header class="site-header">.*?</header>', sib, re.S).group(0)
    footer = re.search(r'<footer class="site-footer">.*?</footer>', sib, re.S).group(0)
    sponsor = re.search(r'  <section class="intro-block">\s*<h2>スポンサーリンク</h2>.*?</section>', sib, re.S).group(0)
    cat_text = a.get('cat_text') or re.search(r'<p class="breadcrumb">.*?<a href="\.\./">(.*?)</a>', sib, re.S).group(1)
    url = f"{BASE}{a['cat']}/{a['slug']}/"
    ttl = a['title']
    mat = a['cta_mat']

    cta_inline = lambda pad, size, mg: f'''  <p style="text-align:center;margin:{mg};">
    <a href="https://px.a8.net/svt/ejp?a8mat={mat}" rel="nofollow sponsored noopener" target="_blank" style="display:inline-block;background:var(--color-primary);color:#fff;padding:{pad};border-radius:999px;font-weight:700;{size}">{esc(a['cta_text'])}</a>
    <img border="0" width="1" height="1" src="https://www{a['pixel']}.a8.net/0.gif?a8mat={mat}" alt="" style="position:absolute;">
  </p>'''

    faq_json = ',\n'.join(
        '    {\n      "@type": "Question",\n      "name": %s,\n      "acceptedAnswer": {\n        "@type": "Answer",\n        "text": %s\n      }\n    }'
        % (json.dumps(q, ensure_ascii=False), json.dumps(ans, ensure_ascii=False)) for q, ans in a['faq'])

    toc_items = [('about', a['about_h']), ('price', a['price_h']), ('merit', 'メリット'),
                 ('demerit', 'デメリットと対策'), ('recommended', 'こんな人におすすめ'),
                 ('compare', a['compare_h']), ('faq', 'よくある質問')]
    toc = '\n'.join(f'      <li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc_items)

    about = '\n'.join(f'    <p>{p}</p>' for p in a['about'])
    if a.get('notice'):
        about += f"\n    <p class=\"notice-box\">{a['notice']}</p>"
    rows = '\n'.join('          <tr>\n' + '\n'.join(f'            <td>{c}</td>' for c in r) + '\n          </tr>' for r in a['rows'])
    head = ''.join(f'<th>{h}</th>' for h in a['cols'])
    merits = '\n'.join(f'          <li>{m}</li>' for m in a['merits'])
    demerits = '\n'.join(f'          <li>{m}</li>' for m in a['demerits'])
    dsec = '\n'.join(f'    <p>{p}</p>' for p in a['demerit_section'])
    personas = '\n'.join(f'      <li>{p}</li>' for p in a['personas'])
    pers_extra = ''.join(f'\n    <p>{p}</p>' for p in a.get('persona_extra', []))
    faq_html = '\n'.join(
        f'      <div class="faq-item">\n        <h3>Q. {esc(q)}</h3>\n        <p>A. {esc(ans)}</p>\n      </div>' for q, ans in a['faq'])
    related = '\n'.join(f'      <li><a href="{h}">{esc(title_of(p))}</a></li>' for h, p in a['related'])
    b = a['banner']
    banner_img = (f'https://{b["host"]}.a8.net/svt/bgt?aid={b["aid"]}&amp;wid=005&amp;eno=01&amp;mid={b["mid"]}&amp;mc=1')

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="../../assets/favicon-32.png" sizes="32x32">
<link rel="icon" href="../../favicon.ico">
<link rel="apple-touch-icon" href="../../assets/apple-touch-icon.png">
<title>{esc(ttl)}｜宅配食ナビ</title>
<meta name="description" content="{esc(a['desc'])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700&amp;display=swap">
<link rel="stylesheet" href="../../assets/style.css?v=10">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="宅配食ナビ">
<meta property="og:title" content="{esc(ttl)}">
<meta property="og:description" content="{esc(a['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ja_JP">
<meta property="og:image" content="{BASE}assets/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE}assets/og-image.jpg">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type": "ListItem", "position": 1, "name": "トップ", "item": "{BASE}"}},
    {{"@type": "ListItem", "position": 2, "name": "{cat_text}", "item": "{BASE}{a['cat']}/"}},
    {{"@type": "ListItem", "position": 3, "name": "{a['short']}", "item": "{url}"}}
  ]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": {json.dumps(ttl, ensure_ascii=False)},
  "image": "{BASE}assets/og-image.jpg",
  "description": {json.dumps(a['desc'], ensure_ascii=False)},
  "author": {{
    "@type": "Organization",
    "name": "宅配食ナビ"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "宅配食ナビ",
    "url": "{BASE}"
  }},
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{url}"
  }},
  "datePublished": "{NOW}",
  "dateModified": "{NOW}"
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
{faq_json}
  ]
}}
</script>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-9SNYF19K6S"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-9SNYF19K6S');
  document.addEventListener('click', function(e) {{
    var a = e.target.closest && e.target.closest('a[href*="px.a8.net"]');
    if (!a) return;
    gtag('event', 'a8_click', {{
      link_url: a.href,
      link_text: (a.textContent || '').trim().slice(0, 60),
      page_path: location.pathname
    }});
  }});
</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3734732668384938"
     crossorigin="anonymous"></script>
</head>
<body>
{header}
<p class="breadcrumb"><a href="/">トップ</a> &gt; <a href="../">{cat_text}</a> &gt; {esc(a['short'])}</p>

<main>
  <section class="hero">
    <div class="hero-inner">
      <h1>{esc(ttl)}</h1>
      <p class="post-meta"><span>公開日 <time datetime="2026-10-29">2026年10月29日</time></span></p>
      <p class="hero-catch">{esc(a['h1'])}</p>
      <p>{esc(a['lead'])}</p>
    </div>
  </section>

  <div class="hero-banner">
    <span class="pr-tag">PR</span>
    <a href="https://px.a8.net/svt/ejp?a8mat={b['mat']}" rel="nofollow sponsored noopener" target="_blank">
      <img src="{banner_img}" width="{b['w']}" height="{b['h']}" alt="{esc(a['short'])}" loading="lazy">
    </a>
  </div>

  <nav class="toc" aria-label="目次">
    <p>目次</p>
    <ol>
{toc}
    </ol>
  </nav>

  <section class="intro-block" id="about">
    <h2>{esc(a['about_h'])}</h2>
{about}
  </section>

  <section id="price">
    <h2>{esc(a['price_h'])}</h2>
    <p class="status-pending">{a['price_status']}</p>
    <div class="compare-table-wrap">
      <table class="compare-table">
        <thead>
          <tr>{head}</tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <p>{a['price_note']}</p>
  </section>

{cta_inline('12px 28px', 'font-size:0.95rem;', '24px 0')}

  <section id="merit">
    <h2>メリット</h2>
    <div class="merit-demerit">
      <div class="merit-box">
        <h3>良い評判として多く見られる点</h3>
        <ul>
{merits}
        </ul>
      </div>
      <div class="demerit-box">
        <h3>気になる点</h3>
        <ul>
{demerits}
        </ul>
      </div>
    </div>
    <p style="font-size:0.9rem;color:var(--color-text-muted);">{a['merit_note']}</p>
  </section>

  <section id="demerit">
    <h2>デメリットと対策</h2>
{dsec}
  </section>

  <section id="recommended">
    <h2>こんな人におすすめ</h2>
    <ul class="persona-list">
{personas}
    </ul>{pers_extra}
  </section>

  <section class="intro-block" id="compare">
    <h2>{esc(a['compare_h'])}</h2>
    <p>{a['compare']}</p>
  </section>

  <section class="intro-block" id="faq">
    <h2>よくある質問</h2>
    <div class="faq-list">
{faq_html}
    </div>
  </section>

  <p class="affiliate-notice">{a['affiliate']}</p>

{cta_inline('14px 32px', '', '30px 0')}

  <section class="intro-block" id="related">
    <h2>関連記事</h2>
    <ul class="persona-list">
{related}
    </ul>
  </section>

{sponsor}
</main>

{footer}
</body>
</html>
'''


COMMON_AFF = ('本記事はアフィリエイトプログラム(A8.net)を利用しています。紹介内容は公開されている口コミ・公式サイトの情報をもとに第三者視点で構成しており、'
              '運営者自身の利用体験ではありません。掲載時点の情報が変更されている場合があるため、最新の内容は必ず公式サイトでご確認ください。')

COMMON_AFF = ('本記事はアフィリエイトプログラム(A8.net)を利用しています。紹介内容は公開されている口コミ・公式サイトの情報をもとに第三者視点で構成しており、'
              '運営者自身の利用体験ではありません。掲載時点の情報が変更されている場合があるため、最新の内容は必ず公式サイトでご確認ください。')

ARTICLES = [
    dict(
        cat='frozen-meal', slug='meal-select', sibling='frozen-meal/tsukurio', short='ミールセレクト',
        title='ミールセレクトの評判・メリット・デメリット',
        desc='紀ノ国屋・大戸屋などの人気ブランド惣菜から好きなものを選んで組み合わせられる定期宅配「ミールセレクト」について、公式情報をもとに特徴・料金の目安・メリット・デメリットを整理しました。',
        h1='ミールセレクト最大の魅力は、紀ノ国屋・大戸屋・柿安など人気ブランドの惣菜から、好きなものを自分で選んで組み合わせて定期で届けてもらえること',
        lead='有名ブランドの惣菜を選んで届けてもらえるミールセレクト。公式サイトで確認できた取扱ブランドと料金の目安をもとに、メリットとデメリットを第三者視点で整理しました。',
        about_h='ミールセレクトとは',
        about=[
            'ミールセレクトは、有名ブランドの惣菜を自分で選んで組み合わせ、定期で届けてもらえる宅配サービスです。公式の案内では、紀ノ国屋、大戸屋、RF1など、よく知られたブランドの惣菜240種類以上から選べるとされています。',
            '公式サイトには、紀ノ国屋、大戸屋、柿安、RF1、RFFF、deria、にんべん、神戸コロッケ、牛たん炙焼き利久、まつおか、ISETAN MITSUKOSHI THE FOODなど、多数のブランドが並んでいます。管理栄養士が夕食の献立を提案するとも案内されています。',
            'コースは、主菜・副菜、主食・主菜・副菜、副菜のように、食卓の組み立て方に合わせて選ぶ形式です。公式の案内では、冷蔵と冷凍を組み合わせて届けることもできるとされています。',
        ],
        notice='お届けエリアや配送方法（冷蔵・冷凍）、送料、スキップや解約の条件は、公式サイトのトップで確認できなかった項目があります。申し込み前に、公式サイトの注文方法やご案内ページで必ずご確認ください。',
        price_h='料金の目安', cols=['コース', '対象', '3日分の価格目安（公式サイト掲載）'],
        rows=[['主菜・副菜コース', 'ファミリー', '9,000〜9,999円'],
              ['主菜・副菜コース', '大人2人', '6,000〜6,999円'],
              ['主食・主菜・副菜コース', '大人1人', '3,400〜3,999円'],
              ['主食・主菜・副菜コース', '大人2人', '6,800〜7,999円'],
              ['副菜コース', 'ファミリー', '6,000〜6,999円'],
              ['副菜コース', '大人2人', '4,000〜4,999円']],
        price_status='2026年10月時点で公式サイトから確認できた定期プランの価格帯の目安です。価格・送料・内容は変更される場合があるため、最新の情報は必ず公式サイトでご確認ください。',
        price_note='個別商品の例として、主菜・副菜セット（ファミリー）が3,234〜3,368円、おすすめ商品は246円〜と案内されています。送料は公式サイトのトップでは確認できませんでした。',
        cta_text='ミールセレクトを公式サイトで見る',
        cta_mat='4BECH2+16VBF6+5V2M+5YJRM', pixel='16',
        banner=dict(mat='4BECH2+16VBF6+5V2M+5YZ75', host='www23', aid='261009830072', mid='s00000027355001003000', w=300, h=250),
        merits=['紀ノ国屋・大戸屋・柿安など、名の知られたブランドの惣菜から好きなものを選べる',
                '主菜・副菜、主食・主菜・副菜、副菜のコースがあり、食卓の足りない部分だけ補う使い方もできる',
                '管理栄養士が夕食の献立を提案すると案内されており、組み合わせに迷いにくい',
                '食べたいものを自分で選べるので、苦手なメニューが入りにくい'],
        demerits=['3日分の価格目安は数千円〜1万円前後で、家族の人数が多いと負担が大きくなりやすい',
                  '送料・配送方法・解約条件は公式サイトのトップで確認できず、申し込み前に調べる手間がある'],
        merit_note='まずは大人1人または2人向けのコースなど小さめの単位から試し、量や好みを確かめてから家族向けに広げる、といった検討の仕方が考えられます。',
        demerit_section=['ブランド惣菜は、自炊や一般的な宅配弁当と比べて1食あたりの単価が高めになりやすい傾向があります。コースの価格帯を確認し、毎日使うのか、忙しい日だけ使うのかを先に決めておくと続けやすくなります。',
                         '送料、お届け曜日、スキップや解約の方法といった条件は、申し込み画面や公式のご案内ページで事前に確認してください。冷蔵品と冷凍品が混ざる場合は、冷蔵庫・冷凍庫の空き容量も確認しておくと安心です。'],
        personas=['有名ブランドの惣菜を、自宅でゆっくり楽しみたい方',
                  '同じメニューの繰り返しに飽きやすく、自分で選べる定期宅配を探している方',
                  '共働きや子育てで夕食づくりの時間を減らしたい方',
                  '副菜だけ、主菜だけなど、足りない部分だけ補いたい方'],
        persona_extra=['毎食を置き換えず、忙しい平日の夕食だけ使うなど、無理のない範囲で取り入れる使い方が考えられます。'],
        compare_h='他の惣菜・冷凍宅配との違いと選び方',
        compare='ミールセレクトは複数ブランドの惣菜から選べる点が特徴です。シェフと管理栄養士が監修したおかずを冷蔵で選びたい場合は<a href="../tsukurio/">ツクリオ</a>、レシピ動画メディアDELISH KITCHENプロデュースの宅配弁当を比べたい場合は<a href="../meals/">Meals</a>も合わせて比較すると、自分に合うサービスを選びやすくなります。',
        faq=[('どんなブランドの惣菜がありますか？', '公式サイトでは、紀ノ国屋、大戸屋、柿安、RF1、RFFF、deria、にんべん、神戸コロッケ、牛たん炙焼き利久、まつおか、ISETAN MITSUKOSHI THE FOODなどのブランドが紹介されています。'),
             ('料金の目安はどのくらいですか？', '公式サイトの定期プランでは、3日分の価格目安として、主食・主菜・副菜コースの大人1人が3,400〜3,999円、大人2人が6,800〜7,999円と案内されています。'),
             ('メニューは自分で選べますか？', '公式の案内では、240種類以上の惣菜から好きなものを選んで組み合わせられるとされています。'),
             ('送料や解約条件はどこで確認できますか？', '公式サイトのトップでは確認できなかったため、注文方法やご案内のページ、申し込み画面で事前にご確認ください。')],
        affiliate=COMMON_AFF,
        related=[('../tsukurio/', 'frozen-meal/tsukurio'), ('../meals/', 'frozen-meal/meals')],
    ),
]

if __name__ == '__main__':
    for a in ARTICLES:
        d = os.path.join(ROOT, a['cat'], a['slug'])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'index.html'), 'w', encoding='utf8', newline='\n') as f:
            f.write(build(a))
        print('wrote', a['cat'], a['slug'])
