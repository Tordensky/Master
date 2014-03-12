from collections import namedtuple
import colorsys
import numpy as np
import cv2


class Color(object):
    max_deg_value = 180.0
    RGB_tuple = namedtuple('RGB', 'r g b')
    HSV_tuple = namedtuple('HSV', 'h s v')
    BGR_tuple = namedtuple('BGR', 'b g r')

    def __init__(self, rgb_color=None):
        self._color = (0, 0, 0)
        if rgb_color is not None:
            self.rgb = rgb_color

    @property
    def rgb(self):
        """
        Returns the color as a RGB color value
        @return: The RGB color tuple
        @rtype: Color.RGB_tuple
        """
        return Color.RGB_tuple(*self._color)

    @rgb.setter
    def rgb(self, rgb_color):
        """
        Sets color value from a RGB tuple (r, g, b)
        @param rgb_color: The new RGB color value
        @type rgb_color: tuple
        """
        self._color = rgb_color

    @property
    def hsv(self):
        """
        Get color as HSV tuple
        @return: Tuple of color coordinates
        @rtype: Color.HSV_tuple
        """
        r, g, b = self.rgb
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        h *= self.max_deg_value
        s *= 255
        v *= 255
        return Color.HSV_tuple(int(h), int(s), int(v))

    @hsv.setter
    def hsv(self, hsv_color):
        """
        Set color from HSV tuple (h, s, v)
        @param hsv_color: The tuple of values
        @type hsv_color: tuple
        """
        h, s, v = hsv_color
        h = float(h) / float(self.max_deg_value)
        s = float(s) / 255.0
        self._color = colorsys.hsv_to_rgb(h, s, v)

    @property
    def bgr(self):
        """
        Get color as BGR tuple
        @return: The color as a BGR tuple
        @rtype: Color.BGR_tuple
        """
        r, g, b = self.rgb
        return Color.BGR_tuple(b, g, r)

    @bgr.setter
    def bgr(self, bgr_color):
        """
        Set color from BGR tuple
        @param bgr_color: Bgr color
        @type bgr_color: tuple
        """
        b, g, r = bgr_color
        self.rgb = (r, g, b)

    @property
    def hex(self):
        """
        Get color as rgb hex string
        @return: Color value as RGB Hex string
        @rtype: str
        """
        return hex(self)

    @hex.setter
    def hex(self):
        # TODO
        raise NotImplementedError

    def __hex__(self):
        r, g, b = self.rgb
        return '#%02x%02x%02x' % (r, g, b)


class BaseFilter(object):
    def get_mask(self, img):
        return img


class ColorFilter(BaseFilter):
    def __init__(self):
        self.lower = Color()
        self.upper = Color()

    def hsv_lower_filter(self, data_size=np.uint8):
        return ColorFilter.to_np_array(self.lower.hsv, data_size)

    def hsv_upper_filter(self, data_size=np.uint8):
        return ColorFilter.to_np_array(self.upper.hsv, data_size)

    @staticmethod
    def to_np_array(color_tuple, data_size):
        return np.array(list(color_tuple), data_size)

    def get_mask(self, img):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_lower_limit = self.hsv_lower_filter()
        hsv_upper_limit = self.hsv_upper_filter()
        return cv2.inRange(hsv_img, hsv_lower_limit, hsv_upper_limit)


class FilterGlow(ColorFilter):
    def __init__(self):
        super(FilterGlow, self).__init__()
        self.lower.hsv = (0, 0, 0)
        self.upper.hsv = (0, 255, 255)


class FilterSpheroBlueCover(ColorFilter):
    def __init__(self):
        ColorFilter.__init__(self)
        self.lower.hsv = (100, 100, 100)
        self.upper.hsv = (120, 255, 255)


class FilterSpheroYellowCover(ColorFilter):
    def __init__(self):
        ColorFilter.__init__(self)
        self.lower.hsv = (20, 100, 100)
        self.upper.hsv = (40, 255, 255)


class FilterSpheroOrangeCover(ColorFilter):
    def __init__(self):
        ColorFilter.__init__(self)
        self.lower.hsv = (160, 113, 146)
        self.upper.hsv = (180, 201, 255)

if __name__ == "__main__":
    color = Color()

    color.rgb = (0, 0, 0)
    print "RGB", color.rgb, "HSV", color.hsv

    color.hsv = (0, 0, 255)
    print "RGB", color.rgb, "HSV", color.hsv

    color.hsv = (0, 255, 255)
    print "RGB", color.rgb, "HSV", color.hsv

    color.hsv = (0, 255, 255)
    print color.rgb, color.hsv, color.bgr

    print hex(color), color.hex
