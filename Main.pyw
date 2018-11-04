# coding=utf-8

import math  # 계산을 위해
import time  # 시간 계산을 위해
import datetime  # 현재 날짜와 시간을 위해
import getpass  # 컴퓨터 사용자 이름 불러오기를 위해
import configparser  # ini파일 불러오기를 위해
import codecs  # ini파일 불러오기를 위헤
from os import system  # 프로그램 외의 명령어를 위해 (cmd명령어 사용 가능함 (!!))

# V 컴퓨터 pygame이 없는 사람을 위한 자동 pygame 설치 서비스
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

# V 저장해놓은 ini 파일들을 쓸어담음
class slo:
    slo = None
    bucker = None
    lastest = None
    lockscreen = None
    surfer = None
    setting = None

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
        slo.setting = slo.configparser_parse('./slo/setting.ini')

    @staticmethod
    def save():
        slo.configparser_write('./slo/slo.ini', slo.slo)
        slo.configparser_write('./slo/bucker.ini', slo.bucker)
        slo.configparser_write('./slo/lastest.ini', slo.lastest)
        slo.configparser_write('./slo/lockscreen.ini', slo.lockscreen)
        slo.configparser_write('./slo/surfer.ini', slo.surfer)
        slo.configparser_write('./slo/setting.ini', slo.setting)

# V slo.init()이라고 생각하면 됨
slo.load()

# V 이 유저가 저번에 접속한 그 PC에서 접속한 게 맞나? 아니면 화면 해상도 다시 설정해야지
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
        window = pygame.display.set_mode(display.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

    state = None

class keyboard:
    lalt = False
    ralt = False
    lctrl = False
    rctrl = False
    space = False
    escape = False

    keydown_unicode = ''
    keydown_key = None

    input_board = '`1234567890-=~!@#$%^&*()_+qwertyuiop[]\QWERTYUIOP{}|asdfghjkl;\'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?\n '

    drill_delay = slo.bucker['input']['key_drill_delay']
    drill_remain_delay = slo.bucker['input']['key_drill_delay']
    drill_loop_delay = slo.bucker['input']['key_drill_loop_delay']
    drill_loop_remain_delay = slo.bucker['input']['key_drill_loop_delay']
    drill_mode = 0
    drill_input = False

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
    white = (255, 255, 255)
    red = (255, 0, 0)
    lime = (0, 255, 0)

objects = []

highlighted_object = None

def remove_object_by_type(_type):
    for OBJ in objects:
        if type(OBJ) == _type:
            OBJ.destroy()

def add_object(_obj):
    objects.append(_obj)

# V 모든 화면 오브젝트의 부모 클래스 RootObject
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

# V 화면에 쓸 글씨를 위한 폰트 오브젝트
class TextFormat:
    def __init__(self, font, size, colour):
        self.font = font
        self.size = size
        self.color = colour

        self.font = pygame.font.Font(self.font, self.size)

    def render(self, text):
        return self.font.render(text, True, self.color)

default_text_format = TextFormat(slo.slo['appearance']['font'], 18, color.text)

# V 잠금화면(락스크린) 오브젝트
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

# V 셧다운(종료 대기화면)
class Shutdown(RootObject):
    gui = 'Shutdown.mode.GUI'
    immediate = 'Shutdown.mode.IMMEDIATE'

    class Button(RootObject):
        text_format = default_text_format

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

# V 배경화면(버커) 오브젝트, 독(Dock)도 여기 있음
class Bucker(RootObject):
    background_image = pygame.transform.smoothscale(pygame.image.load(slo.bucker['background']['image_path']), (slo.slo['display']['size'][0], slo.slo['display']['size'][1])).convert()

    class DockItem(RootObject):
        text_format = default_text_format

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
                    if self.argument[0] in (Shutdown, Surfer, Setting):
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

# V 모든 윈도우(창) 오브젝트
class BuckerWindow(RootObject):
    close = pygame.transform.scale(pygame.image.load('./res/image/icon/close.png'), (20, 20)).convert_alpha()
    text_format = default_text_format

    class BuckerWindowElement(RootObject):
        def __init__(self, window):
            self.window = window

            self.x = 0
            self.y = 0
            self.surface = pygame.Surface((0, 0))

        def render(self):
            # root.window.blit(self.surface, (1 + self.window.x + self.x, self.window.title_height + self.window.y + self.y))
            self.window.surface.blit(self.surface, (self.x, self.y))

    class Text(BuckerWindowElement):
        def __init__(self, x=None, y=None, text=None, text_format=None, window=None):
            super().__init__(window)

            self.x = x
            self.y = y
            self.text = text
            self.text_format = text_format

            if self.x is None:
                self.x = 0
            if self.y is None:
                self.y = 0
            if self.text is None:
                self.text = ''
            if self.text_format is None:
                self.text_format = TextFormat(slo.slo['appearance']['font'], 18, color.background)

            self.surface = self.text_format.render(self.text)

    # V 입력할 수 있는 큰 입력판
    class TextArea(BuckerWindowElement):
        def __init__(self, x=None, y=None, width=None, height=None, value=None, text_format=None, background_color=None, writable=None, window=None):
            super().__init__(window)

            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.value = value
            self.text_format = text_format
            self.background_color = background_color
            self.writable = writable

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

            if cursor.fpressed[0]:
                if self.x + self.window.x + 1 <= cursor.position[0] <= self.x + self.window.x + 1 + self.surface.get_width() and self.y + self.window.y + self.window.title_height <= cursor.position[1] <= self.y + self.window.y + self.window.title_height + self.surface.get_height():
                    self.window.highlighted_object = self

            # if keyboard.drill_input:
            #     print('asdasd')

            if highlighted_object == self.window and self.window.highlighted_object == self:
                if self.writable and keyboard.keydown_unicode and keyboard.drill_input:
                    if keyboard.keydown_unicode in keyboard.input_board:
                        self.value += keyboard.keydown_unicode
                    elif keyboard.keydown_unicode == '\b':
                        self.value = self.value[:-1]
                    elif keyboard.keydown_unicode == '\r':
                        self.value += '\n'

    def __init__(self, program):
        self.program = program

        self.x = 0
        self.y = 0
        self.title_height = 24
        self.width = 150
        self.height = 150
        self.title = 'BuckerWindow'
        self.normal_border_color = slo.bucker['window']['normal_border_color']
        self.highlighted_border_color = slo.bucker['window']['highlighted_border_color']
        self.background_color = slo.bucker['window']['background_color']

        self.exit = False

        if self.title == 'BuckerWindow':
            self.title = self.program.split('/')[-1]
            if '\\' in self.title:
                self.title = self.program.split('//')[-1]

        self.directory = self.program[:-len(self.title) - 1]

        self.elements = []
        try:
            self.build_program(self.program)
        except SyntaxError:
            self.exit = True

        self.highlighted_object = None

        self.width += 2
        self.height += self.title_height + 1

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

        self.window = pygame.Surface((0, 0))
        self.surface = pygame.Surface((self.width - 2, self.height - self.title_height - 1))
        self.surface.fill(self.background_color)

        self.build_surface()

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

        if keyboard.keydown_key == pygame.K_q and (keyboard.lctrl or keyboard.rctrl) and highlighted_object == self:
            self.exit = True

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

            self.highlighted_object = None

        if cursor.epressed[0]:
            self.moving = False

            if self.x + self.width - self.title_height <= cursor.position[0] <= self.x + self.width and self.y <= cursor.position[1] <= self.y + self.title_height and get_on_cursor_window() == self:
                self.exit = True

        for element in self.elements:
            element.tick()

    def render(self):
        root.window.blit(self.window, (self.x, self.y))

        self.surface.fill(self.background_color)

        for element in self.elements:
            element.render()

        root.window.blit(self.surface, (1 + self.x, self.title_height + self.y))

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

    def build_program(self, path):
        def exception(message):
            add_object(Alert(self.title, f'현재 실행하고 있는 프로그램의 {line_number + 1}번째 줄에 다음과 같은 오류가 발견되었습니다: \n' + message))
            raise SyntaxError(message)

        try:
            code = open(path, 'r').read().split('\n')
        except UnicodeDecodeError:
            code = open(path, 'r', encoding='utf-8').read().split('\n')

        variables = {}

        for line_number in range(len(code)):
            line = code[line_number]

            if '?' in line: line = line[:line.index('?')]
            if len(line) <= 0: continue
            while line[-1] == ' ': line = line[:-1]

            sline = line.split()
            if sline[0] == 'set-raw':
                if len(sline) < 3:
                    exception('set-raw 구문의 변수 이름 또는 변수 값이 지정되어 있지 않습니다.')

                try:
                    variables[sline[1]] = eval(' '.join(sline[2:]))
                except Exception as e:
                    exception(str(e))

            elif sline[0] == 'set':
                if len(sline) < 3:
                    exception('set 구문의 변수 이름 또는 변수 값이 지정되어 있지 않습니다.')

                if sline[1] == 'TextFormat':
                    keys = ('font', 'size', 'color')

                    arguments = {}
                    for key in keys:
                        arguments[key] = None

                    for _i in range(len(sline)):
                        _i += 3
                        try:
                            word = sline[_i]
                        except IndexError:
                            break

                        if _i % 2 == 0:
                            if '_' in word: word = word.replace('_', ' ')
                            if '\\ ' in word: word = word.replace('\\ ', '_')

                            if last_key in keys:
                                if word[0] == '$':
                                    arguments[last_key] = variables[word]
                                else:
                                    arguments[last_key] = eval(word)
                        else:
                            last_key = word

                    arguments['font'] = arguments['font'].replace('|', '/')

                    if arguments['font'][0] == '%':
                        arguments['font'] = self.directory + arguments['font'][1:]

                    variables[sline[2]] = TextFormat(font=arguments['font'], size=arguments['size'], colour=arguments['color'])

            elif sline[0] == 'window-set':
                if sline[1] == 'x': self.x = eval(' '.join(sline[2:]))
                if sline[1] == 'y': self.y = eval(' '.join(sline[2:]))
                if sline[1] == 'title_height': self.title_height = eval(' '.join(sline[2:]))
                if sline[1] == 'width': self.width = eval(' '.join(sline[2:]))
                if sline[1] == 'height': self.height = eval(' '.join(sline[2:]))
                if sline[1] == 'title': self.title = eval(' '.join(sline[2:]))
                if sline[1] == 'border_color': self.normal_border_color = eval(' '.join(sline[2:]))
                if sline[1] == 'background_color': self.background_color = eval(' '.join(sline[2:]))
                if sline[1] == 'highlighted_background_color': self.highlighted_border_color = eval(' '.join(sline[2:]))

            elif sline[0] == 'window-add':
                if len(sline) < 2:
                    exception('window-add 구문의 변수형이 지정되어 있지 않습니다.')

                arguments = {}
                last_key = ''

                if sline[1] == 'TextArea':
                    keys = ('x', 'y', 'width', 'height', 'value', 'text_format', 'background_color', 'writable')

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
                                if word[0] == '$':
                                    arguments[last_key] = variables[word]
                                else:
                                    arguments[last_key] = eval(word)
                        else:
                            last_key = word

                    self.elements.append(self.TextArea(x=arguments['x'], y=arguments['y'], width=arguments['width'], height=arguments['height'], value=arguments['value'], text_format=arguments['text_format'], background_color=arguments['background_color'], writable=arguments['writable'], window=self))
                elif sline[1] == 'Text':
                    keys = ('x', 'y', 'text', 'text_format')

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
                                if word[0] == '$':
                                    if word not in variables.keys():
                                        exception(f'{word}라는 변수는 지정되지 않았습니다.\n변수 형에 언더바(_)를 사용했을 가능성이 있습니다.')
                                    arguments[last_key] = variables[word]
                                else:
                                    try:
                                        arguments[last_key] = eval(word)
                                    except NameError as e:
                                        exception(f'{e}')
                        else:
                            last_key = word

                    self.elements.append(self.Text(x=arguments['x'], y=arguments['y'], text=arguments['text'], text_format=arguments['text_format'], window=self))
                else:
                    exception(f'변수형 {sline[1]}을(를) 알 수 없습니다.')

            else:
                exception(f'명령어 {sline[0]}을(를) 알 수 없습니다.')

        return False

# V 프로그램 대기판(서퍼)
class Surfer(RootObject):
    width = (root.display.size[0] - 400) / 108
    height = (root.display.size[1] - 360) / 144

    x_button_start = center(root.display.size[0], width * 108 - 36)
    y_button_start = center(root.display.size[1], height * 144 - 72)

    left = 'Surfer.left'
    right = 'Surfer.right'

    class Button(RootObject):
        text_format = default_text_format

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

# V 알림, 경고 등 창
class Alert(RootObject):
    # error = 'Alert.error'
    # info = 'Alert.info'

    def __init__(self, title: str, message: str, kind=None, background_color=color.black, background_opacity=127, title_text_format=TextFormat(slo.slo['appearance']['font'], 32, color.text), text_format=default_text_format, gap=20):
        self.title = title
        self.messages = message
        self.kind = kind
        self.background_color = background_color
        self.background_opacity = background_opacity
        self.title_text_format = title_text_format
        self.message_text_format = text_format
        self.gap = gap

        self.background_surface = pygame.Surface(root.display.size)
        self.background_surface.fill(self.background_color)
        self.background_surface.set_alpha(self.background_opacity)

        self.title_surface = self.title_text_format.render(self.title)
        self.title_x = center(root.display.size[0], self.title_surface.get_width())

        self.message_surfaces = []
        self.message_xs = []
        for message in self.messages.split('\n'):
            self.message_surfaces.append(self.message_text_format.render(message))
            self.message_xs.append(center(root.display.size[0], self.message_surfaces[-1].get_width()))

        self.title_y = center(root.display.size[1], self.title_surface.get_height() + self.gap + len(self.message_surfaces) * self.message_text_format.size)
        self.message_ys = []
        for I in range(len(self.message_surfaces)):
            self.message_ys.append(self.title_y + self.title_surface.get_height() + self.gap + I * self.message_surfaces[I].get_height())

    def tick(self):
        RootObject.highlight = Alert
        self.ahead()

        if cursor.fpressed[0]:
            self.destroy()

    def render(self):
        root.window.blit(self.background_surface, (0, 0))

        root.window.blit(self.title_surface, (self.title_x, self.title_y))
        for I in range(len(self.message_surfaces)):
            root.window.blit(self.message_surfaces[I], (self.message_xs[I], self.message_ys[I]))

    def destroy(self):
        RootObject.highlight = None
        super().destroy()

# V 설정
class Setting(RootObject):
    class Section(RootObject):
        class Text(RootObject):
            def __init__(self, section, title_text, value_text, title_text_format=TextFormat(slo.slo['appearance']['font'], 18, color.text), value_text_format=TextFormat(slo.slo['appearance']['font'], 14, color.text)):
                self.section = section
                self.title_text = title_text
                self.value_text = value_text
                self.title_text_format = title_text_format
                self.value_text_format = value_text_format

                self.title_surface = self.title_text_format.render(self.title_text)
                self.value_surface = self.value_text_format.render(self.value_text)

                self.line_surface = pygame.Surface((2, self.title_surface.get_height() + self.value_surface.get_height()))
                self.line_surface.fill(color.text)

                self.text_x = 36 + self.section.setting.x

                self.y = 0  # 처음 텍스트의 y 시작좌표

                self.first = True

                self.height = self.title_surface.get_height() + self.value_surface.get_height()

            def tick(self):
                if self.first:
                    index = self.section.elements.index(self)
                    self.y = 20 * (index + 1) + self.section.header_height

                    for I in range(index):
                        self.y += self.section.elements[I].height

                    self.first = False

                self.text_x = 36 + self.section.setting.x

            def render(self):
                root.window.blit(self.line_surface, (self.text_x - 12, self.section.y + self.y))

                root.window.blit(self.title_surface, (self.text_x, self.section.y + self.y))
                root.window.blit(self.value_surface, (self.text_x, self.section.y + self.y + self.title_text_format.size + 8))

        header_height = 40

        def __init__(self, setting, name: str, *elements):
            self.setting = setting
            self.name = name
            self.arguments = elements

            self.elements = []
            for argument in self.arguments:
                self.elements.append(argument[0](self, *argument[1]))

            self.is_open = False

            self.x = 12

            self.header = pygame.Surface((self.setting.width - 25, self.header_height))
            self.header.fill(slo.setting['color']['background'])
            self.header.set_alpha(slo.setting['opacity']['background'])

            self.rect_height = (len(self.elements) + 1) * 20
            for element in self.elements:
                self.rect_height += element.height

            self.element_background_surface = pygame.Surface((self.header.get_width(), self.rect_height))
            self.element_background_surface.fill(slo.setting['color']['background'])
            self.element_background_surface.set_alpha(slo.setting['opacity']['elements_background'])

            self.name_surface = TextFormat(slo.slo['appearance']['font'], 17, color.text).render(self.name)

            self.height = self.header.get_height()

            self.index = 0

            self.y = 0

        def tick(self):
            self.index = self.setting.sections.index(self)

            self.y = self.setting.gap * 2 + 40
            for I in range(self.index):
                self.y += self.setting.sections[I].height

            for element in self.elements:
                element.tick()

        def render(self):
            root.window.blit(self.element_background_surface, (self.x + self.setting.x, self.y + 40))

            for element in self.elements:
                element.render()

            root.window.blit(self.header, (self.x + self.setting.x, self.y))
            root.window.blit(self.name_surface, (self.x + 12 + self.setting.x, self.y + 9))

    gap = 16

    width = 389
    height = root.display.size[1] - gap * 2

    def __init__(self):
        self.background_surface = pygame.Surface((self.width, self.height))
        self.background_surface.fill(slo.setting['color']['background'])
        self.background_surface.set_alpha(slo.setting['opacity']['background'])

        self.header_surface = pygame.Surface((self.width, 40))
        self.header_surface.fill(color.white)
        self.header_surface.set_alpha(10)

        self.x = -self.width - self.gap
        self.x_moving = True
        self.x_target = self.gap

        self.setting_logo_surface = pygame.transform.smoothscale(pygame.image.load('./res/image/icon/setting.png'), (19, 19)).convert_alpha()
        self.setting_text_surface = TextFormat(slo.slo['appearance']['font'], 17, color.text).render('설정')
        self.back_button_surface = pygame.transform.smoothscale(pygame.image.load('./res/image/icon/left_arrow.png'), (19, 19)).convert_alpha()
        self.setting_logo_position = (self.x + 12, self.gap + 10)
        self.setting_text_position = (self.x + 38, self.gap + 7)
        self.back_button_position = (self.x + self.width - 32, self.gap + 10)

        self.quit = False

        self.sections = [
            self.Section(
                self, '시스템 정보',
                (self.Section.Text, ('시스템 버전', slo.slo['metadata']['version'])),
                (self.Section.Text, ('개발', 'Я ШTEЛO의 SloOS 팀'))
            )
        ]

        # self.rect_height = (len(self.sections) + 1) * 20
        # for section in self.sections:
        #     self.rect_height += section.height
        #
        # self.element_background_surface = pygame.Surface((self.width, self.rect_height))
        # self.element_background_surface.fill(slo.setting['color']['background'])
        # self.element_background_surface.set_alpha(slo.setting['opacity']['elements_background'])

    def tick(self):
        if self.x_moving:
            self.x += (self.x_target - self.x) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            self.setting_logo_position = (self.x + 12, self.gap + 10)
            self.setting_text_position = (self.x + 38, self.gap + 7)
            self.back_button_position = (self.x + self.width - 32, self.gap + 10)

            if math.fabs(self.x_target - self.x) < 1:
                self.x = self.x_target
                self.x_moving = False
                self.setting_logo_position = (self.x + 12, self.gap + 10)
                self.setting_text_position = (self.x + 38, self.gap + 7)
                self.back_button_position = (self.x + self.width - 32, self.gap + 10)

        if self.x <= -410 and self.quit:
            self.destroy()

        if keyboard.escape or (cursor.fpressed[0] and not (self.x <= cursor.position[0] <= self.x + self.width and self.gap <= cursor.position[1] <= self.gap + self.height)) or (cursor.fpressed[0] and self.back_button_position[0] <= cursor.position[0] <= self.back_button_position[0] + self.back_button_surface.get_width() and self.back_button_position[1] <= cursor.position[1] <= self.back_button_position[1] + self.back_button_surface.get_height()):
            self.exit()

        for section in self.sections:
            section.tick()

    def render(self):
        root.window.blit(self.header_surface, (self.x, self.gap))
        root.window.blit(self.background_surface, (self.x, self.gap))

        root.window.blit(self.setting_logo_surface, self.setting_logo_position)
        root.window.blit(self.setting_text_surface, self.setting_text_position)
        root.window.blit(self.back_button_surface, self.back_button_position)

        # for I in range(len(self.sections)):
        #     pass

        for section in self.sections:
            section.render()

    def exit(self):
        self.x_target = -416
        self.x_moving = True
        self.quit = True

# V 커서가 가르키고 있는 윈도우를 출력함.
def get_on_cursor_window() -> BuckerWindow:
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

# V 디버그를 위한 HUD(Head-up-display)
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

# V 프레임 고정을 위한 변수. 1 이상 되면 루프를 실행한다.
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
        # if keyboard.keydown_unicode:
        #     keyboard.keydown_unicode = ''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                root.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LALT:
                    keyboard.lalt = True
                elif event.key == pygame.K_RALT:
                    keyboard.ralt = True
                elif event.key == pygame.K_LCTRL:
                    keyboard.lctrl = True
                elif event.key == pygame.K_RCTRL:
                    keyboard.rctrl = True
                elif event.key == pygame.K_SPACE:
                    keyboard.space = True
                elif event.key == pygame.K_ESCAPE:
                    keyboard.escape = True

                keyboard.keydown_unicode = event.unicode
                keyboard.keydown_key = event.key

                keyboard.drill_mode = 1
                keyboard.drill_input = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LALT:
                    keyboard.lalt = False
                elif event.key == pygame.K_RALT:
                    keyboard.ralt = False
                elif event.key == pygame.K_LCTRL:
                    keyboard.lctrl = False
                elif event.key == pygame.K_RCTRL:
                    keyboard.rctrl = False
                elif event.key == pygame.K_SPACE:
                    keyboard.space = False
                elif event.key == pygame.K_ESCAPE:
                    keyboard.escape = False

                if event.key == keyboard.keydown_key:
                    keyboard.keydown_key = None
                    keyboard.drill_mode = 0

        if root.display.display_fps is not None:
            for i in range(3):
                cursor.fpressed[i] = not cursor.ppressed[i] and cursor.pressed[i]
                cursor.epressed[i] = cursor.ppressed[i] and not cursor.pressed[i]

            if keyboard.drill_mode == 1:
                keyboard.drill_remain_delay -= 1 / root.display.display_fps
                if keyboard.drill_remain_delay <= 0:
                    keyboard.drill_mode = 2
            elif keyboard.drill_mode == 2:
                keyboard.drill_loop_remain_delay -= 1 / root.display.display_fps
                if keyboard.drill_loop_remain_delay <= 0:
                    keyboard.drill_loop_remain_delay = keyboard.drill_loop_delay
                    keyboard.drill_input = True
                else:
                    keyboard.drill_input = False
            else:
                keyboard.drill_loop_remain_delay = keyboard.drill_loop_delay
                keyboard.drill_remain_delay = keyboard.drill_delay
                keyboard.drill_input = False

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

            keyboard.drill_input = False
    else:
        delta += (now - pnow) / time_per_tick
pygame.quit()
slo.save()  # ini파일 저장
exit()
