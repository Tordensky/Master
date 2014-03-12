import cv2


class ImageGraphics(object):
    @staticmethod
    def draw_circle(img, pos, radius, color):
        if pos.x and pos.y:
            cv2.circle(img, (int(pos.x), int(pos.y)), radius, color.bgr, -1)

    @staticmethod
    def draw_line(img, pos_a, pos_b, color):
        cv2.line(img, (int(pos_a.x), int(pos_a.y)), (int(pos_b.x), int(pos_b.y)), color.bgr)

    @staticmethod
    def draw_square(img):
        # TODO draw square
        raise NotImplementedError

    @staticmethod
    def text(img, txt, pos, size, color):
        cv2.putText(img, txt, (pos.x, pos.y), cv2.FONT_ITALIC, size, color.bgr)
