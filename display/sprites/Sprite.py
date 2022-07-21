

import baopig as bp


class DynamicSprite(bp.Widget):
    """DynamicSprite represents one shape attached to a dynamic body"""

    def __init__(self, controller, surface, *args, **kwargs):

        bp.Widget.__init__(
            self,
            parent=controller.district.painter,
            surface=surface,
            *args, **kwargs
        )
        self._controller = controller

    def __str__(self):
        return f"{self.__class__.__name__}({self.body})"

    controller = property(lambda self: self._controller)
    body = property(lambda self: self._controller.body)


class StaticSprite(bp.Image):
    """StaticSprite represents one shape attached to the static body of current space"""

    def __init__(self, block, image, *args, **kwargs):

        bp.Image.__init__(
            self,
            parent=block.district.painter,
            image=image,
            *args, **kwargs
        )
        # self._shape = shape
        self._district = block.district
        self._painter = self._district.painter

        self.origin.lock()
        self.lock_size()

    def __str__(self):
        return f"{self.__class__.__name__}({self._shape})"

    body = property(lambda self: self._body)
    controller = district = property(lambda self: self._district)
    painter = property(lambda self: self._painter)
    shape = property(lambda self: self._shape)
