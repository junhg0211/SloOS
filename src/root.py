import slo

import pygame
import socket
import os

pygame.init()

# V 이 유저가 저번에 접속한 그 PC에서 접속한 게 맞나? 아니면 화면 해상도 다시 설정해야지
this_username = socket.getfqdn()
if this_username != slo.lastest['user']['fqdn']:
    slo.lastest['user']['fqdn'] = this_username
    current_main_display = pygame.display.Info()
    slo.slo['display']['size'] = (current_main_display.current_w, current_main_display.current_h)
    slo.slo['display']['fullscreen'] = True

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

def center(x, y):
    return (x - y) // 2

window = None
now_display = pygame.display.Info()
now_display_size = (now_display.current_w, now_display.current_h)
if slo.slo['display']['fullscreen']:
    try:
        window = pygame.display.set_mode(display.size, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    except pygame.error:
        display.size = now_display_size
        slo.slo['display']['size'] = display.size
        window = pygame.display.set_mode(display.size, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
else:
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{center(now_display_size[0], display.size[0])},{center(now_display_size[1], display.size[1])}'
    window = pygame.display.set_mode(display.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.NOFRAME)

state = None