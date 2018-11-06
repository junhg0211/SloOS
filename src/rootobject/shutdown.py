import root
import state
import cursor
import slo
import keyboard
from rootobject import rootobject

import pygame

# V 셧다운(종료 대기화면)
class Shutdown(rootobject.RootObject):
    gui = 'Shutdown.mode.GUI'
    immediate = 'Shutdown.mode.IMMEDIATE'

    class Button(rootobject.RootObject):
        text_format = rootobject.default_text_format

        def __init__(self, surface, text, action, shutdown):
            self.surface = surface
            self.text = text
            self.command = action[0]
            self.argument = action[1:]
            self.shutdown = shutdown

            self.x, self.y = 0, 0

            if self.surface.get_width() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (72, self.surface.get_height()))
            if self.surface.get_height() != 72:
                self.surface = pygame.transform.smoothscale(self.surface, (self.surface.get_width(), 72))

            self.text_surface = self.text_format.render(self.text)
            self.text_x, self.text_y = 0, 0

        def tick(self):
            if self.shutdown.moving:
                self.x = rootobject.center(root.display.size[0], 108 * len(self.shutdown.buttons) - 36) + 108 * self.shutdown.buttons.index(self)
                self.y = rootobject.center(root.display.size[1], 108) + self.shutdown.y * 2

                self.text_x = rootobject.center(root.display.size[0], len(self.shutdown.buttons) * 108 - 36) - self.text_surface.get_width() / 2 + 108 * self.shutdown.buttons.index(self) + 36
                self.text_y = rootobject.center(root.display.size[1], 108) + 108 - self.text_surface.get_height() + self.shutdown.y * 3

            if cursor.epressed[0]:
                if self.x <= cursor.position[0] <= self.x + 72 and self.y <= cursor.position[1] <= self.y + 72:
                    self.command(*self.argument)

        def render(self):
            root.window.blit(self.surface, (self.x, self.y))
            root.window.blit(self.text_surface, (self.text_x, self.text_y))

    def __init__(self, mode=gui):
        self.mode = mode

        self.moving = True
        self.y = -root.display.size[1]
        self.target_y = 0

        self.background = pygame.Surface(root.display.size)

        self.buttons = []
        self.buttons.append(self.Button(pygame.image.load('./res/image/icon/lock.png'), '잠금 화면', (state.change_state, state.lock), self))
        self.buttons.append(self.Button(pygame.image.load('./res/image/icon/shutdown.png'), '시스템 종료', (root.shutdown,), self))

        self.back_button_surface = pygame.transform.smoothscale(pygame.image.load('./res/image/icon/left_arrow.png'), (32, 32))
        self.back_button_surface.convert()
        self.back_button_position = [16, 16]

        rootobject.RootObject.highlight = Shutdown

    def tick(self):
        if self.mode == self.immediate:
            root.shutdown()
            self.destroy()

        if self.moving:
            self.y += (self.target_y - self.y) / (root.display.display_fps / slo.slo['appearance']['motion_speed'])

        for button in self.buttons:
            button.tick()

        self.back_button_position[1] = 16 + self.y
        if cursor.epressed[0] and self.back_button_position[0] <= cursor.position[0] <= self.back_button_position[0] + self.back_button_surface.get_width() and self.back_button_position[1] <= cursor.position[1] <= self.back_button_position[1] + self.back_button_surface.get_height() or keyboard.escape:
            self.quit()

        if self.y <= -root.display.size[1] - 1:
            self.destroy()

    def render(self):
        root.window.blit(self.background, (0, self.y))

        for button in self.buttons:
            button.render()

        root.window.blit(self.back_button_surface, self.back_button_position)

    def quit(self):
        self.target_y = -root.display.size[1] - 1.5
        self.moving = True

    def destroy(self):
        rootobject.RootObject.highlight = None
        super().destroy()