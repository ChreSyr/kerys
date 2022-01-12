

from .Sprite import StaticSprite


class BlockSprite(StaticSprite):
    """
    A BlockSprite is a static sprite (still can be animated, just not mouving)
    representing a BlockShape. This can only receive requests from it.
    A BlockSprite instance is stored in Block.sprites and DistrictZone.blocks,
    wich is a baopig.GridLayer
    """

    def __init__(self, shape, img, row, col, **kwargs):

        # parent is a DistrictZone
        StaticSprite.__init__(self, shape, surface=img,
                              row=row, col=col, layer=shape.painter.blocks, **kwargs)

