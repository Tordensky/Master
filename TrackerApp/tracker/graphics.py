import numpy as np

import cv2

from util.vector import Vector2D


class ImageGraphics(object):
    @staticmethod
    def draw_circle(img, pos, radius, color):
        pos = ImageGraphics.to_screen_coordinates(img, pos)
        cv2.circle(img, (int(pos[0]), int(pos[1])), radius, color.bgr, -1)

    @staticmethod
    def draw_line(img, pos_a, pos_b, color):
        pos_a = ImageGraphics.to_screen_coordinates(img, pos_a)
        pos_b = ImageGraphics.to_screen_coordinates(img, pos_b)
        cv2.line(img, (int(pos_a[0]), int(pos_a[1])), (int(pos_b[0]), int(pos_b[1])), color.bgr)

    @staticmethod
    def draw_square(img):
        # TODO draw square
        raise NotImplementedError

    @staticmethod
    def text(img, txt, pos, size, color):
        pos = ImageGraphics.to_screen_coordinates(img, pos)
        cv2.putText(img, txt, (int(pos[0]), int(pos[1])), cv2.FONT_ITALIC, size, color.bgr)

    @staticmethod
    def to_screen_coordinates(img, pos):
        shape = np.shape(img)
        return Vector2D(int(pos[0]), int(shape[0] - pos[1]))

