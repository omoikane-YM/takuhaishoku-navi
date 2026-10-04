"""トップページ(docs/index.html)の<main>を新デザインで再生成する。
既存の「新着記事」リストと各記事のA8バナーを読み取って再利用する。"""
import re, glob, html, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
p = os.path.join(ROOT, 'index.html')
s = open(p, encoding='utf8').read()

# --- 新着記事を既存HTMLから抽出 ---
m = re.search(r'<ul class="(?:article-list|new-list)">(.*?)</ul>', s, re.S)
items = re.findall(r'<li>(?:<span class="cat">(.*?)</span>)?\s*<a href="([^"]+)">(.*?)</a>\s*<p>(.*?)</p>', m.group(1), re.S)
new_li = []
for chip0, href, title, desc in items:
    cat = re.match(r'【(.*?)】', desc)
    chip_name = chip0 or (cat.group(1) if cat else '')
    chip = f'<span class="cat">{chip_name}</span>' if chip_name else ''
    desc2 = re.sub(r'^【.*?】', '', desc)
    new_li.append(f'      <li>{chip}<a href="{href}">{title}</a><p>{desc2}</p></li>')
new_list = '\n'.join(new_li)

# 既存カードの説明文を拾う(再実行しても保持される)
old = {}
for slug, desc in re.findall(r'<h2><a href="([^/"]+)/">.*?</a></h2>\s*<p>(.*?)</p>', s, re.S):
    old[slug] = desc

# --- バナー展示: カテゴリごとに1つ選ぶ ---
cats = ['mealkit', 'frozen-meal', 'senior-meal', 'baby-food', 'coop-delivery',
        'kitchen-goods', 'otoriyose', 'furusato', 'health-food']
picks = []
for c in cats:
    for f in sorted(glob.glob(os.path.join(ROOT, c, '*', 'index.html'))):
        t = open(f, encoding='utf8').read()
        b = re.search(r'<div class="hero-banner">.*?</div>', t, re.S)
        if not b:
            continue
        im = re.search(r'width="(\d+)" height="(\d+)" alt="([^"]*)"', b.group(0))
        if im and int(im.group(2)) >= 250:
            blk = b.group(0).replace('</div>', f'<span class="name">{html.escape(im.group(3))}</span></div>')
            picks.append(blk)
            break
pick_html = '\n'.join('      ' + re.sub(r'\n\s*', '\n        ', x) for x in picks)

CARDS = [
    ('mealkit', '🥘', '共働き・時短', 'ミールキット', 'Oisix・ヨシケイなど、献立とカット済み食材がセットになったミールキットを紹介します。', 'crop-veg'),
    ('frozen-meal', '🍱', '一人暮らし・ダイエット', '冷凍宅配弁当', 'nosh・GREEN SPOON・FIT FOOD HOMEなど、レンジで完結する冷凍宅配食を紹介します。', 'crop-bento'),
    ('senior-meal', '🍲', '親の見守り・介護', '高齢者・介護食宅配', 'まごころケア食・宅配クック123など、栄養バランスや制限食に配慮した宅配食を紹介します。', 'crop-soup'),
    ('baby-food', '🍼', '子育て', '離乳食宅配', '手作りが大変な離乳食期に役立つ、宅配の離乳食サービスを紹介します。', 'crop-spoon'),
    ('coop-delivery', '🥬', '安全・産直志向', '食材宅配(生協・産直系)', 'らでぃっしゅぼーや・生活クラブ・コープの宅配など、食材そのものを届けるサービスを紹介します。', 'crop-veg'),
    ('kitchen-goods', '🔪', '調理器具・食材保存', 'キッチン用品', '包丁・フライパンから真空パック機まで、毎日の料理を快適にするキッチン用品を紹介します。', 'crop-wok'),
    ('otoriyose', '🎁', 'ギフト・ご当地グルメ', 'お取り寄せグルメ', '馬刺し・和牛・カニ・海産物・京漬物など、産地から直送されるご当地物産を紹介します。', 'crop-bento'),
    ('furusato', '🏠', '節税・返礼品', 'ふるさと納税', 'お肉・海鮮・米など、ふるさと納税の返礼品で食卓を豊かにするサービスを紹介します。', 'crop-wok'),
    ('health-food', '🌿', '食習慣・健康サポート', '美容・健康食品', '毎日の食習慣を手軽に整えたい方向けの、美容・健康食品を紹介します。', 'crop-soup'),
]
cards = []
for slug, icon, tag, name, desc, img in CARDS:
    desc = old.get(slug, desc)
    cards.append(f'''    <article class="category-card">
      <div class="card-photo" style="background-image:url('assets/{img}.webp')"><div class="card-icon">{icon}</div></div>
      <div class="card-body">
        <span class="tag">{tag}</span>
        <h2><a href="{slug}/">{name}</a></h2>
        <p>{desc}</p>
        <span class="card-link">カテゴリを見る</span>
      </div>
    </article>''')
cards_html = '\n'.join(cards)

marq = ''.join(f'<span>{t}</span>' for t in [
    '献立を考える時間、おやすみ。', '買い物の荷物、おやすみ。', 'おいしさは、そのまま。',
    '空いた時間は、じぶんのために。', '今日の夕食は、届いている。'])

main = f'''<main>
  <section class="top-hero">
    <div class="top-hero__text">
      <span class="disclosure-badge">当サイトはアフィリエイト広告を利用しています</span>
      <h1>手作りみたいな<em>ごちそう</em>が、<br>家に届く。<br><span class="red">空いた時間は、じぶんの時間。</span></h1>
      <p class="lead">ミールキット・冷凍宅配弁当・高齢者向け宅配食・離乳食まで。家で作る料理に負けないおいしさの宅配食を、目的別に比べて選べます。</p>
      <div class="cta-row">
        <a class="btn btn--red" href="#categories">目的から探す</a>
        <a class="btn" href="#free-time">1日がどう変わる？</a>
      </div>
    </div>
    <div class="top-hero__visual" aria-hidden="true">
      <div class="plate plate--main"></div>
      <div class="plate plate--bento"></div>
      <div class="plate plate--soup"></div>
      <div class="sticker sticker--a"><span>できたて<small>のおいしさ</small></span></div>
      <div class="sticker sticker--b"><span>自由時間<small>が増える</small></span></div>
    </div>
  </section>

  <div class="marquee" aria-hidden="true"><div class="marquee__track">{marq}{marq}</div></div>

  <section id="free-time">
    <div class="sec-head">
      <span class="eyebrow">TIME TO YOURSELF</span>
      <h2>宅配食にすると、夕方がこう変わります</h2>
      <p>献立・買い物・調理・片付け。毎日くり返す“食のおしごと”を、おいしいまま減らせます。</p>
    </div>
    <div class="timeline">
      <div class="tl tl--before">
        <span class="tl__label">これまで（自炊）</span>
        <ol>
          <li><span class="dot">💭</span><span class="name">今日の献立を考える</span></li>
          <li><span class="dot">🛒</span><span class="name">スーパーで買い物</span></li>
          <li><span class="dot">🍳</span><span class="name">下ごしらえ・調理</span></li>
          <li class="keep"><span class="dot">🍽️</span><span class="name">いただきます</span></li>
          <li><span class="dot">🧽</span><span class="name">片付け・洗い物</span></li>
        </ol>
        <p class="tl__foot">※一般的な自炊の流れのイメージです。</p>
      </div>
      <div class="tl tl--after">
        <span class="tl__label">宅配食なら</span>
        <ol>
          <li><span class="dot">📦</span><span class="name">自宅に届く（献立も食材も手配ずみ）</span></li>
          <li><span class="dot">♨️</span><span class="name">温める・仕上げるだけ</span></li>
          <li><span class="dot">🍽️</span><span class="name">いただきます</span></li>
          <li class="free"><span class="dot">✨</span><span class="name">空いた時間は、じぶんのために</span></li>
        </ol>
        <p class="tl__foot">散歩・趣味・家族との時間・ゆっくりお風呂。使い方はあなた次第。</p>
      </div>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">3 PROMISES</span>
      <h2>「ラクする」だけで終わらせない、3つの選び方</h2>
      <p>時短と引き換えに食事の満足度を下げたくない。そんな方のための比較ポイントです。</p>
    </div>
    <div class="promise-grid">
      <div class="promise"><div class="promise__img" style="background-image:url('assets/crop-wok.webp')"></div><span class="promise__no">1</span>
        <div class="promise__body"><h3>家で作る料理に近いおいしさか</h3><p>素材や調理法にこだわり、できたての満足感を目指すサービスを比べます。</p></div></div>
      <div class="promise"><div class="promise__img" style="background-image:url('assets/crop-veg.webp')"></div><span class="promise__no">2</span>
        <div class="promise__body"><h3>栄養バランスを任せられるか</h3><p>管理栄養士が監修するメニューなど、毎日食べても安心できるかを確認します。</p></div></div>
      <div class="promise"><div class="promise__img" style="background-image:url('assets/crop-bento.webp')"></div><span class="promise__no">3</span>
        <div class="promise__body"><h3>自分の暮らしに合う手軽さか</h3><p>温めるだけ、少し作る、まとめて届くなど、ライフスタイルに合う形で選べます。</p></div></div>
    </div>
  </section>

  <section id="categories">
    <div class="sec-head">
      <span class="eyebrow">CATEGORY</span>
      <h2>目的から宅配食を探す</h2>
      <p>誰のための食事か、どんな暮らしに合わせたいか。気になるカテゴリから見てみてください。</p>
    </div>
    <div class="category-grid">
{cards_html}
    </div>
  </section>

  <section class="pick-wall">
    <div class="sec-head">
      <span class="eyebrow">PICK UP</span>
      <h2>気になるサービスをのぞいてみる</h2>
      <p>各カテゴリで紹介している宅配食サービスの一部です。（PR）</p>
    </div>
    <div class="pick-grid">
{pick_html}
    </div>
  </section>

  <section id="new-articles">
    <div class="sec-head">
      <span class="eyebrow">NEW</span>
      <h2>新着記事</h2>
    </div>
    <ul class="new-list">
{new_list}
    </ul>
  </section>

  <section class="intro-block" style="margin-top:70px">
    <h2>このサイトについて</h2>
    <p>「宅配食ナビ」は、共働き世帯の時短ニーズから、一人暮らしの食事管理、離乳食、高齢の家族の見守り食まで、宅配食・ミールキットサービスを目的別に探せるように情報を整理した比較サイトです。</p>
    <p>当サイトの記事は、公開されている利用者の声や各社の公式情報をもとに第三者視点で構成しており、運営者自身の体験として記載しているものではありません。詳しくは<a href="about/">運営者情報・アフィリエイト開示</a>をご覧ください。</p>
  </section>

  <p class="affiliate-notice">本サイトはアフィリエイトプログラム(A8.net等)による収益を得ています。紹介する商品・サービスの選定や評価に、広告主から評価内容への直接的な影響はありません。</p>
</main>'''

s2 = re.sub(r'<main>.*</main>', lambda _: main, s, flags=re.S)
open(p, 'w', encoding='utf8', newline='\n').write(s2)
print('cards', len(CARDS), 'picks', len(picks), 'new', len(items))
