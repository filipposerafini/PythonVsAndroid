import time
import random
import pygame
from pygame.locals import *

class Apple:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load('apple.png').convert()

    def draw(self, surface, cell_size):
        surface.blit(self.image, (self.x * cell_size, self.y * cell_size))

class Snake:

    def __init__(self, x, y, length, path):
        self.x = []
        self.y = []
        self.direction = 0 if x < 32 else 2
        self.length = length
        self.image = pygame.image.load(path).convert()
        for i in range(0, length):
            self.x.append(x - i if x < 32 else x + i)
            self.y.append(y)

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

    def draw(self, surface, cell_size):
        for i in range(0, self.length):
            surface.blit(self.image, (self.x[i]*cell_size, self.y[i]*cell_size))

def isCollision(x1, y1, x2, y2):
    if x1 == x2 and y1 == y2:
        return True
    else:
        return False

def eatApple(snake, apple):
    if isCollision(snake.x[0], snake.y[0], apple.x, apple.y):
        snake.x.append(snake.x[snake.length - 1])
        snake.y.append(snake.y[snake.length - 1])
        snake.length += 1
        return True
    return False

def hitSnake(snake1, snake2):
    for i in range(1 if snake1 is snake2 else 0, snake2.length):
        if (isCollision(snake1.x[0], snake1.y[0], snake2.x[i], snake2.y[i])):
            return True
    return False

def hitBorder(snake):
    if snake.x[0] < 0 or snake.x[0] > width / cell_size:
        return True
    elif snake.y[0] < 0 or snake.y[0] > height / cell_size:
        return True
    else:
        return False



# Variables
width = 1280
height = 960
cell_size = 20

# Init
pygame.init()
pygame.display.set_caption('Python vs Viper')
display = pygame.display.set_mode((width, height), pygame.HWSURFACE)
viper = Snake(18, 10, 4, 'viper.png')
python = Snake(46, 38, 4, 'python.png')
apple = Apple(random.randint(0, width / cell_size - 1 ), random.randint(0, height / cell_size - 1))
running = True

# Loop
while running:
    pygame.event.pump()
    keys = pygame.key.get_pressed()
    if keys[K_RIGHT]:
        viper.changeDirection(0)
    elif keys[K_LEFT]:
        viper.changeDirection(2)
    elif keys[K_UP]:
        viper.changeDirection(3)
    elif keys[K_DOWN]:
        viper.changeDirection(1)
    if keys[K_d]:
        python.changeDirection(0)
    elif keys[K_a]:
        python.changeDirection(2)
    elif keys[K_w]:
        python.changeDirection(3)
    elif keys[K_s]:
        python.changeDirection(1)
    if keys[K_ESCAPE]:
        running = False

    # Move Snakes
    viper.updatePosition()
    python.updatePosition()

    # Check Collisions
    if hitSnake(viper, viper):
        running = False
    if hitSnake(python, python):
        running = False
    if hitSnake(viper, python):
        running = False
    if hitSnake(python, viper):
        running = False
    if hitBorder(viper):
        running = False
    if hitBorder(python):
        running = False
    if eatApple(viper, apple) or eatApple(python, apple):
        apple = Apple(random.randint(0, width / cell_size - 1 ), random.randint(0, height / cell_size - 1))

    # Update Display
    if running:
        display.fill((0, 0, 0))
        viper.draw(display, cell_size)
        python.draw(display, cell_size)
        apple.draw(display, cell_size)
        pygame.display.flip()

    time.sleep(50.0 / 1000.0)

# Quit
pygame.quit()
