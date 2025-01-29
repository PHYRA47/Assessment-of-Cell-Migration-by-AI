from ultralytics import YOLO

# Load pre-trained yolov11 model
model = YOLO('best.pt')

# Run inference on the source
results = model(source=1, show=True, conf=0.4, save=True) # source can be a file, directory, or webcam (0 for webcam)