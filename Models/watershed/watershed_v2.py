
import cv2
import numpy as np

def deconvolution(image):
    # Applying Wiener deconvolution to sharpen the image
    # First, convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Define a kernel for deconvolution; this is a Gaussian kernel in this example
    kernel = np.ones((3, 3), np.float32) / 9
    deconvolved = cv2.filter2D(gray, -1, kernel)
    
    return deconvolved

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Load and resize the image
image = cv2.imread('./images_reference/cible_edge_case_cropped.jpg', cv2.IMREAD_COLOR)

# Resize to a standard size if needed
image = cv2.resize(image, (640, 640))
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image = cv2.GaussianBlur(image, (3,3), 0, 0, cv2.BORDER_DEFAULT)
# Apply deconvolution

# Convert to grayscale
print(type(image))
print(image.shape)
# Use adaptive thresholding

# Canny edge detection
edges = cv2.Canny(image,80,80*3,3)
show_image(edges)
# Morphological opening to clean up edges
kernel = np.ones((3, 3), np.uint8)
opening = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel, iterations=2)
show_image(opening)
# Background area (dilation)
sure_bg = cv2.dilate(edges, kernel, iterations=3)
show_image(sure_bg)
# Finding sure foreground area using distance transform
dist_transform = cv2.distanceTransform(edges, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
show_image(sure_fg)
# Finding unknown region (areas we aren't sure if it's background or foreground)
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)
show_image(unknown)
# Marker labelling for watershed
_, markers = cv2.connectedComponents(sure_fg)

# Add one to all markers to make sure background is not zero
markers = markers + 1

# Mark the unknown regions as zero
markers[unknown == 255] = 0
# Apply the watershed algorithm
print(type(markers))
print(markers.shape)
markers = cv2.watershed(image, markers)

# Mark boundaries with red
image[markers == -1] = [0, 0, 255]

# Draw circles around detected regions
for marker_value in np.unique(markers):
    if marker_value > 1:  # Ignore background and unknown regions
        mask = (markers == marker_value).astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if radius > 2:  # Filter out very small regions
                cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 0), 2)

# Save the result
cv2.imwrite('./output/segmented_impacts_deconvolved.jpg', image)

# Display result (optional)
cv2.imshow('Segmented Impacts with Deconvolution', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
