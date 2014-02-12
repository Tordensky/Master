import cv2
import freenect
import numpy as np
from traceable import Traceable


class TrackerBase(object):
    TRACK_TYPE_STROBE = 0
    TRACK_TYPE_COLOR = 1
    TRACK_TYPE_DEPTH = 2

    def __init__(self):
        self.track_type = None

        # HSV FILTER
        self._hue_min = 0
        self._hue_max = 179
        self._sat_min = 0
        self._sat_max = 255
        self._val_min = 0
        self._val_max = 255

    def track_object(self, traceable_obj):
        if traceable_obj is None:
            traceable_obj = Traceable()

        return traceable_obj

    def _create_hsv_mask(self, hsv_img):
        hsv_lower_limit = np.array([self._hue_min, self._sat_min, self._val_min], np.uint8)
        hsv_upper_limit = np.array([self._hue_max, self._sat_max, self._val_max], np.uint8)

        mask = cv2.inRange(hsv_img, hsv_lower_limit, hsv_upper_limit)
        return mask

    @staticmethod
    def _remove_noise(mask, erode=1, dilate=1, kernel_size=3, blur=9):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        mask = cv2.erode(mask, kernel, iterations=erode)
        mask = cv2.dilate(mask, kernel, iterations=dilate)
        mask = cv2.medianBlur(mask, blur)
        return mask

    @staticmethod
    def _get_video_frame():
        return cv2.cvtColor(freenect.sync_get_video()[0], cv2.COLOR_RGB2BGR)

    @staticmethod
    def _image_bgr_to_hsv(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    @staticmethod
    def _add_mask(src, mask):
        return cv2.bitwise_and(src, src, mask=mask)

    @staticmethod
    def _find_largest_contour(img):
        cx, cy = None, None
        contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        max_area = 0
        max_contour = None

        for contour in contours:
            area = cv2.contourArea(contour)
            if max_area < area:
                max_area = area
                max_contour = contour

        if max_contour is not None:
            try:
                m = cv2.moments(contour)
                cx, cy = int(m['m10'] / m['m00']), int(m['m01'] / m['m00'])
            except ZeroDivisionError:
                print "ERROR ZERO DIV"
        return cx, cy


class StrobeTracker(TrackerBase):
    """
    Implements a simple strobe tracker. The strobe tracker is used to find positions of a single glowing
    object
    """

    def __init__(self):
        super(StrobeTracker, self).__init__()

        # HSV FILTER FOR SPHEROS
        self._hue_min = 0
        self._hue_max = 255
        self._sat_min = 0
        self._sat_max = 255
        self._val_min = 250
        self._val_max = 255

    def track_object(self, traceable_obj=None):
        traceable_obj = super(StrobeTracker, self).track_object(traceable_obj)
        x, y = self._find_largest_glowing_object()
        traceable_obj.set_pos(x, y)
        return traceable_obj

    def _find_largest_glowing_object(self):
        x, y = None, None
        image = self._get_video_frame()

        mask = self._create_hsv_mask(image)
        mask = self._remove_noise(mask, erode=2, dilate=2, kernel_size=3)

        res = self._add_mask(image, mask)

        cv2.imshow("img", image)
        cv2.imshow("mask", mask)
        cv2.waitKey(1)

        x, y = self._find_largest_contour(mask)

        return x, y


if __name__ == "__main__":
    str_track = StrobeTracker()

    while True:
        trackable_obj = str_track.track_object()
        print trackable_obj.get_pos()
        cv2.waitKey(5)





