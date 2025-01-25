import cv2
from PIL import Image
import os

# Path to the input video
video_path = 'Myoblast__12_MMStack_Pos19WT.ome_processed.mp4'

# Folder to save each frame as a TIFF image
output_folder = 'Session 2 - Face Identification + MySQL'
os.makedirs(output_folder, exist_ok=True)

# Open the video file
cap = cv2.VideoCapture(video_path)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Total frames in video: {frame_count}")

frame_number = 0
tiff_images = []

# Read each frame and save as TIFF
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale if needed
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Save each frame as a TIFF image
    tiff_path = os.path.join(output_folder, f"frame_{frame_number}.tiff")
    cv2.imwrite(tiff_path, gray_frame)
    tiff_images.append(Image.open(tiff_path))

    frame_number += 1

cap.release()

# Combine images into a single TIFF stack
output_stack_path = 'Myoblast__12_MMStack_Pos19WT.ome_processed.tiff'
tiff_images[0].save(output_stack_path, save_all=True, append_images=tiff_images[1:], compression="tiff_deflate")

print(f"TIFF stack saved at {output_stack_path}")
