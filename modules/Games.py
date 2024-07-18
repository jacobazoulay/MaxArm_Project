import sys
from machine import Pin
import time
import random
import _thread as thread
from LedDisplays import LEDDigitDisplay, LEDMatrixDisplay, DisplayAnimator

WIDTH = 16
HEIGHT = 8


class Snake():
    def __init__(self):
        self.head = [(WIDTH) // 2, HEIGHT // 2]
        self.tail = [[(WIDTH) // 2, HEIGHT // 2 - 1]]
        self.food_old = []
        self.food = [3, 3]
        self.alive = True
        self.completed_eating = False
        self.score = 0
        self.victory = False
        self.last_move = 'd'
        self.frame = [[0] * 8 for _ in range(16)]
        for item in [self.head, self.food] + self.tail:
            x, y = item[0], item[1]
            self.frame[x][y] = 1

    def move(self, dir):
        self.last_move = dir
        if dir == 'w':
            delta = (0, 1)
        elif dir == 's':
            delta = (0, -1)
        elif dir == 'd':
            delta = (1, 0)
        elif dir == 'a':
            delta = (-1, 0)

        self.frame[self.tail[-1][0]][self.tail[-1][1]] = 0

        self.tail.insert(0, self.head)
        self.tail.pop()

        self.head = [(self.head[0] + delta[0]) % (WIDTH), (self.head[1] + delta[1]) % (HEIGHT)]
        self.frame[self.head[0]][self.head[1]] = 1

    def checkColision(self):
        if self.head in self.tail:
            self.alive = False

    def eat(self):
        if self.head == self.food:
            self.score += 1
            self.food_old.append(self.food)
            self.food = self.generate_random_point()
            self.frame[self.food[0]][self.food[1]] = 1

    def grow(self):
        if self.completed_eating:
            self.tail.append(self.food_old[0])
            self.food_old.pop(0)
            self.completed_eating = False
        if len(self.food_old) == 0:
            return
        if self.food_old[0] == self.tail[-1]:
            self.completed_eating = True

    def generate_random_point(self):
        excluded_points = self.tail + [self.head]
        available_points = []
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if [x, y] not in excluded_points:
                    available_points.append([x, y])
        if available_points:
            return random.choice(available_points)
        else:
            self.victory = True
            self.alive = False
            return None


class SnakeGame():
    def __init__(self):
        self.led_matrix = LEDMatrixDisplay(clk=Pin(22), dio=Pin(23))
        self.led_digit = LEDDigitDisplay(clk=Pin(33), dio=Pin(32))
        self.snake = Snake()
        self.disp_animator = DisplayAnimator()
        self.keyPress = 'd'
        thread.start_new_thread(self.readKeyInput, ())

    def playGame(self, auto=False):
        try:
            count = 0
            key_count = -3
            while self.snake.alive:
                self.led_digit.tube_display(self.snake.score)
                if count % 2 == 0:
                    self.snake.frame[self.snake.food[0]][self.snake.food[1]] = 0
                    self.displayFrame()
                else:
                    self.snake.frame[self.snake.food[0]][self.snake.food[1]] = 1
                    if auto:
                        if key_count % 16 == 0 or key_count % 16 == 8:
                            self.keyPress = 'd'
                        elif key_count % 16 < 8:
                            self.keyPress = 's'
                        else:
                            self.keyPress = 'w'
                        key_count += 1
                    self.snake.move(self.keyPress)
                    self.snake.checkColision()
                    self.snake.eat()
                    self.snake.grow()
                    self.displayFrame()
                time.sleep_ms(30)
                count += 1
            self.game_over()
        except Exception as e:
            self.snake.alive = False
            time.sleep_ms(500)
            raise e

    def game_over(self):
        game = [0x5c, 0x54, 0x7c, 0x00, 0x7c, 0x14, 0x7c, 0x00, 0x7c, 0x08, 0x7c, 0x00, 0x7c, 0x54, 0x44, 0x00]
        over = [0x7c, 0x44, 0x7c, 0x00, 0x1c, 0x60, 0x1c, 0x00, 0x7c, 0x54, 0x44, 0x00, 0x7c, 0x34, 0x5c, 0x00]
        self.led_matrix.display_flash(self.displayFrame(), 2)
        self.led_matrix.display_flash(game, 1)
        self.led_matrix.display_flash(over, 1)
        self.led_matrix.update_display()
        print("Game Over")

    def readKeyInput(self):
        rev_dir_keys = {'a': 'd',
                        's': 'w',
                        'd': 'a',
                        'w': 's'}
        while self.snake.alive:
            inKey = sys.stdin.read(1)
            if inKey in ['a', 's', 'd', 'w']:
                if inKey != rev_dir_keys[self.snake.last_move]:
                    self.keyPress = inKey
            if inKey == 'q':
                self.snake.alive = False
                return

    def displayFrame(self):
        out = self.disp_animator.conv_frame(self.snake.frame)
        self.led_matrix.write(out)
        return out


class Jumper():
    def __init__(self):
        self.alive = True
        self.score = 0
        self.frame = [[0] * 8 for _ in range(16)]
        self.a = 0
        self.v = 0
        self.ground = 1
        self.pos = [4, self.ground + 2]

    def erase_body(self):
        x, y = self.pos[0], round(self.pos[1])
        self.frame[x][y] = 0
        self.frame[x][y - 1] = 0
        self.frame[x - 1][y] = 0
        self.frame[x - 1][y - 1] = 0

    def draw_body(self):
        x, y = self.pos[0], round(self.pos[1])
        self.frame[x][y] = 1
        self.frame[x][y - 1] = 1
        self.frame[x - 1][y] = 1
        self.frame[x - 1][y - 1] = 1

    def jump(self):
        self.a = -0.2
        self.v = 1.15

    def draw_ground(self):
        for x in range(WIDTH):
            self.frame[x][self.ground] = 1
            if (x + self.score) % 3 == 0:
                self.frame[x][self.ground - 1] = 1
            else:
                self.frame[x][self.ground - 1] = 0

    def update(self):
        self.erase_body()
        self.v += self.a
        self.pos[1] += self.v
        if self.pos[1] > HEIGHT - 1:
            self.pos[1] = HEIGHT - 1
        if self.pos[1] < self.ground + 2:
            self.pos[1] = self.ground + 2
            self.v = 0
            self.a = 0

        self.draw_body()
        self.draw_ground()

    def check_collision(self, obstacles):
        x, y = self.pos[0], round(self.pos[1])
        body = [[x, y], [x, y - 1], [x - 1, y], [x - 1, y - 1]]
        for obs in obstacles:
            if obs in body:
                self.alive = False
                return


class JumperGame():

    def __init__(self):
        self.led_matrix = LEDMatrixDisplay(clk=Pin(22), dio=Pin(23))
        self.led_digit = LEDDigitDisplay(clk=Pin(33), dio=Pin(32))
        self.disp_animator = DisplayAnimator()
        self.jumper = Jumper()
        self.obstacles = []
        self.new_obs_timer = 0
        self.dark_mode = False
        thread.start_new_thread(self.readKeyInput, ())

    def playGame(self):
        try:
            while self.jumper.alive:
                if self.jumper.score % 300 == 0 and self.jumper.score != 0:
                    self.flip_dark_mode()
                self.led_digit.tube_display(self.jumper.score)
                self.update_obstacles()
                self.jumper.update()
                self.displayFrame()
                time.sleep_ms(30)
                self.jumper.score += 1
                self.new_obs_timer += 1
                self.jumper.check_collision(self.obstacles)
            self.game_over()

        except Exception as e:
            self.jumper.alive = False
            time.sleep_ms(500)
            raise e
        
    def flip_dark_mode(self):
        for i in range(7):
            self.dark_mode = not self.dark_mode
            self.displayFrame()
            time.sleep_ms(150)

    def game_over(self):
        game = [0x5c, 0x54, 0x7c, 0x00, 0x7c, 0x14, 0x7c, 0x00, 0x7c, 0x08, 0x7c, 0x00, 0x7c, 0x54, 0x44, 0x00]
        over = [0x7c, 0x44, 0x7c, 0x00, 0x1c, 0x60, 0x1c, 0x00, 0x7c, 0x54, 0x44, 0x00, 0x7c, 0x34, 0x5c, 0x00]
        self.led_matrix.display_flash(self.displayFrame(), 2)
        self.led_matrix.display_flash(game, 1)
        self.led_matrix.display_flash(over, 1)
        self.led_matrix.update_display()
        print("Game Over")

    def readKeyInput(self):
        while self.jumper.alive:
            inKey = sys.stdin.read(1)
            if inKey == ' ':
                self.jumper.jump()
            if inKey == 'q':
                self.jumper.alive = False
                return

    def update_obstacles(self):
        # Move existing obstacles to the left
        for obs in self.obstacles:
            self.jumper.frame[obs[0]][obs[1]] = 0
            obs[0] -= 1

        # Remove obstacles that are out of the screen
        self.obstacles = [obs for obs in self.obstacles if obs[0] >= 0]

        # Add a new obstacle occasionally
        if self.new_obs_timer > (40 - self.jumper.score / 20) and random.randint(0, 5) == 0:
            new_obstacle_pos = [15, random.randint(self.jumper.ground + 1, 7)]  # New obstacle at the far right
            self.obstacles.append(new_obstacle_pos)
            self.new_obs_timer = 0

        # Draw obstacles on the frame
        for obs in self.obstacles:
            self.jumper.frame[obs[0]][obs[1]] = 1

    def displayFrame(self):
        out = self.disp_animator.conv_frame(self.jumper.frame)
        if self.dark_mode:
            out = [~row for row in out]
        self.led_matrix.write(out)
        return out
