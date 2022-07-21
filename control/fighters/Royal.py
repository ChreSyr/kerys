

import math
from .Fighter import Fighter


class Royal(Fighter):

    #               left top
    HITBOX_MARGINS = (3, 26)

    def __init__(self, player, district, id, center):

        Fighter.__init__(self, player, district, id, center, max_jumps=math.inf)

        # TODO : keep UP presssed will make multi jumps

