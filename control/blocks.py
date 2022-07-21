
import baopig as bp
import lib.images as im


class Brick:

    PRIORITY = 1

    def __init__(self, district, name, row, col):

        self.district = district
        self.row = row
        self.col = col
        self.name = name

        left = col * district.block_size[0]
        top = row * district.block_size[1]
        width, height = district.block_size
        centerx = int(width / 2)
        centery = int(height / 2)

        self.center = (left + centerx, top + centery)
        self.hitbox2 = None
        if name == "b1111":
            self.hitbox = bp.Rect(left, top, width, height)
        elif name == "b0011":
            self.hitbox = bp.Rect(left, top + centery, width, centery)
        elif name == "b1100":
            self.hitbox = bp.Rect(left, top, width, centery)
        elif name == "b0101":
            self.hitbox = bp.Rect(left + centerx, top, centerx, height)
        elif name == "b1010":
            self.hitbox = bp.Rect(left, top, centerx, height)
        elif name == "b0001":
            self.hitbox = bp.Rect(left + centerx, top + centery, centerx, centery)
        elif name == "b0010":
            self.hitbox = bp.Rect(left, top + centery, centerx, centery)
        elif name == "b0100":
            self.hitbox = bp.Rect(left + centerx, top, centerx, centery)
        elif name == "b1000":
            self.hitbox = bp.Rect(left, top, centerx, centery)
        elif name == "b1101":
            self.hitbox = bp.Rect(left + centerx, top + centery, centerx, centery)
            self.hitbox2 = bp.Rect(left, top, width, centery)
        elif name == "b1110":
            self.hitbox = bp.Rect(left, top + centery, centerx, centery)
            self.hitbox2 = bp.Rect(left, top, width, centery)
        elif name == "b0111":
            self.hitbox = bp.Rect(left + centerx, top, centerx, centery)
            self.hitbox2 = bp.Rect(left, top + centery, width, centery)
        elif name == "b1011":
            self.hitbox = bp.Rect(left, top, centerx, centery)
            self.hitbox2 = bp.Rect(left, top + centery, width, centery)
        else:
            raise ValueError(name)

        surf_rect = self.hitbox.copy()
        surf_rect.top -= top
        surf_rect.left -= left
        self.image = im.brick.subsurface(surf_rect)
        district.wallpaper.blit(self.image, self.hitbox.topleft)
        district.bricks_grid[row][col] = self

        if self.hitbox2 is not None:
            surf_rect = self.hitbox2.copy()
            surf_rect.top -= top
            surf_rect.left -= left
            self.image2 = im.brick.subsurface(surf_rect)
            district.wallpaper.blit(self.image2, self.hitbox2.topleft)

    def apply_react_fighter(self, fighter):

        reac = fighter.apply_react_brick(self.hitbox)
        fighter.velocity += reac
        if self.hitbox2:
            reac2 = fighter.apply_react_brick(self.hitbox2)
            fighter.velocity += reac2


class SlimeBlock:

    PRIORITY = 2

    def __init__(self, district, name, row, col):

        self.district = district
        self.row = row
        self.col = col
        self.name = name

        left = col * district.block_size[0]
        top = row * district.block_size[1]
        width, height = district.block_size
        self.hitbox = bp.Rect(left, top, width, height)
        self.center = self.hitbox.center
        self.image = im.slimeblock
        district.wallpaper.blit(self.image, self.hitbox.topleft)
        district.bricks_grid[row][col] = self

    def apply_react_fighter(self, fighter):

        reac = bp.Vector2(fighter.apply_react_brick(self.hitbox))
        if reac and fighter.velocity.y > fighter.district.gravity.y * 3:
            reac.scale_to_length(fighter.velocity.y * 1.9)
        fighter.velocity += reac


class Jumper:
    """
        jXP   : A jumper, where X can be U (up), or D (down), and P is the acceleration power
                aU45 -> jumper who gives an acceleration of normalized(0, -1) * 45
    """

    PRIORITY = 3

    def __init__(self, district, name, row, col):

        self.district = district
        self.row = row
        self.col = col
        self.name = name
        self.norm = bp.Vector2(0, 0)
        self.animation_index = 0
        images = im.jumper
        char = name[1]
        if char == "U":
            self.norm.y = -1
            self.images = tuple(images.subsurface((0, i) + district.block_size).copy() for i in range(12))
        elif char == "D":
            self.norm.y = 1
            images = bp.transform.flip(images, flip_x=False, flip_y=True)
            self.images = tuple(images.subsurface((0, 11 - i) + district.block_size).copy() for i in range(12))
        else:
            raise ValueError(char)
        self.norm.normalize_ip()
        self.p_norm = bp.Vector2(-self.norm.y, self.norm.x)
        self.power = int(name[2:])

        left = col * district.block_size[0]
        top = row * district.block_size[1]
        width, height = district.block_size
        self.hitbox = bp.Rect(left, top, width, height)
        self.center = self.hitbox.center
        district.bricks_grid[row][col] = self

        self.sprite = None
        self.image = self.images[0]
        color = images.get_at((0, 0))
        border_width = 2
        for i in self.images:
            bp.draw.rect(i, color, (0, 0) + district.block_size, border_width * 2 - 1)

        """for x in range(32):
            for y in range(43):
                color = images.get_at((x, y))
                color[3] = 128 + 64
                images.set_at((x, y), color)"""

    def apply_react_fighter(self, fighter):

        if fighter.dashing:
            return

        if self.hitbox.colliderect(fighter.hitbox):
            # fighter.acceleration = fighter.acceleration.project(self.p_norm)
            # fighter.velocity = fighter.velocity.project(self.p_norm)
            fighter.acceleration.y = 0
            fighter.velocity.y = 0
            fighter.apply_force(self.norm * self.power)

    def next_animation(self):

        self.animation_index = (self.animation_index + 1) % 12
        self.sprite.set_surface(self.images[self.animation_index])


class Accelerator:
    """
        vW    : An accelerator only improves a fighter's horizontal velocity
    """

    PRIORITY = 3

    def __init__(self, district, name, row, col):

        self.district = district
        self.row = row
        self.col = col
        self.name = name
        self.animation_index = 0
        self.image = im.accelerator
        self.power = int(name[1:])

        left = col * district.block_size[0]
        top = row * district.block_size[1]
        width, height = district.block_size
        self.hitbox = bp.Rect(left, top, width, height)
        self.center = self.hitbox.center
        district.bricks_grid[row][col] = self
        district.wallpaper.blit(self.image, self.hitbox.topleft)

    def apply_react_fighter(self, fighter):

        fighter.accel_coef = max(fighter.accel_coef, self.power)
