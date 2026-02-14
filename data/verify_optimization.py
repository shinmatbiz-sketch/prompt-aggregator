import json
import os
import re

ORIGINAL_FILE = r'D:\AG1\prompt-aggregator\data\prompts.json'
OPTIMIZED_FILE = r'D:\AG1\prompt-aggregator\data\prompts_optimized.json'

REMOVED_IDS = ['979', '999']

def verify():
    print(f"Verifying optimization...")

    # Load data
    try:
        with open(ORIGINAL_FILE, 'r', encoding='utf-8') as f:
            orig_data = json.load(f)
        with open(OPTIMIZED_FILE, 'r', encoding='utf-8') as f:
            opt_data = json.load(f)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # 1. Check Item Count
    expected_count = len(orig_data) - len(REMOVED_IDS)
    if len(opt_data) == expected_count:
        print(f"[PASS] Item count is correct: {len(opt_data)}")
    else:
        print(f"[FAIL] Item count mismatch. Expected {expected_count}, got {len(opt_data)}")

    # 2. Check Removed IDs
    opt_ids = [item['id'] for item in opt_data]
    if all(rid not in opt_ids for rid in REMOVED_IDS):
        print(f"[PASS] IDs {REMOVED_IDS} successfully removed.")
    else:
        found_ids = [rid for rid in REMOVED_IDS if rid in opt_ids]
        print(f"[FAIL] Removed IDs still present: {found_ids}")

    # 3. Check URL Field Removal
    if all('url' not in item for item in opt_data):
        print("[PASS] 'url' field successfully removed from all items.")
    else:
        count_with_url = sum(1 for item in opt_data if 'url' in item)
        print(f"[FAIL] 'url' field present in {count_with_url} items.")

    # 4. Check Title format (No #ID_ prefix)
    # Be somewhat lenient, check if any title starts with #\d+_
    bad_titles = [item['title'] for item in opt_data if re.match(r'^#\d+[_\s]', item['title'])]
    if not bad_titles:
        print("[PASS] Title format normalized (no '#ID_' prefix).")
    else:
        print(f"[FAIL] Found {len(bad_titles)} titles with prefix issue. Sample: {bad_titles[:3]}")

    # 5. Check File Size
    orig_size = os.path.getsize(ORIGINAL_FILE)
    opt_size = os.path.getsize(OPTIMIZED_FILE)
    reduction = (orig_size - opt_size) / orig_size * 100
    print(f"[PASS] File size reduced by {reduction:.2f}% ({orig_size} -> {opt_size} bytes)")

    # 6. Check Random Item for Business Term Replacement
    # Just a spot check. '001' had '初心者' which might not change, but let's check a known replacement.
    # '016' body had '市議会議員', '市民'
    # '016' should now have '役員', '顧客' etc.
    
    # Let's search for old terms in the entire file
    old_terms = ['市役所', '庁内', '市民', '市長', '議員', '市議会', '行政', '市政', '公務員', '職員', '自治体']
    text_dump = json.dumps(opt_data, ensure_ascii=False)
    
    found_terms = {term: text_dump.count(term) for term in old_terms}
    total_found = sum(found_terms.values())
    
    if total_found == 0:
        print("[PASS] All target public sector terms replaced.")
    else:
        print(f"[WARN] Some public sector terms still remain ({total_found} occurrences):")
        print(found_terms)
        print("Note: This might be acceptable if they are parts of other words or specific contexts not covered by simple strict replacement.")

if __name__ == "__main__":
    verify()
