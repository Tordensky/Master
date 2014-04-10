import tracker
from tracker.graphics import ImageGraphics as Ig
from util import Color
from util import Vector2D


class TraceableObject(object):
    """
    Represents a single traceable object
    Holds the filter to use for the tracking of this object and holds
    the samples tracked and logic for handling this data
    """
    default_x = None
    default_y = None

    def __init__(self, name="no-name"):
        super(TraceableObject, self).__init__()
        self.object_name = name

        # Filter used to find the object in the image
        self.filter = None

        # Size of the tracked image
        self.screen_size = (0, 0)

        # TRACKING
        self.tracking_samples = []
        self.max_samples_in_memory = 10

        self.max_samples_dir_determination = 4

        self.is_moving_threshold = 1.0

        # Graphics
        self.draw_direction_vector = True
        self.color = Color((255, 0, 0))
        self.direction_length = 20

    def add_tracking(self, tracking_sample):
        """
        Add a new tracking sample

        @param tracking_sample:
         @type tracking_sample: tracker.sample.TrackingSample
        """
        self.tracking_samples.insert(0, tracking_sample)
        if len(self.tracking_samples) > self.max_samples_in_memory:
            self.tracking_samples.pop(-1)

    @property
    def pos(self):
        """
        Gives the position of the last successfully tracked sample

        @return: Vector2D or None
         @rtype: Vector2D or None
        """
        for tracking in self.tracking_samples:
            if tracking.valid:
                return tracking.pos
        else:
            return None

    @property
    def speed(self):
        """
        Liner speed between the two last successful samples

        @return: The linear speed, None if only one sample
         @rtype: float or None
        """
        try:
            valid_samples = self.valid_tracking_samples(max_samples=2)
            return valid_samples[-1].linear_speed_to_other_sample(valid_samples[-2])
        except IndexError:
            return None

    @property
    def is_moving(self):
        """
        Returns true if the tracked movement is larger than the is_moving_threshold.s

        @return: True if moving False else
         @rtype: bool
        """
        return self.direction_vector.magnitude >= self.is_moving_threshold

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
        """
        Insert all the code for drawing in this method. Is executed after the tracking

        @param image: The image to draw the image on. (Numpy Vector)
        """
        if self.draw_direction_vector:
            try:
                label = round(self.direction_vector.angle, 2)
                if self.is_moving:
                    vector = self.direction_vector.set_length(self.direction_length)
                    Ig.draw_vector_with_label(image, label, self.pos, vector, self.color)
                Ig.draw_circle(image, self.pos, 2, self.color)
            except tracker.graphics.DrawError as e:
                print "Error drawing direction vector:", e.message

    def draw_name(self, image):
        """
        Draws the name of the object to the given image at the objects latest successfully traced position

        @param image:
        """
        if self.pos is not None:
            Ig.text(image, self.object_name, self.pos+(15, 5), 0.35, Color((255, 255, 255)))

    def valid_tracking_samples(self, max_samples=-1):
        """
        Return a list of the all the valid samples.

        @param max_samples: The maximum number of samples to return
         @type max_samples: int
        @return: list of the valid samples
         @rtype: list
        """
        valid_samples = []
        for tracking in self.tracking_samples:
            if tracking.valid:
                valid_samples.append(tracking)
                max_samples -= 1
            if max_samples == 0:
                break
        return valid_samples

    @staticmethod
    def get_avg_of_samples(tracking_samples):
        """
        Gets the average of the given samples

        @raise ZeroDivisionError: If number of samples is Zero
        @param tracking_samples: list of samples
         @type tracking_samples: list
        @return: the average
         @rtype: Vector2D
        """
        avg_sample = Vector2D(0, 0)
        for tracking_sample in tracking_samples:
            avg_sample += tracking_sample.pos
        return avg_sample / len(tracking_samples)

    @property
    def direction_vector(self):
        """
        Returns a vector with the tracked direction of the object
        @return: The direction vector
         @rtype: Vector2D
        """
        valid_samples = self.valid_tracking_samples(max_samples=self.max_samples_dir_determination)
        dir_vec = Vector2D(0, 0)
        try:
            dir_vec = self.pos - self.get_avg_of_samples(valid_samples)
        except ZeroDivisionError:
            pass
        return dir_vec