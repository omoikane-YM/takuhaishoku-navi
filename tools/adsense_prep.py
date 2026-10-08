"""AdSense申請準備 (一度だけ実行): お問い合わせページ新設、プライバシーポリシー追記、全ページのフッターにリンク追加、sitemap登録。"""
import re, pathlib

DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"
BASE = "https://takuhaishoku-navi.net/"

# 1. contact page (privacy page as template)
priv = (DOCS / "privacy/index.html").read_text(encoding="utf-8")
head = priv[: priv.index("<main>")]
head = head.replace("privacy/", "contact/").replace("プライバシーポリシー｜宅配食ナビ", "お問い合わせ｜宅配食ナビ")
head = re.sub(r'(<meta name="description" content=")[^"]*', r"\1宅配食ナビへのお問い合わせ窓口です。掲載内容の誤りのご指摘、情報の更新依頼、広告掲載などのご連絡はメールにてお受けしています。", head)
head = re.sub(r'(<meta property="og:description" content=")[^"]*', r"\1宅配食ナビへのお問い合わせ窓口です。掲載内容の誤りのご指摘、情報の更新依頼などはメールにてお受けしています。", head)
head = head.replace("&gt; プライバシーポリシー</p>", "&gt; お問い合わせ</p>")
foot = priv[priv.index("</main>"):]
foot = foot.replace('<li><a href="./">プライバシーポリシー</a></li>', '<li><a href="../privacy/">プライバシーポリシー</a></li>')
body = """<main>
  <section class="hero">
    <div class="hero-inner">
      <h1>お問い合わせ</h1>
    </div>
  </section>

  <section class="intro-block">
    <h2>お問い合わせ窓口</h2>
    <p>「宅配食ナビ」に関するご連絡は、下記のメールアドレスまでお願いいたします。</p>
    <p>内容を確認のうえ、通常3営業日以内を目安にご返信します。ただし、内容によってはお時間をいただく場合や、ご返信できない場合があります。</p>
  </section>

  <section class="intro-block">
    <h2>こんなときはご連絡ください</h2>
    <ul>
      <li>掲載している価格・内容・リンクに誤りや古い情報を見つけた</li>
      <li>サービス名・商品名などの表記について修正を希望する</li>
      <li>記事の内容についてのご意見・ご要望</li>
      <li>広告掲載・取材などのご相談</li>
    </ul>
  </section>

  <section class="intro-block">
    <h2>ご注意</h2>
    <ul>
      <li>当サイトは情報提供サイトであり、各サービスの注文・配送・返金・解約に関するお問い合わせには対応できません。ご利用中のサービスの運営会社へ直接お問い合わせください。</li>
      <li>健康状態や疾患に関するご相談には対応できません。医師・管理栄養士等の専門家へご相談ください。</li>
      <li>お寄せいただいた個人情報は、お問い合わせへの対応以外の目的では利用しません。</li>
    </ul>
  </section>
"""
(DOCS / "contact").mkdir(exist_ok=True)
(DOCS / "contact/index.html").write_text(head + body + foot, encoding="utf-8")

# 2. privacy policy additions
p = DOCS / "privacy/index.html"
s = priv
assert "Google AdSense" not in s
old = '  <section class="intro-block">\n    <h2>免責事項</h2>'
new = """  <section class="intro-block">
    <h2>Google AdSense（広告配信）について</h2>
    <p>当サイトでは、第三者配信事業者であるGoogleが提供する広告サービス「Google AdSense」を利用する場合があります。</p>
    <p>Googleをはじめとする第三者配信事業者は、Cookieを使用して、ユーザーが当サイトや他のサイトに過去にアクセスした際の情報に基づいて広告を配信します。</p>
    <p>GoogleによるCookieの使用により、ユーザーが当サイトや他のサイトにアクセスした際の情報に基づいて、Googleやそのパートナーが適切な広告をユーザーに表示できます。</p>
    <p>ユーザーは、<a href="https://adssettings.google.com/" target="_blank" rel="noopener">Googleの広告設定</a>でパーソナライズ広告を無効にできます。また、<a href="https://www.aboutads.info/" target="_blank" rel="noopener">www.aboutads.info</a>にアクセスすると、第三者配信事業者がパーソナライズ広告の配信に使用するCookieを無効にできます。</p>
    <p>Googleによる広告でのCookieの取り扱いについては、<a href="https://policies.google.com/technologies/ads?hl=ja" target="_blank" rel="noopener">Googleの広告に関するポリシー</a>をご確認ください。</p>
  </section>

  <section class="intro-block">
    <h2>Googleアナリティクスについて</h2>
    <p>当サイトでは、アクセス状況の把握のためにGoogleアナリティクスを利用しています。Googleアナリティクスはトラフィックデータの収集にCookieを使用します。このデータは匿名で収集されており、個人を特定するものではありません。収集の拒否は、ブラウザのCookie設定を無効にするか、<a href="https://tools.google.com/dlpage/gaoptout?hl=ja" target="_blank" rel="noopener">Googleアナリティクス オプトアウト アドオン</a>の利用で可能です。詳細は<a href="https://policies.google.com/technologies/partner-sites?hl=ja" target="_blank" rel="noopener">Googleのポリシーと規約</a>をご確認ください。</p>
  </section>

  <section class="intro-block">
    <h2>アフィリエイト広告について</h2>
    <p>当サイトは、A8.net等のアフィリエイトプログラムに参加し、広告主の商品・サービスを紹介しています。リンク経由で商品購入やサービス申込みがあった場合、当サイトに報酬が支払われることがあります。詳細は<a href="../about/">運営者情報・アフィリエイト開示</a>をご覧ください。</p>
  </section>

  <section class="intro-block">
    <h2>著作権・リンクについて</h2>
    <p>当サイトの文章・画像・デザインの著作権は運営者または正当な権利者に帰属します。無断での転載・複製はお断りします。引用される場合は、出典として当サイトへのリンクを明記してください。当サイトへのリンクは自由です。</p>
  </section>

""" + old
assert old in s
s = s.replace(old, new, 1)
s = s.replace("アクセス解析（Googleアナリティクス）の利用、Cookieの扱い、広告配信、免責事項について", "アクセス解析（Googleアナリティクス）、広告配信（Google AdSense）、Cookieの扱い、免責事項について")
p.write_text(s, encoding="utf-8")

# 3. footer link on every page
pat = re.compile(r'( *)<li><a href="([^"]*)">プライバシーポリシー</a></li>')
n = 0
for f in DOCS.rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    if "contact/" in t.split("<footer")[-1] and f.name == "index.html" and f.parent.name == "contact":
        continue
    def rep(m):
        href = m.group(2)
        chref = href.replace("privacy/", "contact/") if href.endswith("privacy/") else "../contact/"
        return m.group(0) + "\n" + m.group(1) + f'<li><a href="{chref}">お問い合わせ</a></li>'
    t2, c = pat.subn(rep, t)
    if f.parent.name == "contact":
        continue
    if c:
        f.write_text(t2, encoding="utf-8"); n += 1
print("footers updated:", n)

# 4. sitemaps
for name in ("sitemap.xml", "sitemap-main.xml"):
    sm = DOCS / name
    t = sm.read_text(encoding="utf-8")
    line = f"  <url><loc>{BASE}privacy/</loc></url>"
    assert line in t
    t = t.replace(line, line + f"\n  <url><loc>{BASE}contact/</loc></url>")
    sm.write_text(t, encoding="utf-8")
