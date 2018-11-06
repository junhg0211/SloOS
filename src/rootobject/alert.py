import color
import slo
import root
import cursor
from rootobject import rootobject
from rootobject import textformat

import pygame

# V 알림, 경고 등 창
class Alert(rootobject.RootObject):
    # error = 'Alert.error'
    # info = 'Alert.info'

    def __init__(self, title: str, message: str, kind=None, background_color=color.black, background_opacity=127, title_text_format=textformat.TextFormat(slo.slo['appearance']['font'], 32, color.text), text_format=rootobject.default_text_format, gap=20):
        self.title = title
        self.messages = message
        self.kind = kind
        self.background_color = background_color
        self.background_opacity = background_opacity
        self.title_text_format = title_text_format
        self.message_text_format = text_format
        self.gap = gap

        self.background_surface = pygame.Surface(root.display.size)
        self.background_surface.fill(self.background_color)
        self.background_surface.set_alpha(self.background_opacity)

        self.title_surface = self.title_text_format.render(self.title)
        self.title_x = rootobject.center(root.display.size[0], self.title_surface.get_width())

        self.message_surfaces = []
        self.message_xs = []
        for message in self.messages.split('\n'):
            self.message_surfaces.append(self.message_text_format.render(message))
            self.message_xs.append(rootobject.center(root.display.size[0], self.message_surfaces[-1].get_width()))

        self.title_y = rootobject.center(root.display.size[1], self.title_surface.get_height() + self.gap + len(self.message_surfaces) * self.message_text_format.size)
        self.message_ys = []
        for I in range(len(self.message_surfaces)):
            self.message_ys.append(self.title_y + self.title_surface.get_height() + self.gap + I * self.message_surfaces[I].get_height())

    def tick(self):
        rootobject.highlight = Alert
        self.ahead()

        if cursor.fpressed[0]:
            self.destroy()

    def render(self):
        root.window.blit(self.background_surface, (0, 0))

        root.window.blit(self.title_surface, (self.title_x, self.title_y))
        for I in range(len(self.message_surfaces)):
            root.window.blit(self.message_surfaces[I], (self.message_xs[I], self.message_ys[I]))

    def destroy(self):
        rootobject.highlight = None
        super().destroy()