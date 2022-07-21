
from .Fighter import Fighter


class Sabul(Fighter):

    #               left  top
    HITBOX_MARGINS = (10, 20)

    def __init__(self, player, district, id, center):

        Fighter.__init__(self, player, district, id, center)

