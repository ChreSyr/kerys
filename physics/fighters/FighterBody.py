
import math
import pymunk
from pybao import Object
from physics.collisions import COLLTYPE_FIGHTER, COLLTYPE_BOUNDARY
from physics.collisions import abort_collision_poly_boundary


class DynamicBody(pymunk.Body):  # TODO : file for it

    COLLTYPE = None  # to be defined by sub-classes
    SAFE_VELOCITY_STEP_LENGTH = 32  # there is no tuneling while moving 32 pixels in one step

    def __init__(self, controller, mass, moment):

        # controller is a DynamicBodyController

        self._controller = controller
        pymunk.Body.__init__(self, mass, moment, body_type=pymunk.Body.DYNAMIC)
        self.position = controller.center

        self.position_func = self.__class__.update_position
        self.velocity_func = self.__class__.update_velocity

    angle_degrees = property(lambda self: math.degrees(self.angle))
    controller = property(lambda self: self._controller)

    @staticmethod
    def update_position(body, dt):

        velocity_step_length = body.velocity.length * dt
        if velocity_step_length > body.SAFE_VELOCITY_STEP_LENGTH:
            # print("WARNING : High velocity :", body.velocity * dt)

            n = int(math.ceil(velocity_step_length / body.SAFE_VELOCITY_STEP_LENGTH))

            # print(dt, n, body.velocity.length * dt, body.SAFE_VELOCITY_STEP_LENGTH)
            dt /= n
            for i in range(n):
                pymunk.Body.update_position(body, dt)
                # print(i, body.position)d

                if i < n-1:  # the last step is followed by the default collision slover

                    for shape in body.shapes:
                        for info in body.space.shape_query(shape):

                            # print(f"The collision with {info.shape} might be missed")

                            if shape.collision_type is COLLTYPE_FIGHTER and info.shape.collision_type is COLLTYPE_BOUNDARY:
                                arbiter = Object(
                                    shapes=[shape, info.shape],
                                    contact_point_set=info.contact_point_set,
                                )
                                abort_collision_poly_boundary(arbiter, body.space, None)

                            else:
                                raise NotImplemented("Cannot solve this collision")

        else:
            pymunk.Body.update_position(body, dt)

        body.controller._update_pos_from_body()

    def _step_back(self, dx, dy):
        """Only called by DynamicBodyController.step_back"""

        # absorb velocity, on normal vector
        self.velocity = self.velocity - self.velocity.projection(pymunk.Vec2d(dx, dy))
        self.position += (dx, dy)


class FighterBody(DynamicBody):

    COLLTYPE = COLLTYPE_FIGHTER

    def __init__(self, fighter):

        DynamicBody.__init__(
            self, fighter,
            mass=1,            # mass don't affect fighters
            moment=pymunk.inf  # fighters cannot rotate from standard collisions
        )
        self.gravity = pymunk.Vec2d(fighter.district.space.gravity)
        self.required_rotation_angle = 0
        self.up_norm = - self.gravity.normalized()
        self.left_norm = self.gravity.perpendicular_normal()

    @staticmethod
    def update_velocity(body, gravity, damping, dt):

        pymunk.Body.update_velocity(body, body.gravity, damping, dt)

    def disable_gravity(self):

        def remove_gravity(body, _, damping, dt):
            self.update_velocity(body, (0, 0), damping, dt)
        self.velocity_func = remove_gravity

    def enable_gravity(self):

        self.velocity_func = self.__class__.update_velocity

    def rotate(self, angle_radians):

        if not angle_radians: return
        self.angle -= angle_radians
        self.gravity.angle -= angle_radians  # TODO : = self.angle - math.rad(90)
        self.up_norm = - self.gravity.normalized()
        self.left_norm = self.gravity.perpendicular_normal()
        # print("ROTATE", angle_degrees, self.gravity, self.up_norm, self.left_norm)
        for shape in self.shapes:
            shape.update_rotated_vertices()
        # self.space.reindex_shapes_for_body(self)

    def rotate_degrees(self, angle_degrees):

        self.rotate(math.radians(angle_degrees))

    def set_up_norm_TBR(self, up_norm):
        """Rotates in consequence"""

        self.angle = up_norm.angle + 1.5707963267948966  # 90 in radians
        self.gravity.angle_degrees = up_norm.angle_degrees
        self.gravity *= -1  # from pymunk to pygame
        self.up_norm = - self.gravity.normalized()
        self.left_norm = self.gravity.perpendicular_normal()
        # print("ROTATE", angle_degrees, self.gravity, self.up_norm, self.left_norm)
        for shape in self.shapes:
            shape.update_rotated_vertices()

    def update_angle(self):

        self.rotate(self.required_rotation_angle)
        self.required_rotation_angle = 0

