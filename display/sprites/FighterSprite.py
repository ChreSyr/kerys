

import baopig as bp
from .Sprite import DynamicSprite


class FighterSprite(DynamicSprite):

    def __init__(self, shape):

        fighter = shape.fighter
        DynamicSprite.__init__(self, shape, fighter.images.rest,
                               pos=(fighter.left, fighter.top),
                               layer="fighters_layer")

        self.original = fighter.images.rest.copy()  # TODO : directions, walk animations

        self._fighter = shape.fighter

    fighter = property(lambda self: self._fighter)

    def set_angle(self, angle_degrees):

        self.set_surface(bp.transform.rotate(self.original, angle_degrees))
        self.center = self.controller.center + self.shape.offset

