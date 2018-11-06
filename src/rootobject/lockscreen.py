import slo
import root
import cursor
import color
import state
from rootobject import rootobject
from rootobject import textformat
from rootobject import shutdown

import pygame
import datetime
import math

# V 잠금화면(락스크린) 오브젝트
class LockScreen(rootobject.RootObject):
    time_surface: pygame.Surface
    time_position: tuple
    date_surface: pygame.Surface
    date_position: tuple

    def __init__(self, text_color, background_color, font=slo.slo['appearance']['font']):
        self.text_color = text_color
        self.background_color = background_color

        self.text_format_time = textformat.TextFormat(font, root.display.size[1] // 5, self.text_color)
        self.text_format_date = textformat.TextFormat(font, root.display.size[1] // 20, self.text_color)

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

        if self.time[0][0] == '0':
            self.time[0] = self.time[0][1:]

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

        rootobject.RootObject.highlight = LockScreen

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

            if now_time[0][0] == '0':
                now_time[0] = now_time[0][1:]

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
                    rootobject.add_object(shutdown.Shutdown(mode=shutdown.Shutdown.immediate))
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
            state.change_state(state.home)
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
        rootobject.RootObject.highlight = None
