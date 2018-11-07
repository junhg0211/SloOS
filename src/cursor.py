import pygame

position = pygame.mouse.get_pos()
ppressed = pressed = pygame.mouse.get_pressed()

fpressed = list(pressed)
epressed = list(pressed)

sposition = position

rel = pygame.mouse.get_rel()