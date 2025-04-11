import streamlit as st 
import cv2
from ultralytics import YOLO

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)


# model = YOLO("yolov8n-seg.pt")
model = YOLO("/home/insia/Documents/Projects/target_detector/trarget_detector/train4/weights/best.pt")

while True:
    success, img = cap.read()
    if success:
        
        results = model(img)
        # cv2.imshow("Image", img)
        cv2.imshow("Image", results[0].plot())
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()
