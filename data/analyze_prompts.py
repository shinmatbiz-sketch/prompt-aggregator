import json
import re
from collections import Counter

file_path = r'D:\AG1\prompt-aggregator\data\prompts.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    exit(1)

print(f"Total items: {len(data)}")

# check for duplicate IDs
ids = [item.get('id') for item in data]
duplicate_ids = [item for item, count in Counter(ids).items() if count > 1]
if duplicate_ids:
    print(f"Duplicate IDs found: {duplicate_ids}")
else:
    print("No duplicate IDs found.")

# check title format
title_format_issue = []
for item in data:
    expected_prefix = f"#{item.get('id')}_"
    if not item.get('title', '').startswith(expected_prefix):
        title_format_issue.append(item.get('id'))

print(f"Items with non-standard title format: {len(title_format_issue)}")
if title_format_issue:
    print(f"Sample IDs: {title_format_issue[:5]}")

# analyze body structure
# Common headers in body seem to be [Header Name]
header_pattern = re.compile(r'^\[(.*?)\]', re.MULTILINE)
all_headers = Counter()

for item in data:
    body = item.get('body', '')
    headers = header_pattern.findall(body)
    all_headers.update(headers)

print("\nCommon Headers in Body:")
for header, count in all_headers.most_common(10):
    print(f"{header}: {count}")

# Check for potential duplicates in body
bodies = [item.get('body') for item in data]
duplicate_bodies = [item for item, count in Counter(bodies).items() if count > 1]
if duplicate_bodies:
    print(f"\nDuplicate bodies found: {len(duplicate_bodies)} unique bodies are repeated.")
else:
    print("\nNo duplicate bodies found.")

# Categories analysis
all_categories = Counter()
for item in data:
    for cat in item.get('categories', []):
        all_categories[cat] += 1

print(f"\nTotal unique categories: {len(all_categories)}")
print(f"Top 5 categories: {all_categories.most_common(5)}")
