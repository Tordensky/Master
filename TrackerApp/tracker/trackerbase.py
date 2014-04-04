import freenect
import numpy as np
import cv2
import time
from trackingfilter import FilterSpheroBlueCover, FilterSpheroYellowCover, FilterSpheroOrangeCover, FilterGlow
from traceable import Traceable, TrackingSample
from util import Vector2D


class ImageHandler(object):
    @staticmethod
    def image_bgr_to_hsv(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    @staticmethod
    def noise_reduction(mask, erode=1, dilate=1, kernel_size=3, blur=9):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        mask = cv2.erode(mask, kernel, iterations=erode)
        mask = cv2.dilate(mask, kernel, iterations=dilate)
        mask = cv2.medianBlur(mask, blur)
        return mask

    @staticmethod
    def adjust_contrast_and_brightness(img, contrast, brightness):
        mul_img = cv2.multiply(img, np.array([contrast]))
        img = cv2.add(mul_img, np.array([brightness]))
        return img


class TrackerBase(object):
    TRACK_TYPE_STROBE = 0
    TRACK_TYPE_COLOR = 1
    TRACK_TYPE_DEPTH = 2

    def __init__(self):
        self.camera_ctrl_win_name = "Camera settings"
        self.exposure_bar = "EXPOSURE"
        self.gain_bar = "GAIN"
        self.contrast_bar = "CONTRAST"
        self.brightness_bar = "BRIGHTNESS"

        self._max_gain = 100
        self._max_exposure = 100
        self._max_contrast = 100
        self._max_brightness = 100

        self.track_type = None

        # TODO How to know witch device to connect to
        self.cam = cv2.VideoCapture(-1)
        if not self.cam.isOpened():
            self.cam.open()

        self.cam.set(cv2.cv.CV_CAP_PROP_EXPOSURE, -10)
        self.cam.set(cv2.cv.CV_CAP_PROP_GAIN, 10000.5)
        self.cam.set(cv2.cv.CV_CAP_PROP_CONTRAST, 0.5)

        print "EXPOSURE", self.cam.get(cv2.cv.CV_CAP_PROP_EXPOSURE)

        #self.cam.set(cv2.cv.CV_CAP_PROP_HUE, 0.1)
        #self.cam.set(cv2.cv.CV_CAP_PROP_SATURATION, 0.1)
        #self.cam.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 0.1)

        #self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1920.0)
        #self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 1080.0)

        #self.cam.set(cv2.cv.CV_CAP_PROP_HUE, 0.1)
        self.image_size = (self.cam.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH), self.cam.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        self.setup_camera_adjustments()

    def setup_camera_adjustments(self):
        cv2.namedWindow(self.camera_ctrl_win_name)
        cv2.createTrackbar(self.exposure_bar, self.camera_ctrl_win_name, 50, self._max_exposure, self._set_cam_exposure)
        cv2.createTrackbar(self.gain_bar, self.camera_ctrl_win_name, 10, self._max_gain, self._set_cam_gain)
        cv2.createTrackbar(self.contrast_bar, self.camera_ctrl_win_name, 50, self._max_contrast, self._set_cam_contrast)
        cv2.createTrackbar(self.brightness_bar, self.camera_ctrl_win_name, 50, self._max_brightness, self._set_cam_brightness)

    def _set_cam_exposure(self, value):
        exp = float(value) / float(self._max_exposure * 5.0)
        self.cam.set(cv2.cv.CV_CAP_PROP_EXPOSURE, exp)

    def _set_cam_gain(self, value):
        gain = float(value) / float(self._max_gain * 5.0)
        self.cam.set(cv2.cv.CV_CAP_PROP_GAIN, gain)

    def _set_cam_contrast(self, value):
        contrast = float(value) / float(self._max_contrast)
        self.cam.set(cv2.cv.CV_CAP_PROP_CONTRAST, contrast)

    def _set_cam_brightness(self, value):
        brightness = float(value) / float(self._max_contrast)
        self.cam.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, brightness)

    def track_objects(self, traceable_obj):
        if traceable_obj is None:
            traceable_obj = Traceable()
        return traceable_obj

    def get_video_frame(self):
        # TODO FIX HERE FOR KINECT OR WEBCAM
        ret, frame = self.cam.read()
        return frame
        # return cv2.cvtColor(freenect.sync_get_video()[0], cv2.COLOR_RGB2BGR)

    @staticmethod
    def find_largest_contour_in_image(img):
        contours = TrackerBase.find_all_contours(img)
        largest_contour = TrackerBase.find_largest_contour(contours)

        cx, cy = TrackerBase.get_contour_coordinates(largest_contour)
        return cx, cy

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

    @staticmethod  # TODO Get bounding box
    def get_contour_coordinates(contour):
        cx, cy = -1, -1
        if contour is not None:
            try:
                m = cv2.moments(contour)
                cx, cy = int(m['m10'] / m['m00']), int(m['m01'] / m['m00'])
            except ZeroDivisionError:
                pass
        return cx, cy


class ColorTracker(TrackerBase):
    """
    Implements a simple color tracker. The color tracker is used to find positions of a single glowing
    object
    """
    def __init__(self):
        super(ColorTracker, self).__init__()
        self._masks = None

    def track_objects(self, traceable_objects):
        image = self.get_video_frame()
        image = ImageHandler.adjust_contrast_and_brightness(image, 1.0, 0.0)
        tracking_timestamp = time.time()

        for traceable_obj in traceable_objects:
            # UPDATE SCREEN POSITION
            traceable_obj.screen_size = self.image_size

            # PREPARE FOR TRACKING
            traceable_obj.do_before_tracked()

            # DO TRACKING
            x, y = self._find_traceable_in_image(image, traceable_obj)

            # Create a tracking sample
            tracking_sample = TrackingSample()
            tracking_sample.pos = Vector2D(x, y)
            tracking_sample.timestamp = tracking_timestamp

            traceable_obj.add_tracking(tracking_sample)

            # DRAW GRAPHICS
            traceable_obj.draw_name(self._masks)
            traceable_obj.draw_name(image)
            traceable_obj.draw_graphics(image)

            # FINNISH TRACKING
            traceable_obj.do_after_tracked()

        self._draw_masks()
        cv2.imshow("img", image)
        cv2.waitKey(1)
        return traceable_objects

    def _find_traceable_in_image(self, image, traceable_obj):
        mask = traceable_obj.filter.get_mask(image)
        mask = ImageHandler.noise_reduction(mask, erode=0, dilate=0, kernel_size=2)
        self._add_mask(mask)
        x, y = self.find_largest_contour_in_image(mask)
        y = self.image_size[1] - y
        return x, y

    def _draw_masks(self):
        if self._masks is not None:
            cv2.imshow("All masks", self._masks)
            self._masks = None

    def _add_mask(self, mask):
        if self._masks is None:
            self._masks = mask
        else:
            self._masks = self.merge_masks(self._masks, mask)

    @staticmethod
    def merge_masks(mask_a, mask_b):
        return cv2.bitwise_or(src1=mask_a, src2=mask_b)


if __name__ == "__main__":
    tracker = ColorTracker()

    traceable_glow = Traceable("GLOW")
    traceable_glow.filter = FilterGlow()

    traceable_blue = Traceable("BLUE")
    traceable_blue.filter = FilterSpheroBlueCover()

    traceable_yellow = Traceable("YELLOW")
    traceable_yellow.filter = FilterSpheroYellowCover()

    traceable_orange = Traceable("ORANGE")
    traceable_orange.filter = FilterSpheroOrangeCover()

    traceable_object = [traceable_blue, traceable_orange, traceable_yellow, traceable_glow]

    while True:
        traceable_object = tracker.track_objects(traceable_object)
        cv2.waitKey(5)





