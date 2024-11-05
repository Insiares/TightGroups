
import cv2
import numpy as np

# Load the image
image = cv2.imread('image_with_detected_circles.jpg', cv2.IMREAD_COLOR)

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply a binary threshold to highlight the bright white areas (impacts)
_, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

# Optional: Apply Gaussian Blur to reduce noise
blurred = cv2.GaussianBlur(thresh, (5, 5), 0)

# Detect circles using Hough Circle Transform, adjusted for smaller circles (impacts)
circles = cv2.HoughCircles(blurred, 
                           cv2.HOUGH_GRADIENT, dp=1.2, minDist=1,
                           param1=25, param2=10, minRadius=0, maxRadius=7)

# Draw the detected circles (impacts) on the original image
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    for circle in circles:
        x, y, r = circle
        print(r)
        # Draw the circle
        cv2.circle(image, (x, y), r, (0, 255, 0), 2)
        # Draw the center of the circle
        cv2.circle(image, (x, y), 1, (0, 0, 255), 3)

# Save the modified image with detected impacts
cv2.imwrite('./output/impacts_detected.jpg', image)

# Display result (optional)
cv2.imshow('Detected Impacts', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
