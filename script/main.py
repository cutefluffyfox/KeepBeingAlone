import pygame
import ctypes
from os.path import split, join
from os import environ, getcwd, listdir
from time import time
from random import randint

# system stuff
environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

# screen
user32 = ctypes.windll.user32
SYS_SIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
screensize = width, height = SYS_SIZE
screen = pygame.display.set_mode(screensize, pygame.NOFRAME)

# constants
LEVELS = join(split(getcwd())[0], "levels")
IMAGES = join(split(getcwd())[0], "images")
COLORS = {
    "background": (255, 100, 100),
    "outline": (255, 255, 255)
}

# global variables
all_page_sprites = pygame.sprite.Group()
all_page_resizable = set()


def percentage(limit, percent):
    return int(limit / 100 * percent)


def exit_game():
    global running
    running = False


class Button(pygame.sprite.Sprite):
    def __init__(self, group, x=0, y=0, w=0, h=0, color=(255, 255, 255), outline=3, background=(0, 0, 0),
                 limit=60, speed=0.5, text=""):
        super().__init__(group)
        self.size = (w, h)
        self.outline = outline
        self.color = color
        self.add = 0
        self.speed = speed
        self.start = time()
        self.limit = limit
        self.now_background = background
        self.background = background
        self.image = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, color, (0, 0, w, h), outline)
        self.text = text
        self.font = self.text_surface = self.text_rect = self.rect = None
        self.change_cords(x, y, w, h)

    def change_cords(self, x, y, w, h):
        self.size = (w, h)
        self.font = pygame.font.SysFont('Comic Sans MS', percentage(h, 70))
        self.text_surface = self.font.render(self.text, False, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (w // 2, h // 2)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image,
                         list(map(lambda a: int(min(a + self.add, 255)), self.background)), (0, 0, *self.size), 0)
        pygame.draw.rect(self.image, self.color, (0, 0, w, h), self.outline)
        self.image.blit(self.text_surface, self.text_rect)
        self.rect = self.image.get_rect().move(x, y)

    def update(self, *args):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and self.add < self.limit:
            self.add += self.limit * (time() - self.start) / self.speed
        elif not self.rect.collidepoint(mouse_pos) and self.add > 0:
            self.add -= self.limit * (time() - self.start) / self.speed
        else:
            self.start = time()
            return
        self.add = min(self.add, self.limit)
        self.add = max(self.add, 0)
        pygame.draw.rect(self.image,
                         list(map(lambda a: int(min(a + self.add, 255)), self.background)), (0, 0, *self.size), 0)
        pygame.draw.rect(self.image, self.color, (0, 0, *self.size), self.outline)
        self.image.blit(self.text_surface, self.text_rect)
        self.start = time()


class Menu(pygame.sprite.Sprite):
    class Circle(pygame.sprite.Sprite):
        def __init__(self, group, color=(255, 255, 255), wait_time=0.01):
            super().__init__(group)
            self.color = color
            self.wait_time = wait_time
            self.r = self.x = self.y = 0
            self.image = self.rect = None
            self.start = time()
            self.resize()

        def resize(self):
            self.r = percentage(height, 1)
            self.x = randint(self.r, width - self.r)
            self.y = randint(self.r, height - self.r)
            self.image = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA, 32)
            pygame.draw.circle(self.image, self.color, (self.r, self.r), self.r)
            self.rect = self.image.get_rect().move(self.x, self.y)

        def update(self, *args):
            if time() - self.start > self.wait_time:
                vx = randint(-1, 1)
                vy = randint(-1, 1)
                self.rect = self.rect.move(vx, vy)
                self.start = time()

    def __init__(self):
        global all_page_resizable, all_page_sprites
        self.group = pygame.sprite.Group()
        self.resizable = set()
        super().__init__(self.group)
        self.image = self.rect = None
        self.color = COLORS["outline"]
        self.background = COLORS["background"]
        self.circles = pygame.sprite.Group()
        for _ in range(percentage(height, 9)):
            self.Circle(self.circles, color=self.color)
        self.buttons = pygame.sprite.Group()
        self.texts = {
            "Play": Levels,
            "Settings": list,
            "Info": list,
            "Exit": exit_game,
        }
        self.font = self.text_surface = self.text_rect = None
        for text in self.texts:
            Button(self.buttons, color=self.color, background=self.background, text=text)
        self.resize()
        self.resizable.add(self)
        self.group.add(self.circles)
        self.group.add(self.buttons)
        all_page_sprites = self.group
        all_page_resizable = self.resizable

    def resize(self):
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image.fill(self.background)
        self.rect = self.image.get_rect()
        self.font = pygame.font.SysFont('Comic Sans MS', percentage(height, 24))
        self.text_surface = self.font.render("~UwU~", False, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (percentage(width, 50), percentage(height, 19))
        self.image.blit(self.text_surface, self.text_rect)
        n = len(self.texts)
        free_height = percentage(height, 38)
        free_width = percentage(width, 50)
        free_bottom = percentage(height, 7)
        height_between = percentage(height, 3)
        button_width = width - free_width
        button_height = (height - free_height - free_bottom - height_between * (n - 1)) // n
        for i, button in enumerate(self.buttons):
            button.change_cords(free_width // 2,
                                free_height + i * button_height + i * height_between,
                                button_width,
                                button_height)
        for circle in self.circles:
            circle.resize()

    def update(self, *args):
        if not args:
            self.circles.update()
            self.buttons.update()
            return
        event = args[0]
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.rect.collidepoint(args[0].pos):
                    self.texts[button.text]()


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Levels(pygame.sprite.Sprite):
    def __init__(self):
        global all_page_sprites, all_page_resizable
        self.group = pygame.sprite.Group()
        self.resizable = set()
        super().__init__(self.group)
        self.image = self.rect = None
        self.camera = Camera()
        self.background = COLORS["background"]
        self.color = COLORS["outline"]
        self.font = self.text_surface = self.text_rect = None
        self.buttons = pygame.sprite.Group()
        for text in sorted(listdir(LEVELS), key=lambda a: int(a[:-4])):
            Button(self.buttons, color=self.color, background=self.background, text=text[:-4])
        self.resize()
        self.group.add(self.buttons)
        self.resizable.add(self)
        all_page_sprites = self.group
        all_page_resizable = self.resizable

    def resize(self):
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image.fill(self.background)
        self.rect = self.image.get_rect()
        self.font = pygame.font.SysFont('Comic Sans MS', percentage(height, 20))
        self.text_surface = self.font.render("~Levels~", False, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (percentage(width, 50), percentage(height, 19))
        self.image.blit(self.text_surface, self.text_rect)
        n = len(listdir(LEVELS))
        n_width = 3
        free_width_side = percentage(width, 10)
        free_width_between = percentage(width, 4)
        free_top = percentage(height, 40)
        free_bottom = percentage(height, 10)
        free_height_between = percentage(height, 10)
        button_width = (width - 2 * free_width_side - (n_width - 1) * free_width_between) // n_width
        button_height = (height - 2 * free_bottom - (n_width - 1) * free_height_between) // n_width
        buttons = list(self.buttons)
        for i in range(n // n_width + 1):
            for j in range(min(3, n - i * n_width)):
                buttons[i * n_width + j].change_cords(free_width_side + j * button_width + j * free_width_between,
                                                      free_top + i * button_height + i * free_height_between,
                                                      button_width,
                                                      button_height)
        self.camera.update(self)

    def move_height(self, add):
        pass

    def update(self, *args):
        if not args:
            return
        event = args[0]
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in self.buttons:
                    if button.rect.collidepoint(args[0].pos):
                        print(button.text)
            # SAVED IN REASON OF BEING TO MANY LEVELS
            # if event.button == 4:
            #     self.rect = self.rect.move(0, -percentage(height, 2))
            #     self.camera.update(self)
            #     for elem in self.group:
            #         self.camera.apply(elem)
            # if event.button == 5:
            #     self.rect = self.rect.move(0, percentage(height, 2))
            #     self.camera.update(self)
            #     for elem in self.group:
            #         self.camera.apply(elem)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Menu()


class Game(pygame.sprite.Sprite):
    def __init__(self):
        global all_page_sprites, all_page_resizable
        self.group = pygame.sprite.Group()
        self.resizable = set()
        super().__init__(self.group)
        self.image = self.rect = None
        self.camera = Camera()
        self.buttons = pygame.sprite.Group()
        self.resize()
        all_page_sprites = self.group
        all_page_resizable = self.resizable

    def resize(self):
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image.fill(COLORS["background"])
        self.rect = self.image.get_rect()

    def update(self, *args):
        if not args:
            return
        event = args[0]


Menu()
full_screen = True
running = True
while running:
    for event_glob in pygame.event.get():
        if event_glob.type == pygame.QUIT:
            running = False
        if event_glob.type == pygame.KEYDOWN:
            if event_glob.key == pygame.K_F11 and full_screen:
                pygame.display.set_mode((percentage(width, 70), percentage(height, 70)), pygame.RESIZABLE)
                width = screen.get_width()
                height = screen.get_height()
                full_screen = False
            elif event_glob.key == pygame.K_F11 and not full_screen:
                pygame.display.set_mode(SYS_SIZE, pygame.NOFRAME)
                width, height = SYS_SIZE
                full_screen = True
                for resizable_elem in all_page_resizable:
                    resizable_elem.resize()
        if event_glob.type == pygame.VIDEORESIZE and not full_screen:
            pygame.display.set_mode(event_glob.size, pygame.RESIZABLE)
            width = screen.get_width()
            height = screen.get_height()
            for resizable_elem in all_page_resizable:
                resizable_elem.resize()
        all_page_sprites.update(event_glob)
    all_page_sprites.update()
    all_page_sprites.draw(screen)
    pygame.display.flip()


print("Bye =^=\tLove, Pinka")
pygame.quit()
