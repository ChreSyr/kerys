

from .Fighter import Fighter


class Kocci(Fighter):

    #               left top
    HITBOX_MARGINS = (4, 27)

    def __init__(self, player, district, id, center):

        Fighter.__init__(self, player, district, id, center)

