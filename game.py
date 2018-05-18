import random
import pygame
from pygame.locals import *

# Constants
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
KEYS = {0 : [K_RIGHT, K_d],
        1 : [K_DOWN, K_s],
        2 : [K_LEFT, K_a],
        3 : [K_UP, K_w]}
CELL_COUNT_X = 96
CELL_COUNT_Y = 54
EASY = 30
HARD = 50

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
        if self.x[0] < 0 or self.x[0] > CELL_COUNT_X:
            return True
        elif self.y[0] < 0 or self.y[0] > CELL_COUNT_Y:
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

def showDifficulty(surface, width, height, is_easy):
    easy = display_text(surface, " Easy ", height / 10, WHITE if is_easy else RED, (width / 3, 2.5 * height / 3), RED if is_easy else BLACK)
    hard = display_text(surface, " Hard ", height / 10, WHITE if not is_easy else RED, (2 * width / 3, 2.5 * height / 3), RED if not is_easy else BLACK)
    pygame.display.flip()
    return easy, hard

def showMenu(surface, width, height):
    surface.fill(BLACK)
    display_text(surface, "Python", height / 5, BLUE, (width / 3 + width / 64, height / 3))
    display_text(surface, "VS", height / 5, RED, (width / 2 + width / 64, height / 3))
    display_text(surface, "Viper", height / 5, GREEN, (2 * width / 3 - width / 64, height / 3))
    single = display_text(surface, "Single Player", height / 10, WHITE, (width / 3, 2 * height / 3))
    multi = display_text(surface, "Multi Player", height / 10, WHITE, (2 * width / 3, 2 * height / 3))
    pygame.display.flip()
    return single, multi

def showGameOver(surface, width, height):
    playSong('resources/game_over.wav')
    surface.fill(BLACK)
    display_text(surface, "Game Over!", height / 5, RED, (width / 2, height / 3))
    restart = display_text(surface, "Press Enter to restart the game", height / 12, WHITE, (width / 2, 2 * height / 3))
    menu = display_text(surface, "Press Esc to retrun the menu", height / 12, WHITE, (width / 2, 2 * height / 3 + height / 10))
    pygame.display.flip()
    return restart, menu

# Variables
clock = pygame.time.Clock()
cell_size = 22
width = CELL_COUNT_X * cell_size
height = CELL_COUNT_Y * cell_size

# Init
pygame.init()
pygame.display.set_caption('Python vs Viper')
icon = pygame.image.load('resources/icon.png')
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)
running = True
in_menu = True
is_easy = True

# Loop
while running:

    if in_menu:
        single, multi = showMenu(screen, width, height)
        while in_menu:
            easy, hard = showDifficulty(screen, width, height, is_easy)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    in_menu = False
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        game = Game(1, EASY if is_easy else HARD)
                        in_menu = False
                elif event.type == MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if single.collidepoint(mouse_pos):
                        game = Game(1, EASY if is_easy else HARD)
                        in_menu = False
                    elif multi.collidepoint(mouse_pos):
                        game = Game(2, EASY if is_easy else HARD)
                        in_menu = False
                    elif easy.collidepoint(mouse_pos):
                        is_easy = True
                    elif hard.collidepoint(mouse_pos):
                        is_easy = False
    while game.running:
        # Get Keyboard Input
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                for i in range(0, len(game.snakes)):
                    for direction, keys in KEYS.items():
                        if event.key == keys[i]:
                            game.snakes[i].changeDirection(direction)
                        elif event.key == K_ESCAPE:
                            game.running = False
                            in_menu = True
        # Move and Draw Snakes
        if game.updateSnakes():
            screen.fill(BLACK)
            game.drawSnakes(screen, cell_size)
            game.showScores(screen, width, height)
            pygame.display.flip()
            clock.tick(game.fps)
    else:
        if running:
            restart, menu = showGameOver(screen, width, height)
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
