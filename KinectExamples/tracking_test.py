#!/usr/bin/env python
import freenect
import signal
import cv2
import numpy as np

keep_running = True

cam = cv2.VideoCapture(1)

def get_cv2_video():
    #return cv2.cvtColor(freenect.sync_get_video()[0], cv2.COLOR_RGB2BGR)
    ret, frame = cam.read()
    return frame


def object_tracker_update():
    bgr_img = get_cv2_video()
    hsv_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

    # THRESHOLD STEP
    hue_min = cv2.getTrackbarPos('HUE min', 'Controller')
    hue_max = cv2.getTrackbarPos('HUE max', 'Controller')

    sat_min = cv2.getTrackbarPos('Saturation min', 'Controller')
    sat_max = cv2.getTrackbarPos('Saturation max', 'Controller')

    value_min = cv2.getTrackbarPos('Value min', 'Controller')
    value_max = cv2.getTrackbarPos('Value max', 'Controller')

    hsv_lower_limit = np.array([hue_min, sat_min, value_min], np.uint8)
    hsv_upper_limit = np.array([hue_max, sat_max, value_max], np.uint8)

    mask = cv2.inRange(hsv_img, hsv_lower_limit, hsv_upper_limit)

    # NOISE REDUCTION STEP
    rem = cv2.getTrackbarPos("Rem", "Controller")
    add = cv2.getTrackbarPos("Add", "Controller")

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    mask = cv2.erode(mask, kernel, iterations=rem)
    mask = cv2.dilate(mask, kernel, iterations=add)

    mask = cv2.medianBlur(mask, 9)

    res = cv2.bitwise_and(bgr_img, bgr_img, mask=mask)

    cv2.imshow("mask", mask)
    cv2.imshow("Masked Result", res)
    cv2.imshow("maskBlur", mask)

    # TRACKING STEP
    cx, cy = None, None
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        try:
            m = cv2.moments(contour)
            cx, cy = int(m['m10'] / m['m00']), int(m['m01'] / m['m00'])
            cv2.circle(bgr_img, (cx, cy), 5, 255, -1)
            cv2.putText(bgr_img, "(x: %d, y: %d)" % (cx, cy), (cx + 20, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 255)
        except ZeroDivisionError:
            print "ERROR ZERO DIV"

    cv2.imshow("TRACKING", bgr_img)
    return cx, cy


def handler(signum, frame):
    """Sets up the kill handler, catches SIGINT"""
    global keep_running
    keep_running = False


def onChange(x):
    pass

cv2.namedWindow("Controller")
# HSV FILTER ADJUSTMENTS
cv2.createTrackbar("HUE min", "Controller", 100, 180, onChange)
cv2.createTrackbar("HUE max", "Controller", 120, 180, onChange)

cv2.createTrackbar("Saturation min", "Controller", 50, 255, onChange)
cv2.createTrackbar("Saturation max", "Controller", 255, 255, onChange)


cv2.createTrackbar("Value min", "Controller", 50, 255, onChange)
cv2.createTrackbar("Value max", "Controller", 255, 255, onChange)

# NOISE CONTROLS
cv2.createTrackbar("Rem", "Controller", 0, 15, onChange)
cv2.createTrackbar("Add", "Controller", 0, 15, onChange)


print('Press Ctrl-C in terminal to stop')
signal.signal(signal.SIGINT, handler)

while keep_running:
    cv2.waitKey(5)
    print object_tracker_update()

