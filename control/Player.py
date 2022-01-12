

class Player:
    """
    This class is the reference for every user's input and choices
    """

    def __init__(self):

        self._fighter_class = None
        self._fighter = None  # initialized in Fighter.__init__()

    fighter_class = property(lambda self: self._fighter_class)
    fighter = property(lambda self: self._fighter)

    def create_fighter(self, district, id, center):

        if self._fighter_class is None:
            raise PermissionError("The player has no selected fighter class")
        if self.fighter is not None:
            raise PermissionError("The player already has an instancied fighter")
        self._fighter = self._fighter_class(self, district, id, center)
        return self.fighter

    def delete_fighter(self):
        """Only called from Player"""

        if self.fighter is None:
            raise PermissionError("The player has no instancied fighter")
        self.fighter.district.delete_fighter(self.fighter)
        self._fighter = None

    def set_fighter_class(self, fighter_class):

        self._fighter_class = fighter_class

