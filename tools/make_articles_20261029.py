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
        cat='senior-meal', slug='wellness-dining', sibling='senior-meal/kenko-chokkyubin', short='ウェルネスダイニング',
        title='ウェルネスダイニングの評判・メリット・デメリット',
        desc='食事制限に配慮した冷凍の宅配食「ウェルネスダイニング」について、公式情報をもとにラインナップ・管理栄養士への無料相談・やわらか宅配食などのメリットとデメリットを整理しました。',
        h1='ウェルネスダイニング最大の魅力は、塩分・糖質・たんぱく質などの調整や食べやすさに配慮した宅配食を、管理栄養士に無料で相談しながら選べること',
        lead='食事制限に配慮した冷凍の宅配食を全国へ届けるウェルネスダイニング。公式サイトで確認できたラインナップと相談体制をもとに、メリットとデメリットを第三者視点で整理しました。',
        about_h='ウェルネスダイニングとは',
        about=[
            'ウェルネスダイニングは、ウェルネスダイニング株式会社が運営する、食事制限に配慮した宅配食の通販サイトです。公式サイトによると、制限食に特化して15年間で3,000万食以上を届けてきたとされています（2026年7月末時点）。メニューは管理栄養士が監修しており、冷凍でまとめて届き、電子レンジで温めて食べる形式です。',
            '主力の「気配り宅配食」は、1食に主菜1品と副菜3品が付く構成です。腎臓病の方向けのたんぱく・塩分調整、糖尿病や血糖値が気になる方向けの糖質・カロリー制限、高血圧が気になる方向けの塩分制限、脂質異常症やコレステロールが気になる方向けの脂質制限、栄養バランスを整えたい方向けのコースなど、目的別に用意されています。',
            'このほか、噛む力・飲み込む力が弱くなった方向けの「やわらか宅配食」（レベル1〜3）、脂質を抑えながらたんぱく質を摂れる「たんぱく質が摂れる脂質調整食」、野菜をとりやすくした「野菜を楽しむ スープ食」などのシリーズがあります。',
        ],
        notice='特定の疾患の治療や症状の改善を目的とした食事は、医師や管理栄養士の指導のもとで行うことが大切です。本記事は治療・改善を保証するものではありません。持病のある方や食事制限の指示を受けている方は、利用前に主治医または管理栄養士にご相談ください。',
        price_h='ラインナップと選び方', cols=['シリーズ', '特徴（公式情報）', '向いている方の目安'],
        rows=[['気配り宅配食', '主菜1品＋副菜3品。たんぱく・塩分調整、糖質・カロリー制限、塩分制限、脂質制限、栄養バランスなど目的別', '食事の制限や栄養バランスが気になる方'],
              ['<a href="https://px.a8.net/svt/ejp?a8mat=4BCBRH+E0A98Y+30S4+BX3J6" rel="nofollow sponsored noopener" target="_blank">やわらか宅配食</a>', '3段階のやわらかさ（レベル1：容易にかめる／レベル2：歯ぐきでつぶせる／レベル3：舌でつぶせる）', '噛む力・飲み込む力が弱くなってきた方、そのご家族'],
              ['<a href="https://px.a8.net/svt/ejp?a8mat=4BCBRH+E1H4GI+30S4+ZQFQA" rel="nofollow sponsored noopener" target="_blank">たんぱく質が摂れる脂質調整食</a>', '十六穀ご飯120g付きの場合で、たんぱく質30g以上・脂質10g以下と案内', 'たんぱく質をとりつつ脂質を控えたい方'],
              ['<a href="https://px.a8.net/svt/ejp?a8mat=4BCBRK+169VTE+30S4+NVHCY" rel="nofollow sponsored noopener" target="_blank">野菜を楽しむ スープ食</a>', '管理栄養士監修。1食で1日に必要な野菜の半分、15種類以上の野菜を摂れると案内', '野菜が不足しがちな方']],
        price_status='商品ごとの価格・セット内容・送料は、コースや時期によって異なります。最新の情報は必ず公式サイトでご確認ください。',
        price_note='注文はWEBと電話で24時間・年中無休で受け付けており、お届け日時の指定ができると案内されています。対象となる商品や購入方法（初回・定期など）の条件は商品ごとに異なるため、注文前に公式サイトの表示をご確認ください。',
        cta_text='ウェルネスダイニングを公式サイトで見る',
        cta_mat='4BCBRH+EAEMJ6+30S4+61Z82', pixel='10',
        banner=dict(mat='4BCBRH+EAEMJ6+30S4+62U35', host='www21', aid='260915597864', mid='s00000014098001021000', w=300, h=250),
        merits=['目的別（たんぱく・塩分調整、糖質・カロリー制限、塩分制限、脂質制限など）にコースが分かれており、選ぶ基準が分かりやすい',
                '管理栄養士23名が在籍し、購入の有無にかかわらず無料・予約不要・回数制限なしで栄養相談ができると案内されている',
                '3段階のやわらか宅配食があり、噛む力・飲み込む力に合わせて選べる',
                '冷凍で届くのでストックでき、電子レンジで温めるだけで食べられる'],
        demerits=['価格や送料が公式サイトのトップページでは確認しづらく、コースごとに比較する手間がある',
                  '冷凍庫の保管スペースが必要。コースが多く、自分に合うものを選ぶのに迷いやすい'],
        merit_note='どのコースが合うか迷う場合は、まず管理栄養士の無料相談を使って、食事の目的や制限の内容を伝えてから選ぶ方法が考えられます。',
        demerit_section=['コースは制限の目的別・やわらかさ別・シリーズ別と種類が多く、はじめは選び方に迷うかもしれません。主治医から食事の指示を受けている場合は、その内容をメモして相談窓口に伝えると、候補を絞りやすくなります。',
                         '料金や送料は商品によって異なるため、複数のコースを試したい場合は、セット内容と合計金額を注文前に公式サイトで確認しましょう。冷凍庫の空きスペースも事前にチェックしておくと安心です。'],
        personas=['塩分・糖質・たんぱく質など、食事の制限を意識して宅配食を探している方',
                  '管理栄養士に相談しながらサービスを選びたい方',
                  '親が噛む力・飲み込む力に不安があり、やわらかい食事を探しているご家族',
                  '自炊の手間を減らしつつ、栄養バランスを整えたい一人暮らしや共働きの方'],
        persona_extra=['やわらか宅配食は、実際に召し上がる方がご高齢の場合、ご家族が代わりに注文するケースも多いとされています。かたさの目安を確認して、食べる方に合ったレベルを選びましょう。'],
        compare_h='他の制限食・やわらか食との違いと選び方',
        compare='ウェルネスダイニングは、制限食とやわらか食の両方を同じサービス内で選べる点が特徴です。糖質・カロリー・塩分・たんぱく質の制限からやわらか食までを比べたい場合は<a href="../kenko-chokkyubin/">健康直球便</a>、4段階の食形態から選びたい場合は<a href="../shokurakuzen/">食楽膳</a>、塩分・カロリー・たんぱく質の制限食なら<a href="../medifoods/">メディカルフードサービス</a>も合わせて比較すると、自分に合うサービスを選びやすくなります。',
        faq=[('管理栄養士への相談は無料ですか？', '公式サイトでは、管理栄養士23名が在籍し、購入の有無にかかわらず無料で、予約不要・回数制限なしで相談できると案内されています。'),
             ('やわらか宅配食のレベルはどう違いますか？', 'レベル1は容易にかめるやわらかさ、レベル2は歯ぐきでつぶせるやわらかさ、レベル3は舌でつぶせるやわらかさと案内されています。'),
             ('全国に配送してもらえますか？', '公式サイトでは全国へ配送していると案内されています。注文はWEBと電話で24時間・年中無休で受け付けており、お届け日時の指定もできます。'),
             ('食事制限がある場合、どのコースを選べばよいですか？', 'コースは目的別に分かれていますが、制限の内容は人によって異なります。主治医や管理栄養士の指示を確認したうえで、公式サイトの無料栄養相談も活用して選びましょう。')],
        affiliate=COMMON_AFF + '特定の疾患の治療や症状の改善を保証するものではありません。',
        related=[('../kenko-chokkyubin/', 'senior-meal/kenko-chokkyubin'), ('../shokurakuzen/', 'senior-meal/shokurakuzen')],
    ),
]

if __name__ == '__main__':
    for a in ARTICLES:
        d = os.path.join(ROOT, a['cat'], a['slug'])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'index.html'), 'w', encoding='utf8', newline='\n') as f:
            f.write(build(a))
        print('wrote', a['cat'], a['slug'])
