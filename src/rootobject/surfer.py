import root
import cursor
import slo
import keyboard
from rootobject import rootobject
from rootobject import setting  # 필요한 것임!
from rootobject.buckerwindow import buckerwindow  # 필요한 것임!

import pygame
import math

# V 프로그램 대기판(서퍼)
class Surfer(rootobject.RootObject):
    width = (root.display.size[0] - 400) / 108
    height = (root.display.size[1] - 360) / 144

    x_button_start = rootobject.center(root.display.size[0], width * 108 - 36)
    y_button_start = rootobject.center(root.display.size[1], height * 144 - 72)

    left = 'Surfer.left'
    right = 'Surfer.right'

    class Button(rootobject.RootObject):
        text_format = rootobject.default_text_format

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

        rootobject.RootObject.highlight = Surfer

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
        rootobject.add_object(_object(*args))
        self.quit()

    def quit(self):
        rootobject.highlight = None
        self.moving = True
        if self.side == self.left:
            self.target_x = -root.display.size[0] - 2
        else:
            self.target_x = root.display.size[0] + 2