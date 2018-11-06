from rootobject import rootobject

import pygame

class BuckerWindowElement(rootobject.RootObject):
    def __init__(self, window):
        self.window = window

        self.x = 0
        self.y = 0
        self.surface = pygame.Surface((0, 0))

    def render(self):
        # root.window.blit(self.surface, (1 + self.window.x + self.x, self.window.title_height + self.window.y + self.y))
        self.window.surface.blit(self.surface, (self.x, self.y))