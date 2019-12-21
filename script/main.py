import pygame
import ctypes
from os import environ

environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()


screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
user32 = ctypes.windll.user32

SCREEN_INFO = {
    "pygame_size": screen.get_size(),
    "system_size": (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
}

width = (SCREEN_INFO["pygame_size"][0] + SCREEN_INFO["system_size"][0]) // 2 - 1
height = (SCREEN_INFO["pygame_size"][1] + SCREEN_INFO["system_size"][1]) // 2 - 1
screensize = (width, height)


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
                pygame.display.set_mode(SCREEN_INFO["pygame_size"], pygame.FULLSCREEN)
                width = (SCREEN_INFO["pygame_size"][0] + SCREEN_INFO["system_size"][0]) // 2 - 1
                height = (SCREEN_INFO["pygame_size"][1] + SCREEN_INFO["system_size"][1]) // 2 - 1
                full_screen = True
        if event.type == pygame.VIDEORESIZE and not full_screen:
            pygame.display.set_mode(event.size, pygame.RESIZABLE)
            width = screen.get_width()
            height = screen.get_height()
    pygame.draw.rect(screen, (255, 255, 255), (width - 100, height - 100, 100, 100))
    pygame.display.flip()

pygame.quit()
