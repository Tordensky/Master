from tracker.graphics import ImageGraphics as Ig
from util import Color, Vector2D
from util import Vector2D


class TrackingSample(object):
    """
    Holds one single tracking result
    """
    pos = None
    timestamp = None

    # TODO: Add a success bool?
    # TODO: Add a areal/bounding box field?

    # TODO add a calculate linear speed between two samples
    # MAYBE STORE TRACKED IMAGE HERE?


class TraceableBase(object):
    """
    Represents a single traceable object
    Holds the filter to use for the tracking of this object and hols
    the samples tracked and logic for handling this data
    """
    current_sample_index = -1

    default_x = 0
    default_y = 0

    def __init__(self, name="no-name"):
        super(TraceableBase, self).__init__()
        self.name = name

        # Filter used to find the object in the image
        self.filter = None

        # Size of the tracked image
        self.screen_size = (0, 0)

        # TRACKING
        self.tracking_samples = []
        self.max_samples = 10

    def add_tracking(self, tracking_sample):
        self.tracking_samples.append(tracking_sample)
        if len(self.tracking_samples) > self.max_samples:
            self.tracking_samples.pop(0)

    @property
    def pos(self):
        """
        Gives the position of the last tracked sample
        @return: Vector2D
        """
        try:
            return self.tracking_samples[self.current_sample_index].pos
        except IndexError:
            return Vector2D(self.default_x, self.default_y)

    def do_before_tracked(self, *args, **kwargs):
        """
        This method is called right before the object is tracked in the image
        """
        pass

    def do_after_tracked(self, *args, **kwargs):
        """
        This method is called right after the object is tracked in the image
        """
        pass

    def draw_graphics(self, image):
        pass

    def draw_name(self, image):
        Ig.text(image, self.name, self.pos+(15, 5), 0.35, Color((255, 255, 255)))


class Traceable(TraceableBase):
    def __init__(self, name="no-name"):
        super(Traceable, self).__init__(name)
        self.is_moving_threshold = 2.0

        # GRAPHICS
        self.tail_length = 20.0

    def valid_samples(self):
        valid_sample = []
        for sample in self.tracking_samples:
            if sample.pos.x != -1 and sample.pos.y != -1:
                valid_sample.append(sample)
        return valid_sample

    @staticmethod
    def _avg(samples):
        mean_sample = Vector2D(0, 0)
        for sample in samples:
            mean_sample += sample.pos
        try:
            return mean_sample / len(samples)
        except ZeroDivisionError:
            return mean_sample

    @property
    def direction_vector(self):
        dir_vector = (self.pos - self.avg_samples())
        if self.is_moving(dir_vector):
            dir_vector = self.set_tail_length(dir_vector, self.tail_length)
            return dir_vector
        return Vector2D(TraceableBase.default_x, TraceableBase.default_y)

    def avg_samples(self):
        valid_samples = self.valid_samples()
        return self._avg(valid_samples)

    def is_moving(self, direction):
        return direction.magnitude > self.is_moving_threshold

    @staticmethod
    def set_tail_length(vector, tail_length):
        vector = vector.normalized * tail_length
        return vector

    def draw_graphics(self, image):
        Ig.draw_vector(image, self.pos, self.direction_vector, Color((200, 0, 0)))
        Ig.draw_circle(image, self.pos, 2, Color((200, 0, 0)))

