# tools/ — 宅配食ナビ 運用スクリプト

静的HTML (`docs/`) を扱うためのPythonスクリプト。いずれも `python tools/<name>.py` で実行（リポジトリ直下から）。

| スクリプト | 用途 | 再実行 |
|---|---|---|
| `build_home.py` | トップページ `docs/index.html` の `<main>` を再生成。新着リスト(`.new-list`)と各記事のA8バナーを読み取って再利用。カテゴリチップは保持する | 可 (冪等) |
| `seo_audit.py` | 全ページSEO監査 (title/description/h1/canonical/OG/JSON-LD/alt/リンク切れ/孤立/sitemap)。`sitemap.xml` と `sitemap-main.xml` の一致も検査。`--json out.json` で保存 | 可 |
| `make_articles_20261004.py` | 2026-10-04の4記事を生成。**次回の記事化は、このファイルをコピーして `ARTICLES` のデータだけ差し替える**（ヘッダー/フッター/スポンサー枠は同カテゴリの既存記事から流用、FAQPage/Article/Breadcrumb構造化データ付き） | 同じ記事を上書き |
| `register_articles_20261004.py` | 新記事をカテゴリ一覧の比較表・ItemList・sitemap・トップ新着に登録 | **一度だけ** (assertで二重登録を防止) |
| `seo_fix_20261004.py` | SEO監査の一括修正 (h4→h3、公開日/更新日表示、OG補完、sitemap lastmod) | **一度だけ** |
| `adsense_prep.py` | AdSense申請準備 (contactページ新設・プライバシーポリシー追記・フッターにお問い合わせリンク) | **一度だけ** |
| `add_guide_nav.py` | 全ページのヘッダーナビに「選び方ガイド」を追加 | **一度だけ** |
| `guide_data.py` / `make_guides.py` | `docs/guide/` の選び方ガイド5本＋一覧を生成 (内容は guide_data.py、`[[カテゴリ/記事|表示名]]` で内部リンク)。sitemapにも登録 | 可 (上書き) |
| `enhance_categories.py` | カテゴリ一覧9ページに注意点・かんたん診断・追加FAQ(JSON-LD含む)・ガイド導線を追加 | **一度だけ** |
| `add_article_faqs.py` + `faq/*.py` | 個別記事にFAQ(HTML・FAQPage JSON-LD・目次)を追加。`python tools/add_article_faqs.py <faqモジュール名>`。FAQは記事本文・公式サイトで確認できた事実のみで書く。FAQPage既存の記事はスキップ | 可 (冪等) |

## 新規A8プログラムを記事化する手順（次回用）
1. A8 `/program/list/partnered` を提携日降順で開き、`WRITING_GUIDE.md` にプログラムIDが無いものを抽出（"New" バッジは当てにならない。別名プログラムの可能性も詳細ページで確認）。
2. 各 `/program/detail-partnered?programId=…` で成果条件・否認条件・NG表現を確認（A8用語は本文に書かない）。
3. `/program/create-link?programId=…` で「通常広告用」を1回クリック → 全素材の `textarea` から a8mat を一括取得（`WRITING_GUIDE.md` にID・EPCを記録）。
4. 広告主公式サイトを WebFetch で確認し、事実のみで記事化（体験談は書かない、疾患の治療・改善は断定しない）。
5. `make_articles_*.py` をコピーして生成 → `register_articles_*.py` で登録 → `seo_audit.py` で確認 → コミット/プッシュ → GitHub Pages反映待ち(curl 200) → A8「広告掲載URL管理」へURL提出。
6. CSS を変えたら `style.css?v=N` を全ページで更新（現在 v=8）。

## 注意
- ブラウザペインのスクリーンショットが不安定なときは Edge ヘッドレスで撮る: `msedge --headless --screenshot=out.png --window-size=500,H URL`（最小幅約500px）。
- `build_home.py` は旧版だと新着チップを消す不具合があった（修正済み）。消えたら `git checkout docs/index.html`。
