import pygame_sdl2
pygame_sdl2.import_as_pygame()

import random
import pygame
from pygame.locals import *
import android
import android.mixer as mixer

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

    def addPiece(self, count):
        for i in range(0, count):
            self.x.append(self.x[self.length - 1])
            self.y.append(self.y[self.length - 1])
            self.length += 1

    def eatApple(self, apple):
        if self.isCollision(apple.x, apple.y):
            if apple.type == AppleTypes.NORMAL:
                SOUNDS['Apple'].play()
                self.addPiece(1)
                self.score += 10
            elif apple.type == AppleTypes.GOLDEN:
                SOUNDS['Golden'].play()
                self.addPiece(3)
                self.score += 50
            elif apple.type == AppleTypes.LIFE:
                SOUNDS['Life'].play()
                self.addPiece(1)
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
            self.x[0] = CELL_COUNT_X - 1 if self.x[0] < 0 else 0
            if not self.temp_color == RED:
                self.score -= 20
                self.lives -= 1
                return True
            return False
        elif self.y[0] < 0 or self.y[0] > CELL_COUNT_Y - 1:
            self.y[0] = CELL_COUNT_Y - 1 if self.y[0] < 0 else 0
            if not self.temp_color == RED:
                self.score -= 20
                self.lives -= 1
                return True
            return False
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

    def __init__(self, players, fps, controls):
        self.fps = fps
        self.controls = controls
        self.apple = Apple(CELL_COUNT_X / 2, CELL_COUNT_Y / 2, AppleTypes.NORMAL)
        self.snakes = []
        self.snakes.append(Snake(random.randint(0, CELL_COUNT_X / 2), random.randint(0, CELL_COUNT_Y / 2), 15, 3, BLUE))
        if players == 2:
            self.snakes.append(Snake(random.randint(CELL_COUNT_X / 2, CELL_COUNT_X - 1), random.randint(CELL_COUNT_Y / 2, CELL_COUNT_Y - 1), 15, 3, GREEN))

    def restart(self):
        return Game(len(self.snakes), self.fps, self.controls)

    def updateSnakes(self):
        if self.apple.expiration == 0:
            self.apple.type = AppleTypes.NORMAL
        else:
            self.apple.expiration -= 1
        for snake in self.snakes:
            snake.updatePosition()
            if snake.hitSnake(snake) or snake.hitBorder():
                SOUNDS['Hit'].play()
                android.vibrate(0.2)
                snake.changeColor(RED)
                if snake.lives == 0:
                    return False
            if snake.eatApple(self.apple):
                if not self.apple.type == AppleTypes.NORMAL:
                    snake.changeColor(APPLE_COLORS[self.apple.type])
                self.apple = Apple(random.randint(0, CELL_COUNT_X - 1 ), random.randint(0, CELL_COUNT_Y - 1), random.choice([0, 0, 0, 0, 0, 0, 0, 0, 1, 2]))
        return True

    def drawSnakes(self, surface, cell_size):
        for snake in self.snakes:
            snake.draw(surface, cell_size)
        self.apple.draw(surface, cell_size)
        self.clock.tick(self.fps)

class Page(object):

    def __init__(self, width, height):
        self.surface = pygame.Surface((width, height))
        self.buttons = {}

    def update(self):
        self.surface.fill(BLACK)

    def getButton(self, x, y):
        for button, rect in self.buttons.items():
            if rect.collidepoint(x * self.surface.get_width(), y * self.surface.get_height()):
                return button

    def display_text(self, text, dimension, color, position, background=None):
        font = pygame.font.Font('resources/font.otf', int(dimension))
        text_surface = font.render(text, True, color, background)
        rect = text_surface.get_rect()
        rect.midbottom = position
        self.surface.blit(text_surface, rect)
        return rect

class Menu(Page):

    def __init__(self, width, height):
        super(Menu, self).__init__(width, height)

    def update(self):
        super(Menu, self).update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.display_text('Python', height / 4, BLUE, (2 * width / 7 + width / 64, 2 * height / 5))
        self.display_text('VS', height / 7, RED, (width / 2, 2 * height / 5 - height / 50))
        self.display_text('Android', height / 4, GREEN, (5 * width / 7, 2 * height / 5))
        self.buttons['Single'] = self.display_text('Single Player', height / 10, WHITE, (width / 3, 4.5 * height / 7))
        self.buttons['Multi'] = self.display_text('Multi Player', height / 10, WHITE, (2 * width / 3, 4.5 * height / 7))
        self.buttons['Settings'] = self.display_text(' Settings ', height / 10, BLACK, (width / 3, 6 * height / 7), WHITE)
        self.buttons['Leaderboard'] = self.display_text(' Leaderboard ', height / 10, BLACK, (2 * width / 3, 6 * height / 7), WHITE)

class Leaderboard(Page):

    def __init__(self, width, height):
        super(Leaderboard, self).__init__(width, height)
        self.scores = {
                DIFFICULTY['Easy']: [],
                DIFFICULTY['Normal']: [],
                DIFFICULTY['Hard']: []
                }

    def update(self):
        self.display_text('Leaderboard:', height / 6, YELLOW, (width / 2, 2 * height / 7))
        difficulty = ['Easy', 'Normal', 'Hard']
        for i in range (1, 4):
            self.display_text(str(i) + '.', height / 10, BLUE, (width / 12, height / 2 + (i + 1) * height / 10))
        for j in range(0, len(self.scores.keys())):
            key = list(self.scores.keys())[j]
            self.display_text(difficulty[j], height / 8, RED, ((j + 1) * width / 4, height / 2))
            score = self.scores[key]
            for i in range(0, min(len(score), 3)):
                self.display_text(str(score[i]), height / 10, WHITE, ((j + 1) * width / 4, height / 2 + (i + 2) * height / 10))

class Settings(Page):

    def __init__(self, width, height):
        super(Settings, self).__init__(width, height)
        self.difficulty = 1
        self.controls = 0
        self.sound = True
        self.music = True
        self.loadSettings()

    def update(self):
        super(Settings, self).update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.display_text('Difficulty:', height / 7, WHITE, (width / 3, 2 * height / 6))
        key = list(DIFFICULTY.keys())[self.difficulty]
        self.buttons['Difficulty'] = self.display_text(key, height / 7, RED, (7 * width / 10, 2 * height / 6))
        self.display_text('Controls:', height / 7, WHITE, (width / 3 - width / 70, 7 * height / 12))
        self.buttons['Controls'] = self.display_text(CONTROLS[self.controls], height / 7, RED, (7 * width / 10, 7 * height / 12))
        self.display_text('Audio:', height / 7, WHITE, (width / 3 - width / 20, 5 * height / 6))
        self.buttons['Music'] = self.display_text(' Music ', height / 9, WHITE if self.music else RED, (4 * width / 5, 5 * height / 6 - height / 50), RED if self.music else BLACK)
        self.buttons['Sound'] = self.display_text(' Sound ', height / 9, WHITE if self.sound else RED, (3 * width / 5, 5 * height / 6 - height / 50), RED if self.sound else BLACK)

    def loadSettings(self):
        try:
            with open('resources/.settings', 'r') as f:
                for line in f:
                    settings = line.split(':')
                    if settings[0] == 'Difficulty':
                        self.difficulty = int(settings[1][:-1])
                    elif settings[0] == 'Controls':
                        self.controls = int(settings[1][:-1])
                    elif settings[0] == 'Music':
                        self.music = settings[1][:-1] == 'True'
                    elif settings[0] == 'Sound':
                        self.sound = settings[1][:-1] == 'True'
        except:
            pass

    def saveSettings(self):
        with open('resources/.settings', 'w') as f:
            f.write('Difficulty:' + str(self.difficulty) + '\n')
            f.write('Controls:' + str(self.controls) + '\n')
            f.write('Music:' + str(self.music) + '\n')
            f.write('Sound:' + str(self.sound) + '\n')

class GameField(Page):

    def __init__(self, width, height, cell_size):
        super(GameField, self).__init__(width, height)
        self.cell_size = cell_size
        self.game = None

    def update(self):
        super(GameField, self).update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        if not self.game == None:
            rect = self.display_text('Python: ' + str(self.game.snakes[0].score), height / 10, BLUE, (width / 8, height / 7))
            self.display_text('x' + str(self.game.snakes[0].lives), height / 16, BLUE, (rect.right + width / 30, height / 7 - height / 100))
            # if len(self.game.snakes) == 2:
                # rect = self.display_text('Viper: ' + str(self.game.snakes[1].score), height / 10, GREEN, (width / 1.13, height / 7))
                # self.display_text('x' + str(self.game.snakes[1].lives), height / 16, GREEN, (rect.left - width / 40, height / 7 - height / 100))
            self.game.drawSnakes(self.surface, self.cell_size)
            if self.game.controls == CONTROLS.index('Touch'):
                self.buttons['Move'] = Rect(0, 0, width, height)
                self.buttons['Up'] = Rect(0, 0, 0, 0)
                self.buttons['Down'] = Rect(0, 0, 0, 0)
                self.buttons['Left'] = Rect(0, 0, 0, 0)
                self.buttons['Right'] = Rect(0, 0, 0, 0)
            if self.game.controls == CONTROLS.index('Buttons'):
                self.buttons['Move'] = Rect(0, 0, 0, 0)
                pointlist = [
                        (width / 5 - height / 14, 5 * height / 7 - height / 28),
                        (width / 5, 4 * height / 7 - height / 28),
                        (width / 5 + height / 14, 5 * height / 7 - height / 28)
                        ]
                self.buttons['Up'] = pygame.draw.polygon(self.surface, GREY, pointlist)
                pointlist = [
                        (width / 5 - height / 14, 5 * height / 7 + height / 28),
                        (width / 5, 6 * height / 7 + height / 28),
                        (width / 5 + height / 14, 5 * height / 7 + height / 28)
                        ]
                self.buttons['Down'] = pygame.draw.polygon(self.surface, GREY, pointlist)
                pointlist = [
                        (4 * width / 5 - height / 28, 5 * height / 7 + height / 14),
                        (4 * width / 5 - height / 28 - height / 7, 5 * height / 7),
                        (4 * width / 5 - height / 28, 5 * height / 7 - height / 14)
                        ]
                self.buttons['Left'] = pygame.draw.polygon(self.surface, GREY, pointlist)
                pointlist = [
                        (4 * width / 5 + height / 28, 5 * height / 7 + height / 14),
                        (4 * width / 5 + height / 28 + height / 7, 5 * height / 7),
                        (4 * width / 5 + height / 28, 5 * height / 7 - height / 14)
                        ]
                self.buttons['Right'] = pygame.draw.polygon(self.surface, GREY, pointlist)
            if self.game.controls == CONTROLS.index('Inverted'):
                self.buttons['Move'] = Rect(0, 0, 0, 0)
                pointlist = [
                        (4 * width / 5 - height / 14, 5 * height / 7 - height / 28),
                        (4 * width / 5, 4 * height / 7 - height / 28),
                        (4 * width / 5 + height / 14, 5 * height / 7 - height / 28)
                        ]
                self.buttons['Up'] = pygame.draw.polygon(self.surface, GREY, pointlist)
                pointlist = [
                        (4 * width / 5 - height / 14, 5 * height / 7 + height / 28),
                        (4 * width / 5, 6 * height / 7 + height / 28),
                        (4 * width / 5 + height / 14, 5 * height / 7 + height / 28)
                        ]
                self.buttons['Down'] = pygame.draw.polygon(self.surface, GREY, pointlist)
                pointlist = [
                        (width / 5 - height / 28, 5 * height / 7 + height / 14),
                        (width / 5 - height / 28 - height / 7, 5 * height / 7),
                        (width / 5 - height / 28, 5 * height / 7 - height / 14)
                        ]
                self.buttons['Left'] = pygame.draw.polygon(self.surface, GREY, pointlist)
                pointlist = [
                        (width / 5 + height / 28, 5 * height / 7 + height / 14),
                        (width / 5 + height / 28 + height / 7, 5 * height / 7),
                        (width / 5 + height / 28, 5 * height / 7 - height / 14)
                        ]
                self.buttons['Right'] = pygame.draw.polygon(self.surface, GREY, pointlist)

class Pause(Page):

    def __init__(self, width, height):
        super(Pause, self).__init__(width, height)
        self.game_surface = pygame.Surface((width, height))

    def update(self):
        super(Pause, self).update()
        self.surface.fill(WHITE)
        self.game_surface.set_alpha(220)
        self.surface.blit(self.game_surface, (0, 0))
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.display_text('Paused', height / 4, YELLOW, (width / 2, height / 2))
        self.buttons['Unpause'] = self.display_text('Resume', height / 8, GREEN, (width / 2, 3 * height / 4))

class NotImplementedPage(Page):

    def __init__(self, width, height):
        super(NotImplementedPage, self).__init__(width, height)

    def update(self):
        super(NotImplementedPage, self).update()
        self.display_text('Feature not yet implemented', height / 8, RED, (width / 2, height / 2))
        self.buttons['Menu'] = self.display_text('Go back', height / 8, WHITE, (width / 2, 2 * height / 3))

class GameOver(Page):

    def __init__(self, width, height):
        super(GameOver, self).__init__(width, height)
        self.game = None
        self.scores = None

    def update(self):
        super(GameOver, self).update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        if not self.game == None:
            self.display_text('Game Over!', height / 4, RED, (width / 2, 2 * height / 6))
            if len(self.game.snakes) == 1:
                self.display_text('Score: ' + str(self.game.snakes[0].score), height / 8, GREEN, (width / 2, height / 2))
                self.display_text('Leaderboard:', height / 10, WHITE, (width / 2, 4 * height / 7 + height / 10))
                self.scores.append(self.game.snakes[0].score)
                self.scores = list(set(self.scores))
                self.scores.sort(reverse=True)
                for i in range(0, min(len(self.scores), 3)):
                    pass
                    self.display_text(str(i + 1) + '. ', height / 15, GREEN if self.scores[i] == self.game.snakes[0].score else WHITE, (3 * width / 7, 4 * height / 7 + (i + 2) * height / 11))
                    self.display_text(str(self.scores[i]), height / 15, GREEN if self.scores[i] == self.game.snakes[0].score else WHITE, (4 * width / 7, 4 * height / 7 + (i + 2) * height / 11))
            else:
                pass
                # total = []
                # self.display_text('Score:', height / 15, BLUE, (width / 6, 3 * height / 7))
                # self.display_text(str(self.game.snakes[0].score), height / 15, BLUE, (2 * width / 6, 3 * height / 7))
                # self.display_text('Lives:', height / 15, BLUE, (width / 6, 4 * height / 7))
                # self.display_text(str(self.game.snakes[0].lives * 20), height / 15, BLUE, (2 * width / 6, 4 * height / 7))
                # pygame.draw.line(self.surface, WHITE, (width / 8, 4 * height / 7 + height / 30), (3 * width / 8, 4 * height / 7 + height / 30), 8)
                # total.append(self.game.snakes[0].score + self.game.snakes[0].lives * 20)
                # self.display_text('Total:', height / 15, BLUE, (width / 6, 5 * height / 7))
                # self.display_text(str(total[0]), height / 15, BLUE, (2 * width / 6, 5 * height / 7))
                # self.display_text('Score:', height / 15, GREEN, (4 * width / 6, 3 * height / 7))
                # self.display_text(str(self.game.snakes[1].score), height / 15, GREEN, (5 * width / 6, 3 * height / 7))
                # self.display_text('Lives:', height / 15, GREEN, (4 * width / 6, 4 * height / 7))
                # self.display_text(str(self.game.snakes[1].lives * 20), height / 15, GREEN, (5 * width / 6, 4 * height / 7))
                # pygame.draw.line(self.surface, WHITE, (5 * width / 8, 4 * height / 7 + height / 30), (7 * width / 8, 4 * height / 7 + height / 30), 8)
                # total.append(self.game.snakes[1].score + self.game.snakes[1].lives * 20)
                # self.display_text('Total:', height / 15, GREEN, (4 * width / 6, 5 * height / 7))
                # self.display_text(str(total[1]), height / 15, GREEN, (5 * width / 6, 5 * height / 7))
                # if total[0] > total[1]:
                    # self.display_text('Python Won!', height / 8, BLUE, (width / 2, 17 * height / 18))
                # elif total[0] < total[1]:
                    # self.display_text('Viper Won!', height / 8, GREEN, (width / 2, 17 * height / 18))
                # else:
                    # self.display_text('Draw!', height / 8, YELLOW, (width / 2, 17 * height / 18))
            self.buttons['Menu'] = self.display_text('Return', height / 10, WHITE, (width / 7, 17 * height / 18))
            self.buttons['Restart'] = self.display_text('Restart', height / 10, WHITE, (6 * width / 7, 17 * height / 18))


class UserInterface:

    def __init__(self, width, height, cell_size):
        self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.game = None
        self.pages = {}
        self.pages['Menu'] = Menu(width, height)
        self.pages['NotImplemented'] = NotImplementedPage(width, height)
        self.pages['Settings'] = Settings(width, height)
        self.pages['Leaderboard'] = Leaderboard(width, height)
        self.pages['Leaderboard'].scores[DIFFICULTY['Easy']] = self.readLeaderboard(DIFFICULTY['Easy'])
        self.pages['Leaderboard'].scores[DIFFICULTY['Normal']] = self.readLeaderboard(DIFFICULTY['Normal'])
        self.pages['Leaderboard'].scores[DIFFICULTY['Hard']] = self.readLeaderboard(DIFFICULTY['Hard'])
        self.pages['Game'] = GameField(width, height, cell_size)
        self.pages['Pause'] = Pause(width, height)
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
            self.pages[page].scores = self.readLeaderboard(self.game.fps)
        elif self.current_page == 'GameOver' and len(self.game.snakes) == 1:
            self.saveLeaderboard(self.pages[self.current_page].scores, self.game.fps)
            self.pages['Leaderboard'].scores[self.game.fps] = self.readLeaderboard(self.game.fps)
        self.playMusic(page)
        self.current_page = page
        self.pages[self.current_page].update()
        self.fadeBetweenSurfaces(self.pages[self.current_page].surface)

    def handle(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == APP_TERMINATING:
                return False
            elif event.type == APP_WILLENTERBACKGROUND:
                return False
            elif event.type == KEYDOWN:
                if event.key == pygame_sdl2.K_AC_BACK:
                    if self.current_page == 'Game':
                        pressed = 'Pause'
                    elif self.current_page == 'Menu':
                        return False
                    else:
                        pressed = 'Menu'
            elif event.type == FINGERDOWN:
                pressed = self.pages[self.current_page].getButton(event.x, event.y)
            else:
                continue
            if pressed == 'Single':
                self.game = Game(1, list(DIFFICULTY.values())[self.pages['Settings'].difficulty], self.pages['Settings'].controls)
                self.pages['Game'].game = self.game
                self.pages['GameOver'].game = self.game
                self.changePage('Game')
            elif pressed == 'Multi':
                # self.game = Game(2, EASY if self.pages['Settings'].easy else HARD)
                # self.pages['Game'].game = self.game
                # self.pages['GameOver'].game = self.game
                # self.changePage('Game')
                self.changePage('NotImplemented')
            # elif pressed == 'Left':
                # direction = (self.game.snakes[0].direction - 1) % 4
                # self.game.snakes[0].changeDirection(direction)
            # elif pressed == 'Right':
                # direction = (self.game.snakes[0].direction + 1) % 4
                # self.game.snakes[0].changeDirection(direction)
            elif pressed == 'Move':
                x = event.x * CELL_COUNT_X
                y = event.y * CELL_COUNT_Y
                if self.game.snakes[0].direction % 2 == 0:
                    if y > self.game.snakes[0].y[0]:
                        self.game.snakes[0].changeDirection(1)
                    else:
                        self.game.snakes[0].changeDirection(3)
                else:
                    if x > self.game.snakes[0].x[0]:
                        self.game.snakes[0].changeDirection(0)
                    else:
                        self.game.snakes[0].changeDirection(2)
                break
            elif pressed == 'Up':
                self.game.snakes[0].changeDirection(3)
                break
            elif pressed == 'Down':
                self.game.snakes[0].changeDirection(1)
                break
            elif pressed == 'Left':
                self.game.snakes[0].changeDirection(2)
                break
            elif pressed == 'Right':
                self.game.snakes[0].changeDirection(0)
                break
            elif pressed == 'Settings':
                self.changePage('Settings')
            elif pressed == 'Leaderboard':
                self.changePage('Leaderboard')
            elif pressed == 'Difficulty':
                self.pages['Settings'].difficulty = (self.pages['Settings'].difficulty + 1) % 3
            elif pressed == 'Controls':
                self.pages['Settings'].controls = (self.pages['Settings'].controls + 1) % 3
            elif pressed == 'Sound':
                self.pages['Settings'].sound = not self.pages['Settings'].sound
                for sound in SOUNDS.values():
                    sound.set_volume(1 if self.pages['Settings'].sound else 0)
            elif pressed == 'Music':
                self.pages['Settings'].music = not self.pages['Settings'].music
                mixer.music.set_volume(1 if self.pages['Settings'].music else 0)
            elif pressed == 'Menu':
                    self.changePage('Menu')
            elif pressed == 'Pause':
                self.pages['Pause'].game_surface = self.pages['Game'].surface
                self.changePage('Pause')
            elif pressed == 'Unpause':
                self.changePage('Game')
            elif pressed == 'Yes':
                self.changePage('Menu')
            elif pressed == 'No':
                self.changePage('Game')
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
        if not self.current_page == 'Settings' and not self.current_page == 'NotImplemented' and not self.current_page == 'Leaderboard':
            if page == 'Game':
                if self.current_page == 'Pause':
                    mixer.music.unpause()
                else:
                    mixer.music.load(MUSIC[self.game.fps])
                    mixer.music.play(loops=-1)
            elif page == 'Pause':
                mixer.music.pause()
            elif not page == 'Settings' and not page == 'NotImplemented' and not page == 'Leaderboard':
                mixer.music.load(MUSIC[page])
                mixer.music.play(loops=-1)

    def readLeaderboard(self, difficulty):
        scores = []
        try:
            if difficulty == DIFFICULTY['Easy']:
                file = 'resources/.easy'
            elif difficulty == DIFFICULTY['Normal']:
                file = 'resources/.normal'
            elif difficulty == DIFFICULTY['Hard']:
                file = 'resources/.hard'
            with open(file, 'r') as f:
                for line in f:
                    scores.append(int(line.strip()))
        except:
            scores = []
        return scores

    def saveLeaderboard(self, scores, difficulty):
        if difficulty == DIFFICULTY['Easy']:
            file = 'resources/.easy'
        elif difficulty == DIFFICULTY['Normal']:
            file = 'resources/.normal'
        elif difficulty == DIFFICULTY['Hard']:
            file = 'resources/.hard'
        with open(file, 'w') as f:
            for s in scores[:3]:
                f.write(str(s) + '\n')

# Init
pygame.init()
pygame.display.set_caption('Python vs Android')

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (255, 255, 255, 60)
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
# FPS
DIFFICULTY = {
        'Easy' : 25,
        'Normal' : 40,
        'Hard': 80
        }
# Controls
CONTROLS = ['Touch', 'Buttons', 'Inverted']
# Music
MUSIC = {
        'Menu' : 'resources/intro.wav',
        DIFFICULTY['Easy'] : 'resources/easy.wav',
        DIFFICULTY['Normal'] : 'resources/hard.wav',
        DIFFICULTY['Hard'] : 'resources/hard.wav',
        'Pause' : None,
        'Confirm' : None,
        'GameOver' : 'resources/game_over.wav'
        }
# Sounds
SOUNDS = {
        'Apple' : mixer.Sound('resources/apple.wav'),
        'Golden' : mixer.Sound('resources/golden.wav'),
        'Life' : mixer.Sound('resources/life.wav'),
        'Hit' : mixer.Sound('resources/hit.wav'),
        }
# Utils
ANIMATION_SPEED = 20
APPLE_EXPIRATION = 120
SNAKE_EXPIRATION = 40

# Adapt size to screen
width = pygame.display.Info().current_w
height = pygame.display.Info().current_h
CELL_COUNT_Y = 36
cell_size = int(height / CELL_COUNT_Y)
CELL_COUNT_X = int(width / cell_size)

ui = UserInterface(width, height, cell_size)
ui.changePage('Menu')

# Loop
while ui.handle():
    ui.update()
    # if android.check_pause():
        # android.wait_for_resume()
else:
    ui.pages['Settings'].saveSettings()

# Quit
pygame.quit()
