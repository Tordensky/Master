from tracker.graphics import ImageGraphics
from trackingfilter import Color
from vector import Vector2D


class Traceable(object):
    CURRENT_SAMPLE_INDEX = -1
    LAST_SAMPLE_INDEX = -2

    def __init__(self, name="no-name"):
        self.max_samples = 5
        self.samples = []
        self.name = name

        # Filter used to find the object in the image
        self.filter = None

        # DIRECTION
        self.is_moving_thresh = 2.0

        # GRAPHICS
        self.tail_length = 20.0

    def _add_sample(self, x, y):
        if len(self.samples) > self.max_samples:
            self.samples.pop(0)
        self.samples.append(Vector2D(x, y))

    def valid_samples(self):
        valid_sample = []
        for sample in self.samples:
            if sample.x != -1 and sample.y != -1:
                valid_sample.append(sample)
        return valid_sample

    @staticmethod
    def _avg(samples):
        mean_sample = Vector2D(0, 0)
        for sample in samples:
            mean_sample += sample
        try:
            return mean_sample / len(samples)
        except ZeroDivisionError:
            return mean_sample

    def avg_samples(self):
        valid_samples = self.valid_samples()
        return self._avg(valid_samples)

    @property
    def direction_vector(self, default=Vector2D(-1, -1)):
        direction = (self.avg_samples() - self.pos)
        if self.is_moving(direction):
            direction.invert()
            direction = direction.normalized * self.tail_length
            return self.pos + direction
        return default

    def sample_index(self, index, default=Vector2D(0, 0)):
        try:
            return self.samples[index]
        except IndexError:
            return default

    @property
    def pos(self):
        return self.sample_index(self.CURRENT_SAMPLE_INDEX)

    @pos.setter
    def pos(self, value):
        x, y = value
        self._add_sample(x, y)

    @property
    def last_pos(self):
        return self.sample_index(self.LAST_SAMPLE_INDEX)

    def is_moving(self, direction):
        return direction.magnitude > self.is_moving_thresh

    def draw_graphics(self, image):
        color = Color()
        color.rgb = (200, 0, 0)

        dir_vec = self.direction_vector
        if dir_vec.x > -1 and dir_vec.y > -1:
            ImageGraphics.draw_circle(image, dir_vec, 3, color)
            ImageGraphics.draw_line(image, self.pos, dir_vec, color)

        ImageGraphics.draw_circle(image, self.pos, 2, color)

    def draw_name(self, image):
        color = Color((255, 255, 255))
        ImageGraphics.text(image, self.name, self.pos+(15, 5), 0.35, color)

