import freenect
import numpy as np

import cv2


from trackingfilter import ColorFilter, FilterSpheroBlueCover, FilterSpheroYellowCover, FilterSpheroOrangeCover, Color, \
    FilterGlow
from traceable import Traceable


class TrackerBase(object):
    TRACK_TYPE_STROBE = 0
    TRACK_TYPE_COLOR = 1
    TRACK_TYPE_DEPTH = 2

    def __init__(self):
        self.track_type = None

        self.color_filter = ColorFilter()
        self.color_filter.lower.hsv = (0, 0, 250)
        self.color_filter.upper.hsv = (255, 255, 250)

    def track_object(self, traceable_obj):
        if traceable_obj is None:
            traceable_obj = Traceable()

        return traceable_obj

    @staticmethod
    def noise_reduction(mask, erode=1, dilate=1, kernel_size=3, blur=9):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        mask = cv2.erode(mask, kernel, iterations=erode)
        mask = cv2.dilate(mask, kernel, iterations=dilate)
        mask = cv2.medianBlur(mask, blur)
        return mask

    @staticmethod
    def set_contrast_and_brightness(img, contrast, brightness):
        mul_img = cv2.multiply(img, np.array([contrast]))
        img = cv2.add(mul_img, np.array([brightness]))
        return img

    @staticmethod
    def get_video_frame():
        return cv2.cvtColor(freenect.sync_get_video()[0], cv2.COLOR_RGB2BGR)

    @staticmethod
    def image_bgr_to_hsv(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    @staticmethod
    def add_mask(src, mask):
        # TODO seems to give som issues
        return cv2.bitwise_and(src, src, mask=mask)

    @staticmethod
    def find_all_contours(img):
        contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    @staticmethod
    def find_largest_contour(contours):
        max_area = 0
        max_contour = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if max_area < area:
                max_area = area
                max_contour = contour
        return max_contour

    @staticmethod
    def find_contour_coordinates(contour):
        cx, cy = -1, -1
        if contour is not None:
            try:
                m = cv2.moments(contour)
                cx, cy = int(m['m10'] / m['m00']), int(m['m01'] / m['m00'])
            except ZeroDivisionError:
                print "ERROR ZERO DIV"
        return cx, cy

    @staticmethod
    def draw_circle(img, pos, radius, color):
        if pos.x and pos.y:
            cv2.circle(img, (int(pos.x), int(pos.y)), radius, color.bgr, -1)

    @staticmethod
    def draw_line(img, pos_a, pos_b, color):
        cv2.line(img, (int(pos_a.x), int(pos_a.y)), (int(pos_b.x), int(pos_b.y)), color.bgr)

    @staticmethod
    def _find_largest_contour(img):
        contours = TrackerBase.find_all_contours(img)
        largest_contour = TrackerBase.find_largest_contour(contours)

        cx, cy = TrackerBase.find_contour_coordinates(largest_contour)
        return cx, cy


class ColorTracker(TrackerBase):
    """
    Implements a simple color tracker. The color tracker is used to find positions of a single glowing
    object
    """

    def __init__(self):
        super(ColorTracker, self).__init__()

    def draw_graphics(self, image, traceable_obj):
        color = Color()
        color.rgb = (200, 0, 0)
        self.draw_circle(image, traceable_obj.direction_vector, 3, color)
        color.rgb = (255, 0, 0)

        self.draw_circle(image, traceable_obj.pos, 2, color)
        self.draw_line(image, traceable_obj.pos, traceable_obj.direction_vector, color)

    def track_object(self, traceable_objects):
        image = self.get_video_frame()
        image = self.set_contrast_and_brightness(image, 1.0, 0.0)
        for traceable_obj in traceable_objects:
            x, y = self._find_largest_glowing_object(image, traceable_obj)

            traceable_obj.set_pos(x, y)

            self.draw_graphics(image, traceable_obj)

        cv2.imshow("img", image)
        cv2.waitKey(1)
        return traceable_objects

    def _find_largest_glowing_object(self, image, traceable_obj):
        #hsv_img = self.image_bgr_to_hsv(image)
        mask = traceable_obj.filter.get_mask(image)
        mask = self.noise_reduction(mask, erode=2, dilate=2, kernel_size=3)
        cv2.imshow("mask", mask)

        # res = self.add_mask(image, mask)

        x, y = self._find_largest_contour(mask)

        return x, y


if __name__ == "__main__":
    color_tracker = ColorTracker()

    traceable_blue = Traceable()
    traceable_blue.filter = FilterSpheroBlueCover()

    traceable_glow = Traceable()
    traceable_glow.filter = FilterGlow()

    traceable_yellow = Traceable()
    traceable_yellow.filter = FilterSpheroYellowCover()

    traceable_orange = Traceable()
    traceable_orange.filter = FilterSpheroOrangeCover()

    traceable_list = [traceable_blue, traceable_orange, traceable_yellow, traceable_glow]
    while True:
        traceable_list = color_tracker.track_object(traceable_list)  # TODO Add list of traceable
        cv2.waitKey(5)





