"""
This script processes labeled video data.
It traverses a specified root directory to locate specially formatted videos and their associated
NPZ trajectory files. For each video, it extracts individual frames, saves them as PNG images,
and then generates corresponding label files based on the trajectory data. Gaussian noise is
applied to the bounding box dimensions, which are normalized relative to the frame size. A
progress bar (tqdm) reports frame-by-frame processing progress. Output folders for images and
labels are automatically created as needed, ensuring a structured and organized dataset for
subsequent tasks such as object detection model training.
"""

import os
import cv2
import numpy as np
from scipy.stats import norm
from tqdm import tqdm

# Constants
FRAME_WIDTH = 1392
FRAME_HEIGHT = 1040
IMAGE_FOLDER = "images"
LABEL_FOLDER = "labels"
FRAME_FORMAT = "frame_{:05d}_{}.png"
LABEL_FORMAT = "frame_{:05d}_{}.txt"

# Gaussian parameters for width and height
WIDTH_MEAN = 0.05 # 0.035786445504926115
WIDTH_VARIANCE = 0.0000001 # 0.00040012605749557714
HEIGHT_MEAN = 0.066
HEIGHT_VARIANCE = 0.0000001 # 0.00042180403181982863

def process_videos_and_labels(root_dir):
    print("========================================================")
    print("[START] process_videos_and_labels")
    print("========================================================")

    images_path = os.path.join(root_dir, "dataset", IMAGE_FOLDER)
    labels_path = os.path.join(root_dir, "dataset", LABEL_FOLDER)
    os.makedirs(images_path, exist_ok=True)
    os.makedirs(labels_path, exist_ok=True)
    print(f"-> Created output directories:\n   {images_path}\n   {labels_path}")

    global_frame_count = get_last_frame_number(images_path) + 1
    print(f"-> Starting global frame count at {global_frame_count}")

    for root, dirs, files in os.walk(root_dir):
        if os.path.basename(root) == "Tracks - Expert 01 - Sophie":
            npz_dir = os.path.join(root, "combined_trajectories")
            if not os.path.exists(npz_dir):
                print(f"-> Skipping {root}: 'combined_trajectories' folder not found.")
                continue

            parent_dir = os.path.dirname(root)
            videos_dir = os.path.join(parent_dir, "Videos - Pretreated", "processed")
            if not os.path.exists(videos_dir):
                print(f"-> Skipping {parent_dir}: 'processed' videos folder not found.")
                continue

            print("========================================================")
            print("[INFO] Processing Directory")
            print("--------------------------------------------------------")
            print(f"Videos Path: {videos_dir}")
            print(f"NPZ Path:    {npz_dir}")
            print("========================================================")

            for video_name in os.listdir(videos_dir):
                if video_name.endswith(".mp4"):
                    video_path = os.path.join(videos_dir, video_name)
                    npz_name = video_name.replace(".mp4", ".npz")
                    npz_path = os.path.join(npz_dir, npz_name)
                    if not os.path.exists(npz_path):
                        print(f"-> Warning: No corresponding .npz file for '{video_name}'")
                        continue
                    global_frame_count = process_video(video_path, npz_path, images_path, labels_path, global_frame_count)

def get_last_frame_number(images_path):
    """Find the last frame number from existing files"""
    last_frame = 0
    if os.path.exists(images_path):
        for filename in os.listdir(images_path):
            if filename.startswith("frame_") and filename.endswith(".png"):
                try:
                    frame_num = int(filename.split("_")[1])
                    last_frame = max(last_frame, frame_num)
                except (ValueError, IndexError):
                    continue
    return last_frame

def process_video(video_path, npz_path, images_path, labels_path, start_frame):
    print("--------------------------------------------------------")
    print(f"[START] process_video: {os.path.basename(video_path)}") 

    cap = cv2.VideoCapture(video_path)
    video_basename = os.path.splitext(os.path.basename(video_path))[0]
    current_frame = start_frame
    frame_index = 0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=total_frames, desc=f"Processing {video_basename}", unit="frame")

    while True:
        ret, frame = cap.read()
        if not ret:
            # print("-> End of video reached.")
            break

        frame_filename = FRAME_FORMAT.format(current_frame, video_basename)
        frame_filepath = os.path.join(images_path, frame_filename)
        cv2.imwrite(frame_filepath, frame)

        create_label_file(frame_index, current_frame, video_basename, npz_path, labels_path)

        frame_index += 1
        current_frame += 1
        pbar.update(1)

    pbar.close()
    cap.release()
    print(f"[END]   Processed frames {start_frame} to {current_frame - 1}")
    print("--------------------------------------------------------")
    return current_frame

def create_label_file(frame_index, current_frame, video_basename, npz_path, labels_path):
    npz_data = np.load(npz_path)
    trajectories = npz_data['trajectories']
    if frame_index >= trajectories.shape[1]:
        print(f"-> No data for frame {frame_index}, skipping label creation.")
        return

    frame_data = trajectories[:, frame_index, :]
    label_filename = LABEL_FORMAT.format(current_frame, video_basename)
    label_filepath = os.path.join(labels_path, label_filename)

    # print(f"-> Creating label file: {label_filepath.split(os.sep)[-1]}")
    with open(label_filepath, "w") as label_file:
        for coords in frame_data:
            x, y = coords
            x_norm = x / FRAME_WIDTH
            y_norm = y / FRAME_HEIGHT

            width = norm.rvs(loc=WIDTH_MEAN, scale=np.sqrt(WIDTH_VARIANCE))
            height = norm.rvs(loc=HEIGHT_MEAN, scale=np.sqrt(HEIGHT_VARIANCE))
            label_file.write(f"0 {x_norm} {y_norm} {width} {height}\n")

if __name__ == "__main__":
    root_directory = r"D:\Desktop\pretreatment-example"
    process_videos_and_labels(root_directory)