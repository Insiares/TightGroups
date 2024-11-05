from ultralytics import YOLO
import numpy as np
import cv2
import matplotlib.pyplot as plt

# model = YOLO("/home/insia/Documents/Projects/TightGroups/runs/detect/train/weights/best.pt")
model = YOLO("yolo11n.pt")
input_image = "/home/insia/Documents/Projects/TightGroups/Models/YOLO/synth_dataset/val/target_98.jpg"
#results = model(input_image)
results = model.predict(source=input_image, save = True)

# Load the original image
image = cv2.imread(input_image)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Draw predictions on the image
for box in results[0].boxes:
    # Extract box coordinates
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    confidence = box.conf[0]
    label = results[0].names[int(box.cls[0])]  # Get class name from model's names list
    
    # Draw the bounding box and label
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    label_text = f"{label} {confidence:.2f}"
    cv2.putText(image, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Display the image with matplotlib
plt.imshow(image)
plt.axis("off")
plt.show()
'''
impact_coords = [(box.xyxy[0].item(), box.xyxy[1].item()) for box in results.pred[0]]



def calculate_group_size(impact_coords):
    max_distance = 0
    for i in range(len(impact_coords)):
        for j in range(i + 1, len(impact_coords)):
            dist = np.sqrt((impact_coords[i][0] - impact_coords[j][0])**2 + 
                           (impact_coords[i][1] - impact_coords[j][1])**2)
            max_distance = max(max_distance, dist)
    return max_distance

group_size = calculate_group_size(impact_coords)
print(f"Group size: {group_size}")'''
