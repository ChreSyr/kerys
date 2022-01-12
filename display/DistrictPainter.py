

import pymunk
import baopig as bp
from .sprites.PlateformSprite import PlateformSprite
from .sprites.FighterSprite import FighterSprite
from .interactivewidgets.Button import PlayPauseButton


class FightersLayer(bp.Layer):

    def __init__(self, playground, weight):

        bp.Layer.__init__(self, playground, FighterSprite, weight=weight, name="fighters_layer")


class DistrictPainter(bp.SubZone, bp.Openable, bp.Closable):

    def __init__(self, scene, *args, **kwargs):
        """
        Constructeur de District
        :param name: Le nom du fichier texte qui definit le terrain
                     le fichier doit etre au format .txt et dans le repertoire "lib/terrains"
        """

        bp.SubZone.__init__(self, scene, *args, **kwargs)

        self._district = None
        self.i = 0  # for swap background
        self._blocks = bp.Layer(self, PlateformSprite, weight=1, name="plateforms_layer")
        self._fighters = FightersLayer(self, weight=2)
        self._buttons = bp.Layer(self, bp.Button, weight=3, name="buttons_layer")
        self._space = None

        # self.set_always_dirty()  # TODO : if low fps, set_always_dirty() ?

        self._last_run_time = None

        # debug
        class KillableList(list, bp.Communicative):
            """Kind of WeakTypedList, only contains alive communicative objects"""
            def __init__(self):
                list.__init__(self)
                bp.Communicative.__init__(self)
            def append(self, widget):
                super().append(widget)
                self.connect("remove", widget.signal.KILL)
            def extend(self, widgets):
                for widget in widgets:
                    self.append(widget)
            def remove(self, widget_ref):
                self.disconnect(emitter=widget_ref())
                super().remove(widget_ref())
        self.debug_shapes = False
        self.static_shapes_debugger = KillableList()
        self.animated_shapes_debugger = KillableList()
        self.debug_collisions = False
        self.debug_boundary_stepback = False
        self.debug_jumps = False

        PlayPauseButton(self, (35, 35), layer=self.buttons)

    blocks = property(lambda self: self._blocks)  # TODO : plateforms
    buttons = property(lambda self: self._buttons)
    district = property(lambda self: self._district)
    fighters = property(lambda self: self._fighters)
    space = property(lambda self: self._space)

    def _debug_shapes_of(self, body):

        offset = body.position + body.center_of_gravity
        if body.body_type is pymunk.Body.STATIC:
            l = self.static_shapes_debugger
        else:
            l = self.animated_shapes_debugger
        for shape in body.shapes:
            # if body.body_type is pymunk.Body.STATIC:
            #     print(shape)
            if hasattr(shape, "get_vertices"):  # fighters
                # vertices = tuple(v.rotated(body.angle) for v in shape.get_vertices())
                vertices = shape.get_vertices()
                # assert body.angle == 0, "A body with infinite moment cannot rotate from collisions"
                l.append(bp.Polygon(self, (255, 255, 255), vertices, 1,  # TODO : angle
                                    offset=offset,
                                    touchable=False, offset_angle=body.angle))
                l.append(bp.Line(self, (255, 0, 0), vertices[0], vertices[1], 1,
                                 offset=offset, touchable=False, offset_angle=body.angle))
            elif hasattr(shape, "a"):  # boundaries
                l.append(bp.Line(self, (255, 255, 255), shape.a, shape.b, 1,
                                 offset=offset, touchable=False, offset_angle=body.angle))
                mid = (shape.a + shape.b) / 2
                l.append(bp.Line(self, (0, 0, 255), mid, mid + shape.normal * 5, 1,
                                 offset=offset, touchable=False, offset_angle=body.angle))
            # elif hasattr(shape, "radius"):  # solidpoints
            #     l.append(bp.Circle(self, (255, 255, 255), center=body.position + shape.offset,
            #                        radius=shape.radius+1, touchable=False))
            else:
                raise NotImplemented
        if hasattr(body, "gravity"):
            l.append(bp.Line(self, (127, 127, 255), (0, 0), body.gravity * 3 * self.space.dt, 3,
                             offset=offset, touchable=False))
            # l.append(bp.Rectangle(self, (0, 127, 0), tuple(body.gravity), touchable=False, pos=offset))
        l.append(bp.Line(self, (0, 127, 127), (0, 0), body.velocity * self.space.dt,
                         offset=offset, touchable=False, name="WHEREAMI"))
        l.append(bp.Rectangle(self, color=(0, 255, 0), size=(1, 1), touchable=False, pos=offset))
        # l.append(bp.Rectangle(self, (0, 255, 0), tuple(body.velocity), touchable=False, pos=offset))

    def close(self):

        self.district.close()

        self.terrain = None
        for layer in (self.blocks, self.fighters):
            layer.clear()

        self.debug_shapes = False
        self.debug_collisions = False
        self.debug_boundary_stepback = False
        self.debug_avoided_boundary_stepback = False
        assert len(self.animated_shapes_debugger) is 0
        assert len(self.static_shapes_debugger) is 0

    def set_district(self, district):

        self.set_background_image(district.wallpaper)  # resize the playground
        # self.blocks.set_col_width(district.block_size[0])
        # self.blocks.set_row_height(district.block_size[1])
        # self.blocks.set_nbrows(district.nbrows)
        # self.blocks.set_nbcols(district.nbcols)
        self._district = district
        self._space = self.district.space

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

    def toggle_debug_shapes(self):

        self.debug_shapes = not self.debug_shapes
        if self.debug_shapes:
            self._debug_shapes_of(self.space.static_body)
        else:
            for widget in self.animated_shapes_debugger + self.static_shapes_debugger:
                widget.kill()



    def find_cases_libres(self):
        """
        Methode qui lit self.grid et en fait self.empty_cells
        self.empty_cells est une grille dont les cases font 16*16
        Appuyer sur TAB dans la fen PLAY permet d'avoir une vue de self.empty_cells
        ATTENTION : Adapte aux sprinters seulement
        0 : vide
        1 : bloc
        2 : jump
        3 : jump & axel
        4 : axel
        """
        # On cree une grille qui correspond aux blocs de 15px
        self.empty_cells = []
        x_tot, y_tot = self.nbcols * 2, self.nbrows * 2
        for i in range(y_tot):
            self.empty_cells.append([0] * x_tot)
        # Pour chaque case, les tests considerent qu'on y place le bottomleft d'un sprinter

        # larg est la largeur du sprinter en nb de cases
        larg = 3
        haut = 4

        # Si le sprinter rencontre un bloc a effet, on l'ecrit
        for bloc in self.grp_bloc_effet:
            num = 2 if bloc.name == "jump" else 4
            x, y = int(bloc.rect.centerx / 16), int(bloc.rect.top / 16)
            for i2 in range(larg + 1):
                for j2 in range(haut + 1):
                    # On utilise x - i2 car la case correspond au bottomleft
                    if 0 <= x - i2 < x_tot and 0 <= y + j2 < y_tot:
                        ref = self.empty_cells[y + j2][x - i2]
                        if ref in (2, 4) and ref != num:
                            self.empty_cells[y + j2][x - i2] = 3
                        elif ref == 0:
                            self.empty_cells[y + j2][x - i2] = num

        # Si le sprinter rencontre un bloc, on ecrit 1
        for bloc in self.grp_bloc:
            for i in (0, 16):
                for j in (0, 16):
                    if bloc.rect.collidepoint(bloc.rect.left + i, bloc.rect.top + j):

                        # Alors on met 1 partout ou le sprinter rencontrera ce bloc
                        x, y = int((bloc.rect.left + i) / 16), int((bloc.rect.top + j) / 16)
                        for i2 in range(larg):
                            for j2 in range(haut):
                                # On utilise x - i2 car la case correspond au bottomleft
                                if 0 <= x - i2 < x_tot and 0 <= y + j2 < y_tot:
                                    self.empty_cells[y + j2][x - i2] = 1
        # On rajoute une colonne de 1 sur le mur de droite
        for line in self.empty_cells:
            line[-larg + 1:] = [1] * (larg - 1)

    def case_stand(self, x, y):
        """
        Methode qui permet de savoir si un sprinter peut rester en STANDING en x, y
        pour une case de coord x, y sur la grille self.empty_cells
        ATTENTION : self.empty_cells est en 16*16 alors que self.grid est en 32*32
        :param x: L'abscisse de la case
        :param y: L'ordonnee de la case
        :return: True si la case correspond a de l'air ou un axel au-dessus d'un bloc ou du sol
                 False sinon
        """
        # Si self.empty_cells[y][x] correspond a de l'air ou un axel
        # Et si self.empty_cells[y+1][x] correspond a un bloc ou au sol
        return self.empty_cells[y][x] in (0, 4) and (y + 1 == self.nbrows * 2 or self.empty_cells[y + 1][x] == 1)

    def case_start_jump(self, x, y):
        """
        Methode qui permet de savoir si un sprinter peut commencer un saut en x, y
        ATTENTION : self.empty_cells est en 16*16 alors que self.grid est en 32*32
        :param x: L'abscisse de la case
        :param y: L'ordonnee de la case
        :return: True si la case correspond a de l'air, un jump ou un axel au-dessus d'un bloc ou du sol
                 False sinon
        """
        # Si self.empty_cells[y][x] correspond a un jump
        # Ou si self.empty_cells[y][x] est une case_stand()
        return self.empty_cells[y][x] in (2, 3) or self.case_stand(x, y)

    def sauvegarder(self):
        """
        Methode qui enregistre le terrain dans son fichier texte
        Ne devrait etre appele que lorsqu'on quitte la fen MAPING
        """
        # On cree une copie de self.grid
        grid = []
        for i in range(self.nbrows):
            grid.append(self.grid[i].copy())

        # On insere les positions des joueurs
        grid.append([str(self.fighters_pos[0][0]), str(self.fighters_pos[0][1]),
                     str(self.fighters_pos[1][0]), str(self.fighters_pos[1][1]),
                     str(self.fighters_pos[2][0]), str(self.fighters_pos[2][1])])
        # On le met dans le format du fichier texte
        for i in range(len(grid)):
            grid[i] = "'".join(grid[i])
        grid = "\n".join(grid)

        # On le met dans le fichier texte
        fichier_text = open(self.filepath, "w")
        fichier_text.write(grid)
        fichier_text.close()
        bp.pygame.image.save(self.surface, f"lib/images/terrains/{self.name}.png")

    def save_img(self):
        """
        Methode qui enregistre une image du terrain dans le dossier Districts
        """
        bp.pygame.image.save(self.surface, f"lib/images/terrains/{self.name}.png")
        # bp.pygame.image.save(self.wallpaper, f"lib/images/wallpapers/{self.name}.png")

    def update_wallpaper(self):
        """
        Methode qui cree un landscape adapte aux dimensions du terrain
        """
        wallpaper = im.load(f"wallpapers/{name}")

        def arrondir(x, d=32, mult=True):
            """
            Renvoi le plus grand multiple de d inferieur ou egal a x
            Si mult=False, renvoi combien de fois d est dans x
            """
            return d * int(x / d) if mult else int(x / d)

        largeur = arrondir(wallpaper.get_width())
        hauteur = arrondir(wallpaper.get_height())

        self.wallpaper = bp.pygame.Surface(self.size)
        self.wallpaper.blit(wallpaper.subsurface(0, 0, largeur, hauteur), (0, 0))

        # Si le terrain est plus haut que landscape
        for i in range(self.nbrows - 18):
            self.wallpaper.blit(wallpaper.subsurface(0, hauteur - 32, largeur, 32), (0, hauteur + i * 32))

        # Si le terrain est plus large que landscape
        if self.nbcols > largeur / 32:
            for i in range(int(self.nbcols / largeur * 32)):
                sub = self.wallpaper.copy().subsurface(0, 0, largeur, self.nbrows * 32)
                self.wallpaper.blit(sub, (largeur * (i + 1), 0))

    def create_ptt_ter(self):
        """
        Methode qui cree une petite image de ter pour la fen MENU
        """
        apercu = pygame.Surface((self.nbcols * 32, self.nbrows * 32))
        apercu.blit(self.wallpaper, (0, 0))

        self.grp_bloc.draw(apercu)
        for bloc in self.grp_bloc_effet:
            apercu.blit(bloc.image[0], bloc.rect.topleft)
        for i in range(3):
            apercu.blit(im.sprinter[i][1][0], self.fighters_pos[i])

        w = 30 * 8
        h = int(self.nbrows / self.nbcols * w)
        im_ptt_ter = im.redimensionner(apercu, w, h)

        self.ptt_ter = Object(image=im_ptt_ter, rect=im_ptt_ter.get_rect(), cadre=im.create_cadre(w + 20, h + 20))

    def redimensionner(self, x1, y1, x2, y2):
        """
        Methode qui redimensionne le terrain
        :param x1: Ajouter/Supprimer une colonne a gauche
        :param y1: Ajouter/Supprimer une ligne en haut
        :param x2: Ajouter/Supprimer une colonne a droite
        :param y2: Ajouter/Supprimer une ligne en bas
        """

        for groupe in (self.grp_bloc, self.grp_bloc_effet):
            for bloc in groupe:
                bloc.rect.left += x1
                bloc.rect.top += y1
        for bloc in self.grp_poseur:
            bloc.rect_bonus.left += x1
            bloc.rect_bonus.top += y1
        for btn in jeu.maping.grp_btn_hotbar:
            btn.move(0, y1 + y2)
        for btn in jeu.play.grp_btn_res:
            btn.move((x1 + x2) / 2, (y1 + y2) / 2)

        jeu.define_rect_fen()
        for pers in jeu.grp_pers:
            pers.rect.left += x1
            pers.rect.top += y1
            pers.rect = pers.rect.clamp(jeu.rect_jeu)
            if pers.rect.right == jeu.rect_jeu.right:
                pers.rect.left = jeu.rect_jeu.right - 64
            if pers.rect.bottom == jeu.rect_jeu.bottom:
                pers.rect.top = jeu.rect_jeu.bottom - 64
        self.fighters_pos = [vert.rect.topleft, rouge.rect.topleft, bleu.rect.topleft]
        jeu.maping.right_clic_big_rect.size = self.nbcols * 8 + 120, self.nbrows * 8 + 120
        jeu.maping.right_clic_lit_rect.size = self.nbcols * 8 + 40, self.nbrows * 8 + 40
        jeu.maping.hotbar.top += y1 + y2
        self.cadre_maping = im.create_cadre(self.nbcols * 8 + 40, self.nbrows * 8 + 40)
        self.update_wallpaper()
        self.create_ptt_ter()
        self.sauvegarder()
        # On a pas besoin de recreer ptt_ter, il sera cree quand on quittera la fen MAPING
