import slo
import cursor
import root
import color
import state
from rootobject import rootobject
from rootobject import shutdown
from rootobject import surfer
from rootobject.setting import setting
from rootobject.buckerwindow import buckerwindow

import pygame
import math
import time

# V 배경화면(버커) 오브젝트, 독(Dock)도 여기 있음
class Bucker(rootobject.RootObject):
    background_image = pygame.transform.smoothscale(pygame.image.load(slo.bucker['background']['image_path']), (slo.slo['display']['size'][0], slo.slo['display']['size'][1])).convert()

    class DockItem(rootobject.RootObject):
        text_format = rootobject.default_text_format

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
                    if self.argument[0] in (shutdown.Shutdown, surfer.Surfer, setting.Setting):
                        self.command(self.argument[0](*self.argument[1:]))
                    elif self.argument[0] == buckerwindow.BuckerWindow:
                        self.command(self.argument[0](0, 0, 500, 500, title=str(time.time())))
                    else:
                        self.command(*self.argument)
                self.text_appear = True
            else:
                self.text_appear = False

            self.x = self.original_x + self.dock_bucker.dock_x
            self.y = self.original_y + self.dock_bucker.dock_y

            self.text_x = rootobject.center(self.surface.get_width(), self.text_surface.get_width()) + self.x
            self.text_y = rootobject.center(self.surface.get_height(), self.text_surface.get_height()) + self.y - self.surface.get_height()

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
        self.dock_x = rootobject.center(root.display.size[0], self.dock_width)
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
                rootobject.add_object(surfer.Surfer())

    def render(self):
        if slo.bucker['background']['type'] == 'solid':
            root.window.fill(slo.bucker['background']['color'])
        else:
            root.window.blit(self.background_image, (0, 0))

        root.window.blit(self.dock_surface, (self.dock_x, self.dock_y))

        for item in self.dock_items:
            item.render()