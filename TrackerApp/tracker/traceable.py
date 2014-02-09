from vector import Vector2D


class Traceable(object):
    def __init__(self):
        self.pos = Vector2D()
        self.last_pos = Vector2D()

    def set_pos(self, x, y):
        self.last_pos = self.pos.get_values()
        self.pos.set_values(x, y)

    def get_pos(self):
        return self.pos.get_values()