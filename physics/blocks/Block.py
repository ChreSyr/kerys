

import pymunk


class BlockShape(pymunk.Poly):
    """
    A BlockShape is a static polygon interacting with Fighters

    This is an abstract class, its sub-classes must define COLLTYPE
    """
    COLLTYPE = None

    def __init__(self, space, vertices, *sprites):

        pymunk.Poly.__init__(self, space.static_body, vertices)

        self._painter = space.painter
        self._sprites = sprites

    painter = property(lambda self: self._painter)
    sprites = property(lambda self: self._sprites)
