
import baopig as bp


class _RunablesManager:  # TODO : rework
    def __init__(self):

        self._runables = set()
        self._running = set()
        self._paused = set()

    def add(self, runable):

        assert isinstance(runable, Runable)
        self._runables.add(runable)

    def pause(self, runable):

        assert runable in self._running
        self._running.remove(runable)
        self._paused.add(runable)

    def remove(self, runable):

        assert runable in self._runables
        self._runables.remove(runable)
        if runable in self._running:
            self._running.remove(runable)

    def resume(self, runable):

        assert runable in self._paused
        self._paused.remove(runable)
        self._running.add(runable)

    def start_running(self, runable):

        assert runable in self._runables
        assert runable not in self._running
        assert runable not in self._paused
        self._running.add(runable)

    def stop_running(self, runable):

        assert runable in self._running
        self._running.remove(runable)

    def run_once(self):

        for runable in self._running:
            runable.run()


_runables_manager = _RunablesManager()
del _RunablesManager


class Runable(bp.Communicative):

    def __init__(self, start=False, **kwargs):

        bp.Communicative.__init__(self, **kwargs)

        _runables_manager.add(self)

        self._is_running = False
        self._is_paused = False

        if start:
            self.start_running()

    is_paused = property(lambda self: self._is_paused)
    is_running = property(lambda self: self._is_running)

    def run(self):
        """Stuff to do when the object is running"""

    def pause(self):

        if not self.is_running:
            raise PermissionError("Cannot pause a Runable who didn't start yet")

        if self.is_paused is True:
            return

        _runables_manager.pause(self)
        self._is_running = False
        self._is_paused = True
        self.handle_pause()
        # self.signal.PAUSE.emit()

    def handle_pause(self):
        """Stuff to do when the object is paused"""

    def resume(self):

        if self.is_paused is False:
            raise PermissionError("Cannot resume a Runable who isn't paused")

        _runables_manager.resume(self)
        self._is_running = True
        self._is_paused = False
        self.handle_resume()
        # self.signal.RESUME.emit()

    def handle_resume(self):
        """Stuff to do when the object resume"""

    def start_running(self):

        if self.is_running is True:
            return

        _runables_manager.start_running(self)
        self._is_running = True
        self.handle_startrunning()
        # self.signal.START_RUNNING.emit()

    def handle_startrunning(self):
        """Stuff to do when the object starts to run"""

    def stop_running(self):

        if self.is_paused is True:
            self.resume()

        if self.is_running is False:
            return

        _runables_manager.stop_running(self)
        self._is_running = False
        self.handle_stoprunning()
        # self.signal.STOP_RUNNING.emit()

    def handle_stoprunning(self):
        """Stuff to do when the object stops to run"""


class Body(bp.Communicative):
    """
    States
        0 : in the air
        1 : on the ground
    """
    IN_THE_AIR = 0
    ON_THE_GROUND = 1

    # WALKSTATES, horizontal movement only
    STATIONNARY = 0
    WALKING = 1

    def __init__(self, hitbox):

        bp.Communicative.__init__(self)

        self.hitbox = hitbox
        self.velocity = bp.Vector2(0, 0)
        self.acceleration = bp.Vector2(0, 0)

        self.gravitable = True
        self._old_airstate = 0
        self._airstate = 0

        self._old_walkstate = 0
        self._walkstate = 0

    def _handle_new_airstate(self, airstate):
        """To be overriden"""

    def _handle_new_walkstate(self, walkstate):
        """To be overriden"""

    def apply_react_brick(self, brick_rect):

        if not brick_rect.colliderect(self.hitbox):
            return (0, 0)

        react_support_axis = "X"
        if self.velocity.x == 0:
            react_support_axis = "Y"
        elif self.velocity.y == 0:
            pass
        else:

            if self.velocity.y < 0:
                body_collider_corner = "top"
                brick_collider_corner = "bottom"
            else:
                body_collider_corner = "bottom"
                brick_collider_corner = "top"
            if self.velocity.x < 0:
                body_collider_corner += "left"
                brick_collider_corner += "right"
            else:
                body_collider_corner += "right"
                brick_collider_corner += "left"

            A = bp.Vector2(getattr(self.hitbox, body_collider_corner))
            B = A + self.velocity
            C = bp.Vector2(getattr(brick_rect, brick_collider_corner))
            d = (B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x)  # AB.cross(AC)
            # Si :
            #   d > 0, alors C est à gauche de la droite
            #   d = 0, alors C est sur la droite
            #   d < 0, alors C est à droite de la droite
            if d < 0 and body_collider_corner in ("topright", "bottomleft"):
                react_support_axis = "Y"
            elif d > 0 and body_collider_corner in ("topleft", "bottomright"):
                react_support_axis = "Y"

        if react_support_axis == "X" and self._old_airstate == 1 and self.velocity.y >= 0:
            dy = self.hitbox.bottom - brick_rect.top
            if dy <= 17:
                self.hitbox.bottom = brick_rect.top
                self._airstate = 1
                return (0, dy)

        if react_support_axis == "X":
            assert self.velocity.x
            if self.velocity.x > 0:
                react_support = (brick_rect.left - self.hitbox.right, 0)
                self.hitbox.right = brick_rect.left
                self._walkstate = self.STATIONNARY
            else:
                react_support = (brick_rect.right - self.hitbox.left, 0)
                self.hitbox.left = brick_rect.right
                self._walkstate = self.STATIONNARY
        else:
            if self.velocity.y >= 0:
                react_support = (0, brick_rect.top - self.hitbox.bottom)
                self.hitbox.bottom = brick_rect.top
                self._airstate = 1
            else:
                react_support = (0, brick_rect.bottom - self.hitbox.top)
                self.hitbox.top = brick_rect.bottom
                self.stun()
        return react_support

    def apply_react_ecran(self, ecran_rect):

        if ecran_rect.contains(self.hitbox):
            return

        x, y = self.hitbox.topleft
        self.hitbox.clamp_ip(ecran_rect)  # move hitbox inside ecran_rect
        dy = self.hitbox.top - y
        dx = self.hitbox.left - x

        # Annule l'acceleration qui s'oppose à la reaction du support
        if dy:
            if dy > 0:
                self.stun()
            self.velocity.y = 0
        if dx:
            self.velocity.x = 0
            self._walkstate = self.STATIONNARY

        # Update the state
        if dy < 0:
            self._airstate = 1

    def apply_force(self, force):

        self.acceleration += force  # / self.mass  # TODO : end check, mass is used ?

    def move(self, d):

        self.hitbox.move_ip(*d)

        if d[0] != 0:
            self._walkstate = self.WALKING
        else:
            self._walkstate = self.STATIONNARY

    def stun(self):

        self.gravitable = False  # litle freeze in the air
        bp.SetattrTimer(self, "gravitable", True, delay=abs(self.velocity.y) / 350).start()


class Space(Runable):  # TODO : copy a part of baopig.Runable here

    def __init__(self, size_rect):

        self.gravity = bp.Vector2(0, 1.7)
        self.dt = 1 / 50  # produces 50 steps per second

        self._bodies = []
        self._collision_handlers = []
        self._size_rect = size_rect

        self._step_timer = bp.RepeatingTimer(self.dt, self.step)
        Runable.__init__(self)

    def add(self, *bodies):

        for b in bodies:
            assert isinstance(b, Body)
        self._bodies.extend(bodies)

    def clear(self):

        for body in self._bodies:
            self.remove(body)
        assert len(self._bodies) == 0

    def pause(self):

        self._step_timer.pause()

    def remove(self, *bodies):

        for thing in bodies:
            self._bodies.remove(thing)

    def resume(self):

        self._step_timer.resume()

    def start_running(self):

        self._step_timer.start()

    def step(self):

        # IF THREADED STEP, TODO : whith step_lock

        # PRE STEP
        for body in self._bodies:

            if body.gravitable:
                body.apply_force(self.gravity)

            body._old_airstate = body._airstate
            body._old_walkstate = body._walkstate

        # STEP
        for body in self._bodies:

            # On applique l'acceleration et le frottement de l'air sur la vitesse
            body.velocity += body.acceleration

            # On applique la vitesse sur la position
            body.move(body.velocity)
            body.acceleration *= 0

    def stop_running(self):

        self._step_timer.cancel()


def perpendicular(vector):
    return bp.Vector2(-vector[1], vector[0])
