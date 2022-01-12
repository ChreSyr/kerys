

import pymunk
import baopig as bp
from control.fighters.Fighter import Fighter
from .collisions import COLLTYPE_BOUNDARY, COLLTYPE_FIGHTER
from .collisions import abort_collision_poly_boundary
from .Boundary import Boundary


def round_vec(vec):
    return round(vec[0] * 100000) / 100000, round(vec[1] * 100000) / 100000


def cpfclamp(f, min_, max_):
    """Clamp f between min and max"""
    return min(max(f, min_), max_)


def cpflerpconst(f1, f2, d):
    """Linearly interpolate from f1 to f2 by no more than d."""
    return f1 + cpfclamp(f2 - f1, -d, d)


class DistrictSpace(pymunk.Space, bp.Runable):

    def __init__(self, district):

        pymunk.Space.__init__(self)

        self.gravity = 0, 3000
        # self.damping = 1
        self.dt = 1 / 30  # produces 30 steps per second

        self._district = district
        self._painter_ref = district.painter.get_weakref()

        rect = self.district.wallpaper.get_rect()
        left = rect.left - 1  # + 10
        top = rect.top - 1  # + 10
        right = rect.right  # - 10
        bottom = rect.bottom  # - 10
        # self.walls = (
        #     Boundary()
        # )
        # self.walls = Plateform(self, Segment((right, top), (left, top)))
        # self.walls.add(Segment((right, bottom), (right, top)))
        # self.walls.add(Segment((left, bottom), (right, bottom)))
        # self.walls.add(Segment((left, top), (left, bottom)))
        self.walls = (  # TODO : strong clipping ?
            Boundary(self, (right, top), (left, top)),  # TODO : InfiniteBoundary
            Boundary(self, (right, bottom), (right, top)),
            Boundary(self, (left, bottom), (right, bottom)),
            Boundary(self, (left, top), (left, bottom)),
        )
        self.add(*self.walls)
        self.out = bp.Rect(-1, -1, right+1, bottom+1)

        # TODO : test them
        # Boundary(self, (right / 2, bottom), (right, bottom / 2))
        # Boundary(self, (left, bottom / 2), (right / 2, bottom))
        # Boundary(self, (right / 2, bottom), (right, top))
        # Boundary(self, (left, top), (right / 2, bottom))

        ch = self.add_collision_handler(COLLTYPE_FIGHTER, COLLTYPE_BOUNDARY)
        ch.pre_solve = abort_collision_poly_boundary

        self._step_timer = bp.RepeatingTimer(self.dt, self.step)  # TODO : District.step_timer
        bp.Runable.__init__(self)

    district = property(lambda self: self._district)
    painter = property(lambda self: self._painter_ref())

    def clear(self):
        for shape in self.static_body.shapes:
            self.remove(shape)
        for body in self.bodies:
            self.remove(body, *body.shapes)
        assert len(self.bodies) is 0
        assert len(self.shapes) is 0

    def pause(self):

        self._step_timer.pause()

    def resume(self):

        self._step_timer.resume()

    def start_running(self):

        self._step_timer.start()

    def step(self):

        for s in self.painter.fighters:  # TODO : animated_children
            # here, we influence fighter's x velocity depending on its speed and direction

            if s.body.required_rotation_angle:
                s.body.update_angle()

            # print(s.body.up_norm, s.body.left_norm, s.body.velocity.projection(s.body.left_norm).length, s.body.velocity.x)
            side_v = cpflerpconst(
                - s.body.velocity.dot(s.body.left_norm),
                # s.body.velocity.projection(s.body.left_norm).length,
                s.controller.direction * s.controller.speed,
                (s.controller.speed / Fighter.ACCELERATION_TIME) * self.dt
            )
            s.body.velocity = s.body.velocity.projection(s.body.up_norm) - s.body.left_norm * side_v

        with bp.paint_lock:

            # print("before step")
            super().step(self.dt)
            # print("after step")

            for fighter in self.district.fighters:
                for shape in fighter.shapes:
                    shape.sprite.center = round_vec(shape.offset + fighter.center)

            for shape in self.static_body.shapes:
                if isinstance(shape, Boundary):
                    for solidpoint in shape.endpoints:
                        solidpoint.has_collided = False
            # for plateform in self.district.plateforms:
            #     for solidpoint in plateform.solidpoints:
            #         solidpoint.has_collided = False

            if self.painter.debug_shapes:
                with bp.paint_lock:
                    for widget in tuple(self.painter.animated_shapes_debugger):
                        widget.kill()
                    assert len(self.painter.animated_shapes_debugger) is 0, self.painter.animated_shapes_debugger
                    for body in self.bodies:  # TODO : animated_children
                        self.painter._debug_shapes_of(body)

    def stop_running(self):

        self._step_timer.cancel()
