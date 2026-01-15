import json
import os

file_path = 'sessions/neural_networks/cache.json'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'step_0_manim_code' in data:
        print("Removing step_0_manim_code from cache...")
        del data['step_0_manim_code']
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Cache updated.")
    else:
        print("step_0_manim_code not found in cache.")
else:
    print(f"File not found: {file_path}")
