import json
import re

INPUT_FILE = r'D:\AG1\prompt-aggregator\data\prompts.json'
OUTPUT_FILE = r'D:\AG1\prompt-aggregator\data\prompts_optimized.json'

IDS_TO_REMOVE = ['979', '999']

REPLACEMENTS = {
    '市役所': '貴社',
    '庁内': '社内',
    '市民': '顧客',
    '市長': '経営層',
    '議員': '役員',
    '市議会': '経営会議',
    '行政': '事業',
    '市政': '経営',
    '公務員': '社員',
    '職員': '社員',
    '自治体': '企業',
}

def optimize_prompts():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    optimized_data = []
    
    for item in data:
        # 1. Remove specific IDs
        if item.get('id') in IDS_TO_REMOVE:
            continue

        # 2. Remove URL field
        if 'url' in item:
            del item['url']

        # 3. Optimize Title (Remove #ID_ prefix)
        title = item.get('title', '')
        # Pattern: # + digits + _ or space
        title = re.sub(r'^#\d+[_\s]', '', title)
        item['title'] = title.strip()

        # 4. Content Adaptation (Business Terms)
        # Apply replacements to Title and Body
        for old, new in REPLACEMENTS.items():
            if 'title' in item:
                item['title'] = item['title'].replace(old, new)
            if 'body' in item:
                item['body'] = item['body'].replace(old, new)

        # 5. Trim whitespace
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = value.strip()
            elif isinstance(value, list):
                item[key] = [v.strip() for v in value if isinstance(v, str)]

        optimized_data.append(item)

    # 6. Save as Minified JSON
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(optimized_data, f, ensure_ascii=False, indent=4)
        print(f"Optimization complete. Saved to {OUTPUT_FILE}")
        print(f"Original count: {len(data)}, Optimized count: {len(optimized_data)}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

if __name__ == "__main__":
    optimize_prompts()
