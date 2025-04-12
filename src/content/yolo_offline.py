from ultralytics import YOLO
import cv2
import numpy as np


model = YOLO(
    "/home/insia/Documents/Projects/target_detector/trarget_detector/train4/weights/best.pt"
)


cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

while True:
    ret, frame = cap.read()
    results = model(frame, vid_stride=25, verbose=False, conf=0.95)
    cv2.imshow("Frame", results[0].plot())
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
