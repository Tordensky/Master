import math


class Vector2D(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __str__(self):
        return "(x: " + str(self.x) + ", y:" + str(self.y) + ", deg:" + str(self.angle) + ")"

    def __repr__(self):
        return Vector2D(self.x, self.y)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("value must be integer")
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError("Index out of range, must be value in the range of 0 to 1")

    def __setitem__(self, index, value):
        if not isinstance(index, int):
            raise TypeError("value must be integer")
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("Index out of range, must be value in the range of 0 to 1")

    def __add__(self, other):
        tmp = Vector2D()
        tmp.x = self.x + other[0]
        tmp.y = self.y + other[1]
        return tmp

    def __iadd__(self, other):
        v, w = self._get_values(other)
        self.x += v
        self.y += w
        return self

    def __sub__(self, other):
        tmp = Vector2D()
        v, w = self._get_values(other)
        tmp.x = self.x - v
        tmp.y = self.y - w
        return tmp

    def __isub__(self, other):
        v, w = self._get_values(other)
        self.x -= v
        self.y -= w
        return self

    def __mul__(self, other):
        tmp = Vector2D()
        v, w = self._get_values(other)
        tmp.x = self.x * v
        tmp.y = self.y * w
        return tmp

    def __imul__(self, other):
        v, w = self._get_values(other)
        self.x *= v
        self.y *= w
        return self

    def __div__(self, other):
        tmp = Vector2D()
        v, w = self._get_values(other)
        tmp.x = float(self.x) / v
        tmp.y = float(self.y) / w
        return tmp

    @staticmethod
    def _get_values(other):
        if isinstance(other, (tuple, Vector2D)):
            v = other[0]
            w = other[1]
        else:
            v = other
            w = other
        return v, w

    def __idiv__(self, other):
        v, w = self._get_values(other)
        self.x = float(self.x) / v
        self.y = float(self.y) / w
        return self

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    @property
    def inverted(self):
        return Vector2D(self.x * -1, self.y * -1)

    def invert(self):
        self.x *= -1
        self.y *= -1

    @property
    def angle(self):
        deg = math.degrees(self.angle_radians)
        if deg < 0:
            return 360 - abs(deg)
        return deg

    @property
    def angle_radians(self):
        return math.atan2(self.y, self.x)

    @property
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    @property
    def normalized(self):
        m = self.magnitude
        if m:
            return Vector2D(self.x / m, self.y / m)
        return Vector2D(0, 0)

    def copy(self):
        return Vector2D(self.x, self.y)

    def set_values(self, x, y):
        self.x = x
        self.y = y

    def get_values(self):
        return Vector2D(self.x, self.y)

    def set_angle_rad(self, angle_radians):
        self.x = math.cos(angle_radians)
        self.y = math.sin(angle_radians)
        return Vector2D(self.x, self.y)

    def set_angle_deg(self, angle_deg):
        return self.set_angle_rad(math.radians(angle_deg))

    def rotate_deg(self, angle_deg):
        x = self.x
        y = self.y
        angle = math.radians(angle_deg)
        self.x = x * math.cos(angle) - y * math.sin(angle)
        self.y = y * math.cos(angle) + x * math.sin(angle)
        return Vector2D(self.x, self.y)


if __name__ == "__main__":
    a = Vector2D(0, 1)
    # b = Vector2D(3, 4)
    #
    # a += b * (100, 100)
    # a -= (0, 2)
    # print a
    # print b
    # print a + b, a, b
    # print a - b, a, b
    # print a * b, a, b
    # print a / b, a, b
    #
    # print a[1]
    # print a[0]
    # #a = b
    # print a, b, a == b
    # b - Vector2D(1, 1)
    # print a.magnitude, b.magnitude
    # print a.normalized, b.normalized

    print a.angle
    a.rotate_deg(-89)
    print a.angle
    # s


