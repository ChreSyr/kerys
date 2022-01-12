

import baopig as bp
import lib.images as im


class TextButton(bp.Button):

    STYLE = bp.Button.STYLE.substyle()
    STYLE.modify(
        width=140,
        height=40,
        background_color=(0, 0, 0, 0),
        padding=(20, 4, 20, 8),
        text_style={"font_height": 28, "pos": (0, -2)},
    )

    def __init__(self, parent, text, **kwargs):

        bp.Button.__init__(
            self,
            parent,
            text,
            background_image=im.textbutton_bck,
            hover=-1,
            link=im.textbutton_link,
            focus=im.textbutton_focus,
            **kwargs
        )

    def press(self):

        with bp.paint_lock:
            self.text_widget.y += 3
            self.background.hide()
            self.link_sail.show()

    def unpress(self):

        with bp.paint_lock:
            self.text_widget.y -= 3
            self.background.show()
            self.link_sail.hide()


class PlayPauseButton(bp.Button):

    def __init__(self, parent, pos, **options):


        bp.Button.__init__(
            self, parent,
            pos=pos, background_image=im.play_bck,
            background_color=(0, 0, 0, 0),
            link=im.play_press, focus=-1, hover=30,
            size=im.pause.get_size(),
            **options
        )
        content_layer = bp.Layer(self, bp.Image, weight=self.default_layer.weight + 1)
        self.pause = bp.Image(self, im.pause, layer=content_layer)
        self.play = bp.Image(self, im.play, layer=content_layer)
        self.splash = bp.Image(self, im.play_splash[0], layer=content_layer)
        # self.splash_i = 0
        # def animate_splash():
        #     self.splash_i += 1
        #     print(self.splash_i, im.play_splash)
        #     self.splash.set_surface(im.play_splash[self.splash_i])
        #     if self.splash_i < 2:
        #         self.splash_animator.start()
        # self.splash_animator = bp.Timer(.05, animate_splash)

        self.current = self.pause
        self.play.hide()
        self.splash.hide()

    def press(self):

        with bp.paint_lock:
            self.current.hide()
            self.splash.show()
        # self.splash_i = 0
        # self.splash_animator.start()

    def unpress(self):

        with bp.paint_lock:
            # self.splash_animator.cancel()
            # self.splash_i = 0
            # self.splash.set_surface(im.play_splash[0])
            self.splash.hide()
            self.current.show()

    def validate(self):

        space = self.parent.district.space
        if self.is_paused:
            space.resume()
            self.current = self.pause
        else:
            space.pause()
            self.current = self.play

    is_paused = property(lambda self: self.parent.district.space.is_paused)
