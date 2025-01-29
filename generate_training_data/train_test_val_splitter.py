import os
import shutil
import random

# Define paths
root_dir = "dataset"  # Your root directory containing "images" and "labels" folders
images_dir = os.path.join(root_dir, "images")
labels_dir = os.path.join(root_dir, "labels")

# Define output directories
output_dirs = {
    "train": {
        "images": os.path.join(images_dir, "train"),
        "labels": os.path.join(labels_dir, "train"),
    },
    "val": {
        "images": os.path.join(images_dir, "val"),
        "labels": os.path.join(labels_dir, "val"),
    },
    "test": {
        "images": os.path.join(images_dir, "test"),
        "labels": os.path.join(labels_dir, "test"),
    },
}

# Create directories
for split, paths in output_dirs.items():
    os.makedirs(paths["images"], exist_ok=True)
    os.makedirs(paths["labels"], exist_ok=True)

# Split ratios
train_ratio = 0.8
val_ratio = 0.1
test_ratio = 0.1

# Get all image filenames (assuming .png format)
all_images = sorted([f for f in os.listdir(images_dir) if f.endswith(".png")])
random.shuffle(all_images)  # Shuffle for randomness

# Calculate split indices
total_images = len(all_images)
train_count = int(total_images * train_ratio)
val_count = int(total_images * val_ratio)

train_files = all_images[:train_count]
val_files = all_images[train_count:train_count + val_count]
test_files = all_images[train_count + val_count:]

# Function to move files
def move_files(file_list, split):
    for file_name in file_list:
        # Source paths
        img_src = os.path.join(images_dir, file_name)
        label_src = os.path.join(labels_dir, file_name.replace(".png", ".txt"))
        
        # Destination paths
        img_dst = output_dirs[split]["images"]
        label_dst = output_dirs[split]["labels"]
        
        # Move image and corresponding label
        shutil.move(img_src, os.path.join(img_dst, file_name))
        if os.path.exists(label_src):  # Ensure the label exists
            shutil.move(label_src, os.path.join(label_dst, file_name.replace(".png", ".txt")))

# Move files to splits
move_files(train_files, "train")
move_files(val_files, "val")
move_files(test_files, "test")

print(f"Dataset split complete! Total images: {total_images}")
print(f"Train: {len(train_files)}, Val: {len(val_files)}, Test: {len(test_files)}")