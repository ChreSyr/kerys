

import math
from control.fighters.Fighter import Fighter, cpfclamp
from display.sprites.PlateformSprite import PlateformSprite
from .Utilities import Segment
from .SolidPoint import SolidPoint
from .Boundary import Boundary


class PlateformEdge(Boundary):

    gravitor = False

    def __init__(self, plateform, a, b):

        Boundary.__init__(self, plateform.space, a, b)
        self._plateform = plateform

    plateform = property(lambda self: self._plateform)


class GravityPlateformEdge(PlateformEdge):

    gravitor = True

    def collidepoly(self, poly):

        if True: return
        delta = poly.body.up_norm.angle - self.normal.angle
        if abs(delta) > 1e-9:
            delta = (delta + math.pi / 2) % math.pi - math.pi / 2
            delta = cpfclamp(delta, -Fighter.ROTATION_TIME, Fighter.ROTATION_TIME)
            poly.body.required_rotation_angle += delta


class PlateformSolidPoint(SolidPoint):
    """A PlateformSolidPoint blocks players"""

    def __init__(self, plateform, pos):

        assert pos in plateform.vertices, pos

        SolidPoint.__init__(self, pos)

        self._plateform = plateform

    plateform = property(lambda self: self._plateform)


class Plateform:
    def __init__(self, space, first_segment, gravity_boundary_indexes=None):

        # TODO : remove
        if gravity_boundary_indexes is None: gravity_boundary_indexes = [0, 1, 2, 3]

        assert isinstance(first_segment, Segment)
        self.segments = [first_segment]
        self.boundaries = []
        self.vertices = []
        self.solidpoints = []
        self.gravity_boundary_indexes = gravity_boundary_indexes
        self.is_complete = False
        self.space = space
        self.bb = None
        self.sprite = None

    def __repr__(self):
        r = f"<Plateform(bounding_box={self.bb}, segments=[\n"
        for s in self.segments:
            r += "\t\t{}\n".format(s)
        r += "\t])>"
        return r

    def add(self, seg):
        assert isinstance(seg, Segment)
        connection = self.segments[-1].is_connected(seg)
        self.segments.append(seg)
        self.vertices.append(connection)
        # b = Boundary(self.space, seg.a, seg.b)
        # self.boundaries.append(b)
        # self.space.add(b)
        close_connection = seg.is_connected(self.segments[0])
        if close_connection:
            self.is_complete = True

            self.vertices.append(close_connection)

            for i, v in enumerate(self.vertices):
                solidpoint = PlateformSolidPoint(self, v)
                self.solidpoints.append(solidpoint)

            for i, p in enumerate(self.solidpoints):
                Edge = PlateformEdge
                if False and i in self.gravity_boundary_indexes:
                    Edge = GravityPlateformEdge
                b = Edge(self, self.solidpoints[i - 1], p)
                self.boundaries.append(b)
                self.space.add(b)

            self.bb = (
                min(v[0] for v in self.vertices),
                min(v[1] for v in self.vertices),
                max(v[0] for v in self.vertices),
                max(v[1] for v in self.vertices),
            )
            self.sprite = PlateformSprite(self)
