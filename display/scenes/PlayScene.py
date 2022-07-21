

import baopig as bp
from display.scenes.Scene import Scene
from display.DistrictPainter import DistrictPainter
import lib.images as im
from control.fighters import *


# TODO : try to kill a scene


class PlayScene(Scene, bp.Runable):

    def __init__(self, app):

        Scene.__init__(self, app, MainZone=DistrictPainter)
        bp.Runable.__init__(self, self)
        self.district_painter = self.main_zone
        self.district = app.selected_district
        self.player = app.player

        self.menu_dialog = bp.Dialog(
            self.application,
            title="Quit the current game ?",
            choices=("Cancel", "Yes"),
            description="If you quit now, you won't be able to quit later, be aware of that",
            default_choice_index=1,
        )
        self.application._focused_scene = self  # TODO : find a way to solve this problem
        # Problem : the previous dialog is added to the app before this scene,
        # so the dialog is considered as the main scene

        def go_menu(ans):
            if ans == "Yes":
                app.open("MenuScene")
        self.menu_dialog.signal.ANSWERED.connect(go_menu, owner=None)
        bp.Button(self.buttons_zone, "MENU", pos=(30, 30), command=self.menu_dialog.open)

        def swap_bck():
            self.main_zone.i += 1
            self.main_zone.i %= len(im.wallpapers)
            self.main_zone.set_background_image(im.wallpapers[self.main_zone.i], background_adapt=True)
            self.district.blit_bricks()
        bp.Button(self.buttons_zone, "Swap background", pos=(30, 80), command=swap_bck)

        def swap_class():
            classes = (Kocci, Ebuld, Royal, Ytrei, Sabul)
            old_fighter = self.fighter
            self.player.set_fighter_class(classes[(classes.index(self.player.fighter_class)+1)%len(classes)])
            self.player.delete_fighter()
            self.district.create_fighter(self.player, midbottom=old_fighter.hitbox.midbottom)
        bp.Button(self.buttons_zone, "Swap class", pos=(30, 130), command=swap_class)

        class ResetButton(bp.Button):
            STYLE = bp.Button.STYLE.substyle()
            STYLE.modify(
                width=10,
                height=15,
                background_color=(0, 50, 50),
                background_image=None,
                link_class=bp.Button_LinkSail,
            )

        def set_reset_button(slider):
            reset = ResetButton(self.buttons_zone, pos=(slider.rect.left - 10, slider.rect.top),
                                command=slider.reset, focus=-1)
            bp.Indicator(reset, text="reset")

        self.set_style_for(bp.SliderBloc, wideness="100%", border_width=0, color="green4")
        self.set_style_for(bp.Slider, length=130, wideness=15)

        # TODO : CheckBox : Infinite fps
        # bp.debug_with_assert

        # STEPS PER SECOND
        self.dt_input = bp.Slider(
            self.buttons_zone,
            minval=1, maxval=100, step=1, title="steps per second",
            pos=(40, 200)
        )
        self.dt_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.district, "dt", 1 / val), owner=None
        )
        set_reset_button(self.dt_input)

        # TIME ACCELERATION
        self.dt_coeff_input = bp.Slider(  # TODO : step
            self.buttons_zone,
            minval=.01, maxval=3, step=.01, defaultval=1, title="time acceleration",
            pos=(40, self.dt_input.rect.bottom + 10)
        )
        self.dt_coeff_input.signal.NEW_VAL.connect(
            lambda val: self.district._step_timer.set_interval(self.district.dt / val), owner=None
        )
        self.dt_input.signal.NEW_VAL.connect(
            lambda val: self.district._step_timer.set_interval(1 / (val * self.dt_coeff_input.val)), owner=None
        )
        set_reset_button(self.dt_coeff_input)

        # GRAVITY
        self.gravity_input = bp.Slider(
            self.buttons_zone,
            minval=0, maxval=10, title="gravity",
            pos=(40, self.dt_coeff_input.rect.bottom + 10)
        )
        set_reset_button(self.gravity_input)
        self.gravity_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.district.gravity, "y", val), owner=None
        )

        # ACCELERATION TIME
        from control.fighters.Fighter import Fighter
        self.acceleration_input = bp.Slider(
            self.buttons_zone,
            minval=.001, maxval=3, defaultval=Fighter.ACCELERATION_TIME,
            title="acceleration",
            pos=(40, self.gravity_input.rect.bottom + 10)
        )
        set_reset_button(self.acceleration_input)
        self.acceleration_input.signal.NEW_VAL.connect(
            lambda val: setattr(Fighter, "ACCELERATION_TIME", val), owner=None
        )

        # MAIN FIGHTER SPEED
        self.speed_input = bp.Slider(
            self.buttons_zone,
            minval=0, maxval=16, title="speed",
            pos=(40, self.acceleration_input.rect.bottom + 10)
        )
        self.speed_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.fighter, "_speed", val) or \
                        self.fighter._sprite_animator.set_interval(.3 / self.fighter.speed), owner=None
        )
        set_reset_button(self.speed_input)

        # MAIN FIGHTER JUMP HEIGHT
        self.jump_input = bp.Slider(
            self.buttons_zone,
            minval=0, maxval=600, title="jump height",
            pos=(40, self.speed_input.rect.bottom + 10)
        )
        self.jump_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.fighter, "_jump_height", val), owner=None
        )
        set_reset_button(self.jump_input)

        # MAIN FIGHTER DASH FORCE
        self.dashforce_input = bp.Slider(
            self.buttons_zone,
            minval=0, maxval=1000, title="dashforce",
            pos=(40, self.jump_input.rect.bottom + 10)
        )
        self.dashforce_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.fighter, "_dash_force", val), owner=None
        )
        set_reset_button(self.dashforce_input)

    fighter = property(lambda self: self.player.fighter)

    def handle_scene_open(self):

        if not self.district.is_open:
            self.district.open(painter=self.district_painter)
            self.dt_input.set_defaultval(1 / self.district.dt)
            self.gravity_input.set_defaultval(self.district.gravity.y)
            self.speed_input.set_defaultval(self.player.fighter.speed)
            self.jump_input.set_defaultval(self.player.fighter.jump_height)
            self.dashforce_input.set_defaultval(self.player.fighter.dash_force)

    def handle_event(self, event):

        if self.district.is_paused:
            return  # TODO : better way ?

        if event.type == bp.KEYDOWN:
            self.fighter.handle_keydown(event.key)
            if bp.keyboard.mod.cmd:
                if event.key is bp.K_w:
                    self.district_painter.toggle_debug_shapes()
                elif event.key is bp.K_x:
                    self.district_painter.debug_collisions = not self.district_painter.debug_collisions
                elif event.key is bp.K_c:
                    self.district_painter.debug_boundary_stepback = not self.district_painter.debug_boundary_stepback
                elif event.key is bp.K_v:
                    self.district_painter.debug_jumps = not self.district_painter.debug_jumps
        elif event.type == bp.KEYUP:
            self.fighter.handle_keyup(event.key)

    def run(self):

        self.district.run()
