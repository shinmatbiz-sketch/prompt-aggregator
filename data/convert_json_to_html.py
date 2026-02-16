import json
import os
import html

input_file = r'D:\AG1\prompt-aggregator\data\prompts.json'
output_file = r'D:\AG1\prompt-aggregator\data\prompts.html'

def main():
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} items from JSON.")

        html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompts List</title>
    <style>
        body { font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }
        h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }
        .prompt-item { border: 1px solid #ddd; padding: 20px; margin-bottom: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .prompt-header { display: flex; align-items: baseline; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
        .prompt-id { background-color: #333; color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9em; }
        .prompt-title { font-size: 1.4em; font-weight: bold; margin: 0; color: #2c3e50; }
        .prompt-categories { margin-bottom: 15px; }
        .category-tag { background-color: #e0f0ff; color: #0066cc; padding: 4px 10px; border-radius: 15px; font-size: 0.85em; margin-right: 8px; display: inline-block; margin-bottom: 5px; }
        .prompt-body { white-space: pre-wrap; background-color: #f8f9fa; padding: 20px; border-radius: 4px; border-left: 4px solid #0066cc; font-family: Consolas, "Courier New", monospace; font-size: 0.95em; line-height: 1.7; }
    </style>
</head>
<body>
    <h1>Prompts List</h1>
"""

        for item in data:
            prompt_id = html.escape(item.get('id', 'N/A'))
            title = html.escape(item.get('title', 'No Title'))
            body = html.escape(item.get('body', ''))
            categories = item.get('categories', [])
            
            html_content += f"""
    <div class="prompt-item">
        <div class="prompt-header">
            <span class="prompt-id">#{prompt_id}</span>
            <h2 class="prompt-title">{title}</h2>
        </div>
        <div class="prompt-categories">
"""
            for cat in categories:
                html_content += f'<span class="category-tag">{html.escape(cat)}</span>'
            
            html_content += f"""
        </div>
        <div class="prompt-body">{body}</div>
    </div>
"""

        html_content += """
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Successfully converted to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
