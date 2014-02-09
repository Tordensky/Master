

class Vector2D(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

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
        self.x += other[0]
        self.y += other[1]
        return self

    def __sub__(self, other):
        tmp = Vector2D()
        tmp.x = self.x - other[0]
        tmp.y = self.y - other[1]
        return tmp

    def __isub__(self, other):
        self.x -= other[0]
        self.y -= other[1]
        return self

    def __mul__(self, other):
        tmp = Vector2D()
        tmp.x = self.x * other[0]
        tmp.y = self.y * other[1]
        return tmp

    def __imul__(self, other):
        self.x *= other[0]
        self.y *= other[1]
        return self

    def __div__(self, other):
        tmp = Vector2D()
        tmp.x = float(self.x) / other[0]
        tmp.y = float(self.y) / other[1]
        return tmp

    def __idiv__(self, other):
        self.x = float(self.x) / float(other[0])
        self.y = float(self.y) / float(other[1])
        return self

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def set_values(self, x, y):
        self.x = x
        self.y = y

    def get_values(self):
        return Vector2D(self.x, self.y)


if __name__ == "__main__":
    a = Vector2D(1, 2)
    b = Vector2D(3, 4)

    a += b * (100, 100)
    a -= (0, 2)
    print a
    print b
    print a + b, a, b
    print a - b, a, b
    print a * b, a, b
    print a / b, a, b

    print a[1]
    print a[0]
    #a = b
    print a, b, a == b
    b - Vector2D(1, 1)
    print a, b

