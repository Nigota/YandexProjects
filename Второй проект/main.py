""" This is where the game starts """

import pygame
import os
import sys
from random import randint, shuffle

from tools.Sprites import *
from tools.Constants import *

pygame.init()  # start pygame

pygame.time.set_timer(pygame.USEREVENT, 1000)  # internal timer activation
pygame.display.set_caption('Пиратский pacman')
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()


def terminate():
    """ Closing the program. """
    pygame.quit()
    sys.exit()


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


def load_map(filename):
    """ Return map's params. """
    filename = os.path.join('data', 'maps', filename)
    filename = resource_path(filename)

    # если файл не существует, то выходим
    if not os.path.isfile(filename):
        print(f"Файл '{filename}' не найден")
        terminate()

    with open(filename, 'r') as f:
        data = list()
        lines = dict()
        for row in map(str.strip, f.readlines()):
            lst = list()
            for j in row:
                if j != '#':
                    lines[j] = False
                lst.append(j)
            data.append(lst)

    map_width = len(data[0])
    map_height = len(data)

    return map_width, map_height, data, lines


def load_image(name, color_key=None):
    """ Return pygame image. """
    fullname = os.path.join('data', 'images', name)
    fullname = resource_path(fullname)

    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        terminate()

    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()

    return image


def rendered_text(text, coord, color, centered=False):
    """ Convert text to pygame string.

     Return pygame string and string's rectangle.
    """
    font = pygame.font.Font(None, 30)
    string = font.render(text, True, color)
    rect = string.get_rect()
    rect.top = coord
    if centered:
        rect.x = (WIDTH - rect.width) // 2
    else:
        rect.x = 20
    return string, rect


def start_screen():
    # текст на экране
    intro_text = ["ПИРАТСКИЙ PACMAN", "",
                  "Правила игры",
                  "Вы соединяете все квадраты одного цвета,",
                  "пакман начинает кушать яболки",
                  "всё просто :)", "",
                  "P.S время ограничено, постарайтесь",
                  "собрать как можно больше яболок", "",
                  "РЕЖИМЫ (нажми клавишу)", "1 - легкий",
                  "2 - средний", "3 - сложный"]

    # задний фон
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    # отрисовка текста
    color = pygame.Color('white')
    text_coord = 50
    centered = True
    for line in intro_text:
        if line == 'РЕЖИМЫ (нажми клавишу)':
            centered = False
        text_coord += 10
        string_rendered, intro_rect = rendered_text(line, text_coord, color, centered)
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    # ждем действия пользователя
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                # выбор режима сложности
                if event.key == pygame.K_1:
                    return 1
                elif event.key == pygame.K_2:
                    return 2
                elif event.key == pygame.K_3:
                    return 3
        pygame.display.flip()
        clock.tick(FPS)


def end_screen(score):
    # текст на экране
    intro_text = ["ПИРАТСКИЙ PACMAN", "",
                  "Время вышло!", "", "", "", "", "", "",
                  f"Ваш счет {score}", "",
                  "Нажмите 'пробел', чтобы сыграть еще раз", "",
                  "Нажмите любую клавишу, чтобы закрыть игру"]

    # задний фон
    fon = pygame.transform.scale(load_image('game over.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    # отрисовка текста
    color = pygame.Color('white')
    text_coord = 50
    for line in intro_text:
        text_coord += 10
        string_rendered, intro_rect = rendered_text(line, text_coord, color, True)
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    # ждем действия пользователя
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                return False
        pygame.display.flip()
        clock.tick(FPS)


def draw_text(surface, pos_x, pos_y, text, size):
    """ Draw text on screen """
    font = pygame.font.Font(None, size)
    string = font.render(text, True, (0, 0, 0))
    text_x = pos_x - string.get_width()
    text_y = pos_y
    surface.blit(string, (text_x, text_y))


def create_apple(mod, start, player, *groups):
    """ Add apple's image on main screen  """
    apple_image = load_image('apple.png')
    if mod in [1, 2]:
        cnt = 3
    else:
        cnt = randint(1, 3)
    for i in range(cnt):
        Apple(apple_image, start + 50 * i, 70, player, *groups)


def main(mod):
    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    board_sprites = pygame.sprite.Group()
    bg_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    apple_group = pygame.sprite.Group()

    # создание сцены
    # добавление заднего фона
    bg1 = Background(load_image('background.png'), HERO_AREA, bg_sprites, all_sprites)
    bg2 = Background(load_image('background.png'), HERO_AREA, bg_sprites, all_sprites)
    bg2.rect = bg2.rect.move(WIDTH, 0)
    # создание персонажа
    player = Player(load_image('pacman.png', -1), 6, 11, 20, 50, apple_group, player_group)
    # добавление яблок
    create_apple(mod, 300, apple_group, all_sprites)
    create_apple(mod, 800, apple_group, all_sprites)

    # загрузка всех карт и их перемешивание
    maps = os.listdir(os.path.join('data', 'maps'))
    shuffle(maps)

    # создание игральной доски
    m = 0
    board = Board(*load_map(maps[m]), board_sprites, all_sprites)
    board.set_view((WIDTH - board.width * 50) // 2, HERO_AREA[1], 50)

    # настройка времени
    if mod == 1:
        last_time = 60
    else:
        last_time = 30

    draw = False
    win = False

    while True:

        if last_time < 1:
            return player.cnt_apples

        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                last_time -= 1

            if event.type == pygame.QUIT:
                terminate()

            if not win and event.type == pygame.MOUSEBUTTONDOWN:
                draw = True
                board.get_click(event.pos)  # запуск рисования (если возможно)

            if event.type == pygame.MOUSEBUTTONUP:
                draw = False
                board.erase_color()  # очистка

            if draw and event.type == pygame.MOUSEMOTION:
                board.get_click(event.pos)  # рисование

        if board.check_win():  # проверка на выйгрыш
            win = True

        # обновление экрана
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (135, 98, 59), (0, 200, WIDTH, HEIGHT - 175))
        board_sprites.update()
        all_sprites.draw(screen)
        # приходится отрисовывать героя отдельно, чтобы он был на переднем плане
        player_group.draw(screen)
        draw_text(screen, WIDTH - 20, 10, str(player.cnt_apples), 50)
        draw_text(screen, WIDTH // 2, 10, str(last_time), 70)

        # действия при завершении уровня
        if win:
            # анимация объектов
            apple_group.update()
            bg_sprites.update()
            player_group.update()
            # запуск нового уровня
            if bg1.rect.x == 0 or bg2.rect.x == 0:
                win = False
                m = (m + 1) % len(maps)
                board.reload(*load_map(maps[m]))
                board.set_view((WIDTH - board.width * 50) // 2, HERO_AREA[1], 50)
                create_apple(mod, 800, apple_group, all_sprites)

                if mod == 1:
                    last_time += 7
                elif mod == 2:
                    last_time += 5
                else:
                    last_time += 3

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    mod = 0
    score = 0
    restart = False
    while True:
        mod = start_screen()
        score = main(mod)
        restart = end_screen(score)

        if not restart:
            terminate()
