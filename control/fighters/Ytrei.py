
from .Fighter import Fighter


class Ytrei(Fighter):

    #               left top
    HITBOX_MARGINS = (5, 11)

    def __init__(self, player, district, id, center):

        Fighter.__init__(self, player, district, id, center)

