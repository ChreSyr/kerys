

import baopig as bp
from display.interactivewidgets.Button import TextButton
from display.scenes.Scene import Scene


class MenuScene(Scene):

    def __init__(self, app):

        Scene.__init__(self, app)

        TextButton(self.buttons_zone, "JOUER", pos=(30, 30), command=lambda: bp.get_application().open("PlayScene"))
        TextButton(self.buttons_zone, "MODIFIER", pos=(30, 80), command=lambda: bp.get_application().open("maping"))
        TextButton(self.buttons_zone, "MINI JEUX", pos=(30, 130), command=lambda: bp.get_application().open("mini"))
        TextButton(self.buttons_zone, "QUITTER", pos=(30, 180), command=bp.get_application().exit)

        scroller = bp.Zone(self.main_zone, size=(100, 200))
