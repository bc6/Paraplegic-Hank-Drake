#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/Vector3.py
import types
import math
import random

class Vector3(object):
    __guid__ = 'foo.Vector3'
    __passbyvalue__ = 1
    __slots__ = ['x', 'y', 'z']

    def __init__(self, *arg):
        object.__init__(self)
        nargs = len(arg)
        if nargs == 0:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
        elif nargs == 3:
            self.x = arg[0]
            self.y = arg[1]
            self.z = arg[2]
        elif nargs == 1:
            if isinstance(arg[0], Vector3):
                self.x = arg[0].x
                self.y = arg[0].y
                self.z = arg[0].z
            elif isinstance(arg[0], (types.ListType, types.TupleType)) and len(arg[0]) >= 3:
                self.x = arg[0][0]
                self.y = arg[0][1]
                self.z = arg[0][2]
            else:
                raise TypeError('not a Vector3, list, tuple, or not enough data members %s' % type(arg[0]))
        else:
            raise TypeError('Vector3 : Argument Error : Expectes, 0, 1, 3 arguments, got %d' % len(arg))

    def __getstate__(self):
        return (self.x, self.y, self.z)

    def __setstate__(self, state):
        self.__init__(state)

    def __setattr__(self, name, value):
        if name in self.__slots__:
            object.__setattr__(self, name, float(value))

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return [self.x, self.y, self.z].__repr__()

    def __len__(self):
        return 3

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        if key == 2:
            return self.z
        raise IndexError

    def __setitem__(self, key, value):
        if key == 0:
            self.x = float(value)
        elif key == 1:
            self.y = float(value)
        elif key == 2:
            self.z = float(value)
        else:
            raise IndexError

    def Normalize(self):
        d = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        if d > 0.0:
            self.x = self.x / d
            self.y = self.y / d
            self.z = self.z / d
        return self

    def Randomize(self, radius = 1.0, width = 0.0):
        t = random.random() * 2.0 * math.pi
        u = (random.random() - 0.5) * 2.0
        sq = math.sqrt(1.0 - u * u)
        if width > 0.0:
            if width > radius:
                width = radius
            radius = radius - random.random() * width
        self.x = radius * sq * math.cos(t)
        self.y = radius * sq * math.sin(t)
        self.z = radius * u
        return self

    def Length(self):
        return abs(self)

    def Length2(self):
        return self * self

    def Unit(self):
        a = Vector3(self)
        return a.Normalize()

    def __add__(self, other):
        if type(other) != Vector3:
            raise TypeError
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if type(other) != Vector3:
            raise TypeError
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __div__(self, other):
        return Vector3(self.x / other, self.y / other, self.z / other)

    def __mul__(self, other):
        if type(other) == Vector3:
            return self.x * other.x + self.y * other.y + self.z * other.z
        if type(other) in (float, long, int):
            return Vector3(self.x * other, self.y * other, self.z * other)
        raise TypeError

    def __rmul__(self, other):
        if type(other) == Vector3:
            return self.x * other.x + self.y * other.y + self.z * other.z
        if type(other) in (float, long, int):
            return Vector3(self.x * other, self.y * other, self.z * other)
        raise TypeError

    def __xor__(self, other):
        if type(other) != Vector3:
            raise TypeError
        return Vector3(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def __abs__(self):
        return math.sqrt(self * self)

    def __eq__(self, other):
        if type(other) != Vector3:
            raise TypeError
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        if type(other) != Vector3:
            raise TypeError
        return not self.__eq__(other)

    def AsTuple(self):
        return (self.x, self.y, self.z)