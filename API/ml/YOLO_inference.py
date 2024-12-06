from ultralytics import YOLO
import cv2
from loguru import logger

@logger.catch
def predict_groupsize(image_path : str , model_path :str, output_path : str):

    model = YOLO(model_path)
 

    image = cv2.imread(image_path)
    image = cv2.resize(image, (640, 640))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model.predict(image)

    max_x = 0
    max_y = 0
    min_x = 640
    min_y = 640

    for box in results[0].boxes:

        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        confidence = box.conf[0]
        # label = results[0].names[int(box.cls[0])]  # Get class name from model's names list
        max_x = max(max_x, x2)
        max_y = max(max_y, y2)
        min_x = min(min_x, x1)
        min_y = min(min_y, y1)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 1)
        #label_text = f"{label} {confidence:.2f}"
        # cv2.putText(image, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    group_size = max(max_x - min_x, max_y - min_y)
    cv2.imwrite(output_path, image)

    return group_size
