import cv2
import numpy as np
from PIL import Image
import os
import glob
import csv  # Import the csv module

# Function to process each TIFF file and generate processed video
def process_tif_video(tif_file_path, converted_folder_path, processed_folder_path):
    fps = 30  # Frames per second for the output video

    # --- PART 1: Convert Multi-Frame TIFF to Video ---
    tif = Image.open(tif_file_path)
    width, height = tif.size

    # Create a VideoWriter object for the converted video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_video_path = os.path.join(converted_folder_path, f"{os.path.splitext(os.path.basename(tif_file_path))[0]}_converted.mp4")
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    frame_idx = 0
    try:
        while True:
            # Convert 16-bit to 8-bit by normalizing pixel values
            frame = np.array(tif, dtype=np.float32)
            frame = ((frame - frame.min()) / (frame.max() - frame.min()) * 255).astype(np.uint8)

            # Convert grayscale to BGR for video encoding
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            # Write the frame to the video
            video_writer.write(frame_bgr)

            # Move to the next frame
            frame_idx += 1
            tif.seek(frame_idx)
    except EOFError:
        # End of TIF file
        pass

    # Release the VideoWriter for the converted video
    video_writer.release()
    # print(f"Converted video saved to {output_video_path}")

    # --- PART 2: Calculate Global Brightness for This Video ---
    cap = cv2.VideoCapture(output_video_path)

    if not cap.isOpened():
        # print(f"Error: Could not open video file {output_video_path}")
        return None  # Return None if the video cannot be opened

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Initialize variables to compute global brightness
    brightness_sum = 0
    frame_count = 0

    # Calculate the global average brightness of the video
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        # Convert to grayscale to calculate brightness
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness_sum += np.mean(gray)
        frame_count += 1

    cap.release()

    # Check if there were any frames in the video
    if frame_count == 0:
        # print("Error: No frames found in the video. Cannot compute global brightness.")
        return None  # Return None if no frames are found

    global_brightness = brightness_sum / frame_count
    # print(f"Global average brightness of the video: {global_brightness}")

    # Function to adjust frame illumination to match global brightness
    def match_global_brightness(frame, global_brightness):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        current_brightness = np.mean(gray)

        # Calculate scaling factor
        brightness_scale = global_brightness / current_brightness if current_brightness > 0 else 1.0

        # Scale the frame
        frame_adjusted = cv2.convertScaleAbs(frame, alpha=brightness_scale, beta=0)
        return frame_adjusted

    # Reopen the output video from Part 1 for processing and save the new output
    cap = cv2.VideoCapture(output_video_path)

    final_output_video_path = os.path.join(processed_folder_path, f"{os.path.splitext(os.path.basename(tif_file_path))[0]}_processed.mp4")
    out = cv2.VideoWriter(final_output_video_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        # Adjust illumination to match global brightness
        frame_processed = match_global_brightness(frame, global_brightness)

        # Write to the output video
        out.write(frame_processed)

    # Release resources
    cap.release()
    out.release()
    print(f"Processed video saved to {final_output_video_path}")

    # Return the global brightness value for logging
    return global_brightness


# --- MAIN SCRIPT TO PROCESS ALL TIFF FILES IN A FOLDER ---
root_directory = r"D:\Desktop\pretreatment-example"  # Path to the folder containing TIFF files

# Initialize counters
total_tiff_files = 0

# Create a CSV file to log the results
csv_file_path = os.path.join(root_directory, "tiff_processing_results.csv")
with open(csv_file_path, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write the header row
    csv_writer.writerow(["Path", "Name", "Global Brightness"])

    # Traverse through the root directory and its subfolders
    for root, dirs, files in os.walk(root_directory):
        for dir_name in dirs:
            if dir_name == "Videos - Originales":
                videos_original_path = os.path.join(root, dir_name)
                videos_pretreated_path = os.path.join(root, "Videos - Pretreated")
                
                # Create the videos-pretreated folder if it doesn't exist
                os.makedirs(videos_pretreated_path, exist_ok=True)

                # Create subfolders for converted and processed videos
                converted_folder = os.path.join(videos_pretreated_path, "converted")
                processed_folder = os.path.join(videos_pretreated_path, "processed")
                os.makedirs(converted_folder, exist_ok=True)
                os.makedirs(processed_folder, exist_ok=True)
                
                # Find all TIFF files in the current directory
                tiff_files = glob.glob(os.path.join(videos_original_path, "*.tif"))
                num_tiff_files = len(tiff_files)
                total_tiff_files += num_tiff_files

                print(f"Found {num_tiff_files} TIFF files in {videos_original_path}")

                # Process each TIFF file
                for tif_filename in tiff_files:
                    # print(f"Processing TIFF file: {tif_filename}")
                    global_brightness = process_tif_video(tif_filename, converted_folder, processed_folder)
                    
                    # Log the TIFF file details and global brightness to the CSV file
                    if global_brightness is not None:
                        csv_writer.writerow([tif_filename, os.path.basename(tif_filename), global_brightness])

# Print the total number of TIFF files found and processed
print(f"Total number of TIFF files found and processed: {total_tiff_files}")
print(f"CSV file saved to: {csv_file_path}")