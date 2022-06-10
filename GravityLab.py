# -*- coding: utf-8 -*

import math
import pygame
import random
import baopig as bp
import time


# === Physics ===


# Constants
GRAVITY = bp.Vector2(0, 1)
AIR_FRICTION = .03
NB_CIRCLES = 5
NB_BALLS = 5


class PhysicsManager:

    def __init__(self):
        self.pause = False
        self.update_timer = bp.RepeatingTimer(1/FPS, self.update)

        self.mem = 0

    def update(self):
        for b in balls:
            b.premove()  # collisions and velocity calcul
        for b in balls:
            b.move()  # applying velocities

        # TODO : solve a mathematical issue : reac vectors should be sorted or lenghed
        # TODO : so the cinetic energy always stays the same
        """
        # Donne la moyenne des vitesses
        # Pour des balles de même poids et sans gravité, devrait toujours être une constante
        mem2 = int(time.time())
        if mem2 != self.mem:
            self.mem = mem2
            moy = 0
            for b in balls:
                moy += b.vel.length()
            print(moy / len(balls))
        """


class Cercle:
    """Base pour un cercle"""
    def __init__(self, center, radius, color):
        self.center = bp.Vector2(center)
        self.radius = radius
        self.color = color

        self.widget = CercleWidget(self)

    def __str__(self):
        return f"Cercle(center:{self.center})"

    def collidingcercle(self, cercle):
        return self.center.distance_to(cercle.center) <= self.radius + cercle.radius

    def collidingpoint(self, pnt):
        return self.center.distance_to(pnt) <= self.radius


class Ball(Cercle):
    """Cercle affectee par la gravité"""
    def __init__(self, center, radius, color):
        super(Ball, self).__init__(center, radius, color)
        self.vel = bp.Vector2(0, 0)
        self.acc = bp.Vector2(0, 0)
        density = .01
        surface = math.pi * radius ** 2
        self.mass = density * surface

        # for the reset
        self.origin = bp.Vector2(*center)

    def __str__(self):
        return f"Ball(center:{self.center}, vel:{self.vel})"

    def update_reac(self):
        """Renvoi toutes les reaction de support appliquees a self"""
        for c in circles:
            if self.collidingcercle(c):
                self.apply_react_cercle(c)
        for b in balls:
            if self.collidingcercle(b) and b != self:
                self.apply_react_cercle(b)
        self.apply_react_ecran()

    def apply_force(self, force):
        self.acc += force / self.mass if SIMULATE_MASS else force

    def apply_react_cercle(self, cercle):
        """Renvoi la reaction du support cercle"""

        def closest_pnt_on_cercle(cercle, pnt):
            """Renvoi le pnt de cercle le plus proche de pnt"""
            v = - (cercle.center - pnt).normalize()
            return v * cercle.radius + cercle.center

        I1 = closest_pnt_on_cercle(self, cercle.center)
        I2 = closest_pnt_on_cercle(cercle, self.center)
        react_support = bp.Vector2(I2) - bp.Vector2(I1)
        # print(react_support, I1, I2, self.vel.length(), cercle.vel.length(), react_support.length())

        if SIMULATE_MASS and not isinstance(cercle, Ball):  # if it is an immobile circle
            react_support *= self.mass  # the reaction is equal to the collision
        self.apply_force(react_support)

    def apply_react_ecran(self):
        """Renvoi la reaction du support du cadre de l'ecran"""
        if self.center[1] < self.radius:
            poussee = self.radius - self.center[1]
            if SIMULATE_MASS: poussee *= self.mass  # the reaction is equal to the collision
            react_support = bp.Vector2(0, poussee)
            self.apply_force(react_support)
        elif self.center[1] > physics_zone.h - self.radius:
            poussee = physics_zone.h - self.radius - self.center[1]
            if SIMULATE_MASS: poussee *= self.mass  # the reaction is equal to the collision
            react_support = bp.Vector2(0, poussee)
            self.apply_force(react_support)
        if self.center[0] < self.radius:
            poussee = self.radius - self.center[0]
            if SIMULATE_MASS: poussee *= self.mass  # the reaction is equal to the collision
            react_support = bp.Vector2(poussee, 0)
            self.apply_force(react_support)
        elif self.center[0] > physics_zone.w - self.radius:
            poussee = physics_zone.w - self.radius - self.center[0]
            if SIMULATE_MASS: poussee *= self.mass  # the reaction is equal to the collision
            react_support = bp.Vector2(poussee, 0)
            self.apply_force(react_support)

    def premove(self):
        # On applique le poids
        self.apply_force(GRAVITY * self.mass if SIMULATE_MASS else GRAVITY)

        # On applique les collisions
        self.update_reac()

    def move(self):

        # On applique l'acceleration et le frottement de l'air sur la vitesse
        self.vel += self.acc
        self.vel *= 1 - AIR_FRICTION

        # On applique la vitesse sur la position
        self.center += self.vel
        self.acc *= 0

        self.widget.center = self.center


class Polygon:
    """Base pour un polygone regulier"""
    def __init__(self, center, apotheme, num_faces):
        self.center = bp.Vector2(center)
        self.dir = bp.Vector2(0, -1)
        self.apotheme = apotheme
        self.num_faces = num_faces
        self.len_side = apotheme * 2 * math.tan(math.pi / num_faces)
        self.perimeter = self.len_side * num_faces
        self.surface = apotheme * self.perimeter / 2
        self.radius = math.sqrt(self.apotheme ** 2 + (self.len_side / 2) ** 2)
        self.dir *= self.radius


class Hexadecagone(Polygon):
    """Polygone se rapprochant d'un cercle, non affecte par la gravite"""
    def __init__(self, center, apotheme, color, num_faces):
        super(Hexadecagone, self).__init__(center, apotheme, num_faces)
        self.color = color
        density = .001
        self.mass = density * self.surface

    def collidingcercle(self, cercle):
        return self.center.distance_to(cercle.center) <= self.radius + cercle.radius

    def collidingpoint(self, pnt):
        return self.center.distance_to(pnt) <= self.radius


# === Interface ===


class CercleWidget(bp.Circle):

    def __init__(self, circle):

        assert isinstance(circle, Cercle)
        bp.Circle.__init__(self, physics_zone, circle.color, circle.center, circle.radius)

        self.circle = circle


class Player:
    def __init__(self):
        self.ball = balls[0]
        # self.circle = circles[0]
        self.grip = None
        self.m = pygame.mouse
        self.m_pos = self.m.get_pos()  # in command_zone referencial
        self.m_pos = self.m_pos[0] - command_zone.w, self.m_pos[1]
        self.m_clic = self.m.get_pressed()
        self.m_rel = self.m.get_rel()

    def update_mouse(self):
        self.m_pos = self.m.get_pos()
        self.m_pos = self.m_pos[0] - command_zone.w, self.m_pos[1]
        self.m_clic = self.m.get_pressed()
        self.m_rel = self.m.get_rel()

    def apply_input(self):
        if self.m_clic[0] and physics_zone.collidemouse():
            self.grip.center = bp.Vector2(*self.m_pos)
            self.grip.widget.center = self.grip.center
            if self.grip in balls:
                self.grip.vel = bp.Vector2(*self.m_rel)

        pressed = lambda val: int(bp.keyboard.is_pressed(val))
        dy = pressed("s") - pressed("z")
        dx = pressed("d") - pressed("q")
        mvt = bp.Vector2(dx, dy) * 3 / FPS
        self.ball.acc += mvt


# Constants
FPS = 40
W, H = APP_SIZE = 800, 640
command_zone_W = 140


# App initializaton
physics_enginer = bp.Application(name="Gravity Lab", theme="dark")
physics_enginer.set_default_size(APP_SIZE)
physics_enginer.set_fps(FPS)


# Scene init
class MainScene(bp.Scene):
    def __init__(self):
        bp.Scene.__init__(self, physics_enginer)
        self.shadowing = False
        self.physics_manager = PhysicsManager()

    def close(self):
        self.physics_manager.update_timer.cancel()

    def open(self):
        self.physics_manager.update_timer.start()

    def receive(self, event):
        player.update_mouse()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.physics_manager.pause = not self.physics_manager.pause
            elif event.key == bp.K_b:
                r=16
                balls.append(Ball(
                    [random.randint(r, physics_zone.w - r),
                     random.randint(r, physics_zone.h - r)],
                    r,
                    (80, 63, 0)
                ))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for c in circles:
                if c.collidingpoint(player.m_pos):
                    player.grip = c
                    # player.circle = c
            for b in balls:
                if b.collidingpoint(player.m_pos):
                    player.grip = b
                    player.ball = b
            player.apply_input()

    def run(self):
        player.apply_input()


class PhysicsZone(bp.Zone):

    empty_surf = pygame.Surface((W - command_zone_W, H), pygame.SRCALPHA)
    sail = empty_surf.copy()
    sail.fill((0, 0, 0, 80))

    def _update_rect(self):

        if main_scene.shadowing:
            ancient = PhysicsZone.empty_surf.copy()
            ancient.blit(self.surface, (0, 0))
            ancient.blit(PhysicsZone.sail, (0, 0))
            self.set_background_image(ancient)
        super()._update_rect()


main_scene = MainScene()
main_scene.enable_selecting(False)
physics_enginer.set_style_for(bp.Button, height=40, width=120)
physics_enginer.set_style_for(bp.SliderBar, length=120)

# Zones
command_zone = bp.Zone(main_scene, width=command_zone_W, height="100%", pos=(0, 0), background_color="grey4")
physics_zone = PhysicsZone(main_scene, size=(W-140, "100%"), pos=command_zone.topright, background_color=(0, 0, 0))

# Command Zone & Quit Button
command_buttons_layer = bp.GridLayer(command_zone, nbcols=1, row_height=60, col_width=140)
quit_button = bp.Button(command_zone, text="Quit", command=physics_enginer.exit, sticky="center", row=0)

# TODO : is it possible / logic to set sticky in the style ? Does style has to deal with positionning ?
# TODO : else, is it possible / logic to ask to the gridlayer to set all of its widget at the center ?

# Rest button
def reset_balls():
    for b in balls:
        b.vel = bp.Vector2(0, 0)
        b.center = bp.Vector2(*b.origin)
reset_button = bp.Button(command_zone, row=1, text="Reset balls", sticky="center", command=reset_balls)

# Gravity Slider
gravity_slider = bp.Slider(command_zone, minval=0, maxval=4, sticky="center", step=.1, row=2,
                           title="gravity", defaultval=GRAVITY[1])
gravity_slider.signal.NEW_VAL.connect(lambda val: GRAVITY.__setitem__(1, val))

# Frictions Slider
def update_air_friction(val):
    global AIR_FRICTION
    AIR_FRICTION = val
air_friction_slider = bp.Slider(command_zone, minval=0, maxval=1, sticky="center", step=.01, row=3,
                              title="friction", defaultval=AIR_FRICTION)
air_friction_slider.signal.NEW_VAL.connect(update_air_friction)

# Shadowing
def shadow_command():
    main_scene.shadowing = not main_scene.shadowing
    if main_scene.shadowing is False:
        physics_zone.set_background_image(None)
shadowing_button = bp.CheckBox(command_zone, row=4, text="Shadows", sticky="center", command=shadow_command)
# shadowing_button.signal.VALIDATE.connect(shadow_command)

# Freeze
def freeze_command():
    update_timer = main_scene.physics_manager.update_timer
    if update_timer.is_paused:
        update_timer.resume()
    else:
        update_timer.pause()
freeze_button = bp.Button(command_zone, row=5, text="Freeze", sticky="center", command=freeze_command)

# Mass simulation
SIMULATE_MASS = False
def mass_command():
    global SIMULATE_MASS
    SIMULATE_MASS = not SIMULATE_MASS
mass_button = bp.CheckBox(command_zone, row=6, text="Simulate Mass", sticky="center", command=mass_command)
# mass_button.signal.VALIDATE.connect(mass_command)

# Creating planets
circles = []
for i in range(NB_CIRCLES):
    r = 100
    c = Cercle([random.randint(r, physics_zone.w - r), random.randint(r, physics_zone.h - r)],
                r,
                (random.randrange(255), random.randrange(255), random.randrange(255)),
               )
    while True in [c.collidingcercle(c2) for c2 in circles]:
        c.widget.kill()
        r = random.randint(10, 100)
        c = Cercle([random.randint(r, physics_zone.w - r), random.randint(r, physics_zone.h - r)],
                    r,
                    (random.randrange(255), random.randrange(255), random.randrange(255)),
                   )
    circles.append(c)

# Creating spaceships
balls = []
for i in range(NB_BALLS):
    r = 16
    b = Ball([random.randint(r, physics_zone.w - r), random.randint(r, physics_zone.h - r)], r, (160, 126, 0))
    while True in [b.collidingcercle(c) for c in circles]:
        b.widget.kill()
        b = Ball([random.randint(r, physics_zone.w - r), random.randint(r, physics_zone.h - r)], r, (160, 126, 0))
    balls.append(b)

player = Player()
player.grip = balls[-1]

physics_enginer.launch()
