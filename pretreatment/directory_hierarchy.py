import os
from collections import defaultdict

def print_directory_structure(root_directory):
    for root, dirs, files in os.walk(root_directory):
        level = root.replace(root_directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        
        extension_count = defaultdict(int)
        for f in files:
            ext = os.path.splitext(f)[1]
            extension_count[ext] += 1
        
        ext_info = ', '.join([f"{ext}: {count} files" for ext, count in extension_count.items()])
        print(f"{indent}├── {os.path.basename(root)}/ {ext_info}")

root_directory = r"E:"
print_directory_structure(root_directory)