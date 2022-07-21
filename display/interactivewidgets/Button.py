

import baopig as bp
import lib.images as im


class Button_LinkImage(bp.Image):

    def __init__(self, textbutton):

        bp.Image.__init__(self, textbutton, image=im.textbutton_link, visible=False, layer=textbutton.behind_content)

        def move_text(dy):
            self.parent.text_widget.move(dy=dy)
            if dy > 0:
                self.parent.background_image.hide()
            else:
                self.parent.background_image.show()
        self.signal.SHOW.connect(bp.PrefilledFunction(move_text, dy=3), owner=self)
        self.signal.HIDE.connect(bp.PrefilledFunction(move_text, dy=-3), owner=self)


class Button_FocusImage(bp.Image):

    def __init__(self, textbutton):

        bp.Image.__init__(self, textbutton, image=im.textbutton_focus, visible=False, layer=textbutton.behind_content)


class PlayPauseButton_LinkImage(bp.Image):

    def __init__(self, textbutton):

        bp.Image.__init__(self, textbutton, image=im.play_press, visible=False, layer=textbutton.behind_content)


class PlayPauseButton(bp.Button):
    STYLE = bp.Button.STYLE.substyle()
    STYLE.modify(
        width=im.pause.get_width(),
        height=im.pause.get_width(),
        background_color=(0, 0, 0, 0),
        background_image=im.play_bck,
        focus_class=None,
        hover_class=bp.Button_HoverSail,
        link_class=PlayPauseButton_LinkImage,
    )

    def __init__(self, parent, pos, **options):

        bp.Button.__init__(
            self, parent,
            pos=pos,
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

        district = self.parent.district
        if self.is_paused:
            district.resume()
            self.current = self.pause
        else:
            district.pause()
            self.current = self.play

    is_paused = property(lambda self: self.parent.district.is_paused)
