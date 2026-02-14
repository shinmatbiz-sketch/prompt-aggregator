#!/usr/bin/env python3
"""
Prompt Categorizer
==================
Assigns category tags to each prompt based on title + body keyword analysis.

Categories:
  #文章作成・要約
  #文書校正・編集
  #アイデア創出・企画
  #業務改善
  #情報収集・分析
  #コミュニケーション支援
  #プログラミング
  #意識改革・スキルアップ
"""

import json
import io
import sys
import re
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "prompts.json"

# ---------------------------------------------------------------------------
# Category definitions: (tag, keywords, title_boost_keywords)
#   - keywords: matched against title + body (case-insensitive)
#   - title_boost: if matched in title, score gets extra weight
# ---------------------------------------------------------------------------

CATEGORIES: list[tuple[str, list[str], list[str]]] = [
    (
        "#文章作成・要約",
        [
            "文章を作", "文章作成", "文章案", "文書作成",
            "要約", "要点", "まとめ",
            "原稿", "草案", "ドラフト",
            "レポート作成", "報告書作成", "報告書", "復命書",
            "記事作成", "記事を作", "コンテンツ制作", "コンテンツを制作",
            "メール作成", "メールの自動作成",
            "議事録", "プレスリリース",
            "スピーチ", "挨拶状", "お礼状", "依頼文", "招待状",
            "答弁書", "計画書", "概要書", "提案書作成",
            "テキスト作成", "文書の作成", "PR文", "紹介文",
            "説明文作成", "説明テキスト",
            "チラシ", "タイトル付け", "タイトルを",
            "論述作成", "文章に", "文章を統合",
            "表を作", "書き出し", "作文",
            "翻訳", "多言語", "英訳", "和訳",
            "送付状", "案内文", "通知文", "周知用文書",
            "アンケート作成", "問題作成",
        ],
        [
            "文章", "作成", "要約", "原稿", "レポート", "記事",
            "メール", "議事録", "翻訳", "報告書",
        ],
    ),
    (
        "#文書校正・編集",
        [
            "校正", "添削", "リライト", "推敲",
            "編集", "修正", "チェック",
            "言い換え", "言い回し", "フレーズを",
            "表現を変", "表現を豊か", "表現提案",
            "フォーマットを抽出", "ブラッシュアップ",
            "文章を解析", "文章の議論を分析",
            "一貫性", "誤字", "脱字",
            "変換", "書き換え", "再構築",
            "人間味あふれる", "面白くする",
            "深掘り", "具体例を追加",
            "エピソード風", "共感文章",
            "行動に移しやすい", "説得力を強化",
        ],
        [
            "校正", "添削", "リライト", "言い換え", "編集",
            "ブラッシュアップ", "変換",
        ],
    ),
    (
        "#アイデア創出・企画",
        [
            "アイデア", "企画", "発想", "ブレスト", "ブレインストーミング",
            "キャッチコピー", "コピーの案",
            "創出", "新サービス", "新規事業",
            "イベント企画", "イベントの企画",
            "提案してもらう", "案を出", "案出し",
            "施策案", "事業提案", "ビジネスモデル",
            "プロジェクト推進", "フレームワーク選択",
            "グループワーク", "課題を設計",
            "ビジョンを創出", "サービス創出",
        ],
        [
            "アイデア", "企画", "キャッチコピー", "創出", "提案",
        ],
    ),
    (
        "#業務改善",
        [
            "業務改善", "業務効率", "効率化", "自動化",
            "手順", "プロセス", "ワークフロー",
            "課題解決", "問題解決", "課題洗い出し",
            "トラブル", "是正", "原因を切り分け",
            "改善", "最適化", "合理化",
            "マニュアル", "手続き",
            "論点", "洗い出し",
            "リスク", "先読み", "影響予測",
            "何から始めれば", "相談",
            "作業手順", "手法の提案",
            "チェックリスト",
            "問い合わせ内容の傾向",
        ],
        [
            "業務改善", "効率化", "課題", "改善", "トラブル",
        ],
    ),
    (
        "#情報収集・分析",
        [
            "分析", "リサーチ", "調査", "研究",
            "データ分析", "データを",
            "比較", "評価", "予測", "影響",
            "統計", "傾向", "市場",
            "レポートを作成", "分析レポート",
            "情報収集", "情報整理",
            "プロファイル", "解析",
            "SWOT", "PEST", "マトリクス",
            "調べ", "まとめる",
        ],
        [
            "分析", "リサーチ", "調査", "データ", "評価", "解析",
        ],
    ),
    (
        "#コミュニケーション支援",
        [
            "コミュニケーション", "対話",
            "返信", "メールへの返信", "メールに返信",
            "声掛け", "フィードバック",
            "質問", "想定質問", "FAQ", "Q＆A", "Q&A",
            "クレーム", "対応",
            "説明", "わかりやすく説明",
            "プレゼン", "プレゼンテーション",
            "伝える", "伝わる",
            "注意・指導", "アドバイス",
            "褒め言葉", "感謝", "お礼",
            "フォローアップ", "相談者",
            "読者", "市民の声",
            "立場に応じた", "文化的配慮",
        ],
        [
            "コミュニケーション", "返信", "クレーム", "プレゼン",
            "質問", "説明", "対応",
        ],
    ),
    (
        "#プログラミング",
        [
            "プログラミング", "プログラム",
            "コード", "コーディング",
            "Excel", "エクセル", "数式", "関数",
            "VBA", "マクロ",
            "Python", "JavaScript", "TypeScript",
            "HTML", "CSS", "SQL",
            "API", "スクリプト",
            "データベース", "DB",
            "システム", "アプリ開発", "アプリケーション開発",
            "GAS", "スプレッドシート",
            "正規表現", "テスト",
        ],
        [
            "Excel", "プログラミング", "コード", "VBA", "Python",
            "数式", "関数", "マクロ", "GAS",
        ],
    ),
    (
        "#意識改革・スキルアップ",
        [
            "スキルアップ", "スキル向上",
            "自己分析", "自己評価", "自己肯定",
            "キャリア", "キャリアビジョン",
            "マインド", "マインドチェンジ", "意識改革",
            "アファメーション", "自分を好き",
            "ストレスマネジメント", "アンガーマネジメント",
            "研修", "セミナー", "講座",
            "学習", "勉強", "リスキリング",
            "ビジョン", "目標設定", "目標達成",
            "コーチング", "メンタリング",
            "挫折", "立ち直る", "成長",
            "思考", "TEFCAS", "振り返り",
            "行動計画", "モチベーション",
            "欠点から長所", "自分の思っていること",
            "人を魅了する",
        ],
        [
            "スキルアップ", "自己", "キャリア", "マインド",
            "研修", "コーチング", "ビジョン", "目標",
        ],
    ),
]


def classify(title: str, body: str) -> list[str]:
    """Classify a prompt into one or more categories."""
    text_full = f"{title}\n{body}".lower()
    title_lower = title.lower()

    scores: dict[str, float] = {}

    for tag, keywords, title_boost in CATEGORIES:
        score = 0.0
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in title_lower:
                score += 3.0  # Strong signal: keyword in title
            elif kw_lower in text_full:
                score += 1.0  # Weaker signal: keyword in body

        # Title boost: extra points for high-confidence title keywords
        for bkw in title_boost:
            bkw_lower = bkw.lower()
            if bkw_lower in title_lower:
                score += 2.0

        if score > 0:
            scores[tag] = score

    if not scores:
        # Fallback: assign most generic category
        return ["#文章作成・要約"]

    # Sort by score descending
    sorted_tags = sorted(scores.items(), key=lambda x: -x[1])
    top_score = sorted_tags[0][1]

    # Primary category (highest score)
    result = [sorted_tags[0][0]]

    # Add secondary categories if they score >= 60% of top
    for tag, score in sorted_tags[1:]:
        if score >= top_score * 0.6:
            result.append(tag)
        else:
            break

    return result


def main() -> None:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    print(f"Loaded {len(prompts)} prompts")

    # Category distribution counter
    dist: dict[str, int] = {}

    for p in prompts:
        tags = classify(p["title"], p["body"])
        p["categories"] = tags

        for t in tags:
            dist[t] = dist.get(t, 0) + 1

    # Save
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Updated {len(prompts)} prompts.\n")
    print("Category distribution:")
    for tag, count in sorted(dist.items(), key=lambda x: -x[1]):
        bar = "█" * (count // 5)
        print(f"  {tag:<20s} {count:>4d}  {bar}")

    # Show some examples
    print("\n--- Examples ---")
    for p in prompts[:10]:
        cats = ", ".join(p["categories"])
        title = p["title"][:50]
        print(f"  {p['id']}: {title:<50s} -> {cats}")


if __name__ == "__main__":
    main()
