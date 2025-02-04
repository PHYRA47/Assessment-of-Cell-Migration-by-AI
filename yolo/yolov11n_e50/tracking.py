from collections import defaultdict

# F:\WT - 01-06-10 Months\WT - 10 months\Manip02 - 2023-04-13 - 46Films\Videos - Pretreated\processed
# Myoblast__1_MMStack_Pos9-puit-haut-gauche.ome_processed

import cv2
import numpy as np

from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO("yolov11n_e50/train/weights/best.pt")

# Open the video file
video_path = r"F:\WT - 01-06-10 Months\WT - 10 months\Manip02 - 2023-04-13 - 46Films\Videos - Pretreated\processed\Myoblast__1_MMStack_Pos45-puit-haut-droit.ome_processed.mp4"
cap = cv2.VideoCapture(video_path)

# Store the track history
track_history = defaultdict(lambda: [])

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True)

        # Ensure results and results[0] are not None
        if results is not None and results[0] is not None and results[0].boxes is not None:
            # Get the boxes and track IDs
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Plot the tracks
            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))  # x, y center point
                if len(track) > 30:  # retain 90 tracks for 90 frames
                    track.pop(0)

                # Draw the tracking lines
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=4)

            # Display the annotated frame
            cv2.imshow("YOLO11 Tracking", annotated_frame)
        else:
            print("No detections in this frame.")
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break


# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()