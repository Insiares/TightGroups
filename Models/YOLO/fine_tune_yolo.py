from ultralytics import YOLO

#model = YOLO("yolov8n.pt")
model = YOLO("yolo11n.pt")
model.train(data="data.yaml", epochs=100, imgsz=640, device="0")
