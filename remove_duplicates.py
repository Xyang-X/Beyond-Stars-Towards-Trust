#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove duplicate comments based on (user_id, gmap_id, text) combination.
"""

import json
import sys
from collections import OrderedDict

def detect_file_format(file_path):

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if not first_line:
                return 'json'
            

            try:
                json.loads(first_line)
                f.seek(0)
                lines = f.readlines()
                if len(lines) > 1:
                    return 'jsonl'
                else:
                    # 单行JSON
                    return 'json'
            except json.JSONDecodeError:
                return 'jsonl'
    except Exception:
        return 'json'

def remove_duplicates(input_file, output_file):

    file_format = detect_file_format(input_file)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            if file_format == 'jsonl':
                data = []
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            print(e)
                            continue
            else:
                data = json.load(f)
    except FileNotFoundError:
        print(f" {input_file} does nnot exist.")
        return
    except Exception as e:
        print(f"Fail to read: {e}")
        return
    
    seen_combinations = OrderedDict()
    unique_data = []
    duplicate_count = 0
    
    for item in data:
        user_id = item.get('user_id', '')
        gmap_id = item.get('gmap_id', '')
        text = item.get('text', '')
        

        combination = (user_id, gmap_id, text)
        
        if combination not in seen_combinations:

            seen_combinations[combination] = True
            unique_data.append(item)
        else:
            duplicate_count += 1

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if file_format == 'jsonl' or output_file.endswith('.jsonl'):
                for item in unique_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            else:
                json.dump(unique_data, f, ensure_ascii=False, indent=2)
              
    except Exception as e:
        print(e)
        return
    

def main():

    if len(sys.argv) != 3:
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    remove_duplicates(input_file, output_file)

if __name__ == "__main__":
    main()
