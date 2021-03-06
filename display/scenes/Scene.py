

import baopig as bp
import lib.images as im


class ButtonsZone(bp.SubZone):

    def __init__(self, scene):

        bp.SubZone.__init__(self, scene, size=(200, scene.rect.h), background_color=(0, 0, 0, 0))
        self.set_background_image(im.btnzone_bckgr)


class Scene(bp.Scene):

    def __init__(self, app, MainZone=None):

        if MainZone is None:
            MainZone = bp.Zone

        bp.Scene.__init__(self, app, can_select=False)

        self.buttons_zone = ButtonsZone(self)  # TODO : let the scene decide the organisation ? -> design before
        self.main_zone = MainZone(self, pos=self.buttons_zone.rect.topright,
                                  size=(self.rect.w-self.buttons_zone.rect.w, self.rect.h))

        # self.enable_selecting(False)

