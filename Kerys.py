

import glob
import baopig as bp
import lib.images as im
from control.District import District
from control.Player import Player
from control.fighters import *


# TODO : set the host player id to 0


class Kerys(bp.Application):

    def __init__(self):

        # TODO : ApplicationPainter ? -> ApplicationPainter.update(), etc...

        bp.Application.__init__(self)
        self.set_style_for(
            bp.SliderBloc,
            height="100%",
            border_width=0,
        )
        self.set_caption("Kerys", icontitle="Kerys")
        self.set_icon(im.icon)
        self.set_fps(100000)
        self.set_default_size((1280, 750))
        bp.pygame.display.set_mode(self.default_size)
        bp.ressources.font.config(file="lib/fonts/Edson_Comics_Bold.ttf")
        bp.keyboard.set_repeat(400, 70)  # permet de creer une suite de KEYDOWN lorsque touche reste pressee


        self.grp_ter = [
            District("velocity_district1"),
            District("velocity_district2"),
            District("velocity_district3"),
        ]  # TODO : cities
        self._selected_district = self.grp_ter[0]

        self.player = Player()
        self.player.set_fighter_class(Ebuld)

        from display.scenes.MenuScene import MenuScene
        self.menu = MenuScene(self)

        from display.scenes.PlayScene import PlayScene
        self.playground = PlayScene(self)

        # self._focused_scene = self.playground

    selected_district = property(lambda self: self._selected_district)


if __name__ == '__main__':
    app = Kerys()
    app.launch()
