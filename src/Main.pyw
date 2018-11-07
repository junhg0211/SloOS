# coding=utf-8

import slo
import root
import color
import cursor
import state
import keyboard
import audioplayer
from rootobject import rootobject
from rootobject import textformat
from rootobject import bucker
from rootobject import pointer

import time  # 시간 계산을 위해
import os

# V 컴퓨터 pygame이 없는 사람을 위한 자동 pygame 설치 서비스
try:
    import pygame
except ModuleNotFoundError:
    print('pygame 모듈이 발견되지 않았습니다. pygame 모듈을 다운로드합니다.')
    os.system('pip install pygame')
    import pygame

# os.chdir('\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1]))
total_lines = 0

def search(dirname):
    global total_lines

    try:
        filenames = os.listdir(dirname)
        for filename in filenames:
            full_filename = os.path.join(dirname, filename)
            if os.path.isdir(full_filename):
                search(full_filename)
            else:
                ext = os.path.splitext(full_filename)[-1]
                if ext == '.py':
                    try:
                        total_lines += len(open(full_filename, 'r').readlines())
                    except UnicodeDecodeError:
                        total_lines += len(open(full_filename, 'r', encoding='utf-8').readlines())
    except PermissionError:
        pass

search('./src')
print(total_lines)

pygame.init()

# V 디버그를 위한 HUD(Head-up-display)
class HUD(rootobject.RootObject):
    state_surface: pygame.Surface
    fps_surface: pygame.Surface
    objects_surface: pygame.Surface
    text_format = textformat.TextFormat('./res/font/consola.ttf', 20, color.text)

    def tick(self):
        self.fps_surface = self.text_format.render(str(root.display.display_fps) + ' FPS')
        self.objects_surface = self.text_format.render(str(len(rootobject.objects)) + ' OBJECT')

    def render(self):
        root.window.blit(self.fps_surface, (0, 0))
        root.window.blit(self.objects_surface, (0, 20))

hud = None
if slo.slo['display']['hud']:
    hud = HUD()

rootobject.add_object(bucker.Bucker())
state.change_state(state.lock)

highlighted_object = None

# V 프레임 고정을 위한 변수. 1 이상 되면 루프를 실행한다.
delta = 0

now = time.time()
time_per_tick = 0
if root.display.fps is not None:
    time_per_tick = 1 / root.display.fps

loop = now

audioplayer.playsound('./res/sound/startup.wav')

while root.run:
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
        cursor.rel = pygame.mouse.get_rel()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                root.shutdown()
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
                keyboard.drill_loop_remain_delay = keyboard.drill_loop_delay
                keyboard.drill_remain_delay = keyboard.drill_delay
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

                try:
                    phighlighted_object = highlighted_object
                except NameError:
                    phighlighted_object = rootobject.get_on_cursor_window()
                highlighted_object = rootobject.get_on_cursor_window()

                try:
                    phighlighted_object.build_surface()
                except AttributeError:
                    pass
                try:
                    highlighted_object.build_surface()
                except AttributeError:
                    pass

            if root.display.display_fps > 0:
                for obj in rootobject.objects:
                    if type(obj) == rootobject.highlight or rootobject.highlight is None:
                        obj.tick()
                pointer.pointer.tick()
                if slo.slo['display']['hud']: hud.tick()

                root.window.fill(color.background)
                for obj in rootobject.objects:
                    obj.render()
                pointer.pointer.render()
                if slo.slo['display']['hud']: hud.render()
                pygame.display.update()

            keyboard.drill_input = False
    else:
        delta += (now - pnow) / time_per_tick
pygame.quit()
slo.save()  # ini파일 저장
exit()
