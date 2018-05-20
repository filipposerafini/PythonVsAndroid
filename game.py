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

    def _addPiece(self):
        self.x.append(self.x[self.length - 1])
        self.y.append(self.y[self.length - 1])
        self.length += 1
        self.score += 10

    def _isCollision(self, x, y):
        if self.x[0] == x and self.y[0] == y:
            return True
        else:
            return False

    def eatApple(self, apple):
        if self._isCollision(apple.x, apple.y):
            self._addPiece()
            return True
        return False
    
    def hitSnake(self, snake):
        for i in range(1 if self is snake else 0, snake.length):
            if self._isCollision(snake.x[i], snake.y[i]):
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

class Page:

    def __init__(self, width, height):
        self.surface = pygame.Surface((width, height))
        self.buttons = {}
        self.keys = {
                'Sound' : K_n,
                'Music' : K_m
                }

    def update(self):
        self.surface.fill(BLACK)

    def getButton(self, mouse_pos):
        for button, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                return button

    def getKeys(self, key):
        for action, keyboard in self.keys.items():
            if isinstance(keyboard, list):
                if key in keyboard:
                    return action
            else:
                if key == keyboard:
                    return action

    def display_text(self, text, dimension, color, position, *background):
        font = pygame.font.Font('resources/font.otf', int(dimension))
        text_surface = font.render(text, True, color, background)
        rect = text_surface.get_rect()
        rect.center = position
        self.surface.blit(text_surface, rect)
        return rect

class Menu(Page):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.keys['Single'] = K_1
        self.keys['Multi'] = K_2
        self.keys['Settings'] = K_TAB
        self.keys['Quit'] = K_ESCAPE

    def update(self):
        super().update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.display_text("Python", height / 5, BLUE, (width / 3 + width / 64, height / 3))
        self.display_text("VS", height / 5, RED, (width / 2 + width / 64, height / 3))
        self.display_text("Viper", height / 5, GREEN, (2 * width / 3 - width / 64, height / 3))
        self.buttons['Single'] = self.display_text("Single Player", height / 10, WHITE, (width / 3, 2 * height / 3))
        self.buttons['Multi'] = self.display_text("Multi Player", height / 10, WHITE, (2 * width / 3, 2 * height / 3))
        self.buttons['Settings'] = self.display_text(" Settings ", height / 10, BLACK, (width / 2, 2.5 * height / 3), WHITE)
        
class Settings(Page):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.keys['Menu'] = K_TAB
        self.easy = True
        self.sound = True
        self.music = True

    def update(self):
        super().update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.display_text("Difficulty:", height / 10, WHITE, (width / 2, height / 6))
        self.buttons['Easy'] = self.display_text(" Easy ", height / 10, WHITE if self.easy else RED, (width / 3, 2 * height / 6), RED if self.easy else BLACK)
        self.buttons['Hard'] = self.display_text(" Hard ", height / 10, WHITE if not self.easy else RED, (2 * width / 3, 2 * height / 6), RED if not self.easy else BLACK)
        self.display_text("Audio:", height / 10, WHITE, (width / 2, 3 * height / 6))
        self.buttons['Sound'] = self.display_text(" Sound ", height / 10, WHITE if self.sound else RED, (width / 3, 4 * height / 6), RED if self.sound else BLACK)
        self.buttons['Music'] = self.display_text(" Music ", height / 10, WHITE if self.music else RED, (2 * width / 3, 4 * height / 6), RED if self.music else BLACK)
        self.buttons['Menu'] = self.display_text(" Done ", height / 10, BLACK, (width / 2, 5 * height / 6), WHITE)

class Game(Page):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.clock = pygame.time.Clock()
        self.keys['Menu'] = K_ESCAPE
        self.keys['Python'] = [K_RIGHT, K_DOWN, K_LEFT, K_UP]
        self.keys['Viper'] = [K_d, K_s, K_a, K_w]

    def start(self, players, fps):
        self.fps = fps
        self.apple = Apple(CELL_COUNT_X / 2, CELL_COUNT_Y / 2)
        self.snakes = []
        self.snakes.append(Snake(random.randint(0, CELL_COUNT_X / 2), random.randint(0, CELL_COUNT_Y / 2), 10, BLUE))
        if players == 2:
            self.snakes.append(Snake(random.randint(CELL_COUNT_X / 2, CELL_COUNT_X - 1), random.randint(CELL_COUNT_Y / 2, CELL_COUNT_Y - 1), 10, GREEN))
        self.update()

    def updateSnakes(self):
        for snake in self.snakes:
            snake.updatePosition()
            if snake.hitSnake(snake):
                return False
            if snake.hitBorder():
                return False
            if snake.eatApple(self.apple):
                self.apple = Apple(random.randint(0, CELL_COUNT_X - 1 ), random.randint(0, CELL_COUNT_Y - 1))
        return True
    
    def update(self):
        super().update()
        self.display_text("Python: " + str(self.snakes[0].score), height / 9, BLUE, (width / 8, height / 10))
        if len(self.snakes) == 2:
            self.display_text("Viper: " + str(self.snakes[1].score), height / 9, GREEN, (width / 1.13, height / 10))
        for snake in self.snakes:
            snake.draw(self.surface, cell_size)
        self.apple.draw(self.surface, cell_size)
        self.clock.tick(self.fps)

class GameOver(Page):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.keys['Restart'] = K_RETURN
        self.keys['Menu'] = K_ESCAPE

    def update(self):
        super().update()
        self.display_text("Game Over!", height / 5, RED, (width / 2, height / 3))
        self.buttons['Restart'] = self.display_text("Press Enter to restart the game", height / 12, WHITE, (width / 2, 2 * height / 3))
        self.buttons['Menu'] = self.display_text("Press Esc to retrun the menu", height / 12, WHITE, (width / 2, 2 * height / 3 + height / 10))

class UserInterface:
    
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)
        self.pages = {}
        self.pages['Menu'] = Menu(width, height)
        self.pages['Settings'] = Settings(width, height)
        self.pages['Game'] = Game(width, height)
        self.pages['GameOver'] = GameOver(width, height)
        for page in self.pages:
            if not page == 'Game':
                self.pages[page].update()
        self.current_page = 'Menu'

    def fadeBetweenSurfaces(self, surface1, surface2):
        for i in range(0, 255, ANIMATION_SPEED):
            surface2.set_alpha(i)
            surface1.blit(surface2, (0,0))
            pygame.display.flip()
    
    def changePage(self, page):
        self.current_page = page
        self.fadeBetweenSurfaces(self.screen, self.pages[self.current_page].surface)

    def handle(self):
        flagPython = False
        flagViper= False
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                pressed = self.pages[self.current_page].getKeys(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                pressed = self.pages[self.current_page].getButton(event.pos)
            if not 'pressed' in locals():
                continue
            if pressed == 'Python' and not flagPython:
                self.pages['Game'].snakes[0].changeDirection(self.pages['Game'].keys['Python'].index(event.key))
                flagPython = True
            elif pressed == 'Viper' and len(self.pages['Game'].snakes) == 2 and not flagViper:
                self.pages['Game'].snakes[1].changeDirection(self.pages['Game'].keys['Viper'].index(event.key))
                flagViper = True
            elif pressed == 'Single':
                self.pages['Game'].start(1, EASY if self.pages['Settings'].easy else HARD)
                self.changePage('Game')
            elif pressed == 'Multi':
                self.pages['Game'].start(2, EASY if self.pages['Settings'].easy else HARD)
                self.changePage('Game')
            elif pressed == 'Settings':
                self.changePage('Settings')
            elif pressed == 'Easy':
                self.pages['Settings'].easy = True
            elif pressed == 'Hard':
                self.pages['Settings'].easy = False
            elif pressed == 'Sound':
                self.pages['Settings'].sound = not self.pages['Settings'].sound
            elif pressed == 'Music':
                self.pages['Settings'].music = not self.pages['Settings'].music
            elif pressed == 'Menu':
                self.changePage('Menu')
            elif pressed == 'Restart':
                self.pages['Game'].start(len(self.pages['Game'].snakes), EASY if self.pages['Settings'].easy else HARD)
                self.changePage('Game')
            elif pressed == 'Quit':
                return False
        if self.current_page == 'Game':
            if not self.pages[self.current_page].updateSnakes():
                self.changePage('GameOver')
        return True

    def update(self):
        self.pages[self.current_page].update()
        self.screen.blit(self.pages[self.current_page].surface, (0, 0))
        pygame.display.flip()

    def playSong(song):
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=-1)
    
    def playSound(file):
        sound = pygame.mixer.Sound(file)
        sound.play()
    
# Init
pygame.init()
info = pygame.display.Info()
cell_size = int(info.current_w / 150)
width = CELL_COUNT_X * cell_size
height = CELL_COUNT_Y * cell_size
pygame.display.set_caption('Python vs Viper')
icon = pygame.image.load('resources/icon.png')
pygame.display.set_icon(icon)
# playSong('resources/intro.wav')
ui = UserInterface(width, height)

# Loop
while ui.handle():
    ui.update()

# Quit
pygame.quit()
