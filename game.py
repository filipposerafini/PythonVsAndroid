import random
import pygame
from pygame.locals import *

## Constants
# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
# Keyboard
KEYS = {0 : [K_RIGHT, K_d],
        1 : [K_DOWN, K_s],
        2 : [K_LEFT, K_a],
        3 : [K_UP, K_w]}
# Grid Size
CELL_COUNT_X = 96
CELL_COUNT_Y = 54
# FPS
EASY = 30
HARD = 60
# Animation
ANIMATION_SPEED = 10

class Apple:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface, cell_size):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(RED)
        surface.blit(body, (self.x * cell_size, self.y * cell_size))

class Snake:

    def __init__(self, x, y, length, color):
        self.x = [x]
        self.y = [y]
        self.length = length
        self.color = color
        self.direction = 0 if self.x[0] < CELL_COUNT_X / 2 else 2
        self.score = 0
        for i in range(1, self.length):
            self.x.append(self.x[0] - i if self.x[0] < CELL_COUNT_X / 2 else self.x[0] + i)
            self.y.append(self.y[0])

    def changeDirection(self, direction):
        if direction != (self.direction + 2) % 4:
            self.direction = direction
    
    def updatePosition(self):
        for i in range(self.length - 1 , 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]
        if self.direction == 0:
            self.x[0] += 1 
        elif self.direction == 1:
            self.y[0] += 1
        elif self.direction == 2:
            self.x[0] -= 1
        elif self.direction == 3:
            self.y[0] -= 1

    def addPiece(self):
        self.x.append(self.x[self.length - 1])
        self.y.append(self.y[self.length - 1])
        self.length += 1
        self.score += 10

    def eatApple(self, apple):
        if isCollision(self.x[0], self.y[0], apple.x, apple.y):
            playSound('resources/apple.wav')
            self.addPiece()
            return True
        return False
    
    def hitSnake(self, snake):
        for i in range(1 if self is snake else 0, snake.length):
            if isCollision(self.x[0], self.y[0], snake.x[i], snake.y[i]):
                return True
        return False
    
    def hitBorder(self):
        if self.x[0] < 0 or self.x[0] >= CELL_COUNT_X:
            return True
        elif self.y[0] < 0 or self.y[0] >= CELL_COUNT_Y:
            return True
        else:
            return False

    def draw(self, surface, cell_size):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(self.color)
        for i in range(0, self.length):
            surface.blit(body, (self.x[i] * cell_size, self.y[i] * cell_size))

class Game:

    def __init__(self, players, fps):
        playSong('resources/snake.wav')
        self.fps = fps
        self.apple = Apple(CELL_COUNT_X / 2, CELL_COUNT_Y / 2)
        self.snakes = []
        self.snakes.append(Snake(random.randint(0, CELL_COUNT_X / 2), random.randint(0, CELL_COUNT_Y / 2), 10, BLUE))
        if players == 2:
            self.snakes.append(Snake(random.randint(CELL_COUNT_X / 2, CELL_COUNT_X - 1), random.randint(CELL_COUNT_Y / 2, CELL_COUNT_Y - 1), 10, GREEN))
        self.running = True

    def restart(self):
        return Game(len(self.snakes), self.fps)

    def updateSnakes(self):
        for snake in self.snakes:
            snake.updatePosition()
            if snake.hitSnake(snake):
                self.running = False
            if snake.hitBorder():
                self.running = False
            if snake.eatApple(self.apple):
                self.apple = Apple(random.randint(0, CELL_COUNT_X - 1 ), random.randint(0, CELL_COUNT_Y - 1))
        return self.running

    def drawSnakes(self, surface, cell_size):
        for snake in self.snakes:
            snake.draw(surface, cell_size)
        self.apple.draw(surface, cell_size)

    def showScores(self, surface, width, height):
        display_text(surface, "Python: " + str(self.snakes[0].score), height / 9, BLUE, (width / 8, height / 10))
        if len(self.snakes) == 2:
            display_text(surface, "Viper: " + str(self.snakes[1].score), height / 9, GREEN, (width / 1.13, height / 10))

    def showGameOver(self, surface, width, height):
        playSong('resources/game_over.wav')
        surface.fill(BLACK)
        display_text(surface, "Game Over!", height / 5, RED, (width / 2, height / 3))
        restart = display_text(surface, "Press Enter to restart the game", height / 12, WHITE, (width / 2, 2 * height / 3))
        menu = display_text(surface, "Press Esc to retrun the menu", height / 12, WHITE, (width / 2, 2 * height / 3 + height / 10))
        pygame.display.flip()
        return restart, menu

def display_text(surface, text, dimension, color, position, *background):
    font = pygame.font.Font('resources/font.otf', int(dimension))
    text_surface = font.render(text, True, color, background)
    rect = text_surface.get_rect()
    rect.center = position
    surface.blit(text_surface, rect)
    return rect

def isCollision(x1, y1, x2, y2):
    if x1 == x2 and y1 == y2:
        return True
    else:
        return False

def playSong(song):
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=-1)

def playSound(file):
    sound = pygame.mixer.Sound(file)
    sound.play()

def difficultySettings(surface, width, height, easy):
    easy_button = display_text(surface, " Easy ", height / 10, WHITE if easy else RED, (width / 3, 2 * height / 6), RED if easy else BLACK)
    hard_button = display_text(surface, " Hard ", height / 10, WHITE if not easy else RED, (2 * width / 3, 2 * height / 6), RED if not easy else BLACK)
    return easy_button, hard_button

def audioSettings(surface, width, height, sound, music):
    sound_button = display_text(surface, " Sound ", height / 10, WHITE if sound else RED, (width / 3, 4 * height / 6), RED if sound else BLACK)
    music_button = display_text(surface, " Music ", height / 10, WHITE if music else RED, (2 * width / 3, 4 * height / 6), RED if music else BLACK)
    return sound_button, music_button

def showSettings(width, height, easy, sound, music):
    surface = pygame.Surface((width, height))
    surface.fill(BLACK)
    display_text(surface, "Difficulty:", height / 10, WHITE, (width / 2, height / 6))
    easy_button, hard_button = difficultySettings(surface, width, height, easy)
    sound_button, music_button = audioSettings(surface, width, height, sound, music)
    display_text(surface, "Audio:", height / 10, WHITE, (width / 2, 3 * height / 6))
    done_button = display_text(surface, " Done ", height / 10, BLACK, (width / 2, 5 * height / 6), WHITE)
    return surface, easy_button, hard_button, sound_button, music_button, done_button

def showMenu(width, height):
    surface = pygame.Surface((width, height))
    surface.fill(BLACK)
    display_text(surface, "Python", height / 5, BLUE, (width / 3 + width / 64, height / 3))
    display_text(surface, "VS", height / 5, RED, (width / 2 + width / 64, height / 3))
    display_text(surface, "Viper", height / 5, GREEN, (2 * width / 3 - width / 64, height / 3))
    single_button = display_text(surface, "Single Player", height / 10, WHITE, (width / 3, 2 * height / 3))
    multi_button = display_text(surface, "Multi Player", height / 10, WHITE, (2 * width / 3, 2 * height / 3))
    settings_button = display_text(surface, " Settings ", height / 10, BLACK, (width / 2, 2.5 * height / 3), WHITE)
    return surface, single_button, multi_button, settings_button

def fadeBetweenSurfaces(surface1, surface2):
    for i in range(0, 255, ANIMATION_SPEED):
        surface2.set_alpha(i)
        surface1.blit(surface2, (0,0))
        pygame.display.flip()

# Init
pygame.init()
info = pygame.display.Info()
cell_size = int(info.current_w / 150)
width = CELL_COUNT_X * cell_size
height = CELL_COUNT_Y * cell_size
clock = pygame.time.Clock()
pygame.display.set_caption('Python vs Viper')
icon = pygame.image.load('resources/icon.png')
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)
playSong('resources/intro.wav')
running = True
in_menu = True
in_settings = False
easy = True
sound = True
music = True

menu, single_button, multi_button, settings_button = showMenu(width, height)
settings, easy_button, hard_button, sound_button, music_button, done_button = showSettings(width, height, easy, sound, music)

# Loop
while running:

    while in_menu:
        menu, single_button, multi_button, settings_button = showMenu(width, height)
        screen.blit(menu, (0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                in_menu = False
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    game = Game(1, EASY if easy else HARD)
                    in_menu = False
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if single_button.collidepoint(mouse_pos):
                    game = Game(1, EASY if easy else HARD)
                    in_menu = False
                elif multi_button.collidepoint(mouse_pos):
                    game = Game(2, EASY if easy else HARD)
                    in_menu = False
                elif settings_button.collidepoint(mouse_pos):
                    in_menu = False
                    in_settings = True
                    fadeBetweenSurfaces(screen, settings)
    
    while in_settings:
        settings, easy_button, hard_button, sound_button, music_button, done_button = showSettings(width, height, easy, sound, music)
        screen.blit(settings, (0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                in_settings = False
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if easy_button.collidepoint(mouse_pos):
                    easy = True
                elif hard_button.collidepoint(mouse_pos):
                    easy = False
                elif sound_button.collidepoint(mouse_pos):
                    sound = not sound
                elif music_button.collidepoint(mouse_pos):
                    music = not music
                elif done_button.collidepoint(mouse_pos):
                    in_menu = True
                    in_settings = False
                    fadeBetweenSurfaces(screen, menu)

    while 'game' in locals() and game.running:
        # Get Keyboard Input
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                for i in range(0, len(game.snakes)):
                    for direction, keys in KEYS.items():
                        if event.key == keys[i]:
                            game.snakes[i].changeDirection(direction)
                            break
                        elif event.key == K_ESCAPE:
                            game.running = False
                            in_menu = True
                    continue
        # Move and Draw Snakes
        if game.updateSnakes():
            screen.fill(BLACK)
            game.drawSnakes(screen, cell_size)
            game.showScores(screen, width, height)
            pygame.display.flip()
            clock.tick(game.fps)
    else:
        if running and not in_menu:
            restart, menu = game.showGameOver(screen, width, height)
        while running and not in_menu and not game.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        game = game.restart()
                    elif event.key == K_ESCAPE:
                        in_menu = True
                elif event.type == MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if restart.collidepoint(mouse_pos):
                        game = game.restart()
                    elif menu.collidepoint(mouse_pos):
                        in_menu = True
# Quit
pygame.quit()
