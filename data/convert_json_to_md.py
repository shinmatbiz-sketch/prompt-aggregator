import json
import os

input_file = r'D:\AG1\prompt-aggregator\data\prompts.json'
output_file = r'D:\AG1\prompt-aggregator\data\prompts.md'

def main():
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} items from JSON.")

        with open(output_file, 'w', encoding='utf-8') as f:
            for item in data:
                # ID and Title as Header 1
                prompt_id = item.get('id', 'N/A')
                title = item.get('title', 'No Title')
                f.write(f"# {prompt_id}: {title}\n\n")
                
                # Categories
                categories = item.get('categories', [])
                if categories:
                    # Join categories with comma
                    cats_str = ', '.join(categories)
                    f.write(f"**Categories:** {cats_str}\n\n")
                
                # Body
                body = item.get('body', '')
                # Ensure properly formatted body (maybe handle newlines if needed, but likely fine)
                f.write(body + "\n\n")
                
                # Separator
                f.write("---\n\n")

        print(f"Successfully converted to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
