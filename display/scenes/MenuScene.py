

import baopig as bp
from display.scenes.Scene import Scene


class MenuScene(Scene):

    def __init__(self, app):

        Scene.__init__(self, app)

        bp.Button(self.buttons_zone, "JOUER", pos=(30, 30), command=lambda: app.open("PlayScene"))
        bp.Button(self.buttons_zone, "MODIFIER", pos=(30, 80))
        bp.Button(self.buttons_zone, "MINI JEUX", pos=(30, 130))
        bp.Button(self.buttons_zone, "QUITTER", pos=(30, 180), command=app.exit)

        scroller = bp.Zone(self.main_zone, size=(100, 200))
