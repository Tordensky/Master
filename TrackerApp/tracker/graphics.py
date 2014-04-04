import numpy as np

import cv2
from util import Color

from util.vector import Vector2D


class ImageGraphics(object):
    @staticmethod
    def draw_circle(img, pos, radius, color):
        pos = ImageGraphics.convert_to_screen_coordinates(img, pos)
        cv2.circle(img, (int(pos[0]), int(pos[1])), radius, color.bgr, -1)

    @staticmethod
    def draw_line(img, pos_a, pos_b, color):
        pos_a = ImageGraphics.convert_to_screen_coordinates(img, pos_a)
        pos_b = ImageGraphics.convert_to_screen_coordinates(img, pos_b)
        cv2.line(img, (int(pos_a[0]), int(pos_a[1])), (int(pos_b[0]), int(pos_b[1])), color.bgr)

    @staticmethod
    def draw_square(img):
        # TODO draw square
        raise NotImplementedError

    @staticmethod
    def text(img, txt, pos, size, color):
        pos = ImageGraphics.convert_to_screen_coordinates(img, pos)
        cv2.putText(img, txt, (int(pos[0]), int(pos[1])), cv2.FONT_ITALIC, size, color.bgr)

    @staticmethod
    def draw_vector(image, start_pos, vector, color):
        if vector.x != 0.0 or vector.y != 0.0:
            vector = vector + start_pos
            ImageGraphics.draw_circle(image, vector, 3, color)
            ImageGraphics.draw_line(image, start_pos, vector, color)

    # TODO Draw vector label
    @staticmethod
    def draw_vector_label(image, text, start_pos, vector, color):
        pass

    @staticmethod
    def convert_to_screen_coordinates(img, pos):
        shape = np.shape(img)
        return Vector2D(int(pos[0]), int(shape[0] - pos[1]))

    @staticmethod
    def draw_tracked_path(img, tracked_samples, max_samples=None):
        last_sample = None
        color = Color((255, 0, 0))
        for sample in reversed(tracked_samples):
            if max_samples is not None:
                max_samples -= 1
                if max_samples < 0:
                    break

            if last_sample is not None:
                ImageGraphics.draw_line(img, last_sample.pos, sample.pos, color)
                ImageGraphics.draw_circle(img, sample.pos, 2, color)
            last_sample = sample

