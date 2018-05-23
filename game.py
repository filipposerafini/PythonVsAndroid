import random
import pygame
from pygame.locals import *

class AppleTypes:

    NORMAL, GOLDEN, LIFE = range(3)

class Apple:

    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.expiration = 0
        if not type == AppleTypes.NORMAL:
            self.expiration = APPLE_EXPIRATION

    def draw(self, surface, cell_size):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(APPLE_COLORS[self.type])
        surface.blit(body, (self.x * cell_size, self.y * cell_size))

class Snake:

    def __init__(self, x, y, length, lives, color):
        self.x = [x]
        self.y = [y]
        self.length = length
        self.lives = lives
        self.color = color
        self.expiration = 0
        self.temp_color = color
        self.direction = 0 if self.x[0] < CELL_COUNT_X / 2 else 2
        self.score = 0
        for i in range(1, self.length):
            self.x.append(self.x[0] - i if self.x[0] < CELL_COUNT_X / 2 else self.x[0] + i)
            self.y.append(self.y[0])

    def changeDirection(self, direction):
        if direction != (self.direction + 2) % 4:
            self.direction = direction
            return True
        return False

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

    def isCollision(self, x, y):
        if self.x[0] == x and self.y[0] == y:
            return True
        else:
            return False

    def changeColor(self, color):
        self.temp_color = color
        self.expiration = SNAKE_EXPIRATION

    def eatApple(self, apple):
        if self.isCollision(apple.x, apple.y):
            self.x.append(self.x[self.length - 1])
            self.y.append(self.y[self.length - 1])
            self.length += 1
            if apple.type == AppleTypes.NORMAL:
                self.score += 10
                SOUNDS['Apple'].play()
            elif apple.type == AppleTypes.GOLDEN:
                SOUNDS['Golden'].play()
                self.score += 50
            elif apple.type == AppleTypes.LIFE:
                SOUNDS['Life'].play()
                if self.lives < 5:
                    self.lives += 1
                else:
                    self.score += 20
            return True
        return False

    def hitSnake(self, snake):
        for i in range(1 if self is snake else 0, snake.length):
            if self.isCollision(snake.x[i], snake.y[i]) and not self.temp_color == RED:
                self.score -= 50
                self.lives -= 1
                return True
        return False

    def hitBorder(self):
        if self.x[0] < 0 or self.x[0] > CELL_COUNT_X - 1:
            self.score -= 20
            self.lives -= 1
            self.x[0] = CELL_COUNT_X - 1 if self.x[0] < 0 else 0
            return True
        elif self.y[0] < 0 or self.y[0] > CELL_COUNT_Y - 1:
            self.score -= 20
            self.lives -= 1
            self.y[0] = CELL_COUNT_Y - 1 if self.y[0] < 0 else 0
            return True
        else:
            return False

    def draw(self, surface, cell_size):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(self.temp_color)
        for i in range(0, self.length):
            surface.blit(body, (self.x[i] * cell_size, self.y[i] * cell_size))
        if self.expiration > 0:
            self.expiration -= 1
        else:
            self.temp_color = self.color

class Game:

    clock = pygame.time.Clock()

    def __init__(self, players, fps):
        self.fps = fps
        self.apple = Apple(CELL_COUNT_X / 2, CELL_COUNT_Y / 2, AppleTypes.NORMAL)
        self.snakes = []
        self.snakes.append(Snake(random.randint(0, CELL_COUNT_X / 2), random.randint(0, CELL_COUNT_Y / 2), 15, 3, BLUE))
        if players == 2:
            self.snakes.append(Snake(random.randint(CELL_COUNT_X / 2, CELL_COUNT_X - 1), random.randint(CELL_COUNT_Y / 2, CELL_COUNT_Y - 1), 15, 3, GREEN))

    def restart(self):
        return Game(len(self.snakes), self.fps)

    def updateSnakes(self):
        if self.apple.expiration == 0:
            self.apple.type = AppleTypes.NORMAL
        else:
            self.apple.expiration -= 1
        for snake in self.snakes:
            snake.updatePosition()
            if snake.hitSnake(snake) or snake.hitBorder():
                SOUNDS['Hit'].play()
                snake.changeColor(RED)
                if snake.lives == 0:
                    return False
            if snake.eatApple(self.apple):
                if not self.apple.type == AppleTypes.NORMAL:
                    snake.changeColor(APPLE_COLORS[self.apple.type])
                self.apple = Apple(random.randint(0, CELL_COUNT_X - 1 ), random.randint(0, CELL_COUNT_Y - 1), random.choices([0, 1, 2], weights=[8, 1, 1])[0])
        return True

    def drawSnakes(self, surface, cell_size):
        for snake in self.snakes:
            snake.draw(surface, cell_size)
        self.apple.draw(surface, cell_size)
        self.clock.tick(self.fps)

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
        for action, keys in self.keys.items():
            if isinstance(keys, list):
                if key in keys:
                    return action
            else:
                if key == keys:
                    return action

    def display_text(self, text, dimension, color, position, *background):
        font = pygame.font.Font('resources/font.otf', int(dimension))
        text_surface = font.render(text, True, color, background)
        rect = text_surface.get_rect()
        rect.midbottom = position
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
        self.display_text('Python', height / 4, BLUE, (2 * width / 7 + width / 32, 2 * height / 5))
        self.display_text('VS', height / 7, RED, (width / 2 + width / 40, 2 * height / 5 - height / 50))
        self.display_text('Viper', height / 4, GREEN, (5 * width / 7 - width / 32, 2 * height / 5))
        self.buttons['Single'] = self.display_text('Single Player', height / 10, WHITE, (width / 3, 4.5 * height / 7))
        self.buttons['Multi'] = self.display_text('Multi Player', height / 10, WHITE, (2 * width / 3, 4.5 * height / 7))
        self.buttons['Settings'] = self.display_text(' Settings ', height / 10, BLACK, (width / 2, 6 * height / 7), WHITE)

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
        self.display_text('Difficulty:', height / 10, WHITE, (width / 2, 2 * height / 7))
        self.buttons['Easy'] = self.display_text(' Easy ', height / 10, WHITE if self.easy else RED, (width / 3, 3 * height / 7), RED if self.easy else BLACK)
        self.buttons['Hard'] = self.display_text(' Hard ', height / 10, WHITE if not self.easy else RED, (2 * width / 3, 3 * height / 7), RED if not self.easy else BLACK)
        self.display_text('Audio:', height / 10, WHITE, (width / 2, 4 * height / 7))
        self.buttons['Sound'] = self.display_text(' Sound ', height / 10, WHITE if self.sound else RED, (width / 3, 5 * height / 7), RED if self.sound else BLACK)
        self.buttons['Music'] = self.display_text(' Music ', height / 10, WHITE if self.music else RED, (2 * width / 3, 5 * height / 7), RED if self.music else BLACK)
        self.buttons['Menu'] = self.display_text(' Done ', height / 10, BLACK, (width / 2, 6 * height / 7), WHITE)

class GameField(Page):

    def __init__(self, width, height, cell_size):
        super().__init__(width, height)
        self.cell_size = cell_size
        self.keys['Menu'] = K_ESCAPE
        self.keys['Python'] = [K_RIGHT, K_DOWN, K_LEFT, K_UP]
        self.keys['Viper'] = [K_d, K_s, K_a, K_w]
        self.game = None

    def update(self):
        super().update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        if not self.game == None:
            rect = self.display_text('Python: ' + str(self.game.snakes[0].score), height / 10, BLUE, (width / 8, height / 7))
            self.display_text('x' + str(self.game.snakes[0].lives), height / 16, BLUE, (rect.right + width / 30, height / 7 - height / 100))
            if len(self.game.snakes) == 2:
                rect = self.display_text('Viper: ' + str(self.game.snakes[1].score), height / 10, GREEN, (width / 1.13, height / 7))
                self.display_text('x' + str(self.game.snakes[1].lives), height / 16, GREEN, (rect.left - width / 40, height / 7 - height / 100))
            self.game.drawSnakes(self.surface, self.cell_size)

class GameOver(Page):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.keys['Menu'] = K_ESCAPE
        self.keys['Restart'] = K_RETURN
        self.game = None
        self.scores = None

    def update(self):
        super().update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        if not self.game == None:
            self.display_text('Game Over!', height / 4, RED, (width / 2, 2 * height / 6))
            if len(self.game.snakes) == 1:
                self.display_text('Score: ' + str(self.game.snakes[0].score), height / 8, CYAN, (width / 2, height / 2))
                self.display_text(' Leaderboard: ', height / 10, WHITE, (width / 2, 4 * height / 7 + height / 10))
                for i in range(0, 3):
                    self.display_text(str(i + 1) + '. ', height / 15, CYAN if self.scores[i] is self.game.snakes[0].score else WHITE, (3 * width / 7, 4 * height / 7 + (i + 2) * height / 11))
                    self.display_text(str(self.scores[i]), height / 15, CYAN if self.scores[i] is self.game.snakes[0].score else WHITE, (4 * width / 7, 4 * height / 7 + (i + 2) * height / 11))
            else:
                if self.game.snakes[0].score > self.game.snakes[1].score:
                    # self.display_text('Python: ' + str(self.game.snakes[0].score), height / 8, BLUE, (width / 3, 4 * height / 7))
                    self.display_text('Python Won!', height / 8, BLUE, (width / 2, 4 * height / 7))
                elif self.game.snakes[0].score < self.game.snakes[1].score:
                    # self.display_text('Viper: ' + str(self.game.snakes[1].score), height / 8, GREEN, (2 * width / 3, 4 * height / 7))
                    self.display_text('Viper Won!', height / 8, GREEN, (width / 2, 4 * height / 7))
                else:
                    self.display_text('Draw!', height / 8, YELLOW, (width / 2, 4 * height / 7))
            self.buttons['Menu'] = self.display_text('Return', height / 10, WHITE, (width / 7, 17 * height / 18))
            self.buttons['Restart'] = self.display_text('Restart', height / 10, WHITE, (6 * width / 7, 17 * height / 18))


class UserInterface:

    def __init__(self, width, height, cell_size):
        self.screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)
        self.game = None
        self.pages = {}
        self.pages['Menu'] = Menu(width, height)
        self.pages['Settings'] = Settings(width, height)
        self.pages['Game'] = GameField(width, height, cell_size)
        self.pages['GameOver'] = GameOver(width, height)
        for page in self.pages:
            self.pages[page].update()
        self.current_page = None

    def fadeBetweenSurfaces(self, surface):
        for i in range(0, 255, ANIMATION_SPEED):
            surface.set_alpha(i)
            self.screen.blit(surface, (0,0))
            pygame.display.flip()

    def changePage(self, page):
        if page == 'GameOver' and len(self.game.snakes) == 1:
            self.pages[page].scores = self.readLeaderboard('resources/highscores')
        elif self.current_page == 'GameOver' and len(self.game.snakes) == 1:
            self.writeLeaderboard('resources/highscores', self.pages[self.current_page].scores)
        self.playMusic(page)
        self.current_page = page
        self.pages[self.current_page].update()
        self.fadeBetweenSurfaces(self.pages[self.current_page].surface)

    def handle(self):
        flagPython = False
        flagViper = False
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                pressed = self.pages[self.current_page].getKeys(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                pressed = self.pages[self.current_page].getButton(event.pos)
            else:
                continue
            if pressed == 'Python' and not flagPython:
                if self.game.snakes[0].changeDirection(self.pages['Game'].keys['Python'].index(event.key)):
                    flagPython = True
            elif pressed == 'Viper' and len(self.game.snakes) == 2 and not flagViper:
                if self.game.snakes[1].changeDirection(self.pages['Game'].keys['Viper'].index(event.key)):
                    flagViper = True
            if pressed == 'Single':
                self.game = Game(1, EASY if self.pages['Settings'].easy else HARD)
                self.pages['Game'].game = self.game
                self.pages['GameOver'].game = self.game
                self.changePage('Game')
            elif pressed == 'Multi':
                self.game = Game(2, EASY if self.pages['Settings'].easy else HARD)
                self.pages['Game'].game = self.game
                self.pages['GameOver'].game = self.game
                self.changePage('Game')
            elif pressed == 'Settings':
                self.changePage('Settings')
            elif pressed == 'Easy':
                self.pages['Settings'].easy = True
            elif pressed == 'Hard':
                self.pages['Settings'].easy = False
            elif pressed == 'Sound':
                self.pages['Settings'].sound = not self.pages['Settings'].sound
                for sound in SOUNDS.values():
                    sound.set_volume(1 if self.pages['Settings'].sound else 0)
            elif pressed == 'Music':
                self.pages['Settings'].music = not self.pages['Settings'].music
                pygame.mixer.music.set_volume(1 if self.pages['Settings'].music else 0)
            elif pressed == 'Menu':
                self.changePage('Menu')
            elif pressed == 'Restart':
                self.game = self.game.restart()
                self.pages['Game'].game = self.game
                self.pages['GameOver'].game = self.game
                self.changePage('Game')
            elif pressed == 'Quit':
                return False
        if self.current_page == 'Game':
            if not self.game.updateSnakes():
                self.changePage('GameOver')
        return True

    def update(self):
        self.pages[self.current_page].update()
        self.screen.blit(self.pages[self.current_page].surface, (0, 0))
        pygame.display.flip()

    def playMusic(self, page):
        if not self.current_page == 'Settings' and page in MUSIC.keys():
            if page == 'Game':
                pygame.mixer.music.load(MUSIC[page][0 if
                    self.pages['Settings'].easy else 1])
            else:
                pygame.mixer.music.load(MUSIC[page])
            pygame.mixer.music.play(loops=-1)

    def readLeaderboard(self, file):
        scores = []
        try:
            with open('resources/.highscores', 'r') as f:
                for line in f:
                    scores.append(int(line.strip()))
            scores.append(self.game.snakes[0].score)
            scores.sort(reverse=True)
        except FileNotFoundError:
            scores = [0,0,0]
        return scores

    def writeLeaderboard(self, file, scores):
        with open('resources/.highscores', 'w') as f:
            for s in scores[:3]:
                f.write(str(s) + '\n')

# Init
pygame.init()
pygame.display.set_caption('Python vs Viper')
icon = pygame.image.load('resources/icon.png')
pygame.display.set_icon(icon)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
APPLE_COLORS = {
        AppleTypes.NORMAL : RED,
        AppleTypes.GOLDEN : YELLOW,
        AppleTypes.LIFE : MAGENTA
        }

# Music
MUSIC = {
        'Menu' : 'resources/intro.wav',
        'Game' : ['resources/easy.wav', 'resources/hard.wav'],
        'GameOver' : 'resources/game_over.wav'
        }
# Sounds
SOUNDS = {
        'Apple' : pygame.mixer.Sound('resources/apple.wav'),
        'Golden' : pygame.mixer.Sound('resources/golden.wav'),
        'Life' : pygame.mixer.Sound('resources/life.wav'),
        'Hit' : pygame.mixer.Sound('resources/hit.wav'),
        }
# Grid Size
CELL_COUNT_X = 96
CELL_COUNT_Y = 54
# FPS
EASY = 30
HARD = 60
# Utils
ANIMATION_SPEED = 5
APPLE_EXPIRATION = 120
SNAKE_EXPIRATION = 40

# Adapt size to screen
cell_size = int(pygame.display.Info().current_w / 130)
width = CELL_COUNT_X * cell_size
height = CELL_COUNT_Y * cell_size

ui = UserInterface(width, height, cell_size)
ui.changePage('Menu')

# Loop
while ui.handle():
    ui.update()

# Quit
pygame.quit()
