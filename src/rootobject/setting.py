import slo
import color
import root
import cursor
import keyboard
from rootobject import rootobject
from rootobject import textformat

import pygame
import math

# V 설정
class Setting(rootobject.RootObject):
    class Section(rootobject.RootObject):
        class Text(rootobject.RootObject):
            def __init__(self, section, title_text, value_text, title_text_format=textformat.TextFormat(slo.slo['appearance']['font'], 18, color.text), value_text_format=textformat.TextFormat(slo.slo['appearance']['font'], 14, color.text)):
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
        self.setting_text_surface = textformat.TextFormat(slo.slo['appearance']['font'], 17, color.text).render('설정')
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