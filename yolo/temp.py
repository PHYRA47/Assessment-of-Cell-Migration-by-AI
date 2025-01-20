from ultralytics import YOLO

model = YOLO("yolov8s.pt")
result = model.predict(source="0", show=True)