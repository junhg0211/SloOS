import slo
import color
import root
import cursor
import keyboard
from rootobject import rootobject
from rootobject import textformat
from rootobject.setting.section import section
from rootobject.setting.section import text

import pygame
import math

# V 설정
class Setting(rootobject.RootObject):
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
            section.Section(
                self, '시스템 정보',
                (text.Text, ('시스템 버전', slo.slo['metadata']['version'])),
                (text.Text, ('개발', 'Я ШTEЛO의 SloOS 팀'))
            ),
            section.Section(
                self, '디자인',
                (text.Text, ('버커', 'Bucker')),
                (text.Text, ('잠금화면 ', 'Lock Screen')),
                (text.Text, ('테마', 'Theme'))
            ),
            section.Section(
                self, '독'
            ),
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

        for SECTION in self.sections:
            SECTION.tick()

    def render(self):
        root.window.blit(self.header_surface, (self.x, self.gap))
        root.window.blit(self.background_surface, (self.x, self.gap))

        root.window.blit(self.setting_logo_surface, self.setting_logo_position)
        root.window.blit(self.setting_text_surface, self.setting_text_position)
        root.window.blit(self.back_button_surface, self.back_button_position)

        # for I in range(len(self.sections)):
        #     pass

        for SECTION in self.sections:
            SECTION.render()

    def exit(self):
        self.x_target = -416
        self.x_moving = True
        self.quit = True