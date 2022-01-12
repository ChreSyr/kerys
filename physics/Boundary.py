

import pymunk
from .collisions import COLLTYPE_BOUNDARY
from .SolidPoint import SolidPoint


class Boundary(pymunk.Segment):
    """When a shape collides a Boundary, if the first contact is from a shape's vertex
    against the Boundary's normal direction, the associated body is stepped back"""

    COLLTYPE = COLLTYPE_BOUNDARY

    # WARNING : this shape has no associted sprite

    def __init__(self, space, a, b):

        if not isinstance(a, SolidPoint):
            a = SolidPoint(a)
        if not isinstance(b, SolidPoint):
            b = SolidPoint(b)

        pymunk.Segment.__init__(self, space.static_body, a.pos, b.pos, radius=0)

        self.d = self.b - self.a  # TODO : Utile ?
        self.collision_type = self.COLLTYPE
        self.friction = 1

        self._body = space.static_body
        self._district = space.district
        self._painter = space.painter
        self._space = space  # TODO : Utile ?

        self.endpoints = (a, b)
        self.endpoints[0].set_next_boundary(self)
        self.endpoints[1].set_prev_boundary(self)

        # self.endpoints[0].min_angle = self.normal.perpendicular().angle_degrees % 360
        # self.endpoints[1].max_angle = self.normal.perpendicular().angle_degrees % 360

    body = property(lambda self: self._body)  # TODO : Utile ?
    controller = district = property(lambda self: self._district)
    painter = property(lambda self: self._painter)

    def __str__(self):
        return f"Boundary({self.a}, {self.b})"

    def collidepoly(self, poly):
        """Called each step a Poly shape collides with the boundary"""
        pass
