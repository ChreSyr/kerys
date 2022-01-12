

import pymunk
from display.sprites.FighterSprite import FighterSprite


class FighterShape(pymunk.Poly):

    def __init__(self, fighter, vertices, offset=None):

        if offset is not None: vertices = tuple(offset + v for v in vertices)
        else: offset = (0, 0)
        # WARNING : the first vertice in vertices MUST be the topleft corner, it will be used in FighterSprite

        pymunk.Poly.__init__(self, fighter.body, vertices)
        # self.friction = 1  # TODO : check if correct

        self._fighter = fighter
        self._offset = offset
        self._original_offset = pymunk.Vec2d(offset)
        self._sprite = FighterSprite(self)

        self.rotated_vertices = None
        self.update_rotated_vertices()

    controller = fighter = property(lambda self: self._fighter)
    offset = property(lambda self: self._offset)
    sprite = property(lambda self: self._sprite)

    def get_world_vertices(self):

        return tuple(self.iget_world_vertices())

    def iget_world_vertices(self):

        for v in self.rotated_vertices:
            yield v + self.body.position

    def update_rotated_vertices(self):

        self.rotated_vertices = tuple(v.rotated(self.body.angle) for v in self.get_vertices())
        self._offset = self._original_offset.rotated(self.body.angle)
        self.sprite.set_angle(-self.body.angle_degrees)

    def update_sprite(self):

        self._sprite.center = self.offset + self.body.position

