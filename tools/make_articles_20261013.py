"""2026-10-13 新規承認2件の記事生成 (docs/<cat>/<slug>/index.html)。"""
import os, re, json, html

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
BASE = 'https://takuhaishoku-navi.net/'
NOW = '2026-10-13T18:00:00+09:00'
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
      <p class="post-meta"><span>公開日 <time datetime="2026-10-13">2026年10月13日</time></span></p>
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
        cat='frozen-meal', slug='muscle-deli', sibling='frozen-meal/fit-food-home', short='Muscle Deli（マッスルデリ）',
        title='Muscle Deli（マッスルデリ）の評判・メリット・デメリット',
        desc='管理栄養士監修の高タンパク・低脂質なボディメイク向け冷凍宅配食「Muscle Deli（マッスルデリ）」について、公式情報をもとに栄養基準・料金・メリット・デメリットを整理しました。',
        h1='Muscle Deli最大の魅力は、目的別の4プランごとにカロリー・タンパク質・脂質・糖質の基準が公開された冷凍宅配食を、電子レンジで温めるだけで食べられること',
        lead='株式会社YOUR MEALが運営するボディメイク向けの冷凍宅配食。公式サイトで公開されている栄養基準・料金・解約条件をもとに、メリットとデメリットを第三者視点で整理しました。',
        about_h='Muscle Deli（マッスルデリ）とは',
        about=[
            'Muscle Deli（マッスルデリ）は、株式会社YOUR MEALが運営する、ボディメイクの食事管理をサポートする冷凍宅配食です。冷凍で届き、冷凍庫で保管して、食べるときは電子レンジで温めます。メニューは50種類以上（鶏肉、パスタ、魚、和食、エスニックなど）と案内されています。',
            '公式サイトによると、プランは目的別に4つ。1食あたりの栄養基準が公開されており、LEAN（女性向け）は350〜450kcal・タンパク質30g以上・脂質15g以下・糖質35g以下、MAINTAIN（男性向け）は450〜550kcal・タンパク質35g以上・脂質20g以下・糖質55g以下、GAIN（増量向け）は550〜750kcal・タンパク質50g以上・脂質25g以下・糖質75g以下、LOW CARB（低糖質）は350kcal以上・タンパク質20g以上・糖質15g以下とされています。',
            'お弁当のほか、プロテインスープなどのその他商品も用意されています。1日の目標カロリーとPFCバランスを確認できる食事診断ツールも公式サイトにあります。',
        ],
        notice='栄養基準は公式サイトの記載にもとづく目安で、体重や体型の変化を保証するものではありません。食事制限や持病のある方、妊娠中・授乳中の方は、利用前に医師・管理栄養士などの専門家にご相談ください。アレルギー表示は特定原材料8品目＋準ずる20品目の計28品目に対応していますが、同一ラインで製造しているため完全な除去はできません。',
        price_h='料金と継続割プラン', cols=['契約プラン', '割引率（税抜の商品代金に適用）', '1食あたり（MAINTAIN 5食・隔週お届けの例／税込）'],
        rows=[['通常定期', '10%OFF', '1,164円'],
              ['定期6回プラン', '2〜6回目13%OFF／7〜18回目15%OFF／19回目以降20%OFF', '1,125円'],
              ['定期12回プラン', '2〜12回目15%OFF／13回目以降20%OFF', '1,099円'],
              ['定期24回プラン', '2回目以降ずっと20%OFF', '1,035円']],
        price_status='2026年10月時点で公式サイトから確認できた内容の目安です。割引率・価格・送料はキャンペーンなどで変わる場合があるため、最新の情報は必ず公式サイトでご確認ください。',
        price_note='どのプランも1回目は初回お届け特典として25%OFFと案内されています。送料（税込）は5食1,200円、10食・15食1,420円、北海道・沖縄県は1,530円〜です。契約回数に満たずに解約すると、違約金として直近1回分の商品代金がかかる点には注意が必要です。',
        cta_text='ボディメイクフード「Muscle Deli」を公式サイトで見る',
        cta_mat='4BECH2+2J3FF6+4CPY+5YJRM', pixel='16',
        banner=dict(mat='4BECH2+2J3FF6+4CPY+62MDD', host='www23', aid='261009830153', mid='s00000020311001020000', w=300, h=250),
        merits=['LEAN・MAINTAIN・GAIN・LOW CARBの4プランで、1食あたりの栄養基準が公開されており選ぶ基準が分かりやすい',
                'メニューは50種類以上。電子レンジで温めるだけで、調理や洗い物の手間が少ない',
                '食数や配送サイクルを選べ、マイページから次回配送を1回スキップできる',
                '契約回数が多いほど割引率が上がり、初回は25%OFF。支払いはクレジットカード・Amazon Pay・後払いから選べる'],
        demerits=['継続割プランは契約回数に満たない解約で違約金（直近1回分の商品代金）がかかり、送料も別途必要',
                  '冷凍で届くため、冷凍庫の空きスペースが必要。不在時の保管期間はクール宅急便で3日間'],
        merit_note='価格面では、まず通常定期で食べ心地を確かめてから、続けられそうなら継続割プランへ切り替えるといった検討の仕方も考えられます。プランの途中変更は可能ですが、契約回数の変更はできないと案内されています。',
        demerit_section=['継続割プランは契約回数に満たない場合に違約金がかかり、解約は次回発送の5日前までに専用フォームから手続きします。配送日時や周期の変更もお届け予定日の5日前までのため、余裕をもって管理することが大切です。',
                         '冷凍商品は、冷凍対応の宅配ボックスでのみ受け取れます。通常の宅配ボックスは利用できず、不在票の保管期間（クール宅急便は3日間）を過ぎると商品は廃棄され、再発送はできないと案内されています。受け取れる日時を確認して設定しましょう。'],
        personas=['タンパク質やカロリーの目安を確認しながら、日々の食事管理をしたい方',
                  'トレーニングや運動の習慣があり、食事の準備に時間をかけたくない方',
                  '栄養基準が公開されているサービスから、自分の目的に合うものを選びたい方',
                  '自炊の手間を減らしつつ、メニューのバリエーションも確保したい方'],
        persona_extra=['毎食を置き換える必要はなく、忙しい平日の食事だけ使うなど、無理のない範囲で取り入れる使い方が考えられます。'],
        compare_h='他の冷凍宅配食との違いと選び方',
        compare='Muscle Deliは目的別に栄養基準が決められている点が特徴です。管理栄養士監修のメニューを幅広く選びたいなら<a href="../fit-food-home/">FIT FOOD HOME</a>、バランスの良い食事を日常使いしたいなら<a href="../greenspoon/">GREEN SPOON</a>なども比較すると、自分に合うサービスを選びやすくなります。',
        faq=[('Muscle Deliのプランは何が違いますか？', '公式サイトでは、LEAN（女性向け）、MAINTAIN（男性向け）、GAIN（増量向け）、LOW CARB（低糖質）の4プランがあり、1食あたりのカロリー・タンパク質・脂質・糖質の基準がそれぞれ異なります。'),
             ('スキップや解約はできますか？', 'マイページから次回配送を1回スキップできます。解約はお届け予定日の5日前までに専用フォームから手続きします。継続割プランは契約回数に満たない場合、直近1回分の商品代金が違約金として発生します。'),
             ('送料はいくらですか？', '公式サイトでは、5食1,200円、10食・15食1,420円（いずれも税込）、北海道・沖縄県は1,530円〜と案内されています。'),
             ('冷凍の宅配ボックスで受け取れますか？', '冷凍商品は冷凍対応の宅配ボックスでのみ受け取れると案内されています。通常の宅配ボックスは利用できません。')],
        affiliate=COMMON_AFF + '栄養基準に関する記述は、体重・体型の変化や特定の健康上の効果を保証するものではありません。',
        related=[('../fit-food-home/', 'frozen-meal/fit-food-home'), ('../greenspoon/', 'frozen-meal/greenspoon')],
    ),
    dict(
        cat='delivery-box', cat_text='宅配ボックス', slug='takuhai-box-meihinkan', sibling='kitchen-goods/food-sealer', short='宅配ボックス名品館',
        title='宅配ボックス名品館（ルスネコボックス）の評判・メリット・デメリット',
        desc='工事不要の置き型宅配ボックス「ルスネコボックス」シリーズを扱う「宅配ボックス名品館」について、公式情報をもとにモデル・ロック方式・価格帯・メリット・デメリットを整理しました。',
        h1='宅配ボックス名品館最大の魅力は、工事不要の置き型宅配ボックス「ルスネコボックス」を、ロック方式や容量の違うモデルから選べること',
        lead='宅配や置き配の受け取りを便利にする宅配ボックス専門店。公式サイトで確認できたモデル・価格帯・設置方法をもとに、メリットとデメリットを第三者視点で整理しました。',
        about_h='宅配ボックス名品館とは',
        about=[
            '宅配ボックス名品館は、「ルスネコボックス」シリーズを取り扱う宅配ボックスの専門店です。広告主は「10年後も変わらぬ安心の機能と品質」にこだわり、厳選したモデルのみを掲載していると案内しています。',
            '公式サイトによると、Standard、Premium、Premium＋、ONE、Excellentなどのモデルがあり、ロック方式はゼロリターンキー、デジタルキー、プッシュキー、指紋キーから選べます。ポスト付きや一体型のモデルもあります。',
            '置き型で工事不要とされ、アンカー施工ができない場所向けには、専用ベースやフリーウェイトによる転倒防止・固定補助が案内されています。',
        ],
        notice='宅配ボックスは玄関まわりの設置場所の広さや、受け取る荷物の大きさによって向き不向きがあります。冷凍・冷蔵品の受け取りに対応しているかどうかは公式サイトに記載が確認できないため、食品の受け取りに使う場合は事前に公式サイトや問い合わせでご確認ください。',
        price_h='主なモデルと価格帯', cols=['モデル', '特徴', '価格（税込）'],
        rows=[['ONE', 'プッシュキー、120サイズ', '17,424円'],
              ['Standard（元祖・後付け）', 'ゼロリターンキー、カラー展開あり', '26,884円'],
              ['Premium', 'デジタルキー、左開き対応あり', '39,541円〜43,701円'],
              ['Premium＋', '120サイズ、ポスト一体型', '45,581円'],
              ['Excellent', '指紋キー、ポスト付き', '51,512円〜65,612円']],
        price_status='2026年10月時点で公式サイトから確認できた価格の目安です。価格・在庫・仕様は変更される場合があるため、最新の情報は必ず公式サイトでご確認ください。',
        price_note='専用ベース単品は12,980円〜13,282円、専用フリーウェイト（4個1セット）は7,480円（いずれも送料込）と案内されています。商品名に「2年保証」の記載があり、LINE友だち追加で1年保証が付くキャンペーンも案内されています。',
        cta_text='宅配ボックス名品館を公式サイトで見る',
        cta_mat='4BECH2+M158Y+5TXI+5YJRM', pixel='16',
        banner=dict(mat='4BECH2+M158Y+5TXI+5Z6WX', host='www25', aid='261009830037', mid='s00000027207001004000', w=300, h=250),
        merits=['ロック方式（ゼロリターン・デジタル・プッシュ・指紋）や容量、ポストの有無でモデルを選べる',
                '置き型で工事不要。専用ベースやフリーウェイトで固定を補助できる',
                '17,000円台から65,000円台まで価格帯が幅広く、予算に合わせて検討しやすい',
                '2年保証の記載があり、保証の考え方を事前に確認しやすい'],
        demerits=['モデルが多く、ロック方式や容量の違いから自宅に合うものを選ぶ手間がある',
                  '専用ベースやフリーウェイトは本体に付属せず、別売り'],
        merit_note='選ぶ際は、受け取りたい荷物の大きさ、設置場所の広さ、鍵の扱いやすさの3点を先に整理しておくと、モデルを絞りやすくなります。',
        demerit_section=['同じシリーズでも、Standard・Premium・Excellentなどで価格や機能が異なり、ポスト付きかどうか、左開きに対応するかなど確認すべき点が複数あります。設置場所の寸法を測ってから選ぶと安心です。',
                         '固定用の専用ベースやフリーウェイトは別売りです。置き型は設置後の転倒が気になる場合もあるため、固定方法まで含めて予算を検討しましょう。'],
        personas=['不在がちで、宅配便の再配達を減らしたい戸建て世帯',
                  '工事をせずに、置くだけで宅配ボックスを導入したい方',
                  '鍵の方式（暗証・デジタル・指紋など）にこだわって選びたい方',
                  '宅配食やネット通販の荷物を、玄関先で安全に受け取りたい方'],
        persona_extra=['宅配食を頻繁に利用する場合は、冷凍・冷蔵品を受け取れるかどうかも含めて、宅配ボックスの仕様を事前に確認しておくと安心です。'],
        compare_h='宅配食と合わせて検討するポイント',
        compare='冷凍の宅配食は、冷凍対応の宅配ボックスでのみ受け取れる、と案内しているサービスもあります（例：<a href="../../frozen-meal/muscle-deli/">Muscle Deli</a>）。宅配ボックスを選ぶ前に、よく利用する宅配サービスの受け取り条件を確認しておくとよいでしょう。',
        faq=[('工事は必要ですか？', '公式サイトでは、工事不要で設置できると案内されています。アンカー施工ができない場所向けには、専用ベースやフリーウェイトによる転倒防止・固定補助が用意されています。'),
             ('ロックの方式は選べますか？', 'ゼロリターンキー（Standard）、デジタルキー（Premium）、プッシュキー（ONE）、指紋キー（Excellent）などから選べます。'),
             ('保証はありますか？', '商品名に「2年保証」の記載があります。LINE友だち追加で1年保証が付くキャンペーンも案内されています。詳細は公式サイトでご確認ください。'),
             ('価格帯はどのくらいですか？', '2026年10月時点の公式サイトでは、ONEの17,424円（税込）から、Excellentの最大65,612円（税込）までのモデルが確認できます。')],
        affiliate=COMMON_AFF,
        related=[('../../frozen-meal/muscle-deli/', 'frozen-meal/muscle-deli'), ('../', 'delivery-box')],
    ),
]

if __name__ == '__main__':
    for a in ARTICLES:
        d = os.path.join(ROOT, a['cat'], a['slug'])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'index.html'), 'w', encoding='utf8', newline='\n') as f:
            f.write(build(a))
        print('wrote', a['cat'], a['slug'])
