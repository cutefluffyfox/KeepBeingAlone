import pygame
import ctypes
from os import environ

environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()


user32 = ctypes.windll.user32
SYS_SIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
screensize = width, height = SYS_SIZE
screen = pygame.display.set_mode(screensize, pygame.NOFRAME)


full_screen = True
running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11 and full_screen:
                pygame.display.set_mode((int(width / 100 * 60), int(height / 100 * 60)), pygame.RESIZABLE)
                width = screen.get_width()
                height = screen.get_height()
                full_screen = False
            elif event.key == pygame.K_F11 and not full_screen:
                pygame.display.set_mode(SYS_SIZE, pygame.NOFRAME)
                width, height = SYS_SIZE
                full_screen = True
        if event.type == pygame.VIDEORESIZE and not full_screen:
            pygame.display.set_mode(event.size, pygame.RESIZABLE)
            width = screen.get_width()
            height = screen.get_height()
    pygame.draw.rect(screen, (255, 255, 255), (width - 200, height - 200, 100, 100))
    pygame.draw.rect(screen, (255, 255, 255), (100, 100, 100, 100))
    pygame.display.flip()

pygame.quit()
