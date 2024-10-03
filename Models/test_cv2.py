
import cv2
import numpy as np
from PIL import Image

# Load image
image = cv2.imread('./image_with_circle_9.jpg', cv2.IMREAD_COLOR)

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply GaussianBlur to reduce noise and improve detection
gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)

# Detect circles using Hough Circle Transform
circles = cv2.HoughCircles(gray_blurred, 
                           cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                           param1=100, param2=30, minRadius=20, maxRadius=80)

# Convert coordinates and radii of detected circles to integers
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")

# Find the center circle (assuming it's the largest circle)
center_circle = max(circles, key=lambda c: c[2])  # c[2] is the radius
center_x, center_y, center_r = center_circle

# Draw the detected circles and the center circle (for visualization)
for circle in circles:
    x, y, r = circle
    # Circle outline
    cv2.circle(image, (x, y), r, (0, 255, 0), 2)
    # Circle center
    cv2.circle(image, (x, y), 1, (0, 100, 255), 3)

# Save the image with circles drawn (for reference)
cv2.imwrite('image_with_detected_circles.jpg', image)

# Now calculate the relative positions of all circles to the center
relative_positions = []

for circle in circles:
    x, y, r = circle
    # Skip the center circle itself
    if (x, y) == (center_x, center_y):
        continue

    # Calculate the distance from center
    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    
    # Calculate the angle from center (in degrees)
    angle = np.degrees(np.arctan2(y - center_y, x - center_x))
    
    # Store relative position (distance, angle)
    relative_positions.append((distance, angle))

# Print out the relative positions
for idx, (dist, angle) in enumerate(relative_positions):
    print(f"Circle {idx+1}: Distance = {dist:.2f}, Angle = {angle:.2f} degrees")
