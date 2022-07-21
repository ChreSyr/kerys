

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))  # executable from console
# import sys
# sys.path.insert(0, 'C:\\Users\\symrb\\Documents\\python\\baopig')
import baopig as bp
import lib.images as im
from control.District import District
from control.Player import Player
from control.fighters import *
from display.interactivewidgets.Button import Button_FocusImage, Button_LinkImage

# TODO : set the host player id to 0


theme = bp.Theme()
theme.set_style_for(bp.Text, font_file="lib\\fonts\\Edson_Comics_Bold.ttf")
theme.set_style_for(
    bp.Button,
    width=140,
    height=40,
    background_color=(0, 0, 0, 0),
    background_image=im.textbutton_bck,
    focus_class=Button_FocusImage,
    hover_class=None,
    link_class=Button_LinkImage,
    padding=(20, 4, 20, 8),
    text_style={"font_height": 28, "pos": (0, -2)},
)
theme.set_style_for(bp.DialogFrame, background_color=(0, 0, 0, 0), background_image=im.dialog_background,
                    width=im.dialog_background.get_width(), height=im.dialog_background.get_height())


class Kerys(bp.Application):

    def __init__(self):

        bp.Application.__init__(self, size=(1280, 750), theme=theme)
        self.set_caption("Kerys", icontitle="Kerys")
        self.set_icon(im.icon)
        bp.keyboard.set_repeat(400, 70)  # permet de creer une suite de KEYDOWN lorsque touche reste pressee

        self.grp_ter = [
            District("velocity_district1"),
            # District("velocity_district2"),
            # District("velocity_district3"),
        ]  # TODO : cities
        self._selected_district = self.grp_ter[0]

        self.player = Player()
        self.player.set_fighter_class(Ebuld)

        # TODO : place after the MenuScene
        from display.scenes.PlayScene import PlayScene
        self.playground = PlayScene(self)

        from display.scenes.MenuScene import MenuScene
        self.menu = MenuScene(self)

        # self._focused_scene = self.playground

    selected_district = property(lambda self: self._selected_district)


if __name__ == '__main__':
    Kerys().launch()
