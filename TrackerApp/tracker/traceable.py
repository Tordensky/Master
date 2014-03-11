from vector import Vector2D


class Traceable(object):
    def __init__(self):
        self.tail_length = 20.0
        self.max_samples = 5

        self.pos = Vector2D(0, 0)
        self.last_pos = Vector2D(0, 0)

        self.samples = []

        self.filter = None

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
    def direction_vector(self):
        direction = (self.avg_samples() - self.pos)
        direction.invert()
        direction = direction.normalized * self.tail_length
        return self.pos + direction

    def set_pos(self, x, y):
        self._add_sample(x, y)
        self.last_pos = self.pos.get_values()
        self.pos.set_values(x, y)
