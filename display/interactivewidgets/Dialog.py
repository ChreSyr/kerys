

import baopig as bp
import lib.images as im
from .Button import TextButton


class DialogButton(TextButton):

    def validate(self):

        self.command(self.text_component.text)


class Dialog(bp.SubZone):

    def __new__(cls, *args, **kwargs):

        dialog = super().__new__(cls)
        Dialog.__init__(dialog, *args, **kwargs)
        answer = dialog.ask()
        dialog.kill()
        return answer

    def __init__(self, scene, title, description, choices):

        # TODO : solve : transparent background don't work -> see content corners

        assert isinstance(scene, bp.Scene)
        if bp.get_application().focused_scene is not scene:
            raise PermissionError("A Dialog must be open in the focused scene")

        bp.SubZone.__init__(self, scene, scene.size, pos=(0, 0))
        self.content = bp.SubZone(self, background=im.dialog_background,
                                  origin=bp.Origin(pos=("50%", "35%"), location="center"))
        title = bp.Text(self.content, title, font_height=38,
                        origin=bp.Origin(pos=("50%", 40), location="center"))
        description = bp.Text(self.content, description, font_height=27, pos=(30, title.bottom + 15),
                              max_width=self.content.w-60)

        def plus(l1, l2):
            print(tuple(l1[i] + l2[i] for i in range(len(l1))))
            return tuple(l1[i] + l2[i] for i in range(len(l1)))
        buttons_zone = bp.SubZone(self.content, size=(self.content.w-60, 46 * ((len(choices)-1)//3+1)),
                                  pos=(0, -30), sticky="bottom",
                                  background_color=plus((0, 0, 0, -70),
                                                        self.content.background.surface.get_at(
                                                            self.content.auto.center)))
        grid = bp.GridLayer(buttons_zone, nbrows=(len(choices)-1)//3+1, nbcols=min(len(choices), 3),
                            row_height=46, col_width=int(buttons_zone.w / min(len(choices), 3)))
        for i, choice in enumerate(choices):
            DialogButton(buttons_zone, choice, col=i % 3, row=i // 3, layer=grid, sticky="center",
                         command=lambda ans: setattr(self, "answer", ans))
        scene.parent._focus(grid[0])

        self.answer = None

    def ask(self):

        kerys = bp.get_application()
        background = kerys.display.copy()
        sail = bp.Surface(kerys.size, bp.SRCALPHA)
        sail.fill((0, 0, 0, 50))
        background.blit(sail, (0, 0))
        self.set_background(background)
        def answered():
            kerys._manage_events()
            self.container_paint()
            return self.answer is not None
        kerys.freeze(until=answered)

        """self.i = 0
        def f_is_pressed():
            if self.i == 0:
                self.surface.fill((0, 0, 255))
                self.i = 1
            for event in bp.event.get():
                if event.type is bp.keyboard.KEYDOWN:
                    if event.key is bp.keyboard.F6:
                        kerys.exit("Pressed F6")
                    elif event.key is bp.keyboard.f:
                        return True
                    elif event.key is bp.keyboard.ESCAPE:  # quit fullscreen or exit
                        if kerys.is_fullscreen:
                            kerys.exit_fullscreen()
                        else:
                            kerys.exit("pressed ESCAPE")
                    elif event.key is bp.keyboard.F5:  # fullscreen
                        kerys.focused_scene.toggle_fullscreen()
                    elif event.key is bp.keyboard.F4:  # minimize
                        kerys.iconify()
                    elif event.key is bp.keyboard.F3:  # refresh
                        kerys.refresh()
                        bp.LOGGER.info("Display refreshed")
                    elif event.key is bp.keyboard.F2:  # screenshot TODO : A faire avec un clic droit
                        kerys.painter.screenshot()
                        bp.LOGGER.info("Screenchot !")
            return False
        kerys.freeze(until=f_is_pressed)
        self.content.paint()
        print("Dialog must be hidden")
        kerys.freeze(until=f_is_pressed)"""

        return self.answer
