# Basic Linear Algebra implementations.
#   Only the bare-minimum of functionality will be found. This is not to be used as a catch-all implementation
#   Since this is an experiment only what I find necessary will be implemented.
#   It will also be limited in scope to specifically 2D linear algebra.
#
#   Due to personal choice vectors are represented as rows, e.g., [1.0, 2.0]. This is so vector by matrix multiplication
#   is easier to read. (left to right)
from typing import List, Tuple
from math import cos, sin, atan, atan2, sqrt


def dot_3_3(left: Tuple, right: Tuple):
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def dot_2_3(tuple2: Tuple, tuple3: Tuple):
    return tuple2[0]*tuple3[0] + tuple2[1]*tuple3[1] + tuple3[2]


def dot_2_2(left: Tuple, right: Tuple):
    return left[0]*right[0] + left[1]*right[1]


class Vec2:

    def __init__(self, x=0, y=None, radial=False):
        self._radial: List[float] = [0, 0]  # Theta then Squared Length
        self._values: List[float] = [0, 0]  # X then Y
        self._x, self._y, self._theta, self._square_length = .0, .0, .0, .0

        if radial:
            self.radial = [x, y]
        else:
            if y is None:
                self.values: List[float] = [x, x]
            else:
                self.values: List[float] = [x, y]

    def __mul__(self, other):
        """
        Dot product with vector, or 3 tuple, but reverts to matrix __rmul__ for vector - matrix multiplication
        """
        if isinstance(other, Matrix33):
            return Vec2(dot_2_3(tuple(self.values), other.column_1), dot_2_3(tuple(self.values), other.column_2))
        elif isinstance(other, Vec2):
            return self.x*other.x + self.y*other.y
        elif isinstance(other, Tuple):
            result = self.x*other[0] + self.y*other[1]
            if len(other) > 2:
                result += other[2]
            return  result

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value: float):
        self.values = [value, self._y]

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self.values = [self._x, value]

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, value: float):
        self.radial = [value, self._square_length]

    @property
    def length(self):
        return sqrt(self._square_length)

    @length.setter
    def length(self, value: float):
        self._radial = [self._theta, value**2]
        ratio = value/self.length
        self._square_length = self._radial[1]
        self._x *= ratio
        self._y *= ratio
        self._values = [self._x, self._y]

    @property
    def radial(self):
        return self._radial

    @radial.setter
    def radial(self, value: List[float]):
        self._radial = list(value)
        self._theta, self._square_length = value
        self._x = cos(self._theta) * self.length
        self._y = sin(self._theta) * self.length

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, value: List[float]):
        self._values = list(value)
        self._x, self._y = value
        self._theta = atan2(self._y, self._x)
        self._square_length = self._x**2 + self._y**2


class Matrix33:

    def __init__(self, values):
        self.values: List[float] = values

    @staticmethod
    def rotation_matrix(angle: float):
        rot_cos = cos(angle)
        rot_sin = sin(angle)

        return Matrix33([
         rot_cos, rot_sin, 0,
         -rot_sin, rot_cos, 0,
         0, 0, 1])

    @staticmethod
    def translation_matrix(translate: Vec2 = Vec2(0)):
        return Matrix33([
            1, 0, 0,
            0, 1, 0,
            translate.x, translate.y, 1])

    @staticmethod
    def scale_matrix(scale: Vec2 = Vec2(1)):
        return Matrix33([
            scale.x, 0, 0,
            0, scale.y, 0,
            0, 0, 1])

    @staticmethod
    def all_matrix(translate: Vec2 = Vec2(0), scale: Vec2 = Vec2(1), angle: float = 0):
        rot_cos = cos(angle)
        rot_sin = sin(angle)

        return Matrix33([
            rot_cos*scale.x,  rot_sin*scale.x, 0,
            -rot_sin*scale.y, rot_cos*scale.y, 0,
            translate.x,         translate.y,         1])

    @staticmethod
    def inverse_all_matrix(translate: Vec2 = Vec2(0), scale: Vec2 = Vec2(1), angle: float = 0):
        rot_cos = cos(angle)
        rot_sin = sin(angle)

        return Matrix33([
            rot_cos*(1/scale.x),  -rot_sin*(1/scale.x), 0,
            rot_sin*(1/scale.y),  rot_cos*(1/scale.y), 0,
            -translate.x,         -translate.y,        1])

    @staticmethod
    def lazy_inverse(matrix):
        """
        The "Lazy" way is assuming that this is a transform matrix with all or some parts. This would not work if the
        matrix was anything but a transform matrix, hence the laziness.
        :param matrix: A transform matrix.
        :return: Inverse matrix.
        """

        scale_x = Vec2(matrix[0], matrix[1]).length
        scale_y = Vec2(matrix[3], matrix[4]).length
        rotation_angle = atan(matrix[1]/matrix[0])
        translation = Vec2(matrix[6], matrix[7])

        rotation_cos = cos(rotation_angle)
        rotation_sin = sin(rotation_angle)

        return Matrix33([
            1/scale_x * rotation_cos, 1/scale_x * -rotation_sin, 0,
            1/scale_y * rotation_sin, 1/scale_y * rotation_cos,  0,
            -translation.x,           -translation.y,            1
        ])

    @staticmethod
    def transpose_matrix(matrix):
        v = matrix.values
        return Matrix33([
            v[0], v[3], v[6],
            v[1], v[4], v[7],
            v[2], v[5], v[8]])

    @property
    def column_1(self):
        return self.values[0], self.values[3], self.values[6]

    @property
    def column_2(self):
        return self.values[1], self.values[4], self.values[7]

    @property
    def column_3(self):
        return self.values[2], self.values[5], self.values[8]

    @property
    def row_1(self):
        return self.values[0], self.values[1], self.values[2]

    @property
    def row_2(self):
        return self.values[3], self.values[4], self.values[5]

    @property
    def row_3(self):
        return self.values[6], self.values[7], self.values[8]

    def __mul__(self, other):
        """
        Will always be a matrix.
        """
        return Matrix33([
         dot_3_3(self.row_1, other.column_1), dot_3_3(self.row_1, other.column_2), dot_3_3(self.row_1, other.column_3),
         dot_3_3(self.row_2, other.column_1), dot_3_3(self.row_2, other.column_2), dot_3_3(self.row_2, other.column_3),
         dot_3_3(self.row_3, other.column_1), dot_3_3(self.row_3, other.column_2), dot_3_3(self.row_3, other.column_3)])
