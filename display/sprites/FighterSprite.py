

from .Sprite import DynamicSprite


class FighterSprite(DynamicSprite):

    def __init__(self, fighter):

        DynamicSprite.__init__(self, fighter, fighter.images.rest, layer="fighters_layer", pos=(0, 0))

    def paint(self):

        self.set_surface(self.controller.images.get())
