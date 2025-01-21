"""
This script processes .xls files located in the "Tracks - Expert 01 - Sophie" folders within a given root directory.
It extracts X and Y trajectory data from the .xls files, groups them by their "Pos+number" identifier, and ensures
that each trajectory has at least 220 rows. Trajectories with fewer than 220 rows are excluded. The script then
stacks the valid trajectories into a NumPy array and saves it as an .npz file. The .npz file is named after the
corresponding .mp4 file in the "Videos - Pretreated\processed" folder, which is located in the same parent directory
as the "Tracks - Expert 01 - Sophie" folder.

Functions:
1. extract_pos_number(filename): Extracts the "Pos+number" identifier from a filename using regex.
2. process_xls_file(file_path): Reads an .xls file as a tab-separated CSV and extracts X and Y columns as a NumPy array.
3. Main script: Traverses the directory structure, processes .xls files, and saves the results as .npz files.
"""

import os
import re
import pandas as pd
import numpy as np

# Define root directory
root_directory = r"D:\Desktop\pretreatment-example"

# Function to extract Pos+number from filenames
def extract_pos_number(filename):
    match = re.search(r"Pos(\d+)", filename)
    if match:
        return match.group(1)  # Returns the number after "Pos"
    return None

# Function to process .xls files and extract X, Y data using pd.read_csv
def process_xls_file(file_path):
    try:
        # Read the file as a CSV with tab separator
        df = pd.read_csv(file_path, sep='\t', encoding='ISO-8859-1')  
        if "X" in df.columns and "Y" in df.columns:
            return df[["X", "Y"]].values  # Return X, Y as a NumPy array
        else:
            print(f"Columns 'X' and 'Y' not found in {file_path}")
            return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# Traverse the directory structure
for root, dirs, files in os.walk(root_directory):
    # Check if the current folder is "Tracks - Expert 01 - Sophie"
    if os.path.basename(root) == "Tracks - Expert 01 - Sophie":
        print(f"Processing 'Tracks - Expert 01 - Sophie' folder at: {root}")

        # Create a folder to save .npz files
        output_folder = os.path.join(root, "combined_trajectories")
        os.makedirs(output_folder, exist_ok=True)

        # Group .xls files by Pos+number
        pos_files = {}  # Dictionary to group files by Pos+number
        for file in files:
            if file.endswith(".xls"):
                pos_number = extract_pos_number(file)
                if pos_number:
                    if pos_number not in pos_files:
                        pos_files[pos_number] = []
                    pos_files[pos_number].append(os.path.join(root, file))

        # Process each group of .xls files with the same Pos+number
        for pos_number, file_paths in pos_files.items():
            print(f"Processing Pos{pos_number} with {len(file_paths)} files")

            # Extract X, Y data from all files with the same Pos+number
            trajectories = []
            valid_files = []  # Track files that meet the 220-row requirement
            for file_path in file_paths:
                data = process_xls_file(file_path)
                if data is not None:
                    if len(data) >= 220:
                        print(f"Data shape from {os.path.basename(file_path)}: {data.shape}")
                        trajectories.append(data[:220])  # Truncate to 220 frames
                        valid_files.append(file_path)
                    else:
                        print(f"Skipping {os.path.basename(file_path)}: Only {len(data)} rows (less than 220)")

            # Skip if no valid data was found
            if not trajectories:
                print(f"No valid data found for Pos{pos_number} in {root}")
                continue

            # Debugging: Print shapes after truncation
            print(f"Shapes after truncation for Pos{pos_number}:")
            for i, traj in enumerate(trajectories):
                print(f"Trajectory {i + 1}: {traj.shape}")

            # Stack trajectories into a single NumPy array of shape (num_files, 2, 220)
            try:
                trajectories_array = np.stack(trajectories, axis=0)
                print(f"Stacked array shape for Pos{pos_number}: {trajectories_array.shape}")
            except ValueError as e:
                print(f"Error stacking trajectories for Pos{pos_number}: {e}")
                continue

            # Find the corresponding .mp4 file in the Videos - Pretreated\processed folder
            # Locate the "Videos - Pretreated" folder relative to the current "Tracks - Expert 01 - Sophie" folder
            videos_folder = os.path.join(os.path.dirname(root), "Videos - Pretreated", "processed")
            if not os.path.exists(videos_folder):
                print(f"Videos folder not found for {root}")
                continue

            mp4_files = [f for f in os.listdir(videos_folder) if f.endswith(".mp4") and f"Pos{pos_number}" in f]
            if not mp4_files:
                print(f"No matching .mp4 file found for Pos{pos_number} in {videos_folder}")
                continue

            # Use the first matching .mp4 file's name (without extension) for the .npz file
            mp4_name = os.path.splitext(mp4_files[0])[0]
            npz_file_path = os.path.join(output_folder, f"{mp4_name}.npz")

            # Save the trajectories array as an .npz file
            np.savez(npz_file_path, trajectories=trajectories_array)
            print(f"Saved {npz_file_path} with shape {trajectories_array.shape}")

print("Processing complete.")