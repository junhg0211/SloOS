import keyboard
import cursor
import color
import slo
from rootobject import rootobject
from rootobject import textformat
from rootobject.buckerwindow import buckerwindowelement

import pygame

# V 입력할 수 있는 큰 입력판
class TextArea(buckerwindowelement.BuckerWindowElement):
    def __init__(self, x=None, y=None, width=None, height=None, value=None, text_format=None, background_color=None, writable=None, window=None):
        super().__init__(window)

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = value
        self.text_format = text_format
        self.background_color = background_color
        self.writable = writable

        if self.x is None:
            self.x = 0
        if self.y is None:
            self.y = 0
        if self.width is None:
            self.width = self.window.width
        if self.height is None:
            self.height = self.window.height
        if self.value is None:
            self.value = ''
        if self.text_format is None:
            self.text_format = textformat.TextFormat(slo.slo['appearance']['domino_font'], 18, color.text)
        if self.background_color is None:
            self.background_color = color.background
        if self.writable is None:
            self.writable = True

        self.surface = pygame.Surface((self.width, self.height))

    def tick(self):
        self.surface.fill(self.background_color)
        values = self.value.split('\n')
        for I in range(len(values)):
            if self.text_format.size * I < self.height:
                self.surface.blit(self.text_format.render(values[I]), (0, self.text_format.size * I))

        if cursor.fpressed[0]:
            if self.x + self.window.x + 1 <= cursor.position[0] <= self.x + self.window.x + 1 + self.surface.get_width() and self.y + self.window.y + self.window.title_height <= cursor.position[1] <= self.y + self.window.y + self.window.title_height + self.surface.get_height():
                self.window.highlighted_object = self

        if rootobject.highlighted_object == self.window and self.window.highlighted_object == self:
            if self.writable and keyboard.keydown_unicode and keyboard.drill_input:
                if keyboard.keydown_unicode in keyboard.input_board:
                    self.value += keyboard.keydown_unicode
                elif keyboard.keydown_unicode == '\b':
                    self.value = self.value[:-1]
                elif keyboard.keydown_unicode == '\r':
                    self.value += '\n'