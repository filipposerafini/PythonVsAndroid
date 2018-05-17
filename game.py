import random
import pygame
from pygame.locals import *

def isCollision(x1, y1, x2, y2):
    if x1 == x2 and y1 == y2:
        return True
    else:
        return False

class Apple:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load('resources/apple.png').convert()

    def draw(self, surface, cell_size):
        surface.blit(self.image, (self.x * cell_size, self.y * cell_size))

class Snake:

    def __init__(self, x, y, length, path):
        self.x = [x]
        self.y = [y]
        self.score = 0
        self.length = length
        self.image = pygame.image.load(path).convert()

    def initDirection(self, cell_count_x):
        self.direction = 0 if self.x[0] < cell_count_x / 2 else 2
        for i in range(1, self.length):
            self.x.append(self.x[0] - i if self.x[0] < cell_count_x / 2 else self.x[0] + i)
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
            self.addPiece()
            return True
        return False
    
    def hitSnake(self, snake):
        for i in range(1 if self is snake else 0, snake.length):
            if isCollision(self.x[0], self.y[0], snake.x[i], snake.y[i]):
                return True
        return False
    
    def hitBorder(self, cell_count_x, cell_count_y):
        if self.x[0] < 0 or self.x[0] > cell_count_x:
            return True
        elif self.y[0] < 0 or self.y[0] > cell_count_y:
            return True
        else:
            return False

    def draw(self, surface, cell_size):
        for i in range(0, self.length):
            surface.blit(self.image, (self.x[i]*cell_size, self.y[i]*cell_size))

class Game:

    def __init__(self, players, difficulty, width, height, cell_size):
        self.difficulty = difficulty
        self.cell_count_x = width / cell_size
        self.cell_count_y = height / cell_size
        self.cell_size = cell_size
        self.apple = Apple(self.cell_count_x / 2, self.cell_count_y / 2)
        self.snakes = []
        self.snakes.append(Snake(random.randint(0, self.cell_count_x / 2), random.randint(0, self.cell_count_y / 2), 10, 'resources/python.png'))
        self.snakes[0].initDirection(self.cell_count_x)
        if players == 2:
            self.snakes.append(Snake(random.randint(self.cell_count_x / 2, self.cell_count_x), random.randint(self.cell_count_y / 2, self.cell_count_y), 10, 'resources/viper.png'))
            self.snakes[1].initDirection(self.cell_count_x)
        self.running = True

    def restart(self):
        return Game(len(self.snakes), self.difficulty, self.cell_count_x * self.cell_size, self.cell_count_y * self.cell_size, self.cell_size)

    def updateSnakes(self):
        for snake in self.snakes:
            snake.updatePosition()
            if snake.hitSnake(snake):
                self.running = False
            if snake.hitBorder(self.cell_count_x, self.cell_count_y):
                self.running = False
            if snake.eatApple(self.apple):
                self.apple = Apple(random.randint(0, self.cell_count_x - 1 ), random.randint(0, self.cell_count_y - 1))

    def drawSnakes(self, surface):
        for snake in self.snakes:
            snake.draw(surface, self.cell_size)
        self.apple.draw(surface, self.cell_size)

def write(surface, text, dimension, color, position):
    font = pygame.font.Font('resources/font.otf', dimension)
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    rect.center = position
    surface.blit(text_surface, rect)
    return rect

def showMenu(surface, width, height):
    write(surface, "Python", 200, (0, 0, 255), (width / 3 + 30, height / 3))
    write(surface, "VS", 200, (255, 0, 0), (width / 2 + 30, height / 3))
    write(surface, "Viper", 200, (0, 255, 0), (2 * width / 3 - 30, height / 3))
    single = write(surface, "Single Player", 80, (255, 255, 255), (width / 4, 2 * height / 3))
    multi = write(surface, "Multi Player", 80, (255, 255, 255), (3 * width / 4, 2 * height / 3))
    return single, multi

def showScores(surface, snakes):
    write(surface, "Python: " + str(snakes[0].score), 120, (0, 0, 255), (250, 100))
    if len(snakes) == 2:
        write(surface, "Viper: " + str(snakes[1].score), 120, (0, 255, 0), (1720, 100))

def showGameOver(surface, width, height):
    write(surface, "Game Over!", 200, (255, 0, 0), (width / 2, height / 3))
    restart = write(surface, "Press Enter to restart the game", 80, (255, 255, 255), (width / 2, 2 * height / 3))
    menu = write(surface, "Press Esc to retrun the menu", 80, (255, 255, 255), (width / 2, 2 * height / 3 + 100))
    return restart, menu

# Variables
clock = pygame.time.Clock()
width = 1920
height = 1080
cell_size = 20

# Init
pygame.init()
pygame.display.set_caption('Python vs Viper')
icon = pygame.image.load('resources/icon.png')
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)

running = True
in_menu = True

# Loop
while running:

    while not in_menu and game.running:
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            game.snakes[0].changeDirection(0)
        elif keys[K_LEFT]:
            game.snakes[0].changeDirection(2)
        elif keys[K_UP]:
            game.snakes[0].changeDirection(3)
        elif keys[K_DOWN]:
            game.snakes[0].changeDirection(1)
        if len(game.snakes) == 2:
            if keys[K_d]:
                game.snakes[1].changeDirection(0)
            elif keys[K_a]:
                game.snakes[1].changeDirection(2)
            elif keys[K_w]:
                game.snakes[1].changeDirection(3)
            elif keys[K_s]:
                game.snakes[1].changeDirection(1)
        if keys[K_ESCAPE]:
            in_menu = True
    
        # Move Snakes
        game.updateSnakes()

        # Update Display
        screen.fill((0, 0, 0))
        if game.running:
            game.drawSnakes(screen)
            showScores(screen, game.snakes)

        pygame.display.flip()
        clock.tick(game.difficulty)
    else:
        screen.fill((0, 0, 0))
        if not in_menu:
            restart, menu = showGameOver(screen, width, height)
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
        else:
            single, multi = showMenu(screen, width, height)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        game = Game(1, 30, width, height, cell_size)
                        in_menu = False
                elif event.type == MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if single.collidepoint(mouse_pos):
                        game = Game(1, 30, width, height, cell_size)
                        in_menu = False
                    elif multi.collidepoint(mouse_pos):
                        game = Game(2, 30, width, height, cell_size)
                        in_menu = False
    pygame.display.flip()
# Quit
pygame.quit()

