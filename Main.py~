# coding=utf-8

import math
import pygame
import time
import datetime
import codecs
import getpass
from configparser import ConfigParser

pygame.init()

class state:
    lock = 'state.lock'
    home = 'state.home'

class slo:
    # slo = configparser_parse('./slo/slo.ini')
    # bucker = configparser_parse('./slo/bucker.ini')
    slo = None
    bucker = None

    lastest = None

    @staticmethod
    def configparser_parse(path):
        config = ConfigParser()
        # config.read(path)
        config.readfp(codecs.open(path, 'r', encoding='utf-8'))

        result = {}

        for section in config.sections():
            result[section] = {}
            for key in config[section].keys():
                result[section][key] = eval(config[section][key])

        return result

    @staticmethod
    def configparser_write(path, value: dict):
        cfgfile = open(path, 'w', encoding='utf-8')
        config = ConfigParser()

        for key in value.keys():
            config.add_section(key)
            for name in value[key].keys():
                if type(value[key][name]) == str:
                    config.set(key, name, f'\'{value[key][name]}\'')
                else:
                    config.set(key, name, str(value[key][name]))

        config.write(cfgfile)
        cfgfile.close()

    @staticmethod
    def load():
        slo.slo = slo.configparser_parse('./slo/slo.ini')
        slo.bucker = slo.configparser_parse('./slo/bucker.ini')
        slo.lastest = slo.configparser_parse('./slo/lastest.ini')

    @staticmethod
    def save():
        slo.configparser_write('./slo/slo.ini', slo.slo)
        slo.configparser_write('./slo/bucker.ini', slo.bucker)
        slo.configparser_write('./slo/lastest.ini', slo.lastest)

        print('changed')

slo.load()

this_username = getpass.getuser()
if this_username != slo.lastest['user']['username']:
    slo.lastest['user']['username'] = this_username
    current_main_display = pygame.display.Info()
    slo.slo['display']['size'] = (current_main_display.current_w, current_main_display.current_h)
    slo.slo['display']['fullscreen'] = True

class root:
    class display:
        size = slo.slo['display']['size']
        fps = slo.slo['display']['fps']
        display_fps = None

        pygame.display.set_caption(slo.slo['display']['caption'])
        pygame.display.set_icon(pygame.image.load(slo.slo['display']['icon_path']))
    exit = False

    @staticmethod
    def quit(*_):
        root.exit = True

    window = None
    if slo.slo['display']['fullscreen']:
        window = pygame.display.set_mode(display.size, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    else:
        window = pygame.display.set_mode(display.size)

    state = None

class keyboard:
    lalt = False
    ralt = False
    space = False
    escape = False

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

def remove_object_by_type(_type):
    for obj in objects:
        if type(obj) == _type:
            obj.destroy()

def add_object(_obj):
    objects.append(_obj)

class RootObject(object):
    highlight = None

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

class LockScreen(RootObject):
    time_surface: pygame.Surface
    time_position: tuple
    date_surface: pygame.Surface
    date_position: tuple

    def __init__(self, colour_text, colour_background, font=slo.slo['appearance']['font']):
        self.color_text = colour_text
        self.color_background = colour_background

        self.text_format_time = TextFormat(font, root.display.size[1] // 5, self.color_text)
        self.text_format_date = TextFormat(font, root.display.size[1] // 20, self.color_text)

        self.x = 0
        self.x_target = 0

        self.lock = True

        self.click_start_position = cursor.position
        self.clicking = False

        self.background = pygame.Surface(root.display.size)
        self.background.fill(self.color_background)

        immediate = str(datetime.datetime.now())
        self.date = immediate.split()[0].split('-')[1:]
        self.time = immediate.split()[1].split(':')[:2]

        self.date_surface = self.text_format_date.render('월 '.join(self.date) + '일')
        self.date_position = (self.text_format_date.size + self.x, root.display.size[1] - self.text_format_date.size - self.date_surface.get_height())

        self.time_surface = self.text_format_time.render(':'.join(self.time))
        self.time_position = (self.date_position[0] + self.x, self.date_position[1] - self.time_surface.get_height() + 36)

    def tick(self):
        if self.x != root.display.size[0]:
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
                        offset = 0

                    if offset >= 5:
                        self.x_target = root.display.size[0]
                        self.lock = False
                    else:
                        self.x_target = 0

            if self.x_target != self.x and root.display.display_fps is not None:
                self.x += (self.x_target - self.x) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
                if math.fabs(self.x_target - self.x) < 0.1:
                    self.x = self.x_target

            immediate = str(datetime.datetime.now())
            now_date = immediate.split()[0].split('-')[1:]
            now_time = immediate.split()[1].split(':')[:2]

            if now_date != self.date or now_time != self.time:
                self.date_surface = self.text_format_date.render('월 '.join(self.date) + '일')
                self.time_surface = self.text_format_time.render(':'.join(self.time))

            if self.x < root.display.size[0]:
                self.date_position = (self.text_format_date.size + self.x * 2, root.display.size[1] - self.text_format_date.size - self.date_surface.get_height())
                self.time_position = (self.date_position[0] + self.x, self.date_position[1] - self.time_surface.get_height() + 36)
        else:
            change_state(state.home)
            self.destroy()

    def render(self):
        root.window.blit(self.background, (self.x, 0))

        if self.x < root.display.size[0]:
            root.window.blit(self.date_surface, self.date_position)
            root.window.blit(self.time_surface, self.time_position)

def center(x, y):
    return (x - y) / 2

class Shutdown(RootObject):
    gui = 'Shutdown.mode.GUI'
    immediate = 'Shutdown.mode.IMMEDIATE'

    class Button(RootObject):
        text_format = TextFormat(slo.slo['appearance']['font'], 18, color.text)

        def __init__(self, surface, text, action, shutdown):
            self.surface = surface
            self.text = text
            self.command = action[0]
            self.argument = action[1:]
            self.shutdown = shutdown

            self.x, self.y = 0, 0

            if self.surface.get_width() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (72, self.surface.get_height()))
            if self.surface.get_height() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (self.surface.get_width(), 72))

            self.text_surface = self.text_format.render(self.text)
            self.text_x, self.text_y = 0, 0

        def tick(self):
            if self.shutdown.moving:
                self.x = center(root.display.size[0], 108 * len(self.shutdown.buttons) - 36) + 108 * self.shutdown.buttons.index(self)
                self.y = center(root.display.size[1], 108) + self.shutdown.y * 2

                self.text_x = center(root.display.size[0], len(self.shutdown.buttons) * 108 - 36) - self.text_surface.get_width() / 2 + 108 * self.shutdown.buttons.index(self) + 36
                self.text_y = center(root.display.size[1], 108) + 108 - self.text_surface.get_height() + self.shutdown.y * 3

            if cursor.epressed[0]:
                if self.x <= cursor.position[0] <= self.x + 72 and self.y <= cursor.position[1] <= self.y + 72:
                    self.command(*self.argument)

        def render(self):
            root.window.blit(self.surface, (self.x, self.y))
            root.window.blit(self.text_surface, (self.text_x, self.text_y))

    def __init__(self, mode=gui):
        self.mode = mode

        self.moving = True
        self.y = -root.display.size[1]
        self.target_y = 0

        self.background = pygame.Surface(root.display.size)

        self.buttons = []
        self.buttons.append(self.Button(pygame.image.load('./res/image/lock.png'), '잠금 화면', (change_state, state.lock), self))
        self.buttons.append(self.Button(pygame.image.load('./res/image/shutdown.png'), '시스템 종료', (root.quit,), self))

        self.back_button_surface = pygame.transform.smoothscale(pygame.image.load('./res/image/left_arrow.png'), (32, 32))
        self.back_button_surface.convert()
        self.back_button_position = [16, 16]

        RootObject.highlight = Shutdown

    def tick(self):
        if self.mode == self.immediate:
            root.quit()
            self.destroy()

        if self.moving:
            self.y += (self.target_y - self.y) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])

        for button in self.buttons:
            button.tick()

        self.back_button_position[1] = 16 + self.y
        if cursor.epressed[0] and self.back_button_position[0] <= cursor.position[0] <= self.back_button_position[0] + self.back_button_surface.get_width() and self.back_button_position[1] <= cursor.position[1] <= self.back_button_position[1] + self.back_button_surface.get_height() or keyboard.escape:
            self.quit()

        if self.y <= -root.display.size[1] - 1:
            self.destroy()

    def render(self):
        root.window.blit(self.background, (0, self.y))

        for button in self.buttons:
            button.render()

        root.window.blit(self.back_button_surface, self.back_button_position)

    def quit(self):
        self.target_y = -root.display.size[1] - 1.5
        self.moving = True

    def destroy(self):
        RootObject.highlight = None
        super().destroy()

class Bucker(RootObject):
    class DockItem(RootObject):
        def __init__(self, surface, action, dock_bucker):
            self.surface = surface
            self.command = action[0]
            self.argument = action[1:]
            self.dock_bucker = dock_bucker

            self.original_y = 11
            self.original_x = 20 + len(self.dock_bucker.dock_items) * 92

            if self.surface.get_width() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (72, self.surface.get_height()))
            if self.surface.get_height() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (self.surface.get_width(), 72))
            self.surface.convert()

            self.x = self.original_x
            self.y = self.original_y

        def tick(self):
            if cursor.epressed[0]:
                if self.x <= cursor.position[0] <= self.x + self.surface.get_width() and self.y <= cursor.position[1] <= self.y + self.surface.get_height():
                    if self.command == add_object:
                        self.command(self.argument[0]())
                    else:
                        self.command(*self.argument)

            self.x = self.original_x + self.dock_bucker.dock_x
            self.y = self.original_y + self.dock_bucker.dock_y

        def render(self):
            root.window.blit(self.surface, (self.x, self.y))

    def __init__(self):
        # text_format = TextFormat('./res/font/consola.ttf', 72, color.text)

        self.background_image = pygame.transform.smoothscale(pygame.image.load(slo.bucker['background']['image_path']), (slo.slo['display']['size'][0], slo.slo['display']['size'][1])).convert()

        self.dock_items = []
        self.dock_items.append(self.DockItem(pygame.image.load('./res/image/shutdown.png'), (add_object, Shutdown), self))

        self.dock_width = len(self.dock_items) * 92 + 20
        self.dock_height = 92
        self.dock_x = center(root.display.size[0], self.dock_width)
        self.dock_y = root.display.size[1]
        self.dock_y_target = root.display.size[1]
        self.dock_color = color.gray

    def tick(self):
        if root.state != state.lock:
            self.dock_y_target = root.display.size[1] - self.dock_height

        if self.dock_y_target != self.dock_y and root.display.display_fps is not None:
            self.dock_y += (self.dock_y_target - self.dock_y) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.dock_y_target - self.dock_y) < 0.1:
                self.dock_y = self.dock_y_target

        for item in self.dock_items:
            item.tick()

    def render(self):
        if slo.bucker['background']['type'] == 'solid':
            root.window.fill(slo.bucker['background']['color'])
        else:
            root.window.blit(self.background_image, (0, 0))

        pygame.draw.rect(root.window, self.dock_color, ((self.dock_x, self.dock_y), (self.dock_width, self.dock_height)))

        for item in self.dock_items:
            item.render()

class Window(RootObject):
    pass

class HUD(RootObject):
    state_surface: pygame.Surface
    fps_surface: pygame.Surface
    objects_surface: pygame.Surface
    text_format = TextFormat('./res/font/consola.ttf', 20, color.text)

    def tick(self):
        self.fps_surface = self.text_format.render(str(root.display.display_fps) + ' FPS')
        self.state_surface = self.text_format.render(str(root.state) + ' STATE')
        self.objects_surface = self.text_format.render(str(len(objects)) + ' OBJECT')

    def render(self):
        root.window.blit(self.fps_surface, (0, 0))
        root.window.blit(self.state_surface, (0, 20))
        root.window.blit(self.objects_surface, (0, 40))

hud = None
if slo.slo['display']['hud']:
    hud = HUD()

def change_state(next_state):
    root.state = next_state

    if root.state == state.lock:
        remove_object_by_type(Shutdown)

        add_object(Bucker())
        add_object(LockScreen(color.text, color.background))

change_state(state.lock)

delta = 0
delta2 = 0
delta2_count = 0

now = time.time()
if root.display.fps is not None:
    time_per_tick = 1 / root.display.fps

while not root.exit:
    pnow = now
    now = time.time()
    delta2 += now - pnow

    if delta2 >= 1:
        root.display.display_fps = delta2_count
        delta2 -= 1
        delta2_count = 0

    if delta >= 1 or root.display.fps is None:
        delta -= 1
        delta2_count += 1

        cursor.position = pygame.mouse.get_pos()
        cursor.ppressed = cursor.pressed
        cursor.pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                root.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RALT:
                    keyboard.ralt = True
                elif event.key == pygame.K_LALT:
                    keyboard.lalt = True
                elif event.key == pygame.K_F4:
                    if keyboard.lalt or keyboard.ralt:
                        root.quit()
                elif event.key == pygame.K_SPACE:
                    keyboard.space = True
                elif event.key == pygame.K_ESCAPE:
                    keyboard.escape = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RALT:
                    keyboard.ralt = False
                elif event.key == pygame.K_LALT:
                    keyboard.lalt = False
                elif event.key == pygame.K_SPACE:
                    keyboard.space = False
                elif event.key == pygame.K_ESCAPE:
                    keyboard.escape = False

        for i in range(3):
            cursor.fpressed[i] = not cursor.ppressed[i] and cursor.pressed[i]
            cursor.epressed[i] = cursor.ppressed[i] and not cursor.pressed[i]

        root.window.fill(color.background)
        for obj in objects:
            if type(obj) == RootObject.highlight or RootObject.highlight is None:
                obj.tick()
        if slo.slo['display']['hud']: hud.tick()

        for obj in objects:
            obj.render()
        if slo.slo['display']['hud']: hud.render()
        pygame.display.update()

    else:
        delta += (now - pnow) / time_per_tick
pygame.quit()
slo.save()
