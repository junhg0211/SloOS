import slo
import color
import root
import cursor
from rootobject import rootobject
from rootobject import textformat

import pygame
import math

class Section(rootobject.RootObject):
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

        self.header_width = self.setting.width - 25
        self.header = pygame.Surface((self.header_width, self.header_height))
        self.header.fill(slo.setting['color']['background'])
        self.header.set_alpha(slo.setting['opacity']['background'])

        self.less_icon_surface = pygame.transform.smoothscale(pygame.image.load('./res/image/icon/less.png'), (18, 18))
        self.less_surface = self.less_icon_surface
        self.less_surface_position = [0, 0]

        self.less_angle = 0
        self.less_angle_target = 0
        self.less_angle_moving = False

        self.rect_height = (len(self.elements) + 1) * 20
        for element in self.elements:
            self.rect_height += element.height

        self.element_background_surface = pygame.Surface((self.header.get_width(), self.rect_height))
        self.element_background_surface.fill(slo.setting['color']['background'])
        self.element_background_surface.set_alpha(slo.setting['opacity']['elements_background'])

        self.name_surface = textformat.TextFormat(slo.slo['appearance']['font'], 17, color.text).render(self.name)

        self.height = self.header_height

        self.index = 0

        self.y = 0

    def tick(self):
        self.index = self.setting.sections.index(self)

        self.y = self.setting.gap * 2 + 40
        for I in range(self.index):
            self.y += self.setting.sections[I].height + 20

        for element in self.elements:
            element.tick()

        if cursor.epressed[0]:
            if self.x + self.setting.x <= cursor.position[0] <= self.x + self.setting.x + self.header_width and self.y <= cursor.position[1] <= self.y + self.header_height:
                self.is_open = not self.is_open

                self.less_angle_moving = True
                if self.is_open:
                    self.height = self.header_height + self.element_background_surface.get_height()
                    self.less_angle_target = 45
                else:
                    self.height = self.header_height
                    self.less_angle_target = 0

        if self.less_angle_moving:
            self.less_angle += (self.less_angle_target - self.less_angle) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.less_angle_target - self.less_angle) < 1:
                self.less_angle = self.less_angle_target
                self.less_angle_moving = False

        if self.less_angle != 0:
            self.less_surface = pygame.transform.rotate(self.less_icon_surface, self.less_angle)
        else:
            self.less_surface = self.less_icon_surface

        self.less_surface_position = (self.x + self.setting.x + self.header_width - self.header_height + (self.header_height - self.less_surface.get_width()) / 2, self.y + (self.header_height - self.less_surface.get_height()) / 2)

    def render(self):
        if self.is_open:
            root.window.blit(self.element_background_surface, (self.x + self.setting.x, self.y + 40))

            for element in self.elements:
                element.render()

        root.window.blit(self.header, (self.x + self.setting.x, self.y))
        root.window.blit(self.less_surface, self.less_surface_position)
        root.window.blit(self.name_surface, (self.x + 12 + self.setting.x, self.y + 9))