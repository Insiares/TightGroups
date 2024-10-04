import cv2 as cv

max_lowThreshold = 100
window_name = 'Edge Map'
title_trackbar = 'Min Threshold:'
ratio = 3
kernel_size = 3
 
def CannyThreshold(val):
    low_threshold = val

    img_blur = cv.blur(src_gray, (3,3))
    detected_edges = cv.Canny(img_blur, low_threshold, low_threshold*ratio, kernel_size)
    mask = detected_edges != 0
    dst = src * (mask[:,:,None].astype(src.dtype))
    cv.imshow(window_name, dst)
 
 
src = cv.imread(cv.samples.findFile("images_reference/cible_edge_case_cropped.jpg"))
if src is None:
    print('Could not open or find the image: ')
    exit(0)
 
src = cv.resize(src, (640, 640))
src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
 
cv.namedWindow(window_name)
cv.createTrackbar(title_trackbar, window_name , 0, max_lowThreshold, CannyThreshold)
cv.createTrackbar('Ratio', window_name , 0, 100, CannyThreshold)
cv.createTrackbar('Kernel', window_name , 0, 100, CannyThreshold)
CannyThreshold(0)
## OPTIMAL : MIN THRESHOLD = 80 
cv.waitKey()
