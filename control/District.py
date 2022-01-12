
# TODO : city.district
# TODO : let District manage Fighter.id


import pygame
import lib.images as im
from display.DistrictPainter import DistrictPainter
from physics.DistrictSpace import DistrictSpace
from physics import Plateform, Segment


class _FightersManager:

    def __init__(self):

        self._num_max_players = 18
        self._fighters = []
        self._availible_ids = list(range(self._num_max_players))

        colors = []
        for i in range(self._num_max_players):
            if i is 0:
                color = (200, 50, 50)
            elif i is 3:
                color = (190, 190, 0)
            elif i is 6:
                color = (200, 130, 40)
            elif i is 9:
                color = (50, 150, 240)
            elif i is 12:
                color = (120, 70, 20)
            elif i < 15:
                last_color = colors[-1]
                color = (last_color[1], last_color[2], last_color[0])
            elif i is 15:
                color = (255, 255, 255)
            elif i is 16:
                color = (127, 127, 127)
            elif i is 17:
                color = (0, 0, 0)
            colors.append(color)
        self._fighter_colors = colors

    fighters = property(lambda self: self._fighters)

    def close(self):
        """Only called by District.close()"""
        for fighter in self.fighters:
            fighter.kill()
        self._availible_ids = list(range(self._num_max_players))  # just reset the id rotation

    def create_fighter(self, player, center):
        """Every fighter creation must start here"""

        self.fighters.append(
            player.create_fighter(district=self, id=self._availible_ids.pop(0), center=center)
        )

        # TODO : let players choose a color in availible colors
        #   -> send colors, not id, so the server can choose a plaette

    def delete_fighter(self, fighter):
        """Only called from District.delete_fighter()"""

        if fighter not in self.fighters:
            raise PermissionError(f"{fighter} not in {self.name}")
        self._availible_ids.append(fighter.id)
        self.fighters.remove(fighter)

    def get_color(self, id):

        assert id < self._num_max_players
        return self._fighter_colors[id]


class District(_FightersManager):

    def __init__(self, name):

        _FightersManager.__init__(self)

        self._name = name
        self._filepath = f"lib/districts/{name}.txt"

        # fields initialized in read_file()
        self.players_pos = []  # Les positions des joueurs  # TODO : protect
        self.grid = []  # A 2D grid of strings representing blocs
        self.empty_cells = []
        self.nbcols = None
        self.nbrows = None
        self.block_size = (32, 32)  # TODO : try to change this
        self._width = self._height = None
        self.wallpaper = None

        # file options
        self.corners = False
        self.wallpaper_name = "w1"
        self.wallpaper_is_mosaic = None

        self._read_file()

        # fields initialized in open()
        self._painter = None
        self._space = None
        self._plateforms = []

    name = property(lambda self: self._name)
    space = property(lambda self: self._space)
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
            if content[-1].startswith("corners"):
                self.corners = content[-1][-4:] == "True"
            elif content[-1].startswith("mosaic"):
                self.wallpaper_is_mosaic = content[-1][-4:] == "True"
            elif content[-1].startswith("wallpaper"):
                self.wallpaper_name = content[-1][12:]
            print(content[-1])
            content.pop(-1)
        content.pop(-1)

        self.nbrows = len(content)
        for i in range(self.nbrows):
            content[i] = content[i].split("'")
            if self.nbcols is None:
                self.nbcols = len(content[i])
            assert self.nbcols == len(content[i]), f"Wrong blocks number in row {i+1} of {self.name} " \
                                                   f"({len(content[i])} blocks instead of {self.nbcols})"

        self._width = self.nbcols * self.block_size[0]
        self._height = self.nbrows * self.block_size[1]
        self.grid = content
        self._update_wallpaper()

    def _update_wallpaper(self):
        """
        Methode qui cree un wallpaper adapte aux dimensions du district
        Only called from _read_file()
        """

        wallpaper = im.load(f"wallpapers/{self.wallpaper_name}")

        if self.wallpaper_is_mosaic is False:
            self.wallpaper = pygame.transform.scale(wallpaper, self.size)
            return

        self.wallpaper = pygame.Surface(self.size)
        self.wallpaper.blit(wallpaper, (0, 0))
        w, h = wallpaper.get_size()

        # Si le wallpaper n'est pas assez haut
        if h < self.h:
            wallpaper = pygame.transform.scale(wallpaper, (w, self.h))

        # Si le wallpaper n'est pas assez large
        if w < self.w:
            for i in range(int(self.w / w)):
                self.wallpaper.blit(wallpaper, (w * (i + 1), 0))

    def close(self):
        """Called from DistrictPainter.close(), when the player exit PlayScene"""

        super().close()
        self.space.clear()
        self._painter = None
        self._space = None

    def delete_fighter(self, fighter):
        """Only called from Player.delete_fighter()"""
        for sprite in fighter.isprites:
            sprite.kill()
        self.space.remove(fighter.body, *fighter.shapes)
        super().delete_fighter(fighter)

    def open(self, painter):
        """Called from DistrictPainter.open(), when the player enter PlayScene"""

        assert isinstance(painter, DistrictPainter)

        self._painter = painter
        self._space = DistrictSpace(self)

        # bp.get_application().painter.start_recording(only_at_change=True)  TODO

        # Creation des blocs

        """
        aXYW  : An accelerator, where X and Y can be N (null), F (forward) or B (backward),
                and W is the acceleration power
                aNB45 -> accelerator who gives an acceleration of normalized(0, -1) * 45
        bXXXX : A block, where the first X represents the topleft corner, then topright, bottomleft, and bottomright
                X = 0 -> empty
                X = 1 -> filled
        e     : Empty cell
        g     : A bonus giver
        pI    : A portal, linked to the other portal with I index
        s     : slime block
        vW    : Another accelerator, but only affects velocity
        """
        # TODO : l : ladder (stop your fall, allow you to go up)
        # TODO : j : jelly (like a ladder but solid, so it collides with attacks, and slow you down a little)
        # TODO : w : walkway (a bloc who stop you only if you land on it)


        from display.sprites.BrickSprite import BrickSprite
        bricks = []
        class Brick:

            def __init__(brick, _, name, row, col):
                brick.row = row
                brick.col = col
                brick.name = name

                # TODO : vertices depend from name

                left = col * self.block_size[0]
                top = row * self.block_size[1]
                width, height = self.block_size
                brick.vertices = (
                    (left, top),
                    (left+width-1, top),
                    (left+width-1, top+height-1),
                    (left, top+height-1),
                )
                bricks.append(brick)

        def get_bloc_class(char):
            # if char == 'a':
            #     return Accelerator  # TODO
            if char == 'b':
                return Brick
            # if char == 'g':
            #     return Giver  # TODO
            # if char == 'p':
            #     return Portal  # TODO
            # if char == 's':
            #     return SlimeBlock  # TODO
            # if char == 'v':
            #     return Speeder  # TODO
            raise PermissionError("No Block attached to identifier " + char)

        for row in range(self.nbrows):
            for col in range(self.nbcols):
                name = self.grid[row][col]
                if name != 'e':
                    get_bloc_class(name[0])(self, name, row=row, col=col)

        import pymunk


        all_boundaries = []
        for brick in bricks:
            all_boundaries.extend((
                Segment(brick.vertices[0], brick.vertices[1]),
                Segment(brick.vertices[1], brick.vertices[2]),
                Segment(brick.vertices[2], brick.vertices[3]),
                Segment(brick.vertices[3], brick.vertices[0]),
            ))

        if self.corners:
            t = 120
            m = 45
            corners = [
                ((-1, -1), (t, -1), (m, m), (-1, t)),
                ((-1, self.h+1), (-1, self.h - t), (m, self.h - m), (t, self.h+1)),
                ((self.w+1, self.h+1), (self.w-t, self.h+1), (self.w-m, self.h-m), (self.w+1, self.h-t)),
                ((self.w+1, -1), (self.w+1, t), (self.w-m, m), (self.w-t, -1)),
            ]
            for corner in corners:
                for i, p in enumerate(corner):
                    all_boundaries.append(Segment(corner[i - 1], p))

        middle_ball = False
        if middle_ball:
            import math
            def iget_ball_vertexes(center, radius, delta):
                for i in range(0, 360, delta):
                    radian_delta = math.radians(delta + i)
                    v = pymunk.Vec2d(math.cos(radian_delta), math.sin(radian_delta))
                    v *= radius
                    yield center + v
                    print(delta, radian_delta, v, center)
            ball_vertexes = tuple(iget_ball_vertexes((self.w / 2, self.h / 2), 300, 10))
            print(ball_vertexes)
            for i, vertex in enumerate(ball_vertexes):
                all_boundaries.append(Segment(ball_vertexes[i - 1], vertex))

        if False:
            all_boundaries.extend((
                Segment((10, 60), (40, 60)),
                Segment((40, 60), (10, 140)),
                Segment((10, 140), (10, 60)),
            ))

            all_boundaries.extend((
                Segment((370, 200), (self.w, self.h)),
                Segment((self.w, self.h), (370, self.h)),
                Segment((370, self.h), (370, 200)),
            ))

            for origin in ((450, 64), (270, 200), (270 + self.block_size[0], 200-self.block_size[1])):
                vertices = []
                for n in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    v = pymunk.Vec2d(n)
                    v *= self.block_size
                    v += origin
                    vertices.append(v)
                l = len(vertices)
                for i in range(l):
                    all_boundaries.append(Segment(vertices[i], vertices[i-1 % l]))


        # si deux segments ont des normes opposées et qu'ils ont une distance maximale inférieure ou égale à 1, soit:
        #   1 : un segment est "contenu" dans l'autre
        #   2 : les deux segments se superposent pour en former un plus gros
        # alors on veut supprimer la superposition, puisqu'un segment est une barrière dans un sens
        #   1 : soit :
        #       1a : les deux segments ont la meme longueur : on les supprime tous les deux
        #       1b : un segment est plus petit que l'autre : on supprime le petit
        #   2 : on supprime la superposition à chaque segment

        platform_cutted_boundaries = all_boundaries.copy()
        for i, seg in enumerate(all_boundaries):
            for seg2 in all_boundaries[i+1:]:
                if seg.n == -seg2.n:
                    a = seg - seg.n
                    b = reversed(seg2)
                    if (a == b) or (seg == b):
                        platform_cutted_boundaries.remove(seg)
                        platform_cutted_boundaries.remove(seg2)

        # on recolle les morceaux
        def are_aligned(seg1, seg2):
            """Return True if seg1 and seg2 are on the same line, not just parallel"""
            return seg1.d.cross(seg2.a - seg1.a) == 0
        platform_boundaries = platform_cutted_boundaries.copy()
        for i, seg in enumerate(platform_cutted_boundaries):
            for seg2 in platform_cutted_boundaries[i+1:]:
                if seg.n == seg2.n and are_aligned(seg, seg2):
                    if pymunk.Vec2d(seg.a - seg2.b).length <= 1:
                        platform_boundaries.remove(seg)
                        seg2.config(a=seg2.a, b=seg.b)
                    elif pymunk.Vec2d(seg.b - seg2.a).length <= 1:
                        platform_boundaries.remove(seg)
                        seg2.config(a=seg.a, b=seg2.b)

        # connecting boundaries into plateforms
        plateforms = []
        # r = "Segments [\n"
        # for p in platform_boundaries:
        #     r += "\t{}\n".format(str(p))
        # r += "]"
        # print(r)
        while platform_boundaries:
            p = Plateform(self.space, platform_boundaries.pop(0))
            self.plateforms.append(p)
            while not p.is_complete:
                for b in platform_boundaries:
                    if p.segments[-1].is_connected(b) is not False:
                        p.add(b)
                        platform_boundaries.remove(b)
                        break

        # r = "Plateforms [\n"
        # for p in plateforms:
        #     r += "\t{}\n".format(str(p))
        # r += "]"
        # print(r)

        # TODO : find another way to create bricks sprites
        # for brick in bricks:
        #     BrickSprite(self, brick.row, brick.col)

        # self._shape = Poly(self, self.body, vertices)
        # self.shape.friction = 1
        # self.parent.space.add(self.shape)

        import baopig
        self.create_fighter(baopig.get_application().player, center=(64, 164))  # TODO : use players_pos

        self.painter.set_district(self)
        self.space.start_running()

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
