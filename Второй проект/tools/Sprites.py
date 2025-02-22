import pygame


class Board(pygame.sprite.Sprite):
    def __init__(self, width, height, field, lines, *group):
        super().__init__(*group)
        # параметры поля
        self.width = width
        self.height = height
        self.board = field
        self.lines = lines
        # значения по умолчанию
        self.cell_size = 30
        self.left = 5
        self.top = 5
        self.color = None
        self.cell_start = None
        self.cell_crnt = None
        # создание спрайта
        self.image = pygame.Surface((self.width * self.cell_size + self.left,
                                     self.height * self.cell_size + self.top))
        self.rect = self.image.get_rect()

    def set_view(self, x, y, cell_size):
        """ Customize appearance """
        self.cell_size = cell_size
        self.image = pygame.Surface((self.width * self.cell_size + self.left * 2,
                                     self.height * self.cell_size + self.top * 2))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    # отрисовка поля
    def update(self):
        """ Draw a board"""
        self.image.fill((100, 100, 100))
        colors = {'r': 'red', 'b': 'blue', 'y': 'yellow',
                  'g': 'green', 'p': 'purple', '#': 'grey'}

        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                x = self.left + j * self.cell_size
                y = self.top + i * self.cell_size
                tmp = self.board[i][j].lower()

                pygame.draw.rect(self.image, colors[tmp],
                                 (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.image, pygame.Color('white'),
                                 (x, y, self.cell_size, self.cell_size), width=1)

    def get_cell(self, mouse_pos):
        """ Return coords of cell on board """
        img_x, img_y = self.rect.x, self.rect.y
        x = (mouse_pos[0] - self.left - img_x) // self.cell_size
        y = (mouse_pos[1] - self.top - img_y) // self.cell_size
        if 0 <= x < self.width and 0 <= y < self.height:
            return y, x
        return None

    def on_click(self, cell_coords):
        """ Action on click """
        if cell_coords is None:
            return

        if self.color:
            self.draw(cell_coords)
        else:
            self.start_drawing(cell_coords)

    def get_click(self, mouse_pos):
        """ Start action on click """
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def erase_color(self, dop_color=None):
        """ Clear a field of unfinished colors """
        self.cell_start = None
        self.cell_crnt = None
        self.color = None

        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                color = self.board[i][j]

                if dop_color is not None and color == dop_color and self.lines[dop_color.upper()]:
                    self.board[i][j] = '#'

                if color != '#' and color.islower() and not self.lines[color.upper()]:
                    self.board[i][j] = '#'

        if dop_color is not None:
            self.lines[dop_color.upper()] = False

    def draw(self, cell_coords):
        if self.cell_crnt == cell_coords or cell_coords == self.cell_start \
                or self.lines[self.color.upper()]:
            return

        y, x = cell_coords
        y1, x1 = self.cell_crnt
        if abs(y - y1) + abs(x - x1) < 2:
            if self.board[y][x] == '#':
                self.board[y][x] = self.color
            elif self.board[y][x] == self.color or self.board[y][x] != self.color.upper():
                return
            elif self.board[y][x] == self.color.upper():
                self.lines[self.color.upper()] = True
            self.cell_crnt = y, x

    def start_drawing(self, cell_coords):
        self.cell_start = cell_coords
        self.cell_crnt = cell_coords

        y, x = cell_coords
        if self.board[y][x] != '#':
            self.color = self.board[y][x].lower()
            if self.board[y][x].islower() or self.lines[self.color.upper()]:
                self.erase_color(self.board[y][x].lower())

    def check_win(self):
        if all(self.lines.values()):
            return True
        return False

    def restart(self):
        for key in self.lines:
            self.lines[key] = False
        self.erase_color()

    def reload(self, width, height, field, lines):
        """ Reload the board's params """
        # перезаписть параметров поля
        self.width = width
        self.height = height
        self.board = field
        self.lines = lines
        # создание нового спрайта
        self.image = pygame.Surface((self.width * self.cell_size + self.left,
                                     self.height * self.cell_size + self.top))
        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, food_group, *groups):
        super().__init__(*groups)
        self.cnt_apples = 0
        self.food_group = food_group
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.frames = self.frames[:6]
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(pos_x, pos_y)
        self.time_frames = 0

    def cut_sheet(self, sheet, columns, rows):
        """ Cut frames of animation from sheet """
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size))
                frame = pygame.transform.scale(frame, (100, 100))
                self.frames.append(frame)

    def update(self):
        """ Animation """
        food = pygame.sprite.spritecollideany(self, self.food_group)
        if food:
            self.cnt_apples += 1
            food.kill()

        self.time_frames += 1
        if self.time_frames == 8:
            self.time_frames = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class Background(pygame.sprite.Sprite):
    def __init__(self, image, hero_area, *groups):
        super().__init__(*groups)
        self.spawn = hero_area[0]
        self.image = pygame.transform.scale(image, hero_area)
        self.rect = self.image.get_rect()

    def update(self):
        """ Animation """
        self.rect = self.rect.move(-2, 0)
        x, width = self.rect.x, self.rect.width
        if x + width <= 0:
            self.rect.x = self.spawn


class Apple(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def update(self):
        """ Animation """
        self.rect = self.rect.move(-2, 0)
