from ultralytics import YOLO
import cv2
from loguru import logger
import os
import datetime
from API.ml.scanner.scan import DocScanner


@logger.catch
def predict_groupsize(image_path: str, model_path: str, output_path: str):
    model = YOLO(model_path)
    now = datetime.datetime.now()
    filename = f"detection_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    outputdir = "./API/ml/runs/"

    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    scanner = DocScanner()
    image = scanner.scan(image_path)

    # image = cv2.imread(image_path)
    image = cv2.resize(image, (640, 640))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    results = model.predict(
        image,
        save_txt=True,
        save_conf=True,
        retina_masks=True,
        iou=0.5,
        conf=0.5,
        project=outputdir,
        name=filename,
        exist_ok=True,
    )

    max_x = 0
    max_y = 0
    min_x = image.shape[1]
    min_y = image.shape[0]

    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        max_x = max(max_x, x2)
        max_y = max(max_y, y2)
        min_x = min(min_x, x1)
        min_y = min(min_y, y1)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 1)

    group_size_pixel = max(max_x - min_x, max_y - min_y)
    paper_size = 209.0
    image_size = image.shape[0]
    mm_per_pixel = paper_size / image_size

    group_size = group_size_pixel * mm_per_pixel
    image = cv2.resize(image, (640, 640))
    cv2.imwrite(output_path, image)

    return group_size
