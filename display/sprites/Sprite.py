

import baopig as bp


class DynamicSprite(bp.AnimatedWidget):
    """DynamicSprite represents one shape attached to a dynamic body"""

    def __init__(self, shape, surface, *args, **kwargs):

        bp.AnimatedWidget.__init__(
            self,
            parent=shape.controller.district.painter,
            surface=surface,
            *args, **kwargs
        )
        self._shape = shape

    def __str__(self):
        return f"{self.__class__.__name__}({self._shape})"

    controller = property(lambda self: self._shape.controller)
    body = property(lambda self: self._shape.body)
    shape = property(lambda self: self._shape)


class StaticSprite(bp.Image):
    """StaticSprite represents one shape attached to the static body of current space"""

    def __init__(self, shape, image, *args, **kwargs):

        bp.Image.__init__(
            self,
            parent=shape.district.painter,
            image=image,
            *args, **kwargs
        )
        self._shape = shape
        self._body = shape.body
        self._district = shape.district
        self._painter = shape.district.painter

        self.origin.lock()
        self.lock_size()

    def __str__(self):
        return f"{self.__class__.__name__}({self._shape})"

    body = property(lambda self: self._body)
    controller = district = property(lambda self: self._district)
    painter = property(lambda self: self._painter)
    shape = property(lambda self: self._shape)
