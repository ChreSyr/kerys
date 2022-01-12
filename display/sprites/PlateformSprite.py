

import baopig as bp
from lib.images import brick
from .Sprite import StaticSprite


class PlateformSprite(StaticSprite):

    def __init__(self, plateform):

        self._plateform = plateform

        # --- creation de l'apparence de la plateforme ---

        # on cree une image de brique positonnee en haut a gauche
        # on la resize en mosaique selon la bounding_box
        # on cree une surface de mm taille et un draw un polygon rose avec les vertex deplacés de topleft
        # sur l'image, on supprime tous les pixels qui n'ont pas etes paints par le polygone

        # TODO : subsurface from district.brick_wall

        left, top = plateform.bb[0], plateform.bb[1]
        right, bottom = plateform.bb[2], plateform.bb[3]
        size = right - left, bottom - top  # swap between top and bottom : pymunk error ?
        # print(plateform.bb, size)

        StaticSprite.__init__(self, plateform.boundaries[0], brick, pos=(left, top))
        self.lock_size(False)
        self.resize(*size, tiled=True)
        self.lock_size(True)

        topleft = left, top
        for edge in plateform.boundaries:
            if edge.gravitor:
                bp.draw.line(self.surface, bp.Color("brown"), edge.a-topleft, edge.b-topleft, 3)

        polygon = bp.Surface(size, bp.SRCALPHA)
        bp.draw.polygon(polygon, (255, 255, 255), tuple(v - self.topleft for v in plateform.vertices))
        polygon.blit(self.surface, (0, 0), special_flags=bp.BLEND_MIN)
        self.set_surface(polygon)

