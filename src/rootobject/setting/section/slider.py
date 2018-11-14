import cursor
import root
import color
import slo
from rootobject import textformat
from rootobject.setting.section import sectionelement
import pygame
import math

# TODO 넓게 편 화면 구현
# TODO rootobject.setting에다가 값 변경하는 그거 구현하기.  # self.get() 만들어서 설정할 예정.

class Slider(sectionelement.SectionElement):
    def __init__(self, section, text, contents, text_format=textformat.TextFormat(slo.slo['appearance']['font'], 18, color.text)):
        self.section = section
        self.text = text
        self.contents = contents
        self.text_format = text_format

        self.title_surface = self.text_format.render(self.text)

        self.line_surface = pygame.Surface((2, self.title_surface.get_height()))
        self.line_surface.fill(color.text)

        self.y = 0  # 처음 텍스트의 y 시작좌표

        self.first = True

        self.height = self.title_surface.get_height()

        self.open = False
        self.text_moving = False
        self.line_moving = False
        self.text_x = 36 + self.section.setting.x
        self.line_x = 24 + self.text_x
        self.text_x_target = 0

        self.slider_x = self.section.setting.x_target + self.section.setting.width + self.section.setting.gap
        self.slider_y = -root.display.size[1]
        self.slider_y_target = self.slider_y
        self.slider_moving = False
        self.slider_open = False
        self.line_x_target = 0

        self.slider_background_surface = pygame.Surface((self.section.setting.width, self.section.setting.height))
        self.slider_header_surface = pygame.Surface((self.section.setting.width, 40))
        self.setting_logo_surface = pygame.transform.smoothscale(pygame.image.load('./res/image/icon/setting.png'), (19, 19)).convert_alpha()
        self.setting_text_surface = textformat.TextFormat(slo.slo['appearance']['font'], 17, color.text).render(self.text)
        self.setting_logo_position = [self.slider_x + 12, self.section.setting.gap + 10]
        self.setting_text_position = [self.slider_x + 38, self.section.setting.gap + 7]
        self.slider_background_surface.fill(slo.setting['color']['background'])
        self.slider_background_surface.set_alpha(slo.setting['opacity']['background'])
        self.slider_header_surface.fill(color.white)
        self.slider_header_surface.set_alpha(10)

    def tick(self):
        if self.first:
            index = self.section.elements.index(self)
            self.y = 20 * (index + 1) + self.section.header_height

            for I in range(index):
                self.y += self.section.elements[I].height

            self.first = False

        if cursor.fpressed[0]:
            if not (self.slider_x <= cursor.position[0] <= self.slider_x + self.slider_background_surface.get_width() or self.text_x - 12 <= cursor.position[0] <= self.text_x + self.section.header_width - 20 and self.section.y + self.y <= cursor.position[1] <= self.section.y + self.y + self.height):
                self.open_state(False)

        if cursor.epressed[0]:
            if self.text_x - 12 <= cursor.position[0] <= self.text_x + self.section.header_width - 20 and self.section.y + self.y <= cursor.position[1] <= self.section.y + self.y + self.height:
                self.open_state(not self.open)

        if self.line_moving:
            self.line_x += (self.line_x_target - self.line_x) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.line_x - self.line_x_target) < 1:
                self.line_x = self.line_x_target
                self.line_moving = False

        if self.text_moving:
            self.text_x += (self.text_x_target - self.text_x) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.text_x - self.text_x_target) < 1:
                self.text_x = self.text_x_target
                self.text_moving = False

        if self.slider_moving:
            self.slider_y += (self.slider_y_target - self.slider_y) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])
            if math.fabs(self.slider_y - self.slider_y_target) < 1:
                self.slider_y = self.slider_y_target
                self.slider_moving = False
                self.slider_open = False

        if not (self.line_moving or self.text_moving):
            if not self.open:
                self.text_x = 36 + self.section.setting.x
                self.line_x = 24 + self.section.setting.x
            else:
                self.line_x_target = self.text_x + self.section.header_width - 40 - self.line_surface.get_width() + self.section.setting.x
                self.text_x_target = 24 + self.section.setting.x

        self.setting_logo_position[1] = self.slider_y + 10
        self.setting_text_position[1] = self.slider_y + 7

        if self.section.setting.quit:
            self.destroy()

    def render(self):
        root.window.blit(self.line_surface, (self.line_x, self.section.y + self.y))

        root.window.blit(self.title_surface, (self.text_x, self.section.y + self.y))

        if self.open or self.slider_open:
            root.window.blit(self.slider_background_surface, (self.slider_x, self.slider_y))
            root.window.blit(self.slider_header_surface, (self.slider_x, self.slider_y))

            root.window.blit(self.setting_logo_surface, self.setting_logo_position)
            root.window.blit(self.setting_text_surface, self.setting_text_position)

    def open_state(self, state):
        self.open = state
        self.line_moving = True
        self.text_moving = True
        self.slider_moving = True
        if self.open:
            self.line_x_target = self.text_x + self.section.header_width - 40 - self.line_surface.get_width()
            self.text_x_target = 24 + self.section.setting.x
            self.slider_y_target = self.section.setting.y
        else:
            self.line_x_target = 24 + self.section.setting.x
            self.text_x_target = 36 + self.section.setting.x
            self.slider_y_target = -root.display.size[1]
            self.slider_open = True

    def get_open(self):
        return self.open