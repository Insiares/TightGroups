
import cv2
import numpy as np
from matplotlib import pyplot as plt

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def resize_image(image, target_size=(800,800)):
    height, width = image.shape[:2]
    scale_width = target_size[0] / width
    scale_height = target_size[1] / height

    scale = min(scale_width, scale_height)
    new_size = (int(width * scale), int(height * scale))

    resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    return resized_image


# Load the image
image = cv2.imread('./images_reference/cible_edge_case_cropped.jpg', cv2.IMREAD_COLOR)
image = resize_image(image, target_size=(800,800))
cv2.imwrite('./images_reference/cible_edge_case_cropped_resized.jpg', image)
# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Adaptive threshold 
adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 501, 0.1)
show_image(adaptive_thresh)
# Noise removal (optional)
kernel = np.ones((3,3), np.uint8)
opening = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel, iterations=2)
show_image(opening)
# Background area (dilation)
sure_bg = cv2.dilate(opening, kernel, iterations=3)
show_image(sure_bg)
# Finding sure foreground area
dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
show_image(sure_fg)
# Finding unknown region (areas we aren't sure if it's background or foreground)
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)
show_image(unknown)
# Marker labelling (for the watershed)
_, markers = cv2.connectedComponents(sure_fg)

# Add one to all labels so that sure background is not 0
markers = markers + 1

# Mark the unknown regions as 0
markers[unknown == 255] = 0

# Apply the watershed algorithm
markers = cv2.watershed(gray, markers)

# Mark boundaries with red where the watershed algorithm identified the separation
image[markers == -1] = [0, 0, 255]

# Optional: draw circles around detected impacts (based on marker regions)
for marker_value in np.unique(markers):
    if marker_value > 1:  # Ignore the background and unknown markers
        mask = (markers == marker_value).astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if radius > 5 and radius < 20:  # Filter out very small regions
                cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 0), 2)

# Save and display the result
cv2.imwrite('./output/segmented_impacts.jpg', image)
cv2.imshow('Segmented Overlapping Impacts', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
