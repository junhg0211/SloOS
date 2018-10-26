# coding=utf-8

import math
import time
import datetime
import codecs
import getpass
from os import system
from configparser import ConfigParser

try:
    import pygame
except ModuleNotFoundError:
    print('pygame 모듈이 발견되지 않았습니다. pygame 모듈을 다운로드합니다.')
    system('pip install pygame')
    import pygame

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
        config.read_file(codecs.open(path, 'r', encoding='utf-8'))

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

    red = (255, 0, 0)

objects = []

def remove_object_by_type(_type):
    for obj in objects:
        if type(obj) == _type:
            obj.destroy()

def add_object(_obj):
    objects.append(_obj)

def get_ahead_window():
    for i in range(len(objects))[::-1]:
        if type(objects[i]) == BuckerWindow:
            return objects[i]

def get_on_cursor_window():
    banned_areas = []  # [(x, y, width, height)]
    for i in range(len(objects))[::-1]:
        this_object = objects[i]

        try:
            this_object.width
        except AttributeError:
            continue

        banned = False

        if this_object.x <= cursor.position[0] <= this_object.x + this_object.width and this_object.y <= cursor.position[1] <= this_object.y + this_object.height:
            for banned_area in banned_areas:
                if banned_area[0] <= cursor.position[0] <= banned_area[0] + banned_area[2] and banned_area[1] <= cursor.position[1] <= banned_area[1] + banned_area[3]:
                    banned = True
                    break

            if not banned:
                return this_object

class RootObject(object):
    highlight = None

    def tick(self):
        pass

    def render(self):
        pass

    def destroy(self):
        objects.remove(self)

    def ahead(self):
        objects.remove(self)
        objects.append(self)

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

    def __init__(self, text_color, background_color, font=slo.slo['appearance']['font']):
        self.text_color = text_color
        self.background_color = background_color

        self.text_format_time = TextFormat(font, root.display.size[1] // 5, self.text_color)
        self.text_format_date = TextFormat(font, root.display.size[1] // 20, self.text_color)

        self.x = 0
        self.x_target = 0

        self.lock = True

        self.click_start_position = cursor.position
        self.clicking = False

        self.background = pygame.Surface(root.display.size)
        self.background.fill(self.background_color)

        immediate = str(datetime.datetime.now())
        self.date = immediate.split()[0].split('-')[1:]
        self.time = immediate.split()[1].split(':')[:2]

        if self.time[0] == '0':
            self.time = self.time[1:]

        self.date_surface = self.text_format_date.render('월 '.join(self.date) + '일')
        self.date_position = (self.text_format_date.size + self.x, root.display.size[1] - self.text_format_date.size - self.date_surface.get_height())

        self.time_surface = self.text_format_time.render(':'.join(self.time))
        self.time_position = (self.date_position[0] + self.x, self.date_position[1] - self.time_surface.get_height() + 36)

        RootObject.highlight = LockScreen

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

            if now_time[0] == '0':
                now_time = now_time[1:]

            if now_date != self.date or now_time != self.time:
                self.time = now_time
                self.date = now_date

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

    def destroy(self):
        super().destroy()
        RootObject.highlight = None

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
                    if self.argument[0] == Shutdown:
                        self.command(self.argument[0]())
                    elif self.argument[0] == BuckerWindow:
                        self.command(self.argument[0](0, 0, 500, 500, title=str(time.time())))
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
        self.dock_items.append(self.DockItem(pygame.image.load('./res/image/window.png'), (add_object, BuckerWindow), self))

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

class BuckerWindow(RootObject):
    close = pygame.transform.scale(pygame.image.load('./res/image/close.png'), (20, 20)).convert_alpha()
    text_format = TextFormat(slo.slo['appearance']['font'], 18, color.background)

    def __init__(self, x, y, w, h, title='BuckerWindow', border_color=slo.bucker['window']['border_color'], background_color=slo.bucker['window']['background_color'], title_height=24):
        self.x = x
        self.y = y
        self.title_height = title_height
        self.width = w + 2
        self.height = h + self.title_height + 1
        self.title = title
        self.border_color = border_color
        self.background_color = background_color

        self.text_format.color = self.background_color

        self.moving = False
        self.original_x = None
        self.original_y = None
        self.start_moving_x = None
        self.start_moving_y = None

        self.window = pygame.Surface((0, 0))
        self.surface = pygame.Surface((self.width - 2, self.height - self.title_height - 1))
        self.surface.fill(self.background_color)

        self.build_surface()

    def build_surface(self):
        title_surface = self.text_format.render(self.title)

        self.window = pygame.Surface((self.width, self.height))
        self.window.fill(self.background_color)
        pygame.draw.rect(self.window, self.border_color, ((0, 0), (self.width, self.title_height)))
        pygame.draw.line(self.window, self.border_color, (0, 0), (0, self.height), 1)
        pygame.draw.line(self.window, self.border_color, (0, self.height), (self.width, self.height), 3)
        pygame.draw.line(self.window, self.border_color, (self.width, 0), (self.width, self.height), 3)
        self.window.blit(self.close, (self.width - self.close.get_width() - 2, 2))
        self.window.blit(title_surface, (center(self.width, title_surface.get_width()), 0))

        self.window.blit(self.surface, (1, self.title_height))

        self.surface = self.surface.convert()

    def tick(self):
        if cursor.fpressed[0]:
            if self.x <= cursor.position[0] <= self.x + self.width:
                if self.y <= cursor.position[1] <= self.y + self.title_height and get_ahead_window() == self:
                    self.moving = True
                    self.original_x = self.x
                    self.original_y = self.y
                    self.start_moving_x = cursor.position[0]
                    self.start_moving_y = cursor.position[1]
                if self.y <= cursor.position[1] <= self.y + self.height:
                    self.ahead()
        
        if self.moving:
            self.x = cursor.position[0] - self.start_moving_x + self.original_x
            self.y = cursor.position[1] - self.start_moving_y + self.original_y

        if cursor.epressed[0]:
            if self.x <= cursor.position[0] <= self.x + self.width:
                self.moving = False

            if self.x + self.width - self.title_height <= cursor.position[0] <= self.x + self.width and self.y <= cursor.position[1] <= self.y + self.title_height:
                self.destroy()

    def render(self):
        root.window.blit(self.window, (self.x, self.y))

    @staticmethod
    def add(bucker_window):
        add_object(bucker_window)

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

        add_object(LockScreen(color.text, color.background))

add_object(Bucker())
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
