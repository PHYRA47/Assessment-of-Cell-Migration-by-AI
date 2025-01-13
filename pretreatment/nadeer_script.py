import cv2
import numpy as np
from PIL import Image
import os

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
    print(f"Converted video saved to {output_video_path}")

    # --- PART 2: Calculate Global Brightness for This Video ---
    cap = cv2.VideoCapture(output_video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video file {output_video_path}")
        return

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
        print("Error: No frames found in the video. Cannot compute global brightness.")
        return

    global_brightness = brightness_sum / frame_count
    print(f"Global average brightness of the video: {global_brightness}")

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


# --- MAIN SCRIPT TO PROCESS ALL TIFF FILES IN A FOLDER ---
folder_path = r"C:\Users\nadee\Documents\UPEC_project\Tiff_videos"  # Path to the folder containing TIFF files
converted_folder_path = r"C:\Users\nadee\Documents\UPEC_project\converted"  # Folder for converted videos
processed_folder_path = r"C:\Users\nadee\Documents\UPEC_project\processed"  # Folder for processed videos

# Create output folders if they don't exist
os.makedirs(converted_folder_path, exist_ok=True)
os.makedirs(processed_folder_path, exist_ok=True)

# Loop through all TIFF files in the folder
for tif_filename in os.listdir(folder_path):
    if tif_filename.endswith(".tif"):
        tif_file_path = os.path.join(folder_path, tif_filename)

        # Process the TIFF file and save the videos in separate folders
        process_tif_video(tif_file_path, converted_folder_path, processed_folder_path)