import slo
import color
import root
from rootobject import rootobject
from rootobject import textformat

import pygame

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

        self.header = pygame.Surface((self.setting.width - 25, self.header_height))
        self.header.fill(slo.setting['color']['background'])
        self.header.set_alpha(slo.setting['opacity']['background'])

        self.rect_height = (len(self.elements) + 1) * 20
        for element in self.elements:
            self.rect_height += element.height

        self.element_background_surface = pygame.Surface((self.header.get_width(), self.rect_height))
        self.element_background_surface.fill(slo.setting['color']['background'])
        self.element_background_surface.set_alpha(slo.setting['opacity']['elements_background'])

        self.name_surface = textformat.TextFormat(slo.slo['appearance']['font'], 17, color.text).render(self.name)

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