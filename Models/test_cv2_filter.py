
import cv2
import numpy as np
from collections import Counter

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def most_frequent_color(image):
    pixels = np.reshape(image, (-1, 3))
    
    pixel_list = [tuple(p) for p in pixels]
    
    dominant_color = Counter(pixel_list).most_common(1)[0][0]     
    return np.array(dominant_color)

def resize_image(image, target_size=(800,800)):
    height, width = image.shape[:2]
    scale_width = target_size[0] / width
    scale_height = target_size[1] / height

    scale = min(scale_width, scale_height)
    new_size = (int(width * scale), int(height * scale))

    resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    return resized_image

image = cv2.imread('./image_with_detected_circles.jpg', cv2.IMREAD_COLOR)
#image = cv2.imread('./images_reference/cible_edge_case_cropped.jpg', cv2.IMREAD_COLOR)

image = resize_image(image, target_size=(800,800))
show_image(image)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
show_image(gray)
# binary threshold to highlight bright areas , should test other values
#_, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
blurred = cv2.GaussianBlur(gray, (9, 9), 2)
show_image(blurred)
circles = cv2.HoughCircles(blurred, 
                           cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                           param1=50, param2=15, minRadius=5, maxRadius=20)

dominant_color = most_frequent_color(image)
print(f"Dominant color: {dominant_color}")

if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    for circle in circles:
        x, y, r = circle
        
        reduced_r = int(r/4)
        circle_region = image[y - reduced_r:y + reduced_r, x - reduced_r:x + reduced_r]          
        avg_color = np.mean(circle_region, axis=(0, 1)).astype(int)
        print(f"Average color: {avg_color}")

        if not np.allclose(avg_color, dominant_color, atol=40):  
            cv2.circle(image, (x, y), r, (0, 255, 0), 2)              
            cv2.circle(image, (x, y), 1, (0, 0, 255), 3)  

cv2.imwrite('./output/filtered_circles_by_color.jpg', image)

cv2.imshow('Filtered Detected Impacts', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
