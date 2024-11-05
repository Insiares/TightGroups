
import cv2
import numpy as np

def resize_image(image, target_size=(800,800)):
    height, width = image.shape[:2]
    scale_width = target_size[0] / width
    scale_height = target_size[1] / height

    scale = min(scale_width, scale_height)
    new_size = (int(width * scale), int(height * scale))

    resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    return resized_image

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# Load the image
image = cv2.imread('./images_reference/cible_edge_case_cropped.jpg', cv2.IMREAD_GRAYSCALE)

image = resize_image(image, target_size=(800,800))
# Preprocess the image (Gaussian blur to reduce noise, thresholding for contours)
blurred = cv2.GaussianBlur(image, (5, 5), 0)
_, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
show_image(thresh)
# Detect contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# Known size of a single bullet impact
single_bullet_area = np.pi * (11/2) ** 2

# Detect and process each contour
for contour in contours:
    area = cv2.contourArea(contour)
    
    # Estimate the number of impacts
    num_impacts = int(round(area / single_bullet_area))
    
    # Draw the contour and annotate the number of impacts
    cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
    x, y, w, h = cv2.boundingRect(contour)
    cv2.putText(image, f'{num_impacts}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

# Show the result
cv2.imshow('Detected Impacts', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
