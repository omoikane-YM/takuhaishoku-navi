"""2026-10-04 新規承認4件の記事生成 (docs/<cat>/<slug>/index.html)。
ヘッダー/フッターは同カテゴリの既存記事からそのまま流用する。"""
import os, re, json, html

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
BASE = 'https://takuhaishoku-navi.net/'
NOW = '2026-10-04T18:00:00+09:00'
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
    cat_text = re.search(r'<p class="breadcrumb">.*?<a href="\.\./">(.*?)</a>', sib, re.S).group(1)
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
<link rel="stylesheet" href="../../assets/style.css?v=8">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="宅配食ナビ">
<meta property="og:title" content="{esc(ttl)}">
<meta property="og:description" content="{esc(a['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
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
</head>
<body>
{header}
<p class="breadcrumb"><a href="/">トップ</a> &gt; <a href="../">{cat_text}</a> &gt; {esc(a['short'])}</p>

<main>
  <section class="hero">
    <div class="hero-inner">
      <h1>{esc(a['h1'])}</h1>
      <p class="post-meta"><span>公開日 <time datetime="2026-10-04">2026年10月4日</time></span></p>
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

ARTICLES = [
    dict(
        cat='baby-food', slug='mogumodeli', sibling='baby-food/mogumo', short='モグモデリ',
        title='モグモデリの評判・メリット・デメリット',
        desc='小学生・中学生向けの成長期に特化した無添加の冷凍ワンプレート宅配食「モグモデリ」について、公開されている口コミ・公式情報をもとに料金・メリット・デメリットを整理しました。',
        h1='モグモデリ最大の魅力は、成長期の小学生・中学生向けに栄養基準を設けた無添加の冷凍ワンプレートが、電子レンジで約4分で食卓に並ぶこと',
        lead='冷凍幼児食「モグモ」の新ブランドとして2026年3月に登場したモグモデリ。公開されている公式情報・口コミをもとに、料金やメリット・デメリットを第三者視点で整理しました。',
        about_h='モグモデリとは',
        about=[
            'モグモデリは、冷凍幼児食「モグモ」を展開する株式会社Oxxxが、2026年3月10日に販売を開始した新ブランドです。対象は小学生・中学生などの成長期の子どもで、主菜と副菜がひとつのプレートにまとまった冷凍ワンプレートを、電子レンジで約4分温めるだけで食べられます。',
            '公式サイトによると、栄養基準は1食あたりたんぱく質10g以上・塩分2.0g以下、カルシウムは12商品の平均で70mg以上。管理栄養士が監修し、香料・着色料・うま味調味料は使用していません。ワンプレート、おかず、ご飯・麺の3カテゴリで展開されています。',
            '公式は「成長期に特化した無添加冷凍ワンプレート宅配食として日本初」と案内しており、注釈として「自社調べ（2026年2月時点）」と記載しています。',
        ],
        notice='食物アレルギーがあるお子様は、原材料表示を必ず公式サイトで確認し、必要に応じて医師にご相談ください。お子様の発育や栄養について個別の心配がある場合も、医師・管理栄養士などの専門家へご相談ください。',
        price_h='料金プラン', cols=['定期便の食数', '1食あたりの目安価格（税抜）', '補足'],
        rows=[['8食セット', '920円', '2〜4週間ごとのお届け'],
              ['10食セット', '890円', '2〜4週間ごとのお届け'],
              ['12食セット', '870円（税込939円）', '食数が多いほど1食あたりが割安']],
        price_status='2026年10月時点で公式サイトから確認できた料金の目安です。キャンペーン内容・価格・送料は変更される場合があるため、最新の情報は必ず公式サイトでご確認ください。',
        price_note='送料は配送先のエリアや食数によって異なります。公式サイトでは「すくすく成長応援コース」は送料無料と案内されています。',
        cta_text='成長期の子どもに必要な栄養を、毎日ワンプレートで。【モグモデリ】',
        cta_mat='4BCCJK+22FAHE+5CLW+NTJWY', pixel='18',
        banner=dict(mat='4BCCJK+22FAHE+5CLW+NTZCH', host='www23', aid='260916608125', mid='s00000024962004003000', w=300, h=250),
        merits=['たんぱく質10g以上・塩分2.0g以下など、1食の栄養基準が公開されていて選ぶ基準が分かりやすい',
                '香料・着色料・うま味調味料を使っていない無添加設計',
                '電子レンジで約4分。部活や塾で帰宅が遅い日の夕食にも使いやすい',
                '配送サイクル（2・3・4週間）や食数を調整でき、お届けのスキップもできる柔軟さ'],
        demerits=['定期便が中心で、1食あたり870〜920円（税抜）と、家庭で作る食事と比べると割高に感じる場合がある'],
        merit_note='価格については、毎日の食事をすべて置き換えるのではなく、忙しい平日の夕食や、親の帰宅が遅い日だけ使うなど、必要な日に絞って活用する使い方が考えられます。',
        demerit_section=['価格の他には、冷凍で届くため冷凍庫の空きスペースが必要になる点も確認しておきたいポイントです。公式サイトによると、メニューは発売時点で12種類で、お子様の好みによって合う・合わないに個人差が出る場合があります。',
                         '対策としては、まず少ない食数から始め、お子様の食べ具合を見ながら次回以降の食数や配送サイクルを調整するとよいでしょう。公式は、試食テストで80%以上の子どもが完食したメニューのみを商品化したと案内しています。'],
        personas=['部活・塾・習い事で夕食の時間が不規則な小学生・中学生の保護者',
                  '子どもの食事の栄養バランスが気になるが、毎日の準備に時間が取れない共働き世帯',
                  '添加物の使用をできるだけ控えたいと考えている方',
                  '食べ盛りの子どもの夕食を、レンジ調理で子ども自身に任せたい方'],
        persona_extra=['具体的には、親の帰宅が遅い平日に子どもが自分で温めて食べる、週末は家族で作るなど、家庭の食事づくりと併用する使い方が考えられます。'],
        compare_h='モグモとの違いと選び方',
        compare='同じ運営元の<a href="../mogumo/">モグモ</a>は1歳半〜6歳向けの冷凍幼児食、モグモデリは小学生・中学生向けの成長期特化のワンプレートというように、対象年齢が異なります。離乳食から幼児食へ進む時期なら<a href="../first-spoon/">ファーストスプーン</a>やモグモ、小学生以上になったらモグモデリというように、お子様の成長に合わせて選ぶとわかりやすくなります。',
        faq=[('モグモデリは何歳向けですか？', '公式サイトでは、小学生・中学生などの成長期の子どもを対象としています。1歳半〜6歳の幼児向けには、同じ運営元のモグモがあります。'),
             ('どのくらいの時間で食べられますか？', '電子レンジで約4分温めるだけで食べられると案内されています。火を使わず調理できるため、子どもが自分で準備することもできます。'),
             ('配送サイクルや食数は変えられますか？', '配送サイクルは2週間・3週間・4週間から選べ、食数も注文ごとに調整できます。お届けのスキップにも対応しています。'),
             ('解約はいつでもできますか？', '公式サイトでは、一部のコースを除いていつでも解約でき、次回配送予定日の10日前までに手続きが必要と案内されています。コースごとの条件は必ず公式サイトでご確認ください。')],
        affiliate=COMMON_AFF,
        related=[('../mogumo/', 'baby-food/mogumo'), ('../first-spoon/', 'baby-food/first-spoon')],
    ),
    dict(
        cat='coop-delivery', slug='kinki-coop', sibling='coop-delivery/ouchi-coop', short='コープの宅配（コープきんき）',
        title='コープの宅配（コープきんき）の評判・メリット・デメリット',
        desc='滋賀・京都・奈良・大阪・和歌山で利用できる生協の個人宅配「コープの宅配（コープきんき）」について、公開されている口コミ・公式情報をもとに仕組みやメリット・デメリットを整理しました。',
        h1='コープの宅配（コープきんき）最大の魅力は、滋賀・京都・奈良・大阪・和歌山に毎週約4,000点以上の商品から選べる生協の宅配で、食品から日用品・ベビー用品まで届くこと',
        lead='近畿の5府県で100万人以上が利用していると案内されている生協の個人宅配。公開されている公式情報・口コミをもとに、仕組みやメリット・デメリットを第三者視点で整理しました。',
        about_h='コープの宅配（コープきんき）とは',
        about=[
            'コープきんき事業連合は、滋賀・京都・奈良・大阪・和歌山の7つの生協（コープしが・京都生協・ならコープ・よどがわ生協・おおさかパルコープ・いずみ生協・わかやま生協）で構成される連合組織です。「コープの宅配」は、毎週決まった曜日・時間に自宅まで商品を届けてくれる個人向けの宅配サービスです。',
            '公式サイトによると、毎週約4,000点以上の商品から注文でき、食品カタログのほか、日用品、レシピ情報、ベビー用品・離乳食のカタログも用意されています。注文はインターネット、スマホアプリ「ニコリエ」、パソコン、注文書から選べます。',
            '利用するには生協への加入が必要で、加入時に出資金をお預かりします。出資金は生協を退会する際に返金されると案内されています。',
        ],
        notice='配達エリアは滋賀県・京都府・奈良県・大阪府・和歌山県に限られます。エリア外にお住まいの方は利用できません。配達手数料や出資金は加入する生協・地域によって異なります。',
        price_h='加入の流れと費用', cols=['始め方', '内容', '費用の目安'],
        rows=[['資料請求', 'カタログなどの資料を取り寄せて内容を確認できる', '無料'],
              ['おためしセット', '通常価格2,000円相当の商品を試せるセット（地域別に選択）', '1,000円'],
              ['加入', '出資金をお預かりして利用開始。出資金は退会時に返金', '出資金・配達手数料は生協・地域により異なる']],
        price_status='2026年10月時点で公式サイトから確認できた情報の目安です。セット内容・費用は地域や時期によって変わる場合があるため、最新の情報は必ず公式サイトでご確認ください。',
        price_note='配達手数料は地域により異なり、子育て世帯・ご高齢世帯向けの割引制度や、一定金額以上の利用で割引・無料になる生協もあると案内されています。',
        cta_text='コープの宅配　まずは資料請求',
        cta_mat='4BCBRH+F5D5ZM+4KLU+60H7M', pixel='16',
        banner=dict(mat='4BCBRH+F5D5ZM+4KLU+609HT', host='www28', aid='260915597916', mid='s00000021333001009000', w=300, h=250),
        merits=['毎週約4,000点以上の品ぞろえで、食品から日用品・ベビー用品までまとめて注文できる',
                '資料請求（無料）やおためしセット（1,000円）から始められ、加入前に内容を確認しやすい',
                '毎週の注文は必須ではなく、必要な週だけ注文できる。留守のときは置き配にも対応',
                'ベビー用品・離乳食のカタログがあり、子育て世帯向けの割引制度もある（内容は地域により異なる）'],
        demerits=['配達エリアが近畿5府県に限られ、利用には出資金と配達手数料（地域により異なる）が必要'],
        merit_note='出資金は退会時に返金されると案内されていますが、金額や配達手数料の条件は加入する生協によって異なります。まず資料請求で、お住まいの地域の条件を確認してから決める使い方が考えられます。',
        demerit_section=['エリア外では利用できないほか、オートロックのマンションは事前相談が必要と案内されています。',
                         '対策としては、先に資料請求やおためしセットで、お住まいの地域の配達条件・手数料・出資金を確認してから加入を決めると、想定外の負担を避けやすくなります。'],
        personas=['近畿5府県にお住まいで、食品も日用品もまとめて宅配で済ませたい方',
                  '子育て中で、ベビー用品や離乳食も宅配で注文したい方',
                  '毎週決まった曜日に届くリズムで、買い物の回数を減らしたい方',
                  'いきなり加入するのは不安なので、まず資料請求やおためしセットで試したい方'],
        compare_h='他の生協宅配との違い',
        compare='生協の宅配は、運営する生協ごとに配達エリアが決まっています。<a href="../ouchi-coop/">おうちコープ</a>(ユーコープ)とは運営エリアが異なり、近畿5府県にお住まいの方がコープきんきの対象になります。有機・無添加など商品へのこだわりを重視するなら<a href="../shizenha/">コープ自然派</a>や<a href="../radish-boya/">らでぃっしゅぼーや</a>も比較対象になります。「お住まいのエリアで使えるか」と「何を重視するか」の2点で選ぶのが分かりやすい方法です。',
        faq=[('どのエリアで利用できますか？', '滋賀県・京都府・奈良県・大阪府・和歌山県が配達エリアです。お住まいの地域によって加入する生協が決まります。'),
             ('出資金は戻ってきますか？', '公式サイトでは、加入時にお預かりする出資金は、生協を退会する際に返金されると案内されています。金額は生協ごとに異なるため、加入前に確認してください。'),
             ('毎週必ず注文しないといけませんか？', '毎週の注文は必須ではないと案内されています。必要な週だけ注文する使い方ができます。'),
             ('留守でも受け取れますか？', '留守のときは置き配に対応していると案内されています。オートロックのマンションは事前相談が必要です。'),
             ('おためしセットの内容は？', '公式サイトでは、通常価格2,000円相当の商品を1,000円で試せるセットが案内されています。内容は地域や時期によって変わるため、最新の情報は公式サイトでご確認ください。')],
        affiliate=COMMON_AFF,
        related=[('../ouchi-coop/', 'coop-delivery/ouchi-coop'), ('../shizenha/', 'coop-delivery/shizenha'),
                 ('../radish-boya/', 'coop-delivery/radish-boya')],
    ),
    dict(
        cat='otoriyose', slug='hokkaido-gyoren', sibling='otoriyose/kani-tsuhan', short='北海道ぎょれん',
        title='北海道ぎょれんの評判・メリット・デメリット',
        desc='北海道漁連の公式オンラインショップ「北海道ぎょれん」について、公開されている口コミ・公式情報をもとに、送料無料の産地直送や商品、メリット・デメリットを整理しました。',
        h1='北海道ぎょれん最大の魅力は、北海道の漁協ネットワークから全商品送料無料で届く産地直送の海産物が、常時200点以上そろうこと',
        lead='カニ・ほたて・いくら・鮭など、北海道の海の幸を扱う公式オンラインショップ。公開されている公式情報・口コミをもとに、特徴やメリット・デメリットを第三者視点で整理しました。',
        about_h='北海道ぎょれんとは',
        about=[
            '北海道ぎょれんは、ぎょれん販売株式会社が運営する、北海道漁業協同組合連合会の公式オンラインショップです。北海道の漁協や各産地メーカーとのネットワークを活かした産地直送が特徴で、カニ、ほたて、いくら、鮭、海鮮セットなどの海産物が、常時200点以上そろっています。',
            '公式サイトによると、全商品が送料無料です。配送業者との契約金額を店舗側が全額負担する形で、ヤマト運輸で届きます。ギフト用にも自宅用にも使える商品が並び、お歳暮などの贈り物の需要期にも利用されています。',
            '会員登録をすると300円相当のポイントがすぐに使えるほか、商品レビューを投稿すると1件につき300ポイントがもらえると案内されています。',
        ],
        price_h='人気商品と価格の例', cols=['商品', '内容', '価格の目安（税込）'],
        rows=[['いくら醤油漬', '100g×2', '6,999円'],
              ['塩時鮭', '半身700g', '6,999円'],
              ['ぼたんえび・ほたてセット', '詰め合わせセット', '5,300円'],
              ['ほたて貝柱', '200g×2', '4,500円'],
              ['海鮮丼セット', '内容により異なる', '4,000〜6,800円']],
        price_status='公式サイトのおすすめ・人気商品として掲載されていた価格の例です（2026年10月時点）。商品ラインナップや価格は時期によって変わるため、最新の情報は必ず公式サイトでご確認ください。',
        price_note='全商品が送料無料のため、表示価格のほかに送料が加わることはありません。支払い方法は、クレジットカード、代金引換（手数料330円〜）、後払い、Amazon Pay、PayPay、d払い、楽天ペイが案内されています。',
        cta_text='北海道から産地直送！送料無料！【北海道ぎょれん】',
        cta_mat='4BCCJK+3ITFPU+4OBG+5YJRM', pixel='13',
        banner=dict(mat='4BCCJK+3ITFPU+4OBG+626XT', host='www28', aid='260916608213', mid='s00000021814001018000', w=300, h=250),
        merits=['北海道の漁協ネットワークによる産地直送で、全商品が送料無料',
                'カニ・ほたて・いくら・鮭・海鮮セットなど、常時200点以上から選べる',
                '会員登録で300円相当のポイントが使え、レビュー投稿でもポイントがもらえる',
                'ヤマト運輸で届き、日時指定ができる。支払い方法も多彩（クレジット・後払い・各種ペイなど）'],
        demerits=['高級海産物が中心のため、日常の食卓に使うには価格がやや高めに感じる場合がある'],
        merit_note='価格については、ギフトや年末年始、特別な日の食卓など、用途を絞って利用する方が多いようです。お得用や訳ありのほたて貝柱など、自宅用に使いやすい商品も案内されています。',
        demerit_section=['価格の他には、注文はインターネットからのみで、電話・FAX・メールでの注文は受け付けていない点に注意が必要です。キャンセルは出荷予定日の4日前まで、返品・交換は到着後2営業日以内と案内されています。日時指定は土日祝日を除いて可能とされています。',
                         '対策としては、ギフトで使う場合は日時指定の可否と出荷予定日を早めに確認し、冷凍庫に入るサイズかも注文前にチェックしておくと安心です。'],
        personas=['お歳暮や内祝いなどに、信頼できる産地直送の海産物を贈りたい方',
                  '自宅で北海道のカニ・いくら・ほたてを味わいたい方',
                  '送料を気にせず、複数の海産物をまとめて選びたい方',
                  '支払い方法に後払いやスマホ決済を使いたい方'],
        compare_h='カニ専門の通販との違い',
        compare='カニを中心に選ぶなら<a href="../kani-tsuhan/">カニ通販.com</a>のような専門通販も候補になります。北海道ぎょれんは、カニに限らず、ほたて・いくら・鮭・海鮮セットなど、北海道の海産物を幅広く、送料無料で選べる点が特徴です。「カニだけを比べたい」のか「北海道の海産物をまとめて選びたい」のかで使い分けるとわかりやすくなります。',
        faq=[('送料はかかりますか？', '公式サイトでは、全商品が送料無料と案内されています。配送業者との契約金額は店舗が負担します。'),
             ('電話やメールで注文できますか？', '注文はインターネットのみで、電話・FAX・メールでの注文は受け付けていないと案内されています。'),
             ('キャンセルや返品はできますか？', 'キャンセルは出荷予定日の4日前まで、返品・交換は到着後2営業日以内と案内されています。商品の状態など詳しい条件は公式サイトでご確認ください。'),
             ('どんな支払い方法がありますか？', 'クレジットカード、代金引換、後払い、Amazon Pay、PayPay、d払い、楽天ペイが案内されています。代金引換は手数料がかかります。')],
        affiliate=COMMON_AFF,
        related=[('../kani-tsuhan/', 'otoriyose/kani-tsuhan'), ('../senkaya/', 'otoriyose/senkaya')],
    ),
    dict(
        cat='senior-meal', slug='anshin-soudan', sibling='senior-meal/shokurakuzen', short='シニアのあんしん相談室',
        title='シニアのあんしん相談室（宅配ごはん案内）の評判・メリット・デメリット',
        desc='郵便番号から宅配食を検索・比較し、複数サービスを一括で資料請求できる「シニアのあんしん相談室 -宅配ごはん案内-」について、公開情報をもとにメリット・デメリットを整理しました。',
        h1='シニアのあんしん相談室最大の魅力は、郵便番号を入れるだけで自宅に届けられる宅配食を検索・比較でき、複数サービスの資料をまとめて請求できること',
        lead='離れて暮らす親の食事を考えるご家族などが使う、宅配食の比較・案内サービス。公開されている公式情報をもとに、使い方やメリット・デメリットを第三者視点で整理しました。',
        about_h='シニアのあんしん相談室（宅配ごはん案内）とは',
        about=[
            '「シニアのあんしん相談室 -宅配ごはん案内-」は、株式会社ウェブクルーが運営する、宅配食の検索・比較サービスです。お住まいの郵便番号やエリアから、配達可能な宅配食サービスを探せます。',
            '公式サイトによると、複数のサービスの資料をまとめて請求できる「一括資料請求」と、希望のサービスを伝えて注文のお手伝いを受けられる「注文希望」が用意されています。掲載サービスはワタミ、ニチレイフーズなど35社以上（掲載時点）と案内されており、利用者の口コミやランキングも確認できます。',
            'このサービス自体は宅配食を作る会社ではなく、利用者と宅配食サービスをつなぐ窓口です。実際の料金・メニュー・契約条件は、選んだ各サービスによって決まります。',
        ],
        notice='栄養制限食や介護食を扱うサービスが掲載されていますが、特定の疾患の治療や症状の改善を目的としたものではありません。食事の制限が必要な方は、医師・管理栄養士にご相談のうえ、ご利用ください。',
        price_h='利用の流れと費用', cols=['ステップ', '内容', '費用'],
        rows=[['1. エリアで検索', '郵便番号などを入力して、配達可能な宅配食サービスを探す', '無料（掲載は無料と案内）'],
              ['2. 資料請求・注文希望', '複数サービスの資料を一括請求、または注文希望を申し込む', 'あんしん相談室の利用は無料と案内'],
              ['3. 各サービスを利用', '担当者からの連絡後、注文が確定すると利用開始', '各サービスの料金に準じる']],
        price_status='2026年10月時点で公式サイトから確認できた内容の目安です。掲載サービス・特典・条件は変更される場合があるため、最新の情報は必ず公式サイトでご確認ください。',
        price_note='食べ比べをする場合、お試しコースや初回無料のサービスもありますが、基本的には各サービスの料金がかかります。',
        cta_text='シニアのあんしん相談室-宅配ごはん案内-',
        cta_mat='4BCCJK+32QQDU+3RU+6Y29SI', pixel='16',
        banner=dict(mat='4BCCJK+32QQDU+3RU+6Y6CE9', host='www27', aid='260916608186', mid='s00000000489042020000', w=300, h=250),
        merits=['郵便番号を入れるだけで、自宅に配達できる宅配食サービスを探せる',
                '複数サービスの資料をまとめて請求でき、1社ずつ調べる手間が省ける',
                'バランス型のお弁当から、栄養制限食、介護食まで、目的別に幅広いサービスが掲載されている',
                '利用者の口コミやランキングを見ながら比較でき、注文のお手伝い（注文希望）も用意されている'],
        demerits=['申し込み後に担当者から連絡が入る流れがあり、すぐに自分のペースで注文したい方には手間に感じる場合がある'],
        merit_note='連絡が気になる場合は、まず資料請求だけを利用して内容を比較し、気に入ったサービスが決まってから注文希望を申し込む使い方が考えられます。',
        demerit_section=['比較・案内サービスのため、価格やメニューの詳細は、最終的に各サービスの公式情報を確認する必要があります。サービスによって配送方法や対応エリアが異なる点にも注意が必要です。',
                         '対策としては、気になるサービスをいくつかに絞ったうえで、資料やお試しコースを確認し、量や味付け、冷凍庫の空きなどもあわせて検討するとよいでしょう。'],
        personas=['離れて暮らす親の食事が心配で、どのサービスが合うか分からないご家族',
                  '複数の宅配食を、まとめて比較してから決めたい方',
                  '栄養バランスや塩分・カロリーに配慮した食事を探している方',
                  '自分の住んでいる地域で使える宅配食を、手早く知りたい方'],
        compare_h='個別のサービスとあわせて比較する',
        compare='このサービスで見つけた宅配食は、個別の記事でさらに詳しく比較できます。嚥下に配慮した冷凍惣菜なら<a href="../shokurakuzen/">食楽膳</a>、栄養制限に配慮した食事なら<a href="../medifoods/">メディカルフードサービス</a>、健康づくりを意識した宅配なら<a href="../kenko-chokkyubin/">健康直球便</a>、冷凍惣菜なら<a href="../../frozen-meal/watami-takushoku-direct/">ワタミの宅食ダイレクト</a>、管理栄養士監修の<a href="../../frozen-meal/nichirei-kikubari-gozen/">ニチレイ気くばり御膳</a>などが参考になります。',
        faq=[('利用に料金はかかりますか？', '公式サイトでは、サービスの掲載は無料と案内されています。実際に宅配食を利用する場合は、各サービスの料金がかかります。'),
             ('「注文希望」と「資料請求」の違いは？', '資料請求は、複数サービスの資料をまとめて取り寄せて比較するためのものです。注文希望は、利用したいサービスを伝えると、担当者から連絡があり、注文確定後に利用が始まる流れです。'),
             ('どんな食事のサービスが探せますか？', 'バランス型のお弁当、日替わり献立、栄養制限食、介護食などを扱うサービスが掲載されています。個別の対応可否は各サービスの公式情報でご確認ください。'),
             ('自分の地域で使えるか分かりますか？', '郵便番号などを入力すると、お住まいの地域に配達可能なサービスを検索できます。')],
        affiliate=COMMON_AFF + '栄養制限食・介護食に関する記述は、特定の疾患の治療や改善を保証するものではありません。',
        related=[('../shokurakuzen/', 'senior-meal/shokurakuzen'), ('../medifoods/', 'senior-meal/medifoods'),
                 ('../kenko-chokkyubin/', 'senior-meal/kenko-chokkyubin')],
    ),
]

if __name__ == '__main__':
    for a in ARTICLES:
        d = os.path.join(ROOT, a['cat'], a['slug'])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'index.html'), 'w', encoding='utf8', newline='\n') as f:
            f.write(build(a))
        print('wrote', a['cat'], a['slug'])
