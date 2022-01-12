

import pymunk
import math
import baopig as bp
import lib.images as im
from physics.fighters.FighterBody import FighterBody, DynamicBody
from physics.fighters.FighterShape import FighterShape


def setattr_timer(owner, attr, val, delay):
    assert hasattr(owner, attr)
    return bp.Timer(delay, setattr, owner, attr, val)


def cpfclamp(f, min_, max_):
    """Clamp f between min and max"""
    return min(max(f, min_), max_)


def cpflerpconst(f1, f2, d):
    """Linearly interpolate from f1 to f2 by no more than d."""
    return f1 + cpfclamp(f2 - f1, -d, d)


class _FighterImages:
    """
    A list of images for animations
    """

    def __init__(self, fighter):

        source = getattr(im, fighter.__class__.__name__.lower()+"_sprite")

        assert source.get_height() % 4 == 0
        w = source.get_width()
        h = source.get_height() // 4

        color = fighter.color
        assert len(color) is 3
        color = (
            color[0] + 127,
            color[1] + 127,
            color[2] + 127,
            255
        )

        self.full = source.copy()
        self.list = tuple(self.full.subsurface(0, i*h, w, h) for i in range(4))
        self.rest = self.list[0]
        self.color = color

        inversed_color = tuple(255 - color[i] for i in range(4))
        for x in range(self.full.get_width()):
            for y in range(self.full.get_height()):
                color = self.full.get_at((x, y))
                if color[3] is 0:  # fully transparent pixel
                    continue
                if color[0] is 0:  # skip all black pixels
                    continue
                if color[0] == color[1] == color[2]:
                    self.full.set_at((x, y), (
                        min(255, max(0, color[0] - inversed_color[0])),
                        min(255, max(0, color[1] - inversed_color[1])),
                        min(255, max(0, color[2] - inversed_color[2])),
                        color[3]
                    ))


class DynamicBodyController:  # TODO : kill ?
    """
    A DynamicBodyController is a game object who have a center and a size
    It controls a DynamicBody and some shapes and sprites
    """
    def __init__(self, district, BodyClass, center, hitbox_size):

        assert issubclass(BodyClass, DynamicBody)

        self._center = pymunk.Vec2d(center)
        self._hitbox_size = hitbox_size
        # for efficient hitbox position calculations :
        self._width, self._height = self.hitbox_size
        self._midwidth = self.width / 2
        self._midheight = self.height / 2

        self._district = district
        self._body = BodyClass(self)

        self._clipped_inside_district = False

        # Fields to be initialized in subclass constructor
        self._shapes = None

    district = property(lambda self: self._district)
    body = property(lambda self: self._body)
    shapes = property(lambda self: self._body.shapes)
    isprites = property(lambda self: (shape.sprite for shape in self._shapes))
    sprites = property(lambda self: tuple(self.isprites))

    bottom = property(lambda self: self._center[1] + self._midheight)
    center = property(lambda self: self._center)
    centerx = property(lambda self: self._center[0])
    centery = property(lambda self: self._center[1])
    h = height = property(lambda self: self._height)
    hitbox_size = property(lambda self: self._hitbox_size)
    left = property(lambda self: self._center[0] - self._midwidth)
    midheight = property(lambda self: self._midheight)
    midwidth = property(lambda self: self._midwidth)
    right = property(lambda self: self._center[0] + self._midwidth)
    top = property(lambda self: self._center[1] - self._midheight)
    w = width = property(lambda self: self._width)

    def _update_pos_from_body(self):
        """Only called by DynamicBody.update_position()"""

        self._center = self.body.position

        if self._clipped_inside_district:
            dx = dy = 0
            # NOTE : because of using pygame.Rect value who are integers, sometimes, after the step_back,
            # the fighter's shape is still a very little out of the playground
            if self.left < 0:
                dx = - self.left
            elif self.right > self.district.width:
                dx = self.district.width - self.right
            if self.top < 0:
                dy = - self.top
            elif self.bottom > self.district.height:
                dy = self.district.height - self.bottom
                # self.touch_ground((0, -1))  # TODO : find another method
            if dx or dy:
                self.step_back(dx, dy)
                # self.body._step_back(dx, dy)
                # self._center = self.body.position

    def step_back(self, dx, dy):

        # absorb velocity, on normal vector
        self.body._step_back(dx, dy)
        self._update_pos_from_body()


class Fighter(DynamicBodyController):
    """
    A Fighter is a Player's selected game object who control a body, shapes and sprites
    """

    STATIC = 0
    WALKING = 1
    JUMPING = 2

    ACCELERATION_TIME = .17
    ROTATION_TIME = .1

    def __init__(self, player, district, id, center, speed=350, jump_height=170, max_jumps=1):

        self._player = player
        self._id = id
        self._color = district.get_color(self.id)
        self._images = _FighterImages(self)

        DynamicBodyController.__init__(self, district, FighterBody,
                                       center, self.images.rest.get_size())

        vertices = (
            (-self.midwidth, -self.midheight),
            (self.midwidth-1, -self.midheight),
            (self.midwidth-1, self.midheight-1),
            (-self.midwidth, self.midheight-1)
        )

        ebuld_shape = True
        if ebuld_shape:
            vertices = [
                (13, 0),
                (35, 0),
                (56, 22),
                (45, 44),
                (3, 44),
                (3, 30)
            ]
            midsize = pymunk.Vec2d(self.midwidth, self.midheight)
            for i, v in enumerate(vertices):
                vertices[i] = v - midsize

        self._shapes = [FighterShape(self, vertices)]# , FighterShape(self, vertices, offset=(100, 0))]

        self.district.space.add(self.body, *self.shapes)
        self._state = self.STATIC  # TODO

        self._direction = 0
        self._speed = speed
        self._jump_height = jump_height  # unit : pixels
        self._max_jumps = max_jumps
        self._remaining_jumps = self.max_jumps
        self._can_jump_in_air = True  # TODO (actually, a drop will not decrease remaining_jumps)
        self._want_to_jump = False  # able to jump when hit the ground if jump button is pressed 0.1 seconds before
        self._want_to_jump_reset_timer = bp.SetattrTimer(self, "_want_to_jump", False, .05)
        self._dash_force = 1000  # TODO : rename ?
        self._have_dashed = False

    can_dash = property(lambda self: not self._have_dashed)
    color = property(lambda self: self._color)
    dash_force = property(lambda self: self._dash_force)
    direction = property(lambda self: self._direction)
    id = property(lambda self: self._id)
    images = property(lambda self: self._images)
    jump_height = property(lambda self: self._jump_height)
    max_jumps = property(lambda self: self._max_jumps)
    player = property(lambda self: self._player)
    remaining_jumps = property(lambda self: self._remaining_jumps)
    speed = property(lambda self: self._speed)

    def _update_direction(self):

        self._direction = bp.keyboard.is_pressed(bp.keyboard.d) - bp.keyboard.is_pressed(bp.keyboard.q)  # TODO : "q"

    def handle_keydown(self, key):
        """Receive every keydown caught by PlaygroundScene"""
        print(key)

        if key is bp.keyboard.z:  # TODO : solve : keep the jump pressed and then move left will quit the UP repeat
            if self.remaining_jumps > 0:
                self.jump()
            else:
                self._want_to_jump_reset_timer.cancel()
                self._want_to_jump = True
                self._want_to_jump_reset_timer.start()
                # delayed_setattr(self, "_want_to_jump", False, delay=.1)  # Warning : must be canceled 2 lines before

        elif key is bp.keyboard.s:
            if self.can_dash:
                # TODO : solve : can go through bricks
                # self.body.velocity = pymunk.Vec2d(self.body.velocity.x, 0)

                jump_v = math.sqrt(2.0 * self.dash_force * abs(self.body.space.gravity.y))
                impulse = (0, self.body.mass * jump_v - self.body.velocity.y)
                self.body.velocity = (0, 0)  # TODO : lock movements
                self.body.disable_gravity()
                def dash():
                    self.body.enable_gravity()
                    self.body.apply_impulse_at_local_point(impulse)
                bp.Timer(.1, dash).start()
                self._have_dashed = True

        elif key in (bp.keyboard.q, bp.keyboard.d):
            self._update_direction()

        elif key is bp.keyboard.j:
            self.rotate(90)
        elif key is bp.keyboard.k:
            self.rotate(-90)

        elif key is bp.keyboard.g:
            self.body.position = self.district.w / 2, self.district.h / 2

    def handle_keyup(self, key):
        """Receive every keyup caught by PlaygroundScene"""

        if bp.debug_with_assert:
            try:
                assert not bp.keyboard.is_pressed(key)
            except AssertionError as e:
                raise e
        if key in (bp.keyboard.q, bp.keyboard.d):
            self._update_direction()

    def jump(self):

        assert self.remaining_jumps > 0, self.remaining_jumps
        jump_v = math.sqrt(2.0 * self.jump_height * abs(self.body.space.gravity.y))
        impulse = self.body.up_norm * jump_v
        self.body.velocity = self.body.velocity.projection(self.body.left_norm) + impulse
        self._remaining_jumps -= 1
        self._want_to_jump = False  # TODO : Correct ?

        if self.district.painter.debug_jumps:
            l = bp.Line(self.district.painter, (255, 255, 0),
                        (0, 0), - impulse * self.body.space.dt, 5,
                        offset=self.body.position)
            bp.Timer(1, l.kill).start()

    def kill(self):  # TODO : difference between kill from close PlayScene and kill from damages ?

        self.player.delete_fighter()

    def rotate(self, angle_degrees):

        self.body.rotate_degrees(angle_degrees)

    def step_back(self, dx, dy):

        super().step_back(dx, dy)
        ground_norm = pymunk.Vec2d(dx, dy).normalized()
        if self.body.up_norm.dot(ground_norm) > .001:
            self.touch_ground(ground_norm)

    def touch_ground(self, ground_norm):
        """To be called when the player is touching a ground with an normal.y < 0"""
        self._remaining_jumps = self.max_jumps
        self._have_dashed = False

        if False:
            delta = self.body.up_norm.angle - ground_norm.angle
            if abs(delta) > 1e-9:
                delta = (delta + math.pi / 2) % math.pi - math.pi / 2
                delta = cpfclamp(delta, -Fighter.ROTATION_TIME, Fighter.ROTATION_TIME)
                self.body.required_rotation_angle += delta

        if self._want_to_jump:
            self.jump()

