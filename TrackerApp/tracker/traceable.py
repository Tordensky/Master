from tracker.graphics import ImageGraphics
from trackingfilter import Color
from vector import Vector2D


class TraceableBase(object):
    def __init__(self):
        super(TraceableBase, self).__init__()

        # Filter used to find the object in the image
        self.filter = None
        self._pos = Vector2D(0, 0)

        self.screen_size = (0, 0)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    def do_before_tracked(self, *args, **kwargs):
        pass

    def do_after_tracked(self, *args, **kwargs):
        pass

    def draw_graphics(self, image):
        pass

    def draw_name(self, image):
        pass


class Traceable(TraceableBase):
    CURRENT_SAMPLE_INDEX = -1
    LAST_SAMPLE_INDEX = -2

    def __init__(self, name="no-name"):
        self.max_samples = 5
        self.samples = []
        self.name = name

        # DIRECTION
        self.is_moving_threshold = 2.0

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
    def direction_angle(self):
        return self.direction_vector.angle

    @property
    def direction_vector(self, default=Vector2D(0, 0)):
        direction = (self.pos - self.avg_samples())
        if self.is_moving(direction):
            direction = direction.normalized * self.tail_length
            return direction
        return default

    def get_sample_at_idx(self, index, default=Vector2D(0, 0)):
        try:
            return self.samples[index]
        except IndexError:
            return default

    @property
    def pos(self):
        return self.get_sample_at_idx(self.CURRENT_SAMPLE_INDEX)

    @pos.setter
    def pos(self, value):
        x, y = value
        self._add_sample(x, y)

    def is_moving(self, direction):
        return direction.magnitude > self.is_moving_threshold

    # DRAWING FUNCTIONS
    def draw_name(self, image):
        color = Color((255, 255, 255))
        ImageGraphics.text(image, self.name, self.pos+(15, 5), 0.35, color)

    def draw_graphics(self, image):
        color = Color()
        color.rgb = (200, 0, 0)

        start_pos = self.pos
        end_pos = self.pos + self.direction_vector

        if end_pos.x > 0 and end_pos.y > 0:
            ImageGraphics.draw_circle(image, end_pos, 3, color)
            ImageGraphics.draw_line(image, start_pos, end_pos, color)

        ImageGraphics.draw_circle(image, self.pos, 2, color)

