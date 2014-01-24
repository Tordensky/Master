#!/usr/bin/env python
import freenect
import matplotlib.pyplot as mp
import time
import frame_convert
import signal
import cv2
import numpy as np

keep_running = True


def get_depth():
    return frame_convert.pretty_depth(freenect.sync_get_depth()[0])


def get_video():
    return freenect.sync_get_video()[0]


def getCv2Video():
    return freenect.sync_get_video()[0][:, :, ::-1]


def drawCV2Image():
    image = getCv2Video()



    # EXTRACT BLUE OBJECTS
    hsvImg = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsvImg, lower_blue, upper_blue)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    #mask = cv2.medianBlur(mask, 5)

    res = cv2.bitwise_and(image, image, mask=mask)
    cv2.imshow("hsv", hsvImg)
    cv2.imshow("mask", mask)
    cv2.imshow("res", res)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)



    cv2.imshow("maskBlur", mask)
    res = cv2.medianBlur(res, 5)

    #ret, thresh = cv2.threshold(gray, 80, 150, cv2.THRESH_BINARY_INV)


    circles = cv2.HoughCircles(mask, cv2.cv.CV_HOUGH_GRADIENT, 1, 10, 15,
                               param1=50, param2=10, minRadius=10, maxRadius=20)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(gray, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(gray, (i[0], i[1]), 2, (0, 0, 255), 3)

            cv2.putText(gray, "(x: %d, y: %d)" % (i[0], i[1]), (i[0] - 25, i[1] + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                        255)
    else:
        print "NO CIRCLES"

    cv2.imshow("TRACKING", cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))


def handler(signum, frame):
    """Sets up the kill handler, catches SIGINT"""
    global keep_running
    keep_running = False


mp.ion()
mp.gray()
mp.figure(1)
image_depth = mp.imshow(get_depth(), interpolation='nearest', animated=True)
mp.figure(2)
image_rgb = mp.imshow(get_video(), interpolation='nearest', animated=True)
drawCV2Image()
print('Press Ctrl-C in terminal to stop')
signal.signal(signal.SIGINT, handler)

while keep_running:
    mp.figure(1)
    image_depth.set_data(get_depth())
    mp.figure(2)
    image_rgb.set_data(get_video())
    mp.draw()
    mp.waitforbuttonpress(0.01)
    cv2.waitKey(5)
    drawCV2Image()

