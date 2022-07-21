

import math
import baopig as bp
import lib.images as im
from control.physics import Body
from display.sprites.FighterSprite import FighterSprite


class _FighterImages:
    """
    A list of images for animations
    """

    def __init__(self, fighter):

        source = im.fighters[fighter.__class__.__name__.lower()]

        assert source.get_height() % 4 == 0
        w = source.get_width()
        h = source.get_height() // 4

        color = fighter.color
        assert len(color) == 3
        color = (
            color[0] + 127,
            color[1] + 127,
            color[2] + 127,
            255
        )

        self.fighter = fighter
        self.full = source.copy()
        self.color = color

        inversed_color = tuple(255 - color[i] for i in range(4))
        for x in range(self.full.get_width()):
            for y in range(self.full.get_height()):
                color = self.full.get_at((x, y))
                if color[3] == 0:  # fully transparent pixel
                    continue
                if color[0] == 0:  # skip all black pixels
                    continue
                if color[0] == color[1] == color[2]:
                    self.full.set_at((x, y), (
                        min(255, max(0, color[0] - inversed_color[0])),
                        min(255, max(0, color[1] - inversed_color[1])),
                        min(255, max(0, color[2] - inversed_color[2])),
                        color[3]
                    ))

        self.list = [tuple(self.full.subsurface(0, i*h, w, h) for i in range(4))]
        self.list.append(tuple(bp.transform.flip(self.list[0][i], flip_x=True, flip_y=False) for i in range(4)))
        self.rest = self.list[0][0]

    def get(self):

        if self.fighter.direction > 0:
            list = self.list[0]
        elif self.fighter.direction < 0:
            list = self.list[1]
        elif self.fighter._olddirection > 0:
            list = self.list[0]
        elif self.fighter._olddirection < 0:
            list = self.list[1]
        else:  # left and right keys are pressed together
            return self.fighter.sprite.surface

        return list[self.fighter._sprite_index]


class Fighter(Body):

    HITBOX_MARGINS = (0, 0, 0)

    ACCELERATION_TIME = .17

    def __init__(self, player, district, id, midbottom, speed=8, jump_height=170, max_jumps=2):

        self._color = district.get_color(id)
        self._images = _FighterImages(self)
        hitbox = bp.Rect(0, 0, 64, 64)
        hitbox.width -= self.HITBOX_MARGINS[0] * 2
        hitbox.height -= self.HITBOX_MARGINS[1]
        hitbox.midbottom = midbottom
        Body.__init__(self, hitbox)
        district.add(self)

        self._player = player
        self._id = id
        self._district = district
        self._speed = speed
        self._jump_height = jump_height  # unit : pixels
        self._max_jumps = max_jumps
        self._remaining_jumps = self.max_jumps
        self._can_jump_in_air = True  # TODO (actually, a drop will not decrease remaining_jumps)
        self._want_to_jump = False  # able to jump when hit the ground if jump button is pressed 0.1 seconds before
        self._want_to_jump_reset_timer = bp.SetattrTimer(self, "_want_to_jump", False, .05)
        self._dash_force = 750
        self._have_dashed = False
        self.accel_coef = 1

        self._sprite = FighterSprite(self)
        self._sprite_index = 0
        self._direction = 0
        self._olddirection = 0
        self._is_walking = False  # if q or s is pressed
        def next_sprite_index():
            self._sprite_index = (self._sprite_index + 1) % 4
            self._sprite.send_paint_request()
        self._sprite_animator = bp.RepeatingTimer(.3 / self.speed, next_sprite_index)

    can_dash = property(lambda self: (not self._have_dashed) and self._airstate == self.IN_THE_AIR)
    color = property(lambda self: self._color)
    dash_force = property(lambda self: self._dash_force)
    dashing = property(lambda self: self._have_dashed and self._airstate == self.IN_THE_AIR)
    direction = property(lambda self: self._direction)
    district = property(lambda self: self._district)
    id = property(lambda self: self._id)
    images = property(lambda self: self._images)
    jump_height = property(lambda self: self._jump_height)
    max_jumps = property(lambda self: self._max_jumps)
    player = property(lambda self: self._player)
    remaining_jumps = property(lambda self: self._remaining_jumps)
    speed = property(lambda self: self._speed)
    sprite = property(lambda self: self._sprite)

    def _update_direction(self):

        self._olddirection = self._direction
        self._direction = bp.keyboard.is_pressed(bp.K_d) - bp.keyboard.is_pressed(bp.K_q)
        if self._direction != 0:
            self._is_walking = True

    def _handle_new_airstate(self, airstate):

        if airstate == Body.ON_THE_GROUND:
            self._remaining_jumps = self._max_jumps
            self._have_dashed = False
            if bp.keyboard.is_pressed(bp.K_z):
                self.jump()
        else:
            if self._remaining_jumps == self._max_jumps:
                self._remaining_jumps -= 1

    def _handle_new_walkstate(self, walkstate):

        if walkstate == self.STATIONNARY:
            self._sprite_index = 0
            self._sprite_animator.cancel()
        else:
            self._sprite_animator.start()
        self._sprite.send_paint_request()

    def handle_keydown(self, key):
        """Receive every keydown caught by PlaygroundScene"""

        if key is bp.K_z:
            if self.remaining_jumps > 0:
                self.jump()
            else:
                self._want_to_jump_reset_timer.cancel()
                self._want_to_jump = True
                self._want_to_jump_reset_timer.start()

        elif key is bp.K_s:
            if self.can_dash:
                jump_v = math.sqrt(2.0 * self.dash_force * abs(self.district.gravity.y))
                impulse = (0, jump_v - self.velocity.y)
                self.velocity = bp.Vector2(0, 0)
                self.gravitable = False  # litle freeze in the air
                def dash():
                    self.gravitable = True
                    self.apply_force(impulse)
                bp.Timer(.1, dash).start()
                self._have_dashed = True

        elif key in (bp.K_q, bp.K_d):
            self._update_direction()

        elif key == bp.K_g:  # If problem, # TODO : remove when stable
            self.hitbox.center = self.district.w / 2, self.district.h / 2

    def handle_keyup(self, key):
        """Receive every keyup caught by PlaygroundScene"""

        if key in (bp.K_q, bp.K_d):
            self._update_direction()
        elif key == bp.K_q:
            self._update_direction()
        elif key == bp.K_d:
            self._update_direction()

    def jump(self):

        assert self.remaining_jumps > 0, self.remaining_jumps
        jump_strengh = math.sqrt(2.0 * self.jump_height * self.district.gravity.y)
        self.velocity.y = - jump_strengh
        self.acceleration.y = 0
        self._remaining_jumps -= 1
        self._want_to_jump = False  # TODO : Correct ?

    def kill(self):  # TODO : difference between kill from close PlayScene and kill from damages ?

        self.player.delete_fighter()
