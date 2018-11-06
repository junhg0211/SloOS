import slo

import pygame

pygame.init()

class display:
    size = slo.slo['display']['size']
    fps = slo.slo['display']['fps']
    display_fps = None

    pygame.display.set_caption(slo.slo['display']['caption'])
    pygame.display.set_icon(pygame.image.load(slo.slo['display']['icon_path']))
run = True

def shutdown(*_):
    global run

    run = False

window = None
if slo.slo['display']['fullscreen']:
    window = pygame.display.set_mode(display.size, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
else:
    window = pygame.display.set_mode(display.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

state = None