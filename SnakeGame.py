import pygame
import random

title = 'Snake game by Juani y Lucas'

WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 600

SNAKE_BLOCK = 20
INITIAL_SPEED = 10
FOODS_PER_LEVEL = 8
DEFAULT_LIVES = 3

SNAKE_CANVAS_XI = 0
SNAKE_CANVAS_XF = DISPLAY_WIDTH
SNAKE_CANVAS_YI = 2 * SNAKE_BLOCK
SNAKE_CANVAS_YF = DISPLAY_HEIGHT


class SnakeGame:
    food_collection = [
        {
            "is_power_up": False,
            "image": "assets/cherry.png"
        },
        {
            "is_power_up": True,
            "image": "assets/carrot.png"
        },
        {
            "is_power_up": False,
            "image": "assets/orange.png"
        },
        {
            "is_power_up": False,
            "image": "assets/strawberry.png"
        },
        {
            "is_power_up": False,
            "image": "assets/watermelon.png"
        }
    ]

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Snake game by Juani y Lucas')
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.font_style = pygame.font.SysFont("comicsansms", 35)
        self.score_font = pygame.font.SysFont("comicsansms", 35)
        self.game_over = False
        self.game_close = False
        self.power_up_on = False
        self.level = 1
        self.remaining_lives = DEFAULT_LIVES
        self.x1_change = 0
        self.y1_change = 0
        self.x1 = 0
        self.y1 = 0
        self.snake_head = None
        self.snake_list = []
        self.length_of_snake = 1
        self.food_x = None
        self.food_y = None
        self.curr_food_power_up = False
        self.image_path = None
        self.eaten_food = 0
        self.game_score = 0
        self.food_catch_sound = pygame.mixer.Sound("assets/sound/food_catch.wav")

    def play_level(self):
        self.reset_positions()
        _quit_game = True

        while not self.game_over:
            # event parsing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.x1_change == 0:
                        self.x1_change = -SNAKE_BLOCK
                        self.y1_change = 0
                    elif event.key == pygame.K_RIGHT and self.x1_change == 0:
                        self.x1_change = SNAKE_BLOCK
                        self.y1_change = 0
                    elif event.key == pygame.K_UP and self.y1_change == 0:
                        self.y1_change = -SNAKE_BLOCK
                        self.x1_change = 0
                    elif event.key == pygame.K_DOWN and self.y1_change == 0:
                        self.y1_change = SNAKE_BLOCK
                        self.x1_change = 0

            # Calculate snake new position
            self.calculate_new_snake_position()

            # check if loose a life
            if self.hit_a_wall() or self.touched_itself():
                self.remaining_lives -= 1
                if self.remaining_lives <= 0:
                    _quit_game = self.show_game_over_and_ask_to_quit()
                    self.game_over = True
                else:
                    self.show_life_lost_confirmation()
                    self.reset_positions()

            # check caught food
            if self.caught_food():
                pygame.mixer.Sound.play(self.food_catch_sound)
                self.handle_caught_food()
                self.spawn_food()

            if self.eaten_food == FOODS_PER_LEVEL:
                self.snow_message_confirmation(f"Level {self.level} completed! press C to continue ...", pygame.K_c)
                self.level += 1
                self.game_score += 10
                self.eaten_food = 0
                self.reset_positions()

            # Display Updates
            self.update_window()

            # Clock
            self.clock.tick(INITIAL_SPEED + 5 * self.level)

        return _quit_game

    def show_game_over_and_ask_to_quit(self):
        while True:
            self.message(f"Game Over. Press C to play again or Q to quit", BLACK)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return True
                    if event.key == pygame.K_c:
                        return False

    def show_life_lost_confirmation(self):
        if self.remaining_lives == 1:
            msg = f"Ouch! Last life, better be careful ... press C key to continue"
        else:
            msg = "Ouch! press C key to continue"

        self.snow_message_confirmation(msg, pygame.K_c, YELLOW)

    def update_window(self):
        self.display.fill(BLUE)
        self.show_top_bar()
        self.draw_snake()
        self.draw_food()
        pygame.display.update()

    def play(self):
        _quit_game = self.play_level()
        pygame.quit()
        return _quit_game

    def caught_food(self):
        return self.x1 == self.food_x and self.y1 == self.food_y

    def handle_caught_food(self):
        self.length_of_snake += random.randint(1, 8)
        self.eaten_food += 1
        self.game_score += 1
        if not self.power_up_on:
            self.power_up_on = self.curr_food_power_up

    def spawn_food(self):
        # random pick from food collection
        food_index = random.randint(0, len(self.food_collection) - 1)
        self.curr_food_power_up = self.food_collection[food_index]["is_power_up"]
        self.image_path = self.food_collection[food_index]["image"]
        self.food_x = random.choice(range(SNAKE_CANVAS_XI, SNAKE_CANVAS_XF - SNAKE_BLOCK, SNAKE_BLOCK))
        self.food_y = random.choice(range(SNAKE_CANVAS_YI, SNAKE_CANVAS_YF - SNAKE_BLOCK, SNAKE_BLOCK))

    def hit_a_wall(self):
        return self.x1 >= SNAKE_CANVAS_XF or \
               self.x1 < SNAKE_CANVAS_XI or \
               self.y1 >= SNAKE_CANVAS_YF or \
               self.y1 < SNAKE_CANVAS_YI

    def touched_itself(self):
        # check if snake touched itself
        for x in self.snake_list[:-2]:
            if x == self.snake_head:
                return True
        return False

    def calculate_new_snake_position(self):
        self.x1 += self.x1_change
        self.y1 += self.y1_change
        if self.hit_a_wall() and self.power_up_on:
            # power up implemented, we move snake into the "mirror" position on the opposite wall.
            if self.x1 >= SNAKE_CANVAS_XF:
                self.x1 -= SNAKE_CANVAS_XF - SNAKE_CANVAS_XI
            if self.x1 < SNAKE_CANVAS_XI:
                self.x1 += SNAKE_CANVAS_XF - SNAKE_CANVAS_XI
            if self.y1 < SNAKE_CANVAS_YI:
                self.y1 += SNAKE_CANVAS_YF - SNAKE_CANVAS_YI
            if self.y1 >= SNAKE_CANVAS_YF:
                self.y1 -= SNAKE_CANVAS_YF - SNAKE_CANVAS_YI

        self.snake_head = [self.x1, self.y1]
        self.snake_list.append(self.snake_head)

        if len(self.snake_list) > self.length_of_snake:
            del self.snake_list[0]

    def show_top_bar(self):
        value = self.score_font.render("Level: {} Score: {} Fruits: {}".format(self.level,
                                                                               self.game_score,
                                                                               self.eaten_food),
                                       True,
                                       YELLOW)
        lives_text = self.score_font.render(str(self.remaining_lives), True, WHITE)

        self.display.blit(value, [0, 0])
        self.display.blit(lives_text, (DISPLAY_WIDTH - 70, 8))
        self.display.blit(pygame.image.load("assets/heart.png").convert_alpha(), (DISPLAY_WIDTH - 48, 0))

        pygame.draw.line(self.display, BLACK,
                         (SNAKE_CANVAS_XI, SNAKE_CANVAS_YI),
                         (SNAKE_CANVAS_XF, SNAKE_CANVAS_YI),
                         width=3)

        if self.power_up_on:
            self.display.blit(pygame.image.load("assets/star.png").convert_alpha(), (DISPLAY_WIDTH / 2 - 20, 0))

    def draw_snake(self):
        for x in self.snake_list:
            pygame.draw.rect(self.display, BLACK, [x[0], x[1], SNAKE_BLOCK, SNAKE_BLOCK])

    def draw_food(self):
        self.display.blit(pygame.image.load(self.image_path).convert_alpha(), (self.food_x, self.food_y))

    def reset_positions(self):
        self.x1 = DISPLAY_WIDTH / 2
        self.y1 = DISPLAY_HEIGHT / 2
        self.x1_change = 0
        self.y1_change = 0
        self.snake_head = [self.x1, self.y1]
        self.snake_list = []
        self.length_of_snake = 1
        self.spawn_food()
        self.power_up_on = False

    def message(self, message, color):
        msg = self.font_style.render(message, True, color)
        self.display.blit(msg, [DISPLAY_WIDTH / 4, DISPLAY_HEIGHT / 3])
        pygame.display.update()

    def snow_message_confirmation(self, message, key, color=BLACK):
        while True:
            self.message(message, color)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == key:
                        return


quit_game = False
while not quit_game:
    snake_game = SnakeGame()
    quit_game = snake_game.play()

pygame.quit()
