

# import pymunk
import baopig as bp
from display.interactivewidgets.Button import TextButton
# from display.interactivewidgets.Dialog import Dialog
from display.scenes.Scene import Scene
from display.DistrictPainter import DistrictPainter
import lib.images as im
from control.fighters import *
import pygame


# TODO : try to kill a scene


class PlayScene(Scene):

    def __init__(self, app):

        Scene.__init__(self, app, MainZone=DistrictPainter)
        self.district_painter = self.main_zone
        self.district = bp.get_application().selected_district
        self.player = bp.get_application().player

        self.menu_dialog = bp.Dialog(
            self.application,
            title="Quit the current game ?",
            choices=("Cancel", "Yes"),
            description="If you quit now, you won't be able to quit later, be aware of that",
            index_default_choice=1,
            background_image=im.dialog_background,
        )
        def go_menu(ans):
            if ans == "Yes":
                bp.get_application().open("MenuScene")
        self.menu_dialog.signal.ANSWERED.connect(go_menu)
        TextButton(self.buttons_zone, "MENU", pos=(30, 30), command=self.menu_dialog.open)

        def swap_bck():
            self.main_zone.i += 1
            self.main_zone.i %= len(im.wallpapers)
            self.main_zone.set_background_image(im.wallpapers[self.main_zone.i], background_adapt=True)
        TextButton(self.buttons_zone, "Swap background", pos=(30, 80), command=swap_bck)

        def swap_class():
            classes = (Kocci, Ebuld, Royal, Ytrei, Sabul)
            old_fighter = self.fighter
            self.player.set_fighter_class(classes[(classes.index(self.player.fighter_class)+1)%len(classes)])
            self.player.delete_fighter()
            self.district.create_fighter(self.player, center=old_fighter.center)
        TextButton(self.buttons_zone, "Swap class", pos=(30, 130), command=swap_class)

        class ResetButton(bp.Button): pass
        self.set_style_for(
            ResetButton,
            width=10,
            height=15,
            background_color=(0, 50, 50),
            background_image=None,
        )
        def set_reset_button(slider):
            reset = ResetButton(self.buttons_zone, pos=(slider.x-10, slider.y),
                               command=slider.reset, focus=-1)
            reset.set_indicator(text="reset")
        slider_size = (130, 15)

        # TODO : CheckBox : Infinite fps
        # bp.debug_with_assert

        # STEPS PER SECOND
        self.dt_input = bp.Slider(
            self.buttons_zone, bar_size=slider_size,
            minval=1, maxval=100, step=1, title="steps per second",
            pos=(40, 200)
        )
        self.dt_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.district.space, "dt", 1 / val)
        )
        set_reset_button(self.dt_input)

        # TIME ACCELERATION
        self.dt_coeff_input = bp.Slider(  # TODO : step
            self.buttons_zone, bar_size=slider_size,
            minval=.01, maxval=3, step=.01, defaultval=1, title="time acceleration",
            pos=(40, self.dt_input.bottom + 10)
        )
        self.dt_coeff_input.signal.NEW_VAL.connect(
            lambda val: self.district.space._step_timer.set_interval(self.district.space.dt / val)
        )
        self.dt_input.signal.NEW_VAL.connect(
            lambda val: self.district.space._step_timer.set_interval(1 / (val * self.dt_coeff_input.val))
        )
        set_reset_button(self.dt_coeff_input)

        # GRAVITY
        self.gravity_input = bp.Slider(
            self.buttons_zone, bar_size=slider_size,
            minval=1, maxval=10000, title="gravity",
            pos=(40, self.dt_coeff_input.bottom + 10)
        )
        set_reset_button(self.gravity_input)
        self.gravity_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.fighter.body.gravity, "length", val)
        )

        # ACCELERATION TIME
        from control.fighters.Fighter import Fighter
        self.acceleration_input = bp.Slider(
            self.buttons_zone, bar_size=slider_size,
            minval=.001, maxval=3, defaultval=Fighter.ACCELERATION_TIME,
            title="acceleration",
            pos=(40, self.gravity_input.bottom + 10)
        )
        set_reset_button(self.acceleration_input)
        self.acceleration_input.signal.NEW_VAL.connect(
            lambda val: setattr(Fighter, "ACCELERATION_TIME", val)
        )

        # ROTATION TIME
        self.rotation_input = bp.Slider(
            self.buttons_zone, bar_size=slider_size,
            minval=0, maxval=.2, defaultval=Fighter.ROTATION_TIME,
            step=.0001, title="rotation speed",
            pos=(40, self.acceleration_input.bottom + 10)
        )
        set_reset_button(self.rotation_input)
        self.rotation_input.signal.NEW_VAL.connect(
            lambda val: setattr(Fighter, "ROTATION_TIME", val)
        )

        # MAIN FIGHTER SPEED
        self.speed_input = bp.Slider(
            self.buttons_zone, bar_size=slider_size,
            minval=0, maxval=800, title="speed",
            pos=(40, self.rotation_input.bottom + 10)
        )
        self.speed_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.fighter, "_speed", val)
        )
        set_reset_button(self.speed_input)

        # MAIN FIGHTER JUMP HEIGHT
        self.jump_input = bp.Slider(
            self.buttons_zone, bar_size=slider_size,
            minval=0, maxval=600, title="jump height",
            pos=(40, self.speed_input.bottom + 10)
        )
        self.jump_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.fighter, "_jump_height", val)
        )
        set_reset_button(self.jump_input)

        # MAIN FIGHTER DASH FORCE
        self.dashforce_input = bp.Slider(
            self.buttons_zone, bar_size=slider_size,
            minval=0, maxval=100000, title="dashforce",
            pos=(40, self.jump_input.bottom + 10)
        )
        self.dashforce_input.signal.NEW_VAL.connect(
            lambda val: setattr(self.fighter, "_dash_force", val)
        )
        set_reset_button(self.dashforce_input)

        # NOT IMPLEMENTED, WILL NOT BE
        self.bricksfiction_input = bp.Slider(
            self.buttons_zone, bar_size=slider_size,
            minval=0, maxval=1.5, step=.01, defaultval=1, title="bricks friction",
            pos=(40, self.dashforce_input.bottom + 10)
        )
        def set_bricksfriction(val):
            for boundary in self.district.space.static_body.shapes:
                boundary.friction = val
                print(boundary, boundary.friction)
        self.bricksfiction_input.signal.NEW_VAL.connect(set_bricksfriction)
        set_reset_button(self.bricksfiction_input)

        # TODO : Acceleration time

        # bp.TextEdit(self.buttons_zone, pos=(40, self.bricksfiction_input.bottom + 10), max_width=140)

    fighter = property(lambda self: self.player.fighter)

    def open(self):

        self.district.open(painter=self.district_painter)
        self.dt_input.set_defaultval(1 / self.district.space.dt)
        self.gravity_input.set_defaultval(self.fighter.body.gravity.length)
        self.speed_input.set_defaultval(self.player.fighter.speed)
        self.jump_input.set_defaultval(self.player.fighter.jump_height)
        self.dashforce_input.set_defaultval(self.player.fighter.dash_force)
        # self.resize(*self.district_painter.bottomright)

    def receive(self, event):
        print(event, event.type, pygame.KEYDOWN)
        if event.type == 768:
            print(event.key)
            self.fighter.handle_keydown(event.key)

        if self.district.space.is_paused: return  # TODO : better way ?

        if event.type is bp.keyboard.KEYDOWN:
            if bp.keyboard.mod.cmd:
                if event.key is bp.keyboard.w:
                    self.district_painter.toggle_debug_shapes()
                elif event.key is bp.keyboard.x:
                    self.district_painter.debug_collisions = not self.district_painter.debug_collisions
                elif event.key is bp.keyboard.c:
                    self.district_painter.debug_boundary_stepback = not self.district_painter.debug_boundary_stepback
                elif event.key is bp.keyboard.v:
                    self.district_painter.debug_jumps = not self.district_painter.debug_jumps
        elif event.type is bp.keyboard.KEYUP:
            self.fighter.handle_keyup(event.key)

