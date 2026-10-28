"""2026-10-13 「宅配ボックス」カテゴリを新設する(一度だけ実行)。
1) 全ページのヘッダーナビ等に「宅配ボックス」を追加
2) 宅配ボックス名品館の記事を kitchen-goods から delivery-box へ移動し、旧カテゴリの登録を除去
3) delivery-box/index.html(カテゴリ一覧)を生成
4) 冷凍宅配弁当の社数表記を実数(15社)に修正
sitemap・トップ新着・トップのカードは別途(build_home.py / 本スクリプト末尾)で更新する。"""
import os, re, glob, html, json, shutil, subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
B = 'https://takuhaishoku-navi.net/'
SLUG = 'takuhai-box-meihinkan'
LABEL = '宅配ボックス'


def rd(p):
    return open(os.path.join(ROOT, p), encoding='utf8').read()


def wr(p, t):
    open(os.path.join(ROOT, p), 'w', encoding='utf8', newline='\n').write(t)


# ---------- 0) 記事を移動し旧カテゴリの登録を除去 ----------
old_dir = os.path.join(ROOT, 'kitchen-goods', SLUG)
new_dir = os.path.join(ROOT, 'delivery-box')
if os.path.isdir(old_dir):
    shutil.rmtree(old_dir)  # 記事は make_articles_20261013.py で delivery-box に再生成する
t = rd('kitchen-goods/index.html')
t = re.sub(r'          <tr class="clickable-row" onclick="location.href=\'%s/\'">.*?</tr>\n' % SLUG, '', t, flags=re.S)
t = re.sub(r',\n    \{"@type": "ListItem", "position": \d+, "url": "[^"]*/kitchen-goods/%s/"\}' % SLUG, '', t)
assert SLUG not in t
wr('kitchen-goods/index.html', t)
t = rd('sitemap.xml')
t = re.sub(r'  <url><loc>[^<]*/kitchen-goods/%s/</loc>.*?</url>\n' % SLUG, '', t)
wr('sitemap.xml', t)
t = rd('index.html')
t = re.sub(r'      <li><span class="cat">キッチン用品</span><a href="kitchen-goods/%s/">.*?</li>\n' % SLUG, '', t)
wr('index.html', t)

# ---------- 1) ナビ追加 ----------
def add_nav(text):
    if 'delivery-box/' in text:
        return text
    # 通常ページ(他カテゴリ・トップ・ガイド・404)
    text = re.sub(r'(<li><a href="((?:\./|(?:\.\./)+)?)kitchen-goods/">キッチン用品</a></li>)',
                  lambda m: m.group(1) + f'\n{indent(text, m.start())}<li><a href="{m.group(2)}delivery-box/">{LABEL}</a></li>', text)
    # キッチン用品カテゴリ配下ページ(自ページへのリンクが ./ または ../ )
    def kit(m):
        href, cur = m.group(2), m.group(3) or ''
        pre = '../' if href == './' else '../../'
        return m.group(1) + f'\n{indent(text, m.start())}<li><a href="{pre}delivery-box/">{LABEL}</a></li>'
    text = re.sub(r'(<li><a href="(\./|\.\./)"( aria-current="page")?>キッチン用品</a></li>)', kit, text)
    return text


def indent(text, pos):
    ls = text.rfind('\n', 0, pos) + 1
    return text[ls:pos] if text[ls:pos].strip() == '' else '        '


n = 0
for f in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
    s = open(f, encoding='utf8').read()
    s2 = add_nav(s)
    if s2 != s:
        open(f, 'w', encoding='utf8', newline='\n').write(s2)
        n += 1
print('nav updated', n)

# ---------- 4) 社数表記 ----------
t = rd('frozen-meal/index.html')
assert '14社' in t
wr('frozen-meal/index.html', t.replace('14社', '15社'))

# ---------- 3) カテゴリ一覧 ----------
FAQ = [
    ('宅配ボックスと置き配はどう違いますか？', '置き配は荷物を玄関先などに置いてもらう方法で、宅配ボックスは施錠できる箱に荷物を入れてもらう方法です。人目につきにくく、雨風や持ち去りが気になる場合は、宅配ボックスの導入を検討する方が多いようです。'),
    ('工事なしで設置できる宅配ボックスはありますか？', '床や地面に置くだけで使える「置き型」があります。たとえば宅配ボックス名品館が扱うルスネコボックスは、公式サイトで工事不要の置き型と案内されています。ただし転倒や持ち去りが気になる場合は、専用ベースなどで固定する方法も確認しておくと安心です。'),
    ('サイズはどう選べばよいですか？', 'よく届く荷物の大きさ（段ボールの寸法や、複数個がまとめて届くかどうか）を基準に選びます。設置場所の広さや、扉の開閉に必要なスペースも事前に測っておきましょう。'),
    ('ロックの方式にはどんな種類がありますか？', '鍵を使うもの、ダイヤルや暗証番号を設定するもの、デジタルキー、指紋認証などがあります。ルスネコボックスでは、ゼロリターンキー、デジタルキー、プッシュキー、指紋キーのモデルが公式サイトで案内されています。使う人の人数や、鍵を管理する手間も考えて選びましょう。'),
    ('冷凍や冷蔵の宅配食は宅配ボックスで受け取れますか？', '一般的な宅配ボックスには保冷機能がないものが多く、宅配食サービスによっては「冷凍対応の宅配ボックスでのみ受け取れる」と案内している場合があります。冷凍・冷蔵品の受け取りを想定する場合は、宅配ボックスの仕様と、利用する宅配食サービスの受け取り条件を確認しましょう。'),
    ('賃貸住宅でも設置できますか？', '設置場所や固定方法によっては、管理会社や大家さんの許可が必要になる場合があります。集合住宅の共用部分には置けないことがあるため、契約内容や管理規約を事前に確認してください。'),
]

SERVICES = [
    (SLUG, '宅配ボックス名品館（ルスネコボックス）', '工事不要の置き型。ロック方式や容量の違うモデルから選べる', '再配達を減らし、荷物を安全に受け取りたい戸建て世帯'),
]

furu = rd('furusato/index.html')
head_end = furu.index('<body>')
sponsor = re.search(r'  <section class="intro-block">\s*<h2>スポンサーリンク</h2>.*?</section>', furu, re.S).group(0)
footer = re.search(r'<footer class="site-footer">.*?</footer>', furu, re.S).group(0)
header = re.search(r'<header class="site-header">.*?</header>', furu, re.S).group(0)
# ヘッダーを「宅配ボックス」が現在ページの状態にする
header = header.replace('<li><a href="./" aria-current="page">ふるさと納税</a></li>', '<li><a href="../furusato/">ふるさと納税</a></li>')
header = header.replace(f'<li><a href="../delivery-box/">{LABEL}</a></li>', f'<li><a href="./" aria-current="page">{LABEL}</a></li>')
assert 'aria-current' in header

TITLE = '宅配ボックスおすすめ比較｜自宅向けの選び方まとめ'
DESC = '自宅に置ける宅配ボックスの選び方を、設置タイプ・容量・ロック方式・固定方法・受け取る荷物の5つの観点で整理。工事不要の置き型モデルを扱う宅配ボックス名品館も紹介します。'
faq_json = ',\n'.join('    {\n      "@type": "Question",\n      "name": %s,\n      "acceptedAnswer": {\n        "@type": "Answer",\n        "text": %s\n      }\n    }'
                      % (json.dumps(q, ensure_ascii=False), json.dumps(a, ensure_ascii=False)) for q, a in FAQ)
faq_html = '\n'.join(f'    <div class="intro-block">\n      <h3>Q. {html.escape(q, quote=False)}</h3>\n      <p>A. {html.escape(a, quote=False)}</p>\n    </div>' for q, a in FAQ)
rows = '\n'.join(f'''          <tr class="clickable-row" onclick="location.href='{s}/'">
            <td>{n}</td>
            <td>{st}</td>
            <td>{w}</td>
            <td><a href="{s}/">記事を読む</a></td>
          </tr>''' for s, n, st, w in SERVICES)
items = ',\n'.join(f'    {{"@type": "ListItem", "position": {i+1}, "url": "{B}delivery-box/{s}/"}}' for i, (s, *_) in enumerate(SERVICES))

page = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="../assets/favicon-32.png" sizes="32x32">
<link rel="icon" href="../favicon.ico">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<title>{TITLE}｜宅配食ナビ</title>
<meta name="description" content="{DESC}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700&amp;display=swap">
<link rel="stylesheet" href="../assets/style.css?v=8">
<link rel="canonical" href="{B}delivery-box/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="宅配食ナビ">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{B}delivery-box/">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type": "ListItem", "position": 1, "name": "トップ", "item": "{B}"}},
    {{"@type": "ListItem", "position": 2, "name": "{LABEL}", "item": "{B}delivery-box/"}}
  ]
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
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [
{items}
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
<p class="breadcrumb"><a href="/">トップ</a> &gt; {LABEL}</p>

<main>
  <section class="hero">
    <div class="hero-inner">
      <h1>📦 {TITLE}</h1>
      <p>再配達の手間を減らし、不在でも荷物を受け取りやすくする宅配ボックス。自宅に置く宅配ボックスを選ぶときのポイントを、設置タイプ・容量・ロック方式などの観点でまとめています。宅配食や通販の荷物を受け取る方にも役立つ内容です。</p>
    </div>
  </section>

  <nav class="toc" aria-label="目次">
    <p>目次</p>
    <ol>
      <li><a href="#about">宅配ボックスとは</a></li>
      <li><a href="#recommended">こんな方におすすめ</a></li>
      <li><a href="#how-to-choose">選び方5つのポイント</a></li>
      <li><a href="#notes">購入前に確認したい注意点</a></li>
      <li><a href="#diagnosis">かんたん診断</a></li>
      <li><a href="#services">宅配ボックス比較表</a></li>
      <li><a href="#faq">よくある質問</a></li>
    </ol>
  </nav>

  <section class="intro-block" id="about">
    <h2>宅配ボックスとは</h2>
    <p>宅配ボックスは、不在時に宅配業者が荷物を入れて施錠できる、受け取り用の箱です。置き配のように荷物が外から見える状態になりにくく、再配達の依頼や受け取りのための在宅時間を減らしやすくなります。</p>
    <p>戸建て向けには、床や地面に置くだけで使える置き型、門柱やポストと一体になったタイプなどがあります。本カテゴリでは、自宅に設置する宅配ボックスの選び方と、取り扱いショップを紹介します。</p>
  </section>

  <section id="recommended">
    <h2>こんな方におすすめ</h2>
    <ul class="persona-list">
      <li>仕事や外出で不在がちで、再配達の依頼を減らしたい方</li>
      <li>通販や宅配食の荷物を、玄関先で安全に受け取りたい方</li>
      <li>工事をせずに、置くだけで宅配ボックスを導入したい方</li>
      <li>鍵・暗証番号・指紋など、家族が使いやすいロック方式で選びたい方</li>
    </ul>
  </section>

  <section id="how-to-choose">
    <h2>選び方5つのポイント</h2>
    <div class="merit-demerit">
      <div class="merit-box">
        <h3>①設置タイプ（置き型・一体型など）</h3>
        <p>置き型は工事なしで導入しやすく、門柱一体型などは外観になじませやすい特徴があります。設置場所と工事の可否から選びましょう。</p>
      </div>
      <div class="merit-box">
        <h3>②容量とサイズ</h3>
        <p>よく届く荷物の大きさと、複数個がまとめて届くかどうかを基準にします。設置場所の広さも事前に測っておきましょう。</p>
      </div>
      <div class="merit-box">
        <h3>③ロック方式</h3>
        <p>鍵、ダイヤル、暗証番号、デジタルキー、指紋認証など、方式によって使い勝手や管理の手間が変わります。家族で使う場合は、全員が扱いやすい方式を選びます。</p>
      </div>
      <div class="merit-box">
        <h3>④固定方法と防犯性</h3>
        <p>置き型は転倒や持ち去りへの備えとして、専用ベースなどでの固定を確認します。素材や構造、保証の有無も比べましょう。</p>
      </div>
      <div class="merit-box">
        <h3>⑤受け取りたい荷物の種類</h3>
        <p>冷凍・冷蔵品の受け取りに対応しているかは、モデルによって異なります。宅配食を頻繁に利用する場合は、仕様を事前に確認しておきましょう。</p>
      </div>
    </div>
  </section>

  <section class="intro-block" id="notes">
    <h2>購入前に確認したい注意点</h2>
    <ul>
      <li>設置スペース：本体の寸法に加え、扉を開けるための余裕があるかを確認する。</li>
      <li>賃貸・集合住宅：設置場所や固定方法によっては、管理会社や管理組合の許可が必要になる場合がある。</li>
      <li>冷凍・冷蔵品：保冷機能のない宅配ボックスでは受け取れない場合がある。利用する宅配サービスの受け取り条件も確認する。</li>
      <li>配送業者の対応：配送業者や荷物の種類によって、宅配ボックスに入れられない場合がある。</li>
      <li>自治体の制度：自治体によっては、宅配ボックスの設置に関する補助制度が設けられている場合がある。最新の情報は各自治体の案内で確認する。</li>
    </ul>
  </section>

  <section id="diagnosis">
    <h2>かんたん診断：あなたに合うのはどのタイプ？</h2>
    <p class="diag-hint">いちばん当てはまるものを選ぶと、おすすめの選び方が表示されます。</p>
    <div class="merit-demerit">
      <div class="merit-box"><h3>工事をせずに置くだけで使いたい</h3><p>床や地面に置く置き型を選びます。固定が必要な場合は専用ベースなどの有無も確認しましょう。例：<a href="{SLUG}/">宅配ボックス名品館</a>。</p></div>
      <div class="merit-box"><h3>家族みんなが使いやすいロックにしたい</h3><p>暗証番号・デジタルキー・指紋認証など、家族が操作しやすい方式のモデルを比べます。</p></div>
      <div class="merit-box"><h3>大きな荷物や複数個の荷物が多い</h3><p>容量が大きいモデルや、複数個を受け取れるモデルを選びます。設置場所の広さも先に測りましょう。</p></div>
      <div class="merit-box"><h3>冷凍の宅配食も受け取りたい</h3><p>保冷機能の有無を確認し、利用する宅配食サービスの受け取り条件とあわせて選びます。</p></div>
    </div>
  </section>

  <section id="services">
    <h2>宅配ボックス比較表</h2>
    <p class="status-pending">個別の紹介記事は順次追加します。下表は公式サイトで確認できた内容をもとにした概要です。</p>
    <div class="compare-table-wrap">
      <table class="compare-table">
        <thead>
          <tr><th>サービス名</th><th>一番の強み</th><th>こんな人向け</th><th>詳細記事</th></tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
  </section>

  <section id="faq">
    <h2>よくある質問</h2>
{faq_html}
  </section>

  <p class="affiliate-notice">本サイトはアフィリエイトプログラム(A8.net等)による収益を得ています。紹介内容は公開情報・利用者の声をもとに第三者視点で構成しており、運営者自身の体験談ではありません。</p>

{sponsor}
</main>

{footer}
<script src="../assets/diagnosis.js" defer></script>
</body>
</html>
'''
os.makedirs(new_dir, exist_ok=True)
wr('delivery-box/index.html', page)

# ---------- sitemap ----------
t = rd('sitemap.xml')
add = (f'  <url><loc>{B}delivery-box/</loc><lastmod>2026-10-13</lastmod></url>\n'
       f'  <url><loc>{B}delivery-box/{SLUG}/</loc><lastmod>2026-10-13</lastmod></url>\n')
i = t.index(f'  <url><loc>{B}otoriyose/</loc>')
wr('sitemap.xml', t[:i] + add + t[i:])

# ---------- トップ新着 ----------
t = rd('index.html')
li = (f'      <li><span class="cat">{LABEL}</span><a href="delivery-box/{SLUG}/">宅配ボックス名品館（ルスネコボックス）の評判・メリット・デメリット</a>'
      '<p>工事不要の置き型宅配ボックス「ルスネコボックス」を扱う専門店を紹介します。</p></li>\n')
a = t.index('<ul class="new-list">') + len('<ul class="new-list">\n')
wr('index.html', t[:a] + li + t[a:])
print('done')
