# coding=utf-8

import math
import time
import datetime
import codecs
import getpass
import configparser
from os import system

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
    slo = None
    bucker = None
    lastest = None
    lockscreen = None
    surfer = None

    @staticmethod
    def configparser_parse(path):
        config = configparser.ConfigParser()
        try:
            config.read_file(codecs.open(path, 'r', encoding='utf-8'))
        except UnicodeDecodeError:
            config.read_file(codecs.open(path, 'r'))

        result = {}

        for section in config.sections():
            result[section] = {}
            for key in config[section].keys():
                result[section][key] = eval(config[section][key])

        return result

    @staticmethod
    def configparser_write(path, value: dict):
        cfgfile = open(path, 'w', encoding='utf-8')
        config = configparser.ConfigParser()

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
        slo.lockscreen = slo.configparser_parse('./slo/lockscreen.ini')
        slo.surfer = slo.configparser_parse('./slo/surfer.ini')

    @staticmethod
    def save():
        slo.configparser_write('./slo/slo.ini', slo.slo)
        slo.configparser_write('./slo/bucker.ini', slo.bucker)
        slo.configparser_write('./slo/lastest.ini', slo.lastest)
        slo.configparser_write('./slo/lockscreen.ini', slo.lockscreen)
        slo.configparser_write('./slo/surfer.ini', slo.surfer)

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

    keydown_unicode = ''

    input_board = '`1234567890-=~!@#$%^&*()_+qwertyuiop[]\QWERTYUIOP{}|asdfghjkl;\'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?\n '

class cursor:
    position = pygame.mouse.get_pos()
    ppressed = pressed = pygame.mouse.get_pressed()

    fpressed = list(pressed)
    epressed = list(pressed)

    sposition = position

class color:
    background = (31, 33, 37)
    text = (222, 222, 222)
    gray = (127, 127, 127)
    black = (0, 0, 0)
    red = (255, 0, 0)

objects = []

highlighted_object = None

def remove_object_by_type(_type):
    for OBJ in objects:
        if type(OBJ) == _type:
            OBJ.destroy()

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
        self.target_x = 0

        self.lock = True

        self.click_start_position = cursor.position
        self.clicking = False

        self.background = pygame.Surface(root.display.size)
        if slo.lockscreen['background']['type'] == 'solid':
            self.background.fill(self.background_color)
        else:
            tmp = pygame.transform.smoothscale(pygame.image.load(slo.lockscreen['background']['image_path']), root.display.size).convert()
            self.background.blit(tmp, (0, 0)); del tmp

        immediate = str(datetime.datetime.now())
        self.date = immediate.split()[0].split('-')[1:]
        self.time = immediate.split()[1].split(':')[:2]

        if self.time[0] == '0':
            self.time = self.time[1:]

        self.date_surface = self.text_format_date.render('월 '.join(self.date) + '일')
        self.date_position = (self.text_format_date.size + self.x, root.display.size[1] - self.text_format_date.size - self.date_surface.get_height())

        self.time_surface = self.text_format_time.render(':'.join(self.time))
        self.time_position = (self.date_position[0] + self.x, self.date_position[1] - self.time_surface.get_height() + 36)

        self.system_shutdown_icon_appear = False
        self.system_shutdown_icon_pappear = False
        self.system_shutdown_icon_fappear = False
        self.system_shutdown_icon_eappear = False
        self.system_shutdown_icon_surface = pygame.transform.smoothscale(pygame.image.load('./res/image/icon/shutdown.png'), (72, 72))
        self.system_shutdown_icon_x = root.display.size[0]
        self.system_shutdown_icon_y = -72
        self.system_shutdown_icon_target_x = 0
        self.system_shutdown_icon_target_y = 0
        self.system_shutdown_icon_x_moving = False
        self.system_shutdown_icon_y_moving = False
        self.system_shutdown_delay = 0.5
        self.system_shutdown_time = 0
        self.system_shutdown_surface = pygame.Surface(root.display.size)
        self.system_shutdown_surface.fill(color.black)

        RootObject.highlight = LockScreen

    def tick(self):
        if self.x != root.display.size[0]:
            if self.lock:
                if cursor.fpressed[0]:
                    self.click_start_position = cursor.position
                    self.clicking = True

                if self.clicking:
                    self.target_x = -min(0, self.click_start_position[0] - cursor.position[0])

                if cursor.epressed[0]:
                    self.clicking = False

                    x_offset = cursor.position[0] - self.click_start_position[0]
                    y_offset = math.fabs(cursor.position[1] - self.click_start_position[1])

                    try:
                        offset = x_offset / y_offset
                    except ZeroDivisionError:
                        offset = 0

                    if offset >= 5:
                        self.target_x = root.display.size[0]
                        self.lock = False
                        self.system_shutdown_icon_target_x = root.display.size[0]
                    else:
                        self.target_x = 0

            if self.target_x != self.x and root.display.display_fps is not None:
                self.x += (self.target_x - self.x) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
                if math.fabs(self.target_x - self.x) < 0.1:
                    self.x = self.target_x

            immediate = str(datetime.datetime.now())
            now_date = immediate.split()[0].split('-')[1:]
            now_time = immediate.split()[1].split(':')[:2]

            if now_time[0] == '0':
                now_time = now_time[1:]

            self.system_shutdown_icon_pappear = self.system_shutdown_icon_appear
            self.system_shutdown_icon_appear = cursor.position[0] >= root.display.size[0] - 5 and cursor.position[1] < 5

            self.system_shutdown_icon_fappear = not self.system_shutdown_icon_pappear and self.system_shutdown_icon_appear
            self.system_shutdown_icon_eappear = self.system_shutdown_icon_pappear and not self.system_shutdown_icon_appear

            if self.system_shutdown_icon_fappear and self.lock:
                self.system_shutdown_icon_target_x = root.display.size[0] - 82
                self.system_shutdown_icon_target_y = 10
                self.system_shutdown_icon_x_moving = True
                self.system_shutdown_icon_y_moving = True

            if self.system_shutdown_icon_eappear:
                self.system_shutdown_icon_target_x = root.display.size[0]
                self.system_shutdown_icon_target_y = -72
                self.system_shutdown_icon_x_moving = True
                self.system_shutdown_icon_y_moving = True

            if self.system_shutdown_icon_x_moving:
                self.system_shutdown_icon_x += (self.system_shutdown_icon_target_x - self.system_shutdown_icon_x) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
                if math.fabs(self.system_shutdown_icon_target_x - self.system_shutdown_icon_x) < 1:
                    self.system_shutdown_icon_x = self.system_shutdown_icon_target_x
                    self.system_shutdown_icon_x_moving = False

            if self.system_shutdown_icon_y_moving:
                self.system_shutdown_icon_y += (self.system_shutdown_icon_target_y - self.system_shutdown_icon_y) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
                if math.fabs(self.system_shutdown_icon_target_y - self.system_shutdown_icon_y) < 1:
                    self.system_shutdown_icon_y = self.system_shutdown_icon_target_y
                    self.system_shutdown_icon_y_moving = False

            if self.system_shutdown_icon_appear and cursor.pressed[0] and self.lock:
                self.system_shutdown_time += 1 / root.display.display_fps
                self.system_shutdown_surface.set_alpha(self.system_shutdown_time / self.system_shutdown_delay * 255)
                if self.system_shutdown_delay <= self.system_shutdown_time:
                    add_object(Shutdown(mode=Shutdown.immediate))
            else:
                self.system_shutdown_time = 0
                self.system_shutdown_surface.set_alpha(None)

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

        if self.system_shutdown_icon_appear:
            root.window.blit(self.system_shutdown_icon_surface, (self.system_shutdown_icon_x, self.system_shutdown_icon_y))

        if self.x < root.display.size[0]:
            root.window.blit(self.date_surface, self.date_position)
            root.window.blit(self.time_surface, self.time_position)

        if 0 < self.system_shutdown_time:
            root.window.blit(self.system_shutdown_surface, (0, 0))

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
        self.buttons.append(self.Button(pygame.image.load('./res/image/icon/lock.png'), '잠금 화면', (change_state, state.lock), self))
        self.buttons.append(self.Button(pygame.image.load('./res/image/icon/shutdown.png'), '시스템 종료', (root.quit,), self))

        self.back_button_surface = pygame.transform.smoothscale(pygame.image.load('./res/image/icon/left_arrow.png'), (32, 32))
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
    background_image = pygame.transform.smoothscale(pygame.image.load(slo.bucker['background']['image_path']), (slo.slo['display']['size'][0], slo.slo['display']['size'][1])).convert()

    class DockItem(RootObject):
        text_format = TextFormat(slo.slo['appearance']['font'], 18, color.text)

        def __init__(self, surface, action, text, dock_bucker):
            self.surface = surface
            self.command = action[0]
            self.argument = action[1:]
            self.text = text
            self.dock_bucker = dock_bucker

            self.original_x = 20 + len(self.dock_bucker.dock_items) * 92
            self.original_y = 12

            if self.surface.get_width() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (72, self.surface.get_height()))
            if self.surface.get_height() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (self.surface.get_width(), 72))
            self.surface.convert()

            self.x = self.original_x
            self.y = self.original_y

            self.text_surface = self.text_format.render(self.text)
            self.text_appear = False

            self.text_x = 0
            self.text_y = 0

        def tick(self):
            if self.x <= cursor.position[0] <= self.x + self.surface.get_width() and self.y <= cursor.position[1] <= self.y + self.surface.get_height():
                if cursor.epressed[0]:
                    if self.argument[0] in (Shutdown, Surfer):
                        self.command(self.argument[0](*self.argument[1:]))
                    elif self.argument[0] == BuckerWindow:
                        self.command(self.argument[0](0, 0, 500, 500, title=str(time.time())))
                    else:
                        self.command(*self.argument)
                self.text_appear = True
            else:
                self.text_appear = False

            self.x = self.original_x + self.dock_bucker.dock_x
            self.y = self.original_y + self.dock_bucker.dock_y

            self.text_x = center(self.surface.get_width(), self.text_surface.get_width()) + self.x
            self.text_y = center(self.surface.get_height(), self.text_surface.get_height()) + self.y - self.surface.get_height()

        def render(self):
            if self.original_y != self.y:
                root.window.blit(self.surface, (self.x, self.y))

            if self.text_appear:
                root.window.blit(self.text_surface, (self.text_x, self.text_y))

    def __init__(self):
        self.dock_items = []
        for item in slo.bucker['dock']['items']:
            self.dock_items.append(eval(item))

        self.dock_width = len(self.dock_items) * 92 + 20
        self.dock_height = 92
        self.dock_x = center(root.display.size[0], self.dock_width)
        self.dock_y = root.display.size[1]
        self.dock_target_y = root.display.size[1]
        self.dock_color = color.gray

        self.dock_surface = pygame.Surface((self.dock_width, self.dock_height))
        self.dock_surface.fill(slo.bucker['dock']['background_color'])
        self.dock_surface.set_alpha(slo.bucker['dock']['opacity'])

    def tick(self):
        if root.state != state.lock:
            self.dock_target_y = root.display.size[1] - self.dock_height

        if self.dock_target_y != self.dock_y and root.display.display_fps is not None:
            self.dock_y += (self.dock_target_y - self.dock_y) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.dock_target_y - self.dock_y) < 0.1:
                self.dock_y = self.dock_target_y

        for item in self.dock_items:
            item.tick()

        if cursor.epressed[0] and cursor.sposition[0] <= 5 and cursor.sposition[1] <= 5:
            try:
                offset = (cursor.position[0] - cursor.sposition[0]) / (cursor.position[1] - cursor.sposition[1])
            except ZeroDivisionError:
                if cursor.position[0] - cursor.sposition[0] <= 0:
                    offset = 0
                else:
                    offset = 10

            if offset >= 10:
                add_object(Surfer())

    def render(self):
        if slo.bucker['background']['type'] == 'solid':
            root.window.fill(slo.bucker['background']['color'])
        else:
            root.window.blit(self.background_image, (0, 0))

        root.window.blit(self.dock_surface, (self.dock_x, self.dock_y))

        for item in self.dock_items:
            item.render()

class BuckerWindow(RootObject):
    close = pygame.transform.scale(pygame.image.load('./res/image/icon/close.png'), (20, 20)).convert_alpha()
    text_format = TextFormat(slo.slo['appearance']['font'], 18, color.background)

    class TextArea(RootObject):
        def __init__(self, x=None, y=None, w=None, h=None, value=None, text_format=None, background_color=None, writable=None, window=None):
            self.x = x
            self.y = y
            self.width = w
            self.height = h
            self.value = value
            self.text_format = text_format
            self.background_color = background_color
            self.writable = writable
            self.window = window

            if self.x is None:
                self.x = 0
            if self.y is None:
                self.y = 0
            if self.width is None:
                self.width = self.window.width
            if self.height is None:
                self.height = self.window.height
            if self.value is None:
                self.value = ''
            if self.text_format is None:
                self.text_format = TextFormat(slo.slo['appearance']['domino_font'], 18, color.text)
            if self.background_color is None:
                self.background_color = color.background
            if self.writable is None:
                self.writable = True

            self.surface = pygame.Surface((self.width, self.height))

        def tick(self):
            self.surface.fill(self.background_color)
            values = self.value.split('\n')
            for I in range(len(values)):
                if self.text_format.size * I < self.height:
                    self.surface.blit(self.text_format.render(values[I]), (0, self.text_format.size * I))

            if highlighted_object == self.window:
                if self.writable and keyboard.keydown_unicode:
                    if keyboard.keydown_unicode in keyboard.input_board:
                        self.value += keyboard.keydown_unicode
                    elif keyboard.keydown_unicode == '\b':
                        self.value = self.value[:-1]
                    elif keyboard.keydown_unicode == '\r':
                        self.value += '\n'

        def render(self):
            self.window.surface.blit(self.surface, (self.x, self.y))

    def __init__(self, program):
        self.program = program

        self.x = 0
        self.y = 0
        self.title_height = 24
        self.width = 150
        self.height = 150 + self.title_height + 1
        self.title = 'BuckerWindow'
        self.normal_border_color = slo.bucker['window']['normal_border_color']
        self.highlighted_border_color = slo.bucker['window']['highlighted_border_color']
        self.background_color = slo.bucker['window']['background_color']

        self.elements = []
        self.build_program(self.program)

        if self.title == 'BuckerWindow':
            self.title = self.program.split('/')[-1]
            if '\\' in self.title:
                self.title = self.program.split('//')[-1]

        self.target_x = self.x
        self.target_y = self.y

        self.x_moving = True
        self.y_moving = True

        self.x = cursor.position[0] - self.width / 2
        self.y = cursor.position[1] - self.height / 2

        self.text_format.color = self.background_color

        self.moving = False
        self.original_x = None
        self.original_y = None
        self.start_moving_x = None
        self.start_moving_y = None

        self.exit = False

        self.window = pygame.Surface((0, 0))
        self.surface = pygame.Surface((self.width - 2, self.height - self.title_height - 1))
        self.surface.fill(self.background_color)

        self.build_surface()

    def build_program(self, path):
        try:
            code = open(path, 'r').read().split('\n')
        except UnicodeDecodeError:
            code = open(path, 'r', encoding='utf-8').read().split('\n')

        for line in code:
            if '?' in line: line = line[:line.index('?')]
            if len(line) <= 0: continue
            while line[-1] == ' ': line = line[:-1]

            sline = line.split()

            if sline[0] == 'window-set':
                if sline[1] == 'x': self.x = eval(' '.join(sline[2:]))
                if sline[1] == 'y': self.y = eval(' '.join(sline[2:]))
                if sline[1] == 'title_height': self.title_height = eval(' '.join(sline[2:]))
                if sline[1] == 'width': self.width = eval(' '.join(sline[2:]))
                if sline[1] == 'height': self.height = eval(' '.join(sline[2:]))
                if sline[1] == 'title': self.title = eval(' '.join(sline[2:]))
                if sline[1] == 'border_color': self.normal_border_color = eval(' '.join(sline[2:]))
                if sline[1] == 'background_color': self.background_color = eval(' '.join(sline[2:]))
                if sline[1] == 'highlighted_background_color': self.highlighted_border_color = eval(' '.join(sline[2:]))

            elif sline[0] == 'add':
                arguments = {}
                last_key = ''

                if sline[1] == 'TextArea':
                    keys = ('x', 'y', 'w', 'h', 'value', 'text_format', 'background_color', 'writable')

                    for key in keys:
                        arguments[key] = None

                    for _i in range(len(sline)):
                        _i += 2
                        try:
                            word = sline[_i]
                        except IndexError:
                            break

                        if _i % 2 == 1:
                            if '_' in word: word = word.replace('_', ' ')
                            if '\\ ' in word: word = word.replace('\\ ', '_')

                            if last_key in keys:
                                arguments[last_key] = eval(word)
                        else:
                            last_key = word

                    self.elements.append(self.TextArea(x=arguments['x'], y=arguments['y'], w=arguments['w'], h=arguments['h'], value=arguments['value'], text_format=arguments['text_format'], background_color=arguments['background_color'], writable=arguments['writable'], window=self))

    def build_surface(self):
        title_surface = self.text_format.render(self.title)

        border_color = self.highlighted_border_color if highlighted_object == self else self.normal_border_color

        self.window = pygame.Surface((self.width, self.height))
        self.window.fill(self.background_color)
        pygame.draw.rect(self.window, border_color, ((0, 0), (self.width, self.title_height)))
        pygame.draw.line(self.window, border_color, (0, 0), (0, self.height), 1)
        pygame.draw.line(self.window, border_color, (0, self.height), (self.width, self.height), 3)
        pygame.draw.line(self.window, border_color, (self.width, 0), (self.width, self.height), 3)
        self.window.blit(self.close, (self.width - self.close.get_width() - 2, 2))
        self.window.blit(title_surface, (center(self.width, title_surface.get_width()), 0))

        self.surface = self.surface.convert()

    def tick(self):
        if self.x_moving:
            self.x += (self.target_x - self.x) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.x - self.target_x) < 1:
                self.x = self.target_x
                self.x_moving = False

        if self.y_moving:
            self.y += (self.target_y - self.y) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.y - self.target_y) < 1:
                self.y = self.target_y
                self.y_moving = False

        if self.exit:
            self.y_moving = True
            self.target_y = root.display.size[1] + 1

            if root.display.size[1] <= self.y:
                self.destroy()

        if self.moving:
            self.target_x = cursor.position[0] - self.start_moving_x + self.original_x
            self.target_y = cursor.position[1] - self.start_moving_y + self.original_y

            self.x_moving = True
            self.y_moving = True

        if cursor.fpressed[0]:
            if self.x <= cursor.position[0] <= self.x + self.width:
                if self.y <= cursor.position[1] <= self.y + self.title_height and get_on_cursor_window() == self:
                    self.moving = True
                    self.original_x = self.x
                    self.original_y = self.y
                    self.start_moving_x = cursor.position[0]
                    self.start_moving_y = cursor.position[1]

            if get_on_cursor_window() == self:
                self.ahead()

        if cursor.epressed[0]:
            self.moving = False

            if self.x + self.width - self.title_height <= cursor.position[0] <= self.x + self.width and self.y <= cursor.position[1] <= self.y + self.title_height and get_on_cursor_window() == self:
                self.exit = True

        for element in self.elements:
            element.tick()

    def render(self):
        root.window.blit(self.window, (self.x, self.y))

        for element in self.elements:
            element.render()

        root.window.blit(self.surface, (1 + self.x, self.title_height + self.y))

class Surfer(RootObject):
    width = (root.display.size[0] - 400) / 108
    height = (root.display.size[1] - 360) / 144

    x_button_start = center(root.display.size[0], width * 108 - 36)
    y_button_start = center(root.display.size[1], height * 144 - 72)

    left = 'Surfer.left'
    right = 'Surfer.right'

    class Button(RootObject):
        text_format = TextFormat(slo.slo['appearance']['font'], 18, color.text)

        def __init__(self, surface, text, surfer, command=None):
            self.surface = surface
            self.command = command
            self.text = text
            self.surfer = surfer

            self.func = command[0]
            self.arguments = command[1:]

            self.x, self.y = 0, 0

            if self.surface.get_width() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (72, self.surface.get_height()))
            if self.surface.get_height() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (self.surface.get_width(), 72))

            self.text_surface = self.text_format.render(self.text)
            self.text_x, self.text_y = 0, 0

        def tick(self):
            if self.surfer.moving:
                number = self.surfer.buttons.index(self)
                x = number % self.surfer.width
                y = max(0, round(number / self.surfer.width + 0.5) - 1)

                self.x = self.surfer.x_button_start + 108 * x + self.surfer.x * 2
                self.y = self.surfer.y_button_start + 144 * y

                self.text_x = self.surfer.x_button_start + 108 * x + 36 - self.text_surface.get_width() / 2 + self.surfer.x * 3
                self.text_y = self.y + self.surface.get_height() + self.text_surface.get_height()

            if cursor.epressed[0]:
                if self.x <= cursor.position[0] <= self.x + self.surface.get_width() and self.y <= cursor.position[1] <= self.y + self.surface.get_height():
                    self.func(*self.arguments)

        def render(self):
            root.window.blit(self.surface, (self.x, self.y))
            root.window.blit(self.text_surface, (self.text_x, self.text_y))

    def __init__(self, side='Surfer.left'):
        self.side = side

        self.close_x = -root.display.size[0] if self.side == self.left else root.display.size[0]

        self.x = self.close_x
        self.target_x = 0
        self.moving = True

        self.background = pygame.Surface(root.display.size)

        self.buttons = []
        for item in slo.surfer['item']['items']:
            self.buttons.append(eval(item))

        self.back_button_surface = pygame.transform.smoothscale(pygame.image.load('./res/image/icon/left_arrow.png'), (32, 32))
        self.back_button_surface.convert()
        self.back_button_position_x = 16
        self.back_button_position_y = 16

        RootObject.highlight = Surfer

    def tick(self):
        if self.moving:
            self.x += (self.target_x - self.x) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])

            if math.fabs(self.x - self.target_x) < 1:
                self.x = self.target_x
                self.moving = False

        for button in self.buttons:
            button.tick()

        self.back_button_position_x = 16 + self.x * 2
        if cursor.epressed[0] and self.back_button_position_x <= cursor.position[0] <= self.back_button_position_x + self.back_button_surface.get_width() and self.back_button_position_y <= cursor.position[1] <= self.back_button_position_y + self.back_button_surface.get_height() or keyboard.escape:
            self.quit()

        if (self.x < -root.display.size[0] - 1 and self.side == self.left) or (self.x > root.display.size[0] + 1 and self.side == self.right):
            self.destroy()

    def render(self):
        root.window.blit(self.background, (self.x, 0))

        for button in self.buttons:
            button.render()

        root.window.blit(self.back_button_surface, (self.back_button_position_x, self.back_button_position_y))

    def start(self, _object, *args):
        add_object(_object(*args))
        self.quit()

    def quit(self):
        RootObject.highlight = None
        self.moving = True
        if self.side == self.left:
            self.target_x = -root.display.size[0] - 2
        else:
            self.target_x = root.display.size[0] + 2

def get_ahead_window():
    for I in range(len(objects))[::-1]:
        if type(objects[I]) == BuckerWindow:
            return objects[I]

def get_on_cursor_window():
    banned_areas = []  # [(x, y, width, height)]
    for I in range(len(objects))[::-1]:
        this_object = objects[I]

        try:
            (this_object.y, this_object.width)
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

        banned_areas.append((this_object.x, this_object.y, this_object.width, this_object.height))

class HUD(RootObject):
    state_surface: pygame.Surface
    fps_surface: pygame.Surface
    objects_surface: pygame.Surface
    text_format = TextFormat('./res/font/consola.ttf', 20, color.text)

    def tick(self):
        self.fps_surface = self.text_format.render(str(root.display.display_fps) + ' FPS')
        self.objects_surface = self.text_format.render(str(len(objects)) + ' OBJECT')

    def render(self):
        root.window.blit(self.fps_surface, (0, 0))
        root.window.blit(self.objects_surface, (0, 20))

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

now = time.time()
if root.display.fps is not None:
    time_per_tick = 1 / root.display.fps

loop = now

while not root.exit:
    pnow = now
    now = time.time()

    if delta >= 1 or root.display.fps is None:
        ploop = loop
        loop = time.time()

        try:
            root.display.display_fps = round(1 / (loop - ploop))
        except ZeroDivisionError:
            root.display.display_fps = 10000

        delta -= 1
        
        cursor.position = pygame.mouse.get_pos()
        cursor.ppressed = cursor.pressed
        cursor.pressed = pygame.mouse.get_pressed()
        if keyboard.keydown_unicode:
            keyboard.keydown_unicode = ''
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

                keyboard.keydown_unicode = event.unicode
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RALT:
                    keyboard.ralt = False
                elif event.key == pygame.K_LALT:
                    keyboard.lalt = False
                elif event.key == pygame.K_SPACE:
                    keyboard.space = False
                elif event.key == pygame.K_ESCAPE:
                    keyboard.escape = False

        if root.display.display_fps is not None:
            for i in range(3):
                cursor.fpressed[i] = not cursor.ppressed[i] and cursor.pressed[i]
                cursor.epressed[i] = cursor.ppressed[i] and not cursor.pressed[i]

            if cursor.fpressed[0]:
                cursor.sposition = cursor.position

                phiehlighted_object = highlighted_object
                highlighted_object = get_on_cursor_window()

                try:
                    phiehlighted_object.build_surface()
                except AttributeError:
                    pass
                try:
                    highlighted_object.build_surface()
                except AttributeError:
                    pass

            if root.display.display_fps > 0:
                for obj in objects:
                    if type(obj) == RootObject.highlight or RootObject.highlight is None:
                        obj.tick()
                if slo.slo['display']['hud']: hud.tick()

                root.window.fill(color.background)
                for obj in objects:
                    obj.render()
                if slo.slo['display']['hud']: hud.render()
                pygame.display.update()

    else:
        delta += (now - pnow) / time_per_tick
pygame.quit()
slo.save()
