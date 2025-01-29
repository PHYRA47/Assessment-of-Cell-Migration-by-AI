# Description: Visualize YOLO labels on images
# Usage: python visualizer.py <image_path> <label_path> [--width <frame_width>] [--height <frame_height>]
# Example: python visualizer.py data/image.png data/label.txt --width 1392 --height 1040
# Example: visualizer.py AssessmentOfCellMigration.v1i.yolov11\train\images\frame_006_jpg.rf.ea024d01adb1d0bdbae987c2138b303b.jpg AssessmentOfCellMigration.v1i.yolov11\train\labels\frame_006_jpg.rf.ea024d01adb1d0bdbae987c2138b303b.txt --width 1392 --height 1040
import cv2
import numpy as np
import os
import argparse

def read_yolo_labels(label_path, img_width, img_height):
    """
    Read YOLO format labels and convert to pixel coordinates
    Returns: List of [class_id, x, y, w, h] in pixel coordinates
    """
    boxes = []
    with open(label_path, 'r') as f:
        for line in f.readlines():
            data = line.strip().split()
            # YOLO format: class_id, x_center, y_center, width, height (normalized)
            class_id = int(data[0])
            x_center = float(data[1]) * img_width
            y_center = float(data[2]) * img_height
            width = float(data[3]) * img_width
            height = float(data[4]) * img_height
            
            # Convert to pixel coordinates
            x1 = int(x_center - width/2)
            y1 = int(y_center - height/2)
            x2 = int(x_center + width/2)
            y2 = int(y_center + height/2)
            
            boxes.append([class_id, x_center, y_center, width, height, [x1, y1, x2, y2]])
    return boxes

def draw_boxes(image, boxes):
    """Draw boxes and centers on the image"""
    img_draw = image.copy()
    
    for box in boxes:
        # Extract coordinates
        class_id, x_center, y_center, width, height, coords = box
        x1, y1, x2, y2 = coords
        
        # Draw rectangle
        cv2.rectangle(img_draw, (x1, y1), (x2, y2), (80, 255, 224, 200), 2)
        
        # Draw center point
        center = (int(x_center), int(y_center))
        cv2.circle(img_draw, center, 3, (0, 0, 255), -1)
        
        # Add label with dimensions
        label = f"ID:{class_id} {width:.1f}x{height:.1f}"
        cv2.putText(img_draw, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return img_draw

def visualize_labels(image_path, label_path, frame_width=1392, frame_height=1040):
    """Main function to visualize labels on image"""
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return
    
    # Read and convert labels
    if not os.path.exists(label_path):
        print(f"Error: Label file not found {label_path}")
        return
    
    boxes = read_yolo_labels(label_path, frame_width, frame_height)
    
    # Draw boxes on image
    img_with_boxes = draw_boxes(image, boxes)
    
    # Create window and display
    window_name = 'YOLO Label Visualization'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 800)
    
    while True:
        cv2.imshow(window_name, img_with_boxes)
        
        # Wait for key press
        key = cv2.waitKey(1) & 0xFF
        
        # 'q' or 'ESC' to quit
        if key == ord('q') or key == 27:
            break
        # 's' to save
        elif key == ord('s'):
            output_path = image_path.replace('.png', '_labeled.png')
            cv2.imwrite(output_path, img_with_boxes)
            print(f"Saved labeled image to: {output_path}")
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize YOLO labels on images')
    parser.add_argument('image_path', help='Path to the image file')
    parser.add_argument('label_path', help='Path to the corresponding label file')
    parser.add_argument('--width', type=int, default=1392, help='Frame width (default: 1392)')
    parser.add_argument('--height', type=int, default=1040, help='Frame height (default: 1040)')
    
    args = parser.parse_args()
    
    visualize_labels(args.image_path, args.label_path, args.width, args.height)