# Prompt Aggregator - Dify版 セットアップ手順

## 前提条件

- [Dify on PAPP] アカウント
- LLM API Key（OpenAI GPT-4o-mini 推奨）

---

## Step 1: Knowledge Base 作成

1. Dify にログイン
2. 左メニュー **Knowledge** → **Create Knowledge**
3. 以下を設定:

| 項目 | 設定値 |
|------|--------|
| 名前 | `prompt-collection` |
| 説明 | `AIプロンプト集` |

4. **Create** をクリック

## Step 2: ドキュメントアップロード

`dify/batches/` 内の ZIP ファイルを順番にアップロードします。

1. Knowledge Base `prompt-collection` を開く
2. **Add File** → **Upload Files**
3. `batch_01.zip` 内の 20 ファイルを選択してアップロード
4. チャンク設定:

| 項目 | 設定値 |
|------|--------|
| チャンクモード | General |
| セパレータ | `---` |
| 最大チャンクサイズ | 4000 tokens |
| チャンクオーバーラップ | 0 |

5. インデックス方式: **High Quality**
6. Embedding Model: `text-embedding-3-small`（推奨）
7. 検索設定: **Hybrid Search**（セマンティック + キーワード）
8. **Save & Process** をクリック
9. batch_02 ~ batch_41 まで同じ手順で繰り返す

> **Tips**: `knowledge_base_all.zip` (2MB) を解凍して全814ファイルを一括選択も可能（ただし1回20ファイルまで）

## Step 3: 検索テスト

1. Knowledge Base の **Testing** タブを開く
2. テストクエリを入力して検索精度を確認:

```
テスト例:
- 「議事録を要約したい」 → 要約系プロンプトがヒットするか
- 「Pythonのコードレビュー」 → プログラミング系がヒットするか
- 「メール文面を作成」 → 文章作成系がヒットするか
- 「001」 → ID指定で正確にヒットするか
```

3. 精度が低い場合は Top-K や検索方式を調整

## Step 4: Chatflow アプリ作成

1. 左メニュー **Studio** → **Create App**
2. **Chatflow** を選択
3. 名前: `プロンプト検索アシスタント`
4. DSL インポート: `dify/prompt-aggregator-chatflow.yml` をインポート
   - または、以下の手順で手動構築

### 手動構築の場合

#### 4-1: Question Classifier ノード追加

Start の次に **Question Classifier** ノードを配置。

| 分類 | 説明 | キーワード例 |
|------|------|-------------|
| Class 1: 検索 | プロンプトを探す意図 | 「探して」「したい」「ある？」 |
| Class 2: ID指定 | 特定IDの詳細 | 「#001」「番の詳細」「を見せて」 |
| Class 3: カテゴリ | カテゴリ別一覧 | 「〜系」「カテゴリ」「一覧」 |
| Class 4: その他 | 挨拶・ヘルプ | 「こんにちは」「使い方」 |

#### 4-2: Knowledge Retrieval ノード追加（3個）

各分類フローに Knowledge Retrieval ノードを配置:

- **検索用**: Top-K=5, Score Threshold=0.5
- **ID指定用**: Top-K=1
- **カテゴリ用**: Top-K=10

すべて Knowledge Base `prompt-collection` を指定。

#### 4-3: LLM ノード追加（4個）

各 Knowledge Retrieval の後に LLM ノードを配置。

**モデル設定（共通）**:
| 項目 | 設定値 |
|------|--------|
| Model | gpt-4o-mini |
| Temperature | 0.3 |
| Max Tokens | 2000 |

**各ノードのシステムプロンプト**: `dify/prompts/` ディレクトリ内のファイルを参照。

#### 4-4: End ノード接続

各 LLM ノードの出力を End ノードに接続。

## Step 5: 会話オープナー設定

Chatflow のオープナーメッセージを設定:

```
プロンプト検索アシスタントへようこそ！
814件のAIプロンプトから、あなたに最適なプロンプトをお探しします。

使い方:
- やりたいことを入力 → 「メール文面を作りたい」
- カテゴリで探す → 「プログラミング系を見せて」
- ID指定 → 「#001の詳細を見せて」
```

サジェスト質問:
- 「文章を要約するプロンプトを探して」
- 「プログラミング系のプロンプト一覧」
- 「業務改善に使えるプロンプトは？」

## Step 6: テストと公開

1. **Preview** ボタンで動作テスト
2. テスト項目:
   - 検索: 「議事録を要約するプロンプト」
   - ID指定: 「#003の詳細を見せて」
   - カテゴリ: 「プログラミング系のプロンプト」
   - フォローアップ: 「もっとビジネス向けは？」
   - ヘルプ: 「使い方を教えて」
3. **Publish** → **Update** でアプリを公開
4. **Access** から Web App URL をコピー

### 埋め込み設定

**iframe**:
```html
<iframe
  src="https://udify.app/chatbot/YOUR_APP_TOKEN"
  style="width: 100%; height: 600px; border: none;"
  allow="clipboard-write"
></iframe>
```

**チャットウィジェット**:
```html
<script>
  window.difyChatbotConfig = { token: 'YOUR_APP_TOKEN' };
</script>
<script
  src="https://udify.app/embed.min.js"
  defer
></script>
```

## Step 7: DSL エクスポート（バックアップ）

1. Studio でアプリを開く
2. 右上メニュー → **Export DSL**
3. YAML ファイルを `dify/prompt-aggregator-chatflow.yml` として保存

---

## ディレクトリ構成

```
dify/
├── README.md                         # この手順書
├── knowledge_base/                   # 個別テキストファイル (814件)
│   ├── prompt_001.txt
│   ├── prompt_002.txt
│   └── ...
├── batches/                          # 20ファイルずつの ZIP (41個)
│   ├── batch_01.zip
│   ├── batch_02.zip
│   └── ...
├── knowledge_base_all.zip            # 全件一括 ZIP (2MB)
├── prompts/                          # LLM ノード用プロンプト
│   ├── search_result.md
│   ├── detail_view.md
│   ├── category_list.md
│   └── guide_response.md
└── prompt-aggregator-chatflow.yml    # Chatflow DSL (構築後エクスポート)
```

