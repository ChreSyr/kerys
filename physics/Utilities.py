

import pymunk


class Segment:
    def __init__(self, a, b):
        self.a = None
        self.b = None
        self.d = None
        self.n = None
        self.config(a, b)

    def __add__(self, other):
        if isinstance(other[0], (int, float)):
            return Segment(self.a + other, self.b + other)

    def __eq__(self, other):
        return self.a == other[0] and self.b == other[1]

    def __getitem__(self, item):
        if item is 0: return self.a
        if item is 1: return self.b

    def __reversed__(self):
        return Segment(self.b, self.a)

    def __repr__(self):
        return f"Segment(a={self.a}, b={self.b}, normal={self.n})"

    def __sub__(self, other):
        if isinstance(other[0], (int, float)):
            return Segment(self.a - other, self.b - other)

    def config(self, a, b):
        self.a = pymunk.Vec2d(a)
        self.b = pymunk.Vec2d(b)
        self.d = pymunk.Vec2d(self.b - a)
        self.n = self.d.perpendicular_normal()

    def is_connected(self, seg):
        if self.b == seg.a:
            return self.b
        elif self.b + seg.n == seg.a + self.n:
            return self.b + seg.n
        elif self.b - self.n == seg.a - seg.n:
            return self.b + seg.n

        return False

    def mindist_to_point(self, point):
        """Return the minimum distance from point to segment"""
        return ((point - self.a).cross(self.d))/self.d.get_length_sqrd()

    def mindist_to_segment(self, seg):
        """Return the length of the shortest vector betwwen self and seg"""
        return min((  # WARNING : forgot intersections, but not usefull with only horizontal and vertical segments
            self.mindist_to_point(seg.a),
            self.mindist_to_point(seg.b),
            seg.mindist_to_point(self.a),
            seg.mindist_to_point(self.b),
        ))
