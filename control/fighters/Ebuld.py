

from .Fighter import Fighter


class Ebuld(Fighter):

    #               left top
    HITBOX_MARGINS = (5, 19)

    def __init__(self, player, district, id, midbottom):

        Fighter.__init__(self, player, district, id, midbottom)

