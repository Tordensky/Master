import numpy as np
import cv2

cap = cv2.VideoCapture("TestImages/Video.avi")


while True:
    # Capture fram by frame
    ret, frame = cap.read()

    # operations on the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #gray = cv2.medianBlur(gray, 5)
    ret, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    circles = cv2.HoughCircles(thresh, cv2.cv.CV_HOUGH_GRADIENT, 1, 20, 50,
                               param1=50, param2=35, minRadius=0, maxRadius=40)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(thresh,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            #cv2.circle(gray,(i[0],i[1]),2,(0,0,255),3)



    # Display the resulting image
    cv2.imshow("frame", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
