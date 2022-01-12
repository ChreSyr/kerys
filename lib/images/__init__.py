

import pygame


def load(name):
    try:
        # return pygame.image.load("lib/images/icon.png")
        return pygame.image.load("lib/images/"+name+".png")
    except pygame.error:
        return pygame.image.load("lib/images/"+name+".jpg")
    except FileNotFoundError:
        return pygame.image.load("lib/images/"+name+".jpg")


# ICON
icon = load("icon")

# BUTTONS
textbutton = load("buttons/textbutton")
w, h = 140, 40
textbutton = pygame.transform.scale(textbutton, (w, h * 3))
textbutton_bck = textbutton.subsurface(0, 0, w, h)
# textbutton_hover = textbutton.subsurface(0, h, w, h)
textbutton_focus = textbutton.subsurface(0, h, w, h)
textbutton_link = textbutton.subsurface(0, h*2, w, h)
button_background = load("buttons/button_background")
button_hover = load("buttons/button_hover")
button_link = load("buttons/button_link")
button_focus = load("buttons/button_focus")

playpause = load("buttons/playpause")
w, h = 42, 42
playpause = pygame.transform.scale(playpause, (w, h * 8))
play_bck = playpause.subsurface(0, 0, w, h)
play_press = playpause.subsurface(0, h, w, h)
play = playpause.subsurface(0, h*2, w, h)
pause = playpause.subsurface(0, h*3, w, h)
play_splash = tuple(playpause.subsurface(0, h*i, w, h) for i in (6, 5, 4))

# DIALOG
dialog_background = load("dialog_background")

# MENU
btnzone_bckgr = load("buttons_zone_background")

# WALLPAPERS
wallpapers = tuple(load("wallpapers/w"+str(i)) for i in range(1, 18))

# BLOCKS
brick = load("blocks/brick")

# FIGHTERS
fighters = load("fighters/all")
kocci_sprite = load("fighters/kocci")
ebuld_sprite = load("fighters/ebuld")
royal_sprite = load("fighters/royal")
ytrei_sprite = load("fighters/ytrei")
sabul_sprite = load("fighters/sabul")