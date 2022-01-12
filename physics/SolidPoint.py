

import pymunk


class SolidPoint:
    """A SolidPoint can block StepBackable objects"""

    def __init__(self, pos):

        self._pos = pymunk.Vec2d(pos)
        self._x, self._y = self.pos
        self._prev_boundary = self._next_boundary = None

        self.min_angle = 0
        self.max_angle = 360

        # this prevents a lot of useless calculs when two shapes can call this solidpoint in the same step
        # or solve bugs, depending on if we use movement_polygon for collisions between boundary and poly
        self.has_collided = False

    def __str__(self):
        return f"{self.__class__.__name__}(pos={self.pos}, angle={self.min_angle}->{self.max_angle})"

    next_boundary = property(lambda self: self._next_boundary)
    pos = property(lambda self: self._pos)
    prev_boundary = property(lambda self: self._prev_boundary)
    x = property(lambda self: self._x)
    y = property(lambda self: self._y)

    def can_impulse(self, impulse):
        """Return wether the impulse is in the range of min_angle -> max_angle"""

        # NOTE : angles are inverted on y axis because of pygame inversed coordonate system
        angle_degrees = 360 - impulse.angle_degrees % 360

        # print(self.max_angle, self.min_angle, angle_degrees, impulse)

        if self.min_angle == self.max_angle:
            return angle_degrees == self.min_angle
        elif self.max_angle > self.min_angle:  # TODO : optimization ?
            return self.min_angle <= angle_degrees <= self.max_angle
        else:
            return not (self.max_angle < angle_degrees < self.min_angle)

    def inside(self, poly):
        """Return True if self.pos is inside the poly, clockwise rotation"""

        bb = poly.bb
        # inverted bottom and top for the switch between pymunk and pygame coordonate system
        if not ((bb.left <= self.x <= bb.right) and (bb.bottom <= self.y <= bb.top)):
            return False
        vertices = poly.get_world_vertices()
        for i, v in enumerate(vertices):
            AB = vertices[i-1] - v
            AP = self.pos - v
            if AB.cross(AP) > 0:
                return False
        return True

    def set_next_boundary(self, boundary):
        """Dans le sens horaire"""

        assert self._next_boundary is None
        self._next_boundary = boundary
        normal = boundary.normal
        normal.y *= -1
        angle_degrees = normal.angle_degrees % 360
        opp = (angle_degrees + 180) % 360

        if self._prev_boundary is None:
            self.min_angle = angle_degrees
            self.max_angle = opp
        else:
            if self._prev_boundary.d.cross(self._next_boundary.b - self._prev_boundary.a) < 0:
                self.max_angle = -1
                self.min_angle = -1
            else:
                self.min_angle = angle_degrees

    def set_prev_boundary(self, boundary):
        """Dans le sens horaire"""

        assert self._prev_boundary is None
        self._prev_boundary = boundary
        normal = boundary.normal
        normal.y *= -1
        angle_degrees = normal.angle_degrees % 360
        opp = (angle_degrees + 180) % 360

        if self._next_boundary is None:
            self.max_angle = angle_degrees
            self.min_angle = opp
        else:
            if self._prev_boundary.d.cross(self._next_boundary.b - self._prev_boundary.a) < 0:
                self.max_angle = -1
                self.min_angle = -1
            else:
                self.max_angle = angle_degrees




