
# TODO : city.district
# TODO : let District manage Fighter.id
import math

import baopig as bp
import lib.images as im
from display.DistrictPainter import DistrictPainter
from control.blocks import Accelerator, Brick, Jumper, SlimeBlock
from control.physics import Space
from display.sprites.Sprite import DynamicSprite


class _FightersManager:

    def __init__(self):

        self._num_max_players = 18
        self._fighters = []
        self._availible_ids = list(range(self._num_max_players))

        colors = []
        for i in range(self._num_max_players):
            if i == 0:
                color = (200, 50, 50)
            elif i == 3:
                color = (190, 190, 0)
            elif i == 6:
                color = (200, 130, 40)
            elif i == 9:
                color = (50, 150, 240)
            elif i == 12:
                color = (120, 70, 20)
            elif i < 15:
                last_color = colors[-1]
                color = (last_color[1], last_color[2], last_color[0])
            elif i == 15:
                color = (255-32, 255-32, 255-32)
            elif i == 16:
                color = (127, 127, 127)
            elif i == 17:
                color = (32, 32, 32)
            colors.append(color)
        self._fighter_colors = colors

    fighters = property(lambda self: self._fighters)

    def close(self):
        """Only called by District.close()"""
        for fighter in self.fighters:
            fighter.kill()
        self._availible_ids = list(range(self._num_max_players))  # just reset the id rotation

    def create_fighter(self, player, midbottom):
        """Every fighter creation must start here"""

        self.fighters.append(
            player.create_fighter(district=self, id=self._availible_ids.pop(0), midbottom=midbottom)
        )

        # TODO : let players choose a color in availible colors
        #   -> send colors, not id, so the server can choose a plaette

    def delete_fighter(self, fighter):
        """Only called from District.delete_fighter()"""

        if fighter not in self.fighters:
            raise PermissionError(f"{fighter} not in {self}")
        self._availible_ids.append(fighter.id)
        self.fighters.remove(fighter)

    def get_color(self, id):

        assert id < self._num_max_players
        return self._fighter_colors[id]


class District(_FightersManager, Space):

    def __init__(self, name):

        _FightersManager.__init__(self)

        self._name = name
        self._filepath = f"lib/districts/{name}.txt"

        # fields initialized in read_file()
        self.players_pos = []  # Les positions des joueurs
        self.str_grid = []  # A 2D grid of strings representing blocs
        self.empty_cells = []
        self.nbcols = 0
        self.nbrows = 0
        self.block_size = (32, 32)  # TODO : try to change this ?
        self._width = self._height = 0
        self.wallpaper = None

        def animate_blocks():
            for b in self.bricks:
                if hasattr(b, "next_animation"):
                    b.next_animation()
        self.blocks_animator = bp.RepeatingTimer(.05, animate_blocks)

        # file options
        self.wallpaper_name = "w1"
        self.wallpaper_is_mosaic = None

        self._read_file()
        Space.__init__(self, size_rect=bp.Rect(0, 0, self._width, self._height))

        """
        bXXXX : A block, where the first X represents the topleft corner, then topright, bottomleft, and bottomright
                0 means empty and 1 means filled
                b1011 -> staircase going down to the right
        e     : Empty cell
        jXP   : A jumper, where X can be U (up), or D (down), and P is the acceleration power
                aU45 -> jumper who gives an acceleration of normalized(0, -1) * 45
        pI    : A portal, linked to the other portal with I index
        s     : slime block
        vW    : An accelerator only improves a fighter's horizontal velocity
        # TODO : l : ladder (stop your fall, allow you to go up)
        # TODO : j : jelly (like a ladder but solid, so it collides with attacks, and slow you down a little)
        # TODO : w : walkway (a bloc who stop you only if you land on it)
        """

        def get_bloc_class(char):
            if char == 'b':
                return Brick
            if char == 'j':
                return Jumper
            # if char == 'p':
            #     return Portal  # TODO
            if char == 's':
                return SlimeBlock
            if char == 'v':
                return Accelerator
            raise PermissionError("No Block attached to identifier " + char)

        self.bricks_grid = []  # A 2D dict of all the bricks
        for i in range(self.nbrows):
            self.bricks_grid.append([None] * self.nbcols)
        for row in range(self.nbrows):
            for col in range(self.nbcols):
                name = self.str_grid[row][col]
                if name != 'e':
                    get_bloc_class(name[0])(self, name, row=row, col=col)

        # fields initialized in open()
        self._painter = None
        self._plateforms = []

    def _get_bricks(self):
        for row in self.bricks_grid:
            for brick in row:
                if brick:
                    yield brick
    bricks = property(_get_bricks)
    is_open = property(lambda self: self._painter is not None)
    name = property(lambda self: self._name)
    painter = property(lambda self: self._painter)
    plateforms = property(lambda self: self._plateforms)

    h = height = property(lambda self: self._height)
    size = property(lambda self: (self.w, self.h))
    w = width = property(lambda self: self._width)

    def _read_file(self):
        """
        Methode qui lit le fichier self.filepath pour initialiser les blocs et le wallpaper
        Appelee dans __init__()
        """
        fichier_text = open(self._filepath, "r")
        content = fichier_text.read().split("\n")
        fichier_text.close()

        # wallpaper_is_mosaic = content[-1]
        while not content[-1].startswith("OPTIONS"):
            if content[-1].startswith("mosaic"):
                self.wallpaper_is_mosaic = content[-1][-4:] == "True"
            elif content[-1].startswith("wallpaper"):
                self.wallpaper_name = content[-1][12:]
            content.pop(-1)
        content.pop(-1)

        self.nbrows = len(content)
        for i in range(self.nbrows):
            content[i] = content[i].split("'")
            if self.nbcols == 0:
                self.nbcols = len(content[i])
            assert self.nbcols == len(content[i]), f"Wrong blocks number in row {i+1} of {self.name} " \
                                                   f"({len(content[i])} blocks instead of {self.nbcols})"

        self._width = self.nbcols * self.block_size[0]
        self._height = self.nbrows * self.block_size[1]
        self.str_grid = content
        self._update_wallpaper()

    def _update_wallpaper(self):
        """
        Methode qui cree un wallpaper adapte aux dimensions du district
        Only called from _read_file()
        """

        wallpaper = im.load(f"wallpapers/{self.wallpaper_name}")

        if self.wallpaper_is_mosaic is False:
            self.wallpaper = bp.transform.scale(wallpaper, self.size)
            return

        # Mosaic
        self.wallpaper = bp.Surface(self.size)
        self.wallpaper.blit(wallpaper, (0, 0))
        w, h = wallpaper.get_size()

        # Si le wallpaper n'est pas assez haut
        if h < self.h:
            for i in range(int(self.h / h)):
                self.wallpaper.blit(wallpaper, (0, h * (i + 1)))
            wallpaper = self.wallpaper.subsurface((0, 0, w, self.h)).copy()

        # Si le wallpaper n'est pas assez large
        if w < self.w:
            for i in range(int(self.w / w)):
                self.wallpaper.blit(wallpaper, (w * (i + 1), 0))

    def blit_bricks(self):  # TODO : remove (only ther for the button Swap background)

        surf = self.painter.background_image.surface
        for brick in self.bricks:
            if hasattr(brick, "sprite"):
                continue
            surf.blit(brick.image, brick.hitbox.topleft)
            if hasattr(brick, "image2"):
                surf.blit(brick.image2, brick.hitbox2.topleft)
        self.painter.background_image.set_surface(surf)

    def close(self):
        """Called from DistrictPainter.close(), when the player exit PlayScene"""

        if not self.is_open:
            return

        self.blocks_animator.cancel()
        super().close()
        self.clear()
        self.painter.close()
        self._painter = None

    def delete_fighter(self, fighter):
        """Only called from Player.delete_fighter()"""
        fighter._sprite_animator.cancel()
        fighter.sprite.kill()
        self.remove(fighter)
        super().delete_fighter(fighter)

    def open(self, painter):
        """Called from DistrictPainter.open(), when the player enter PlayScene"""

        if self.is_open:
            return
        assert isinstance(painter, DistrictPainter)

        self._painter = painter
        self.create_fighter(self.painter.application.player, midbottom=(0, 179))  # TODO : use players_pos
        self.painter.set_district(self)
        self.start_running()
        for b in self.bricks:
            if hasattr(b, "next_animation"):
                b.sprite = DynamicSprite(self.fighters[0], b.images[0], pos=b.hitbox.topleft)
        self.blocks_animator.start()

        """
        i = 0
        Kocci(self, pos=(0*64, 64*i))
        Ebuld(self, pos=(1*64, 64*i))
        Royal(self, pos=(2*64, 64*i))
        i += 1
        Ytrei(self, pos=(0*64, 64*i))
        Sabul(self, pos=(1*64, 64*i))
        Kocci(self, pos=(2*64, 64*i))
        i += 1
        Ebuld(self, pos=(0*64, 64*i))
        Royal(self, pos=(1*64, 64*i))
        Ytrei(self, pos=(2*64, 64*i))
        i += 1
        Sabul(self, pos=(0*64, 64*i))
        Kocci(self, pos=(1*64, 64*i))
        Ebuld(self, pos=(2*64, 64*i))
        i += 1
        Royal(self, pos=(0*64, 64*i))
        Ytrei(self, pos=(1*64, 64*i))
        Sabul(self, pos=(2*64, 64*i))
        # admin color
        i += 1
        Ebuld(self, pos=(0*64, 64*i))
        Ebuld(self, pos=(1*64, 64*i))
        Ebuld(self, pos=(2*64, 64*i))
        """

    def step(self):

        for fighter in self.fighters:  # TODO : animated_children

            if fighter.dashing:  # Dashing means no lateral movement
                continue

            # here, we influence fighter'sprite x velocity depending on its speed and direction
            fighter.velocity.x = fighter.direction * fighter.speed * fighter.accel_coef
            fighter.accel_coef = 1

        with bp.paint_lock:

            super().step()

            for fighter in self.fighters:

                fighter._airstate = 0

                top_row = int(fighter.hitbox.top / self.block_size[1])
                bottom_row = int(fighter.hitbox.bottom / self.block_size[1])
                left_col = int(fighter.hitbox.left / self.block_size[0])
                right_col = int(fighter.hitbox.right / self.block_size[0])
                collidable_bricks = []
                for row in self.bricks_grid[top_row: bottom_row + 1]:
                    for brick in row[left_col: right_col + 1]:
                        if brick:
                            collidable_bricks.append(brick)
                            # brick.apply_react_fighter(fighter)
                collidable_bricks.sort(key=lambda b: math.dist(b.center, fighter.hitbox.center - fighter.velocity))
                collidable_bricks.sort(key=lambda b: b.PRIORITY)
                for brick in collidable_bricks:
                    brick.apply_react_fighter(fighter)
                fighter.apply_react_ecran(self._size_rect)

                if fighter._airstate != fighter._old_airstate:
                    fighter._handle_new_airstate(fighter._airstate)
                if fighter._walkstate != fighter._old_walkstate:
                    fighter._handle_new_walkstate(fighter._walkstate)

                fighter.sprite.set_pos(midbottom=fighter.hitbox.midbottom)
