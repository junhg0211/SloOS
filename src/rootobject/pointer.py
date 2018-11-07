import cursor
import root
import slo
from rootobject import rootobject

import pygame

normal = 'normal'
resize_width = 'resize_width'
resize_height = 'resize_height'

class Pointer(rootobject.RootObject):
    def __init__(self):
        keys = ('normal', 'resize_width', 'resize_height')

        self.cursors = {}
        for key in keys:
            self.cursors[key] = {}
            self.cursors[key]['surfaces'] = []
            for i in range(2):
                tmp = pygame.image.load(slo.bucker['cursor']['directory'] + '/' + slo.bucker['cursor'][key] + f'{i}.' + slo.bucker['cursor']['extension'])
                original_height = tmp.get_height()
                width_ratio = tmp.get_width() / tmp.get_height()
                self.cursors[key]['surfaces'].append(pygame.transform.smoothscale(tmp, (round(width_ratio * slo.bucker['cursor']['height']), slo.bucker['cursor']['height'])))
                edited_height = self.cursors[key]['surfaces'][0].get_height()
            self.cursors[key]['position_offset'] = [float(open(slo.bucker['cursor']['directory'] + '/' + slo.bucker['cursor'][key] + '.txt', 'r').read().split()[i]) * (edited_height / original_height) for i in range(2)]

        self.mode = 'normal'

        self.surface = pygame.Surface((0, 0))

        pygame.mouse.set_visible(False)

        self.positions = []

    def tick(self):
        self.surface = self.cursors[self.mode]['surfaces'][1 if True in cursor.pressed else 0]

        self.positions = [[cursor.position[i] - cursor.rel[i] for i in range(2)], cursor.position]

    def render(self):
        for position in self.positions:
            root.window.blit(self.surface, [position[i] - self.cursors[self.mode]['position_offset'][i] for i in range(2)])

    def destroy(self):
        super().destroy()
        pygame.mouse.set_visible(True)

pointer = Pointer()