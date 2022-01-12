
# TODO

import pygame
from display.sprites.BrickSprite import BrickSprite
from .Block import BlockShape, pymunk

1/0  # TODO : remove file ?

def get_vertices_from_digits(digits, width, height):
    """
    Return a list of vertices without offset from a string in format 'XXXX'
    where the first X tells if we want a filled topleft corner (1 is yes,
    0 is no), the second X is for the topright corner, then bottomleft and
    bottomright. This is made for staircases.
    width and height are
    """

    try:
        assert len(digits) is 4
        for digit in digits:
            assert digit in ('0', '1')
    except AssertionError:
        raise PermissionError(f"Wrong digits for a brick : {digits}")

    brick = pygame.Rect(0, 0, width, height)

    if digits == "1111":
        return brick.topleft, brick.topright, brick.bottomright, brick.bottomleft


class BrickShape(BlockShape):
    """
    A BrickSprite represents a Brick on the display
    """

    def __init__(self, district, vertices, sprites_grid_pos):

        BlockShape.__init__(self, district, vertices,
                            *tuple(BrickSprite(self, row, col) for row, col in sprites_grid_pos))

