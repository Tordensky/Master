

class TrackingSample(object):
    """
    Holds one single tracking result
    """
    pos = None
    timestamp = None
    valid = False

    def linear_speed_to_other_sample(self, other):
        """
        Calculates the linear speed from this sample to the given sample
        @param other: Other sample to calculate linear speed to
        @type other: TrackingSample
        @return: The given speed in pixels per second
        @rtype: float
        """
        distance = (self.pos - other.pos).magnitude
        time_diff = abs(self.timestamp - other.timestamp)
        try:
            speed = distance / time_diff
        except ZeroDivisionError:
            speed = None
        return speed

    # TODO: Add a success bool?
    # TODO: Add a areal/bounding box field?

    # TODO is accelerating?
    # MAYBE STORE TRACKED IMAGE HERE?