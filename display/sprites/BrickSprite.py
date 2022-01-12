

import baopig as bp
import lib.images as im
from .BlockSprite import BlockSprite


class BrickSprite(BlockSprite):
    """A BrickSprite represents a BrickShape on the display"""

    def __init__(self, district, row, col):

        size = district.block_size

        surf = im.brick
        if True or False == "b1111":  # TODO : rework, mosaic=True somewhere
            surf = bp.transform.scale(surf, size)

        else:
            assert size % 2 == 0, "must be pair"
            midsize = int(size / 2)
            corners = (name[1] == '1', name[2] == '1'), (name[3] == '1', name[4] == '1')
            print(corners)
            stoneblock = bp.transform.scale(im.stoneblock, (size, size))
            surf = bp.Surface((size, size), bp.SRCALPHA)
            for i in range(2):
                for j in range(2):
                    if corners[i][j]:
                        surf.blit(stoneblock.subsurface(j*midsize, i*midsize, midsize, midsize), (j*midsize, i*midsize))

        BlockSprite.__init__(self, next(iter(district.space.static_body.shapes)), surf, row, col)

    def __str__(self):
        return f"{self.__class__.__name__}(row={self.row}, col={self.col})"

