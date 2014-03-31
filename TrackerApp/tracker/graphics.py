import numpy as np

import cv2

from util.vector import Vector2D


class ImageGraphics(object):
    @staticmethod
    def draw_circle(img, pos, radius, color):
        pos = ImageGraphics.to_screen_coordinates(img, pos)
        cv2.circle(img, (int(pos.x), int(pos.y)), radius, color.bgr, -1)

    @staticmethod
    def draw_line(img, pos_a, pos_b, color):
        pos_a = ImageGraphics.to_screen_coordinates(img, pos_a)
        pos_b = ImageGraphics.to_screen_coordinates(img, pos_b)
        cv2.line(img, (int(pos_a.x), int(pos_a.y)), (int(pos_b.x), int(pos_b.y)), color.bgr)

    @staticmethod
    def draw_square(img):
        # TODO draw square
        raise NotImplementedError

    @staticmethod
    def text(img, txt, pos, size, color):
        pos = ImageGraphics.to_screen_coordinates(img, pos)
        cv2.putText(img, txt, (pos.x, pos.y), cv2.FONT_ITALIC, size, color.bgr)

    @staticmethod
    def to_screen_coordinates(img, pos):
        shape = np.shape(img)
        return Vector2D(int(pos.x), int(shape[0] - pos.y))

