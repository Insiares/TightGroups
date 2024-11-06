from ultralytics import YOLO
import numpy as np
import cv2
import matplotlib.pyplot as plt

model = YOLO("/home/insia/Documents/Projects/TightGroups/runs/detect/train16/weights/best.pt")
#model = YOLO("yolo11n.pt")

#test 
input_image = "/home/insia/Documents/Projects/TightGroups/Models/YOLO/synth_dataset/val/target_98.jpg"

#real image
#input_image = "/home/insia/Documents/Projects/TightGroups/Models/images_reference/cible_edge_case_cropped_resized.jpg"

#Inso image
#input_image = "/home/insia/Documents/Projects/TightGroups/Models/images_reference/cible_inso.jpg"

#pistol 10m 
#input_image = "/home/insia/Documents/Projects/TightGroups/Models/images_reference/10m_pistol.jpg"
#easy spread 
#input_image = "/home/insia/Documents/Projects/TightGroups/Models/test/image_with_circle_9.jpg"
# apply filter to the image 
image = cv2.imread(input_image)
image = cv2.resize(image, (640, 640))
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # Black and white image and apply gaussian blur
 #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# image = cv2.blur(gray, (5, 5))
# treated_image = "/home/insia/Documents/Projects/TightGroups/Models/images_reference/cible_edge_case_cropped_resized_treated.jpg"
# cv2.imwrite(treated_image, image)
#results = model(input_image)
results = model.predict(source=image, save = True, iou=0.7, augment=True, retina_masks=True, conf=0.45)

# Load the original image
# Draw predictions on the image
for box in results[0].boxes:
    # Extract box coordinates
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    confidence = box.conf[0]
    label = results[0].names[int(box.cls[0])]  # Get class name from model's names list
    
    # Draw the bounding box and label
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 1)
    label_text = f"{label} {confidence:.2f}"
    #cv2.putText(image, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Display the image with matplotlib
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()


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
