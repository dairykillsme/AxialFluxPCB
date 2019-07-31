from math import *


class Vector:
    def __init__(self, xCoord, yCoord=None):
        if yCoord is None:
            if isinstance(xCoord, Vector):
                self.x = xCoord.x
                self.y = xCoord.y
            else:
                self.x = xCoord
                self.y = xCoord
        else:
            self.x = xCoord
            self.y = yCoord

    @classmethod
    def polarInit(cls, radius, ccwAngle):
        angleRadians = radians(ccwAngle)
        x = radius * cos(angleRadians)
        y = radius * sin(angleRadians)
        return cls(x, y)

    def list(self):
        return [self.x, self.y]

    def __add__(self, other):
        other = Vector(other)
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        other = Vector(other)
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __rmul__(self, other):
        return Vector(self.x * other, self.y * other)

    def rotate(self, ccwAngle):
        angleRadians = radians(ccwAngle)
        newX = self.x * cos(angleRadians) - self.y * sin(angleRadians)
        newY = self.x * sin(angleRadians) + self.y * cos(angleRadians)
        return Vector(newX, newY)

    def length(self):
        return sqrt(self.x**2 + self.y**2)

    def scale(self, newLength):
        return newLength * self / self.length()


class Line:
    def __init__(self, start, end=None):
        if end is None:
            if isinstance(start, Vector):
                self.start = Vector(0,0)
                self.end = start
            elif isinstance(start, Line):
                self.start = start.start
                self.end = start.end
            else:
                self.start = Vector(start, start)
                start.end = Vector(start, start)
        else:
            self.start = start
            self.end = end

    def shift(self, vector):
        self.start += vector
        self.end += vector

    def length(self):
        return sqrt((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)

    def vectorize(self):
        return Vector(self.end.x - self.start.x, self.end.y - self.start.y)


class Winding:
    def __init__(self, initLayer):
        self.layer = initLayer
        self.points = []

    def rotate(self, ccwAngle):
        newWinding = Winding(self.layer)
        for point in self.points:
            newWinding.points.append(point.rotate(ccwAngle))
        return newWinding

    def addPoint(self, point):
        self.points.append(point);


class Coil:
    def __init__(self):
        self.windings = []

    def addWinding(self, newWinding):
        self.windings.append(newWinding)

    def rotate(self, ccwAngle):
        newCoil = Coil()
        for winding in self.windings:
            newCoil.windings.append(winding.rotate(ccwAngle))
        return newCoil


def calcArcLength(radius, angle):
    angleRad = radians(angle)
    return radius * angleRad