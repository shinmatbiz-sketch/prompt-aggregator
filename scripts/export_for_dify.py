"""
export_for_dify.py
prompts.json を Dify Knowledge Base 用の個別テキストファイルに変換し、
20ファイルずつの ZIP バッチにまとめる。

出力:
  dify/knowledge_base/prompt_001.txt ~ prompt_XXX.txt
  dify/batches/batch_01.zip ~ batch_XX.zip  (20ファイルずつ)
  dify/knowledge_base_all.zip              (全件一括)
"""

import io
import json
import os
import sys
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(PROJECT_DIR, "data", "prompts.json")
KB_DIR = os.path.join(PROJECT_DIR, "dify", "knowledge_base")
BATCH_DIR = os.path.join(PROJECT_DIR, "dify", "batches")
ALL_ZIP_PATH = os.path.join(PROJECT_DIR, "dify", "knowledge_base_all.zip")

BATCH_SIZE = 20  # Dify の 1回アップロード上限


def load_prompts():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def format_prompt(p):
    """1件のプロンプトを Dify Knowledge Base 用テキストに整形"""
    pid = p["id"]
    title = p["title"]
    categories = ", ".join(p.get("categories", []))
    body = p["body"]

    return f"""ID: {pid}
タイトル: {title}
カテゴリ: {categories}

---

{body}
""".strip()


def export_text_files(prompts):
    """個別テキストファイルとして出力"""
    os.makedirs(KB_DIR, exist_ok=True)
    paths = []
    for p in prompts:
        filename = f"prompt_{p['id']}.txt"
        filepath = os.path.join(KB_DIR, filename)
        content = format_prompt(p)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        paths.append((filename, filepath))
    return paths


def create_batch_zips(file_paths):
    """20ファイルずつの ZIP バッチを作成"""
    os.makedirs(BATCH_DIR, exist_ok=True)
    batch_count = 0
    for i in range(0, len(file_paths), BATCH_SIZE):
        batch_count += 1
        batch = file_paths[i : i + BATCH_SIZE]
        zip_path = os.path.join(BATCH_DIR, f"batch_{batch_count:02d}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, filepath in batch:
                zf.write(filepath, filename)
        print(f"  batch_{batch_count:02d}.zip ({len(batch)} files)")
    return batch_count


def create_all_zip(file_paths):
    """全件一括 ZIP を作成"""
    with zipfile.ZipFile(ALL_ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, filepath in file_paths:
            zf.write(filepath, filename)


def main():
    print("=== Dify Knowledge Base エクスポート ===\n")

    # 1. データ読み込み
    prompts = load_prompts()
    print(f"読み込み: {len(prompts)} 件\n")

    # 2. 個別テキストファイル生成
    print("個別テキストファイルを生成中...")
    file_paths = export_text_files(prompts)
    print(f"  -> {len(file_paths)} ファイル生成完了: dify/knowledge_base/\n")

    # 3. バッチ ZIP 作成
    print(f"バッチ ZIP 作成中 ({BATCH_SIZE} ファイル/バッチ)...")
    batch_count = create_batch_zips(file_paths)
    print(f"  -> {batch_count} バッチ生成完了: dify/batches/\n")

    # 4. 全件一括 ZIP 作成
    print("全件一括 ZIP 作成中...")
    create_all_zip(file_paths)
    size_mb = os.path.getsize(ALL_ZIP_PATH) / (1024 * 1024)
    print(f"  -> knowledge_base_all.zip ({size_mb:.2f} MB)\n")

    # サマリー
    print("=== 完了 ===")
    print(f"テキストファイル: {len(file_paths)} 件")
    print(f"バッチ ZIP:       {batch_count} 個 (各 {BATCH_SIZE} ファイル)")
    print(f"一括 ZIP:         1 個")
    print(f"\n出力先: {os.path.join(PROJECT_DIR, 'dify')}")


if __name__ == "__main__":
    main()
