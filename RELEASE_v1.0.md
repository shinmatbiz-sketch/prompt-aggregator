# Prompt Aggregator v1.0 - 初版リリース記録

**リリース日**: 2026-02-14
**プロジェクト**: prompt-aggregator
**ソースデータ**: https://nanyo-city.jpn.org/prompt/ (001.html - 999.html)

---

## 概要

南陽市が公開しているAIプロンプト集（全999ページ）をクロールし、モダンな検索・閲覧Webアプリとして再構成したプロジェクト。即座に検索、コピー、外部AIサービスへの送信ができるインターフェースを提供する。

---

## データ取得

### クロール結果

| 項目 | 値 |
|------|-----|
| 対象URL | 001.html - 999.html (999ページ) |
| 取得成功 | **816件** |
| 404/エラー | 183件 |
| データファイル | `data/prompts.json` (5.6MB) |
| クロール方式 | Python (requests + BeautifulSoup) |
| 再開可能 | progress.log によるレジューム対応 |

### HTMLパーサー仕様

- **タイトル抽出**: `.box-title` > `<title>` > `<h1>` の優先順で取得
- **本文抽出**: `.box-bun` 配下の `<p>`, `<h2>`, `<textarea>` を結合
- **エンコーディング**: サーバーは ISO-8859-1 を返すが実体は UTF-8 のため強制指定
- **ポライトネス**: 1秒間隔、50件ごとに中間保存

---

## カテゴリ分類

### 手法

キーワードスコアリングによる自動分類:
- タイトル内キーワード一致: +3.0pt
- 本文内キーワード一致: +1.0pt
- タイトルブーストキーワード: +2.0pt
- 閾値: 最高スコアの60%以上で副カテゴリとして付与
- フォールバック: 未分類は「#文章作成・要約」に割り当て

### カテゴリ分布

| カテゴリ | 件数 |
|----------|------|
| #文章作成・要約 | 318 |
| #情報収集・分析 | 311 |
| #コミュニケーション支援 | 288 |
| #意識改革・スキルアップ | 246 |
| #業務改善 | 205 |
| #文書校正・編集 | 105 |
| #アイデア創出・企画 | 101 |
| #プログラミング | 38 |

※ 1つのプロンプトが複数カテゴリに属する場合があるため、合計は816を超える。

---

## 機能一覧

### 一覧ページ (`/`)

- **あいまい検索**: Fuse.js による即座のクライアントサイド検索 (タイトル重み0.7, 本文0.3)
- **カテゴリフィルタ**: 8カテゴリのチップUI、カテゴリ別件数表示、トグル操作
- **検索 + カテゴリ併用**: テキスト検索とカテゴリフィルタの同時適用
- **無限スクロール**: IntersectionObserver による30件ずつの遅延読み込み
- **キーボードショートカット**: `/` で検索フォーカス、`Esc` でクリア

### カード (`PromptCard`)

- ID バッジ、タイトル、カテゴリタグ（クリックでフィルタ）、本文プレビュー
- **コピー**: クリップボードにプロンプト全文をコピー（トースト通知付き）
- **ChatGPTで開く**: chatgpt.com にプロンプトを渡して新規タブで開く
- **Geminiで開く**: gemini.google.com にプロンプトを渡して新規タブで開く

### 詳細ページ (`/[id]`)

- プロンプト全文表示（等幅フォント、行保持）
- コピー / ChatGPT / Gemini ボタン
- リンクコピーボタン
- カテゴリタグ（クリックで一覧ページのフィルタへ遷移）
- 前後ナビゲーション
- 動的ページタイトル設定

---

## 技術スタック

| レイヤー | 技術 |
|----------|------|
| フレームワーク | Next.js 14 (App Router) |
| 言語 | TypeScript, React 18 |
| スタイリング | Tailwind CSS |
| 検索 | Fuse.js 7 |
| アイコン | lucide-react |
| データ取得 | Python 3 (requests, BeautifulSoup4) |
| ビルド出力 | standalone |

---

## ファイル構成

```
prompt-aggregator/
├── app/
│   ├── layout.tsx          # ルートレイアウト (メタデータ, 日本語lang)
│   ├── page.tsx            # 一覧ページ (検索, カテゴリフィルタ, 無限スクロール)
│   ├── globals.css         # Tailwind + トーストアニメーション
│   └── [id]/
│       └── page.tsx        # 詳細ページ
├── components/
│   ├── PromptCard.tsx      # カード型プロンプト表示コンポーネント
│   └── Toast.tsx           # トースト通知コンポーネント
├── lib/
│   └── utils.ts            # 型定義, ユーティリティ関数, カテゴリ色定義
├── data/
│   └── prompts.json        # 全816件のプロンプトデータ (5.6MB)
├── scripts/
│   ├── crawl_prompts.py    # Webクローラー (レジューム対応)
│   ├── categorize_prompts.py # カテゴリ自動分類スクリプト
│   ├── requirements.txt    # Python依存パッケージ
│   ├── progress.log        # クロール進捗ログ
│   └── crawler.log         # クロール実行ログ
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── next.config.js
├── postcss.config.js
└── .gitignore
```

---

## 開発中に対処した課題

### 1. HTMLパーサーの修正

**問題**: 元サイトのタイトルが `<h1>` ではなく `.box-title` に格納されていた
**対応**: パーサーを `.box-title` → `<title>` → `<h1>` の優先順に変更

### 2. エンコーディング問題

**問題**: サーバーの Content-Type ヘッダーが ISO-8859-1 を返すが、実際のコンテンツは UTF-8
**対応**: `resp.encoding = "utf-8"` で強制指定（バイトレベルで UTF-8 であることを確認済み）

### 3. Windows コンソール出力

**問題**: Python の `print()` が cp932 エンコードで失敗（日本語の特殊文字）
**対応**: `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")`

### 4. textarea 内容の取得漏れ

**問題**: プロンプト本文が `<textarea>` のデフォルト値に格納されており、本文が空になるケースがあった
**対応**: パーサーに `<textarea>` 要素のテキスト取得を追加

### 5. Next.js Suspense 要件

**問題**: `useSearchParams()` が Suspense 境界なしで使用されエラー
**対応**: `HomePage` コンポーネントを `<Suspense>` でラップし、内部コンポーネントに分離

### 6. Fuse.js 型エラー

**問題**: `Fuse.IFuseOptions` が名前空間として認識されない
**対応**: `import { type IFuseOptions } from "fuse.js"` に変更

---

## 実行方法

### データ取得（初回のみ）

```bash
cd D:\AG1\prompt-aggregator\scripts
pip install -r requirements.txt
python crawl_prompts.py       # 816件取得 (~25分)
python categorize_prompts.py  # カテゴリ自動付与
```

### 開発サーバー

```bash
cd D:\AG1\prompt-aggregator
npm install
npm run dev
# http://localhost:3000
```

### 本番ビルド

```bash
npm run build
npm start
```

---

## 今後の拡張候補

- [ ] SSG (Static Site Generation) による静的エクスポート
- [ ] OGP メタタグ対応（詳細ページのSNS共有最適化）
- [ ] ダークモード
- [ ] お気に入り・ブックマーク機能（localStorage）
- [ ] プロンプト使用回数のトラッキング
- [ ] Claude で開く ボタン追加
- [ ] PWA 対応（オフライン閲覧）
- [ ] 定期クロールによるデータ自動更新

---

*v1.0 - Initial Release*
