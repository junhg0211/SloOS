import root
import color
import slo
from rootobject import rootobject
from rootobject import textformat

import pygame

class Text(rootobject.RootObject):
    def __init__(self, section, title_text, value_text,
                 title_text_format=textformat.TextFormat(slo.slo['appearance']['font'], 18, color.text),
                 value_text_format=textformat.TextFormat(slo.slo['appearance']['font'], 14, color.text)):
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