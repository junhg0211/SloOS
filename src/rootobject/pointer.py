import cursor
import root
import slo
from rootobject import rootobject

import pygame

class Pointer(rootobject.RootObject):
    def __init__(self):
        self.cursors = [pygame.image.load(slo.bucker['cursor']['normal']), pygame.image.load(slo.bucker['cursor']['pressed'])]

        for i in range(2):
            width_ratio = self.cursors[i].get_width() / self.cursors[i].get_height()
            self.cursors[i] = pygame.transform.smoothscale(self.cursors[i], (round(width_ratio * slo.bucker['cursor']['height']), slo.bucker['cursor']['height']))

        self.surface = pygame.Surface((0, 0))

        pygame.mouse.set_visible(False)

        self.positions = []

    def tick(self):
        self.surface = self.cursors[1 if True in cursor.pressed else 0]

        self.positions = [[cursor.position[i] - cursor.rel[i] for i in range(2)], cursor.position]

    def render(self):
        for position in self.positions:
            root.window.blit(self.surface, position)

    def destroy(self):
        super().destroy()
        pygame.mouse.set_visible(True)