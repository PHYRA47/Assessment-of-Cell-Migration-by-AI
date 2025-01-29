# Count the number of .npz and .mp4 files in a directory that
# contain the word "processed" in their filenames

import os

def count_files(root_directory, extensions):
    file_counts = {ext: 0 for ext in extensions}
    
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in extensions and "processed" in file:
                file_counts[ext] += 1
    
    return file_counts

# Define the root directory
root_directory = r"E:\WT - 01-06-10 Months"

# Define the file extensions to count
extensions = ['.npz', '.mp4']

# Count the files
file_counts = count_files(root_directory, extensions)

# Print the results
print(f"Number of .npz files: {file_counts['.npz']}")
print(f"Number of .mp4 files: {file_counts['.mp4']}")