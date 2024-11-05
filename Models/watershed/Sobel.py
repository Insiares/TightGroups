import cv2 
import numpy as np 

def sobel(image):
    resized_image = cv2.resize(image, (640, 640))
    blur = cv2.GaussianBlur(resized_image, (3,3),0,0,cv2.BORDER_DEFAULT)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3)
    abs_x = cv2.convertScaleAbs(sobelx)
    abs_y = cv2.convertScaleAbs(sobely)
    sobel = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
    return sobel

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


image = cv2.imread('./images_reference/cible_edge_case_cropped.jpg', cv2.IMREAD_COLOR)

sobel_image = sobel(image)

show_image(sobel_image)

