# coding=utf-8

import math
import pygame
import time
import datetime
from configparser import ConfigParser

pygame.init()

class state:
    lock = 'state.lock'
    home = 'state.home'

def configparser_parse(path):
    config = ConfigParser()
    config.read(path)

    result = {}

    for section in config.sections():
        result[section] = {}
        for key in config[section].keys():
            result[section][key] = eval(config[section][key])

    return result

class slo:
    slo = configparser_parse('./slo/slo.ini')
    bucker = configparser_parse('./slo/bucker.ini')

class game:
    class display:
        size = slo.slo['display']['size']
        fps = slo.slo['display']['fps']
        display_fps = fps

        pygame.display.set_caption(slo.slo['display']['caption'])
        pygame.display.set_icon(slo.slo['display']['icon'])
    exit = False

    window = None
    if slo.slo['display']['fullscreen']:
        window = pygame.display.set_mode(display.size, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    else:
        window = pygame.display.set_mode(display.size)

    state = None

slo.bucker['background']['image'] = pygame.transform.smoothscale(pygame.image.load(slo.bucker['background']['image_path']), (slo.slo['display']['size'][0], slo.slo['display']['size'][1])).convert()

class keyboard:
    lalt = False
    ralt = False
    space = False

class cursor:
    position = pygame.mouse.get_pos()
    ppressed = pressed = pygame.mouse.get_pressed()

    fpressed = list(pressed)
    epressed = list(pressed)

class color:
    background = (31, 33, 37)
    text = (222, 222, 222)
    gray = (127, 127, 127)

objects = []

def add_object(_obj):
    objects.append(_obj)

class GameObject(object):
    def tick(self):
        pass

    def render(self):
        pass

    def destroy(self):
        objects.remove(self)

class TextFormat:
    def __init__(self, font, size, colour):
        self.font = font
        self.size = size
        self.color = colour

        self.font = pygame.font.Font(self.font, self.size)

    def render(self, text):
        return self.font.render(text, True, self.color)

class LockScreen(GameObject):
    time_surface: pygame.Surface
    time_position: tuple
    date_surface: pygame.Surface
    date_position: tuple

    def __init__(self, colour_text, colour_background, font='./res/font/AppleSDGothicNeoSB.ttf'):
        self.color_text = colour_text
        self.color_background = colour_background

        self.text_format_time = TextFormat(font, game.display.size[1] // 5, self.color_text)
        self.text_format_date = TextFormat(font, game.display.size[1] // 20, self.color_text)

        self.x = 0
        self.x_target = 0

        self.lock = True

        self.click_start_position = None
        self.clicking = False

        self.background = pygame.Surface(game.display.size)
        self.background.fill(self.color_background)

        immediate = str(datetime.datetime.now())
        self.date = immediate.split()[0].split('-')[1:]
        self.time = immediate.split()[1].split(':')[:2]

        self.date_surface = self.text_format_date.render('월 '.join(self.date) + '일')
        self.date_position = (self.text_format_date.size + self.x, game.display.size[1] - self.text_format_date.size - self.date_surface.get_height())

        self.time_surface = self.text_format_time.render(':'.join(self.time))
        self.time_position = (self.date_position[0] + self.x, self.date_position[1] - self.time_surface.get_height() + 36)

    def tick(self):
        if self.x != game.display.size[0]:
            if self.lock:
                if cursor.fpressed[0]:
                    self.click_start_position = cursor.position
                    self.clicking = True

                if self.clicking:
                    self.x_target = -min(0, self.click_start_position[0] - cursor.position[0])

                if cursor.epressed[0]:
                    self.clicking = False

                    x_offset = cursor.position[0] - self.click_start_position[0]
                    y_offset = math.fabs(cursor.position[1] - self.click_start_position[1])

                    try:
                        offset = x_offset / y_offset
                    except ZeroDivisionError:
                        offset = 5

                    if offset >= 5:
                        self.x_target = game.display.size[0]
                        self.lock = False
                    else:
                        self.x_target = 0

            if self.x_target != self.x and game.display.display_fps is not None:
                self.x += (self.x_target - self.x) / (game.display.display_fps / 6)
                if math.fabs(self.x_target - self.x) < 0.1:
                    self.x = self.x_target

            immediate = str(datetime.datetime.now())
            now_date = immediate.split()[0].split('-')[1:]
            now_time = immediate.split()[1].split(':')[:2]

            if now_date != self.date or now_time != self.time:
                self.date_surface = self.text_format_date.render('월 '.join(self.date) + '일')
                self.time_surface = self.text_format_time.render(':'.join(self.time))

            if self.x < game.display.size[0]:
                self.date_position = (self.text_format_date.size + self.x * 2, game.display.size[1] - self.text_format_date.size - self.date_surface.get_height())
                self.time_position = (self.date_position[0] + self.x, self.date_position[1] - self.time_surface.get_height() + 36)
        else:
            change_state(state.home)
            self.destroy()

    def render(self):
        game.window.blit(self.background, (self.x, 0))

        if self.x < game.display.size[0]:
            game.window.blit(self.date_surface, self.date_position)
            game.window.blit(self.time_surface, self.time_position)

def center(x, y):
    return (x - y) / 2

class Shutdown(GameObject):
    gui = 'Shutdown.mode.GUI'
    immediate = 'Shutdown.mode.IMMEDIATE'

    def __init__(self, mode='IMMEDIATE'):
        self.mode = mode

        if self.mode == self.immediate:
            game.exit = True
            self.destroy()

class Bucker(GameObject):
    class DockItem(GameObject):
        def __init__(self, surface, action, x, y, dock_bucker):
            self.surface = surface
            self.command = action[0]
            self.argument = action[1:]
            self.original_x = x
            self.original_y = y
            self.dock_bucker = dock_bucker
            
            self.x = self.original_x
            self.y = self.original_y

        def tick(self):
            if cursor.epressed[0]:
                if self.x <= cursor.position[0] <= self.x + self.surface.get_width() and self.y <= cursor.position[1] <= self.y + self.surface.get_height():
                    self.command(*self.argument)
                    print('asd')

            self.x = self.original_x + self.dock_bucker.dock_x
            self.y = self.original_y + self.dock_bucker.dock_y

        def render(self):
            game.window.blit(self.surface, (self.x, self.y))

    def __init__(self):
        self.dock_width = game.display.size[0] / 4 * 3
        self.dock_height = game.display.size[1] / 15
        self.dock_x = center(game.display.size[0], self.dock_width)
        self.dock_y = game.display.size[1]
        self.dock_y_target = game.display.size[1]
        self.dock_color = color.gray

        text_format = TextFormat('./res/font/consola.ttf', 72, color.text)

        self.dock_items = [self.DockItem(text_format.render('SD'), (add_object, Shutdown()), 10, 10, self)]

    def tick(self):
        if game.state != state.lock:
            self.dock_y_target = game.display.size[1] - self.dock_height

        if self.dock_y_target != self.dock_y and game.display.display_fps is not None:
            self.dock_y += (self.dock_y_target - self.dock_y) / (game.display.display_fps / 6)
            if math.fabs(self.dock_y_target - self.dock_y) < 0.1:
                self.dock_y = self.dock_y_target

        for item in self.dock_items:
            item.tick()

    def render(self):
        if slo.bucker['background']['type'] == 'solid':
            game.window.fill(slo.bucker['background']['color'])
        else:
            game.window.blit(slo.bucker['background']['image'], (0, 0))

        pygame.draw.rect(game.window, self.dock_color, ((self.dock_x, self.dock_y), (self.dock_width, self.dock_height)))

        for item in self.dock_items:
            item.render()

class HUD(GameObject):
    state_surface: pygame.Surface
    fps_surface: pygame.Surface
    text_format = TextFormat('./res/font/consola.ttf', 20, color.text)

    def tick(self):
        self.fps_surface = self.text_format.render(str(game.display.display_fps) + ' FPS')
        self.state_surface = self.text_format.render(str(game.state) + ' STATE')

    def render(self):
        game.window.blit(self.fps_surface, (0, 0))
        game.window.blit(self.state_surface, (0, 20))

hud = None
if slo.slo['display']['hud']:
    hud = HUD()

def change_state(next_state):
    game.state = next_state

    if game.state == state.lock:
        add_object(Bucker())
        add_object(LockScreen(color.text, color.background))

change_state(state.lock)

delta = 0
delta2 = 0
delta2_count = 0

now = time.time()
if game.display.fps is not None:
    time_per_tick = 1 / game.display.fps

while not game.exit:
    pnow = now
    now = time.time()
    delta2 += now - pnow

    if delta2 >= 1:
        game.display.display_fps = delta2_count
        delta2 -= 1
        delta2_count = 0

    if delta >= 1 or game.display.fps is None:
        delta -= 1
        delta2_count += 1

        cursor.position = pygame.mouse.get_pos()
        cursor.ppressed = cursor.pressed
        cursor.pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RALT:
                    keyboard.ralt = True
                elif event.key == pygame.K_LALT:
                    keyboard.lalt = True
                elif event.key == pygame.K_F4:
                    if keyboard.lalt or keyboard.ralt:
                        game.exit = True
                elif event.key == pygame.K_SPACE:
                    keyboard.space = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RALT:
                    keyboard.ralt = False
                elif event.key == pygame.K_LALT:
                    keyboard.lalt = False
                elif event.key == pygame.K_SPACE:
                    keyboard.space = False

        for i in range(3):
            cursor.fpressed[i] = not cursor.ppressed[i] and cursor.pressed[i]
            cursor.epressed[i] = cursor.ppressed[i] and not cursor.pressed[i]

        game.window.fill(color.background)
        for obj in objects:
            obj.tick()
        if slo.slo['display']['hud']: hud.tick()

        for obj in objects:
            obj.render()
        if slo.slo['display']['hud']: hud.render()
        pygame.display.update()

    else:
        delta += (now - pnow) / time_per_tick
pygame.quit()
exit()
