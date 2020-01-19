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
MUSIC = join(split(getcwd())[0], "music")
USER_LEVELS = join(split(getcwd())[0], "user_levels")
COLORS = {
    # "background": (255, 100, 100),
    "background": (250, 100, 100),
    "outline": (255, 255, 255)
}
BLOCK_SIZE = (30, 30)  # размер всех изображение

# global variables
all_page_sprites = pygame.sprite.Group()
all_page_resizable = set()


def percentage(limit, percent):
    return int(limit / 100 * percent)


def exit_game():
    global running
    running = False


def load_image(name, color_key=None):
    image = pygame.image.load(name)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class MusicPlayer:
    def __init__(self, mute=False, playing=True, now_ind=0, volume=0.5):
        self.volume = volume
        self.mute = mute
        self.playing = playing
        self.now_ind = now_ind
        self.songs = listdir(MUSIC)

    def check_and_start_next(self, song=""):
        if not pygame.mixer.music.get_busy() or not self.playing:
            self.playing = True
            if not song:
                self.now_ind = (self.now_ind + 1) % len(self.songs)
                pygame.mixer.music.load(join(MUSIC, self.songs[self.now_ind]))
            else:
                pygame.mixer.music.load(join(MUSIC, song))
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(self.volume)

    def play_song(self, song):
        if self.mute:
            return
        pygame.mixer.music.load(join(MUSIC, song))
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(self.volume)

    def change_volume(self, numb):
        self.mute = False
        self.volume = min(max(self.volume + numb, 0), 1)
        pygame.mixer.music.set_volume(self.volume)

    def mute_song(self):
        if self.mute:
            pygame.mixer.music.set_volume(self.volume)
        else:
            pygame.mixer.music.set_volume(0)
        self.mute = not self.mute

    def stop(self):
        self.playing = False
        pygame.mixer.music.pause()

    def stop_play(self):
        if not self.playing:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.playing = not self.playing

    def set_volume_directly(self, numb):
        self.volume = max(min(numb, 1), 0)
        pygame.mixer.music.set_volume(self.volume)


music_player = MusicPlayer()


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
            "Create": Create,
            "Settings": list,
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
            music_player.check_and_start_next("menu.mp3")
            return
        event = args[0]
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.rect.collidepoint(args[0].pos):
                    self.texts[button.text]()


class LevelEditor(pygame.sprite.Sprite):
    def __init__(self, level: str):
        global all_page_sprites, all_page_resizable

        self.level = level
        self.group = pygame.sprite.Group()
        self.resizable = set()
        super().__init__(self.group)
        self.image = self.rect = None

        self.background = COLORS["background"]
        self.color = COLORS["outline"]

        self.w = 500
        self.h = 500
        self.board = [[0] * self.w for _ in range(self.h)]

        self.resize()
        self.resizable.add(self)
        all_page_sprites = self.group
        all_page_resizable = self.resizable

    def resize(self):
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image.fill(self.background)
        self.rect = self.image.get_rect()
        # HERE NEEDED BOARD!!!!!!

    def update(self, *args):
        if not args:
            music_player.check_and_start_next("menu.mp3")
            return
        event = args[0]
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Create()


class NameInput(pygame.sprite.Sprite):
    def __init__(self):
        global all_page_sprites, all_page_resizable
        self.group = pygame.sprite.Group()
        self.resizable = set()
        super().__init__(self.group)
        self.image = self.rect = None

        self.background = COLORS["background"]
        self.color = COLORS["outline"]
        self.font = self.text_surface = self.text_rect = None
        self.font_static = self.text_surface_static = self.text_rect_static = None
        self.text = ""

        self.resize()
        self.resizable.add(self)
        all_page_sprites = self.group
        all_page_resizable = self.resizable

    def resize(self):
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image.fill(self.background)
        self.rect = self.image.get_rect()
        self.font = pygame.font.SysFont('Comic Sans MS', percentage(height, 20))
        self.text_surface_static = self.font.render("Type level name", False, self.color)
        self.text_rect_static = self.text_surface_static.get_rect()
        self.text_rect_static.center = (percentage(width, 50), percentage(height, 19))
        self.image.blit(self.text_surface_static, self.text_rect_static)

        self.text_surface = self.font.render(self.text, False, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (percentage(width, 50), percentage(height, 65))
        self.image.blit(self.text_surface, self.text_rect)

    def update(self, *args):
        if not args:
            music_player.check_and_start_next("menu.mp3")
            return
        event = args[0]
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Create()
            if ((ord("0") <= event.key <= ord("9") or ord("a") <= event.key <= ord("z") or event.key == pygame.K_SPACE)
                    and len(self.text) < 5):
                self.text += chr(event.key)
                self.resize()
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.resize()
            if event.key == pygame.K_RETURN and self.text != "" and self.text + ".txt" not in listdir(USER_LEVELS):
                with open(join(USER_LEVELS, self.text + ".txt"), "w", encoding="UTF-8"):
                    pass
                LevelEditor(self.text)


class EditLevel(pygame.sprite.Sprite):
    def __init__(self):
        global all_page_sprites, all_page_resizable
        self.group = pygame.sprite.Group()
        self.resizable = set()
        super().__init__(self.group)
        self.image = self.rect = None

        self.background = COLORS["background"]
        self.color = COLORS["outline"]
        self.font = self.text_surface = self.text_rect = None

        self.buttons = pygame.sprite.Group()
        self.texts = {
            "new": list,
            "edit": list,
            "delete": list
        }
        for text in self.texts.keys():
            Button(self.buttons, color=self.color, background=self.background, text=text)

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
        self.text_surface = self.font.render("Choose level", False, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (percentage(width, 50), percentage(height, 19))
        self.image.blit(self.text_surface, self.text_rect)
        n = len(self.texts)
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

    def update(self, *args):
        if not args:
            music_player.check_and_start_next("menu.mp3")
            return
        event = args[0]
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in self.buttons:
                    if button.rect.collidepoint(args[0].pos):
                        print(button.text)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Create()


class Create(pygame.sprite.Sprite):
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
        self.texts = {
            "new": NameInput,
            "edit": EditLevel,
            "delete": list
        }
        for text in self.texts.keys():
            Button(self.buttons, color=self.color, background=self.background, text=text)
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
        self.text_surface = self.font.render("~Create level~", False, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (percentage(width, 50), percentage(height, 19))
        self.image.blit(self.text_surface, self.text_rect)
        n = len(self.texts)
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

    def update(self, *args):
        if not args:
            return
        event = args[0]
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in self.buttons:
                    if button.rect.collidepoint(args[0].pos):
                        self.texts[button.text]()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Menu()


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
        for text in sorted(listdir(LEVELS)):
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
            music_player.check_and_start_next("menu.mp3")
            return
        event = args[0]
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in self.buttons:
                    if button.rect.collidepoint(args[0].pos):
                        Game(button.text)
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


class Block(pygame.sprite.Sprite):
    def __init__(self, group, image, x, y, text=""):
        super().__init__(group)
        self.text = text
        self.image = load_image(image)
        self.rect = self.image.get_rect().move(x, y)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self, group, solid_group, transparent_group, image, x, y, restart, completed):
        super().__init__(group)
        self.group = group
        self.completed = completed
        self.start_pos = (x, y)
        self.restart = restart
        self.solid_group = solid_group
        self.transparent_group = transparent_group
        self.image = load_image(image)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(x, y)
        self.jump_power = 7
        self.gravity = 0.30
        self.y_vel = 0
        self.x_vel = 0
        self.on_ground = False
        self.finished = False

    def move(self, vx, vy):
        if self.finished:
            return
        self.rect.x += vx
        self.rect.y += vy
        for block in self.solid_group:
            if pygame.sprite.collide_mask(self, block):
                if vx > 0:
                    self.rect.x -= vx
                if vx < 0:
                    self.rect.x -= vx
                if vy > 0:
                    self.rect.bottom = block.rect.top
                    self.on_ground = True
                    self.y_vel = 0
                if vy < 0:
                    self.rect.top = block.rect.bottom
                    self.y_vel = 0
        for block in self.transparent_group:
            if pygame.sprite.collide_mask(self, block):
                if block.text == "e":
                    self.finish_level()
                if block.text in [".", ":", "*"]:
                    self.restart()

    def jump(self):
        if self.on_ground:
            self.y_vel = -self.jump_power
            self.on_ground = False

    def finish_level(self):
        self.finished = True
        self.image = load_image(join(IMAGES, "player_won.png"))
        self.mask = pygame.mask.from_surface(self.image)
        self.completed()

    def update(self, *args):
        if self.finished:
            return
        if not args:
            self.y_vel += self.gravity
            self.move(0, self.y_vel)
            return


class Game(pygame.sprite.Sprite):
    SOLID_BLOCKS = {
        "#": join(IMAGES, "solid.png")
    }
    TRANSPARENT_BLOCKS = {
        ".": join(IMAGES, "water_top.png"),
        ":": join(IMAGES, "water_solid.png"),
        "e": join(IMAGES, "end.png"),
        "*": join(IMAGES, "spikes.png"),
        ">": join(IMAGES, "point_right.png"),
        "<": join(IMAGES, "point_left.png"),
        "^": join(IMAGES, "point_up.png"),
        "|": join(IMAGES, "point_down.png")
    }
    PLAYERS = {
        "@": join(IMAGES, "player.png")
    }

    def __init__(self, level):
        global all_page_sprites, all_page_resizable
        self.level = level
        self.group = pygame.sprite.Group()
        self.resizable = set()
        self.background = COLORS["background"]
        super().__init__(self.group)
        self.image = self.rect = None
        self.camera = Camera()
        self.solid_blocks = pygame.sprite.Group()
        self.transparent_blocks = pygame.sprite.Group()
        self.players_group = pygame.sprite.Group()
        self.all_blocks = pygame.sprite.Group()
        self.player = None
        self.load_level()
        self.all_blocks.add(self.solid_blocks)
        self.all_blocks.add(self.transparent_blocks)
        self.resize()
        self.group.add(self.all_blocks)
        self.group.add(self.players_group)
        self.resizable.add(self)
        all_page_sprites = self.group
        all_page_resizable = self.resizable
        self.font = self.text_surface = self.text_rect = None
        music_player.stop()

    def load_level(self):
        size = 30
        with open(join(LEVELS, self.level + ".txt"), "r", encoding="UTF-8") as level:
            level_data = list(map(str.strip, level.readlines()))
        for i, line in enumerate(level_data):
            for j, elem in enumerate(line):
                if elem in self.SOLID_BLOCKS:
                    Block(self.solid_blocks, self.SOLID_BLOCKS[elem], j * size, i * size, elem)
                if elem in self.TRANSPARENT_BLOCKS:
                    Block(self.transparent_blocks, self.TRANSPARENT_BLOCKS[elem], j * size, i * size, elem)
                if elem in self.PLAYERS:
                    Player(self.players_group, self.solid_blocks, self.transparent_blocks, self.PLAYERS[elem],
                           j * size, i * size, self.restart, self.resize)
        self.player = list(self.players_group)[0]

    def restart(self):
        self.__init__(self.level)

    def resize(self):
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image.fill(self.background)
        if self.player.finished:
            self.font = pygame.font.SysFont('Comic Sans MS', percentage(height, 30))
            self.text_surface = self.font.render("Completed!", False, (255, 255, 255))
            self.text_rect = self.text_surface.get_rect()
            self.text_rect.center = (width // 2, percentage(height, 15))
            self.image.blit(self.text_surface, self.text_rect)
        self.rect = self.image.get_rect()
        self.camera.update(self.player)
        for elem in self.all_blocks:
            self.camera.apply(elem)
        self.camera.apply(self.player)

    def update(self, *args):
        if not args:
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_SPACE] or pressed[pygame.K_w] or pressed[pygame.K_UP]:
                self.player.jump()
            if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
                self.player.move(-2, 0)
            if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
                self.player.move(2, 0)
            self.camera.update(self.player)
            for elem in self.all_blocks:
                self.camera.apply(elem)
            self.camera.apply(self.player)
            return
        event = args[0]
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Levels()
            if event.key == pygame.K_r:
                self.restart()


Menu()
fps = 60
clock = pygame.time.Clock()
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
            elif event_glob.key == pygame.K_F1:
                music_player.mute_song()
            elif event_glob.key == pygame.K_F2:
                music_player.change_volume(-0.05)
            elif event_glob.key == pygame.K_F3:
                music_player.change_volume(0.05)
        if event_glob.type == pygame.VIDEORESIZE and not full_screen:
            pygame.display.set_mode(event_glob.size, pygame.RESIZABLE)
            width = screen.get_width()
            height = screen.get_height()
            for resizable_elem in all_page_resizable:
                resizable_elem.resize()
        all_page_sprites.update(event_glob)
    all_page_sprites.update()
    all_page_sprites.draw(screen)
    pygame.display.update()
    clock.tick(fps)


print("Bye =^=\nLove, Pinka")
pygame.quit()
