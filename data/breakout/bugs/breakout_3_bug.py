# CREATE: breakout
# ERROR: Traceback (most recent call last):
# ERROR:   File "C:\work\lsdk\playable-data\data\breakout\bugs\breakout_3_bug.py", line 252, in <module>
# ERROR:     game.run()
# ERROR:   File "C:\work\lsdk\playable-data\data\breakout\bugs\breakout_3_bug.py", line 243, in run
# ERROR:     self.draw_screen()
# ERROR:   File "C:\work\lsdk\playable-data\data\breakout\bugs\breakout_3_bug.py", line 213, in draw_screen
# ERROR:     "Score: " + self.current_score, True, WHITE
# ERROR:     ~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~
# ERROR: TypeError: can only concatenate str (not "int") to str

"""
Breakout - A paddle and ball brick breaking game.
Control the paddle with arrow keys to bounce the ball and destroy all the bricks.
Win by clearing all bricks, lose if the ball goes off the bottom of the screen.
Simple physics-based gameplay with collision detection and scoring.
"""

import pygame
import random
import sys

pygame.init()

# Screen configuration
SCREEN_W = 700
SCREEN_H = 500

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)


class Paddle:
    SIZE_W = 110
    SIZE_H = 14
    MOVE_SPEED = 8

    def __init__(self):
        self.x = SCREEN_W // 2 - self.SIZE_W // 2
        self.y = SCREEN_H - 45

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT] and self.x > 0:
            self.x -= self.MOVE_SPEED
        if keys_pressed[pygame.K_RIGHT] and self.x < SCREEN_W - self.SIZE_W:
            self.x += self.MOVE_SPEED

    def render(self, surface):
        pygame.draw.rect(surface, GREEN, (self.x, self.y, self.SIZE_W, self.SIZE_H))

    def bounds(self):
        return pygame.Rect(self.x, self.y, self.SIZE_W, self.SIZE_H)


class Ball:
    SIZE = 14
    BASE_SPEED = 5

    def __init__(self):
        self.reset_position()

    def reset_position(self):
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2
        angle = random.choice([-1, 1])
        self.dx = angle * self.BASE_SPEED
        self.dy = self.BASE_SPEED

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # Check wall collisions
        if self.x <= 0 or self.x >= SCREEN_W - self.SIZE:
            self.dx = -self.dx
        if self.y <= 0:
            self.dy = -self.dy

    def render(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.SIZE // 2)

    def bounds(self):
        return pygame.Rect(
            self.x - self.SIZE // 2, self.y - self.SIZE // 2, self.SIZE, self.SIZE
        )

    def check_fell(self):
        return self.y > SCREEN_H


class Brick:
    WIDTH = 70
    HEIGHT = 28

    def __init__(self, x_pos, y_pos, brick_color):
        self.x = x_pos
        self.y = y_pos
        self.color = brick_color
        self.is_destroyed = False

    def render(self, surface):
        if not self.is_destroyed:
            pygame.draw.rect(
                surface, self.color, (self.x, self.y, self.WIDTH, self.HEIGHT)
            )
            pygame.draw.rect(
                surface, BLACK, (self.x, self.y, self.WIDTH, self.HEIGHT), 2
            )

    def bounds(self):
        return pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)

    def destroy(self):
        self.is_destroyed = True


class BreakoutGame:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Breakout")
        self.game_clock = pygame.time.Clock()
        self.text_font = pygame.font.Font(None, 34)
        self.start_new_game()

    def start_new_game(self):
        self.player_paddle = Paddle()
        self.game_ball = Ball()
        self.brick_list = []
        self.current_score = 0
        self.is_game_over = False
        self.player_won = False
        self.build_bricks()

    def build_bricks(self):
        num_rows = 6
        num_cols = 9
        gap = 4
        brick_colors = [RED, RED, YELLOW, CYAN, BLUE, BLUE]

        total_w = num_cols * Brick.WIDTH + (num_cols - 1) * gap
        offset_x = (SCREEN_W - total_w) // 2
        offset_y = 50

        for r in range(num_rows):
            for c in range(num_cols):
                brick_x = offset_x + c * (Brick.WIDTH + gap)
                brick_y = offset_y + r * (Brick.HEIGHT + gap)
                brick_color = brick_colors[r]
                new_brick = Brick(brick_x, brick_y, brick_color)
                self.brick_list.append(new_brick)

    def handle_events(self):
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return False
            elif evt.type == pygame.KEYDOWN:
                if self.is_game_over:
                    if evt.key == pygame.K_r:
                        self.start_new_game()
                    elif evt.key == pygame.K_q:
                        return False
        return True

    def process_collision(self, obj1_rect, obj2_rect):
        return obj1_rect.colliderect(obj2_rect)

    def update_state(self):
        if not self.is_game_over:
            keys = pygame.key.get_pressed()
            self.player_paddle.update(keys)
            self.game_ball.move()

            # Check paddle collision
            if self.process_collision(
                self.game_ball.bounds(), self.player_paddle.bounds()
            ):
                if self.game_ball.dy > 0:
                    self.game_ball.dy = -self.game_ball.dy
                    # Calculate bounce angle
                    paddle_center = self.player_paddle.x + self.player_paddle.SIZE_W / 2
                    ball_offset = (self.game_ball.x - paddle_center) / (
                        self.player_paddle.SIZE_W / 2
                    )
                    self.game_ball.dx = self.game_ball.BASE_SPEED * ball_offset * 1.5

            # Check brick collisions
            for brick in self.brick_list:
                if not brick.is_destroyed:
                    if self.process_collision(self.game_ball.bounds(), brick.bounds()):
                        brick.destroy()
                        self.game_ball.dy = -self.game_ball.dy
                        self.current_score = self.current_score + 12
                        break

            # Check win condition
            all_destroyed = all(brick.is_destroyed for brick in self.brick_list)
            if all_destroyed:
                self.is_game_over = True
                self.player_won = True

            # Check lose condition
            if self.game_ball.check_fell():
                self.is_game_over = True

    def draw_screen(self):
        self.display.fill(BLACK)

        # Render game objects
        self.player_paddle.render(self.display)
        self.game_ball.render(self.display)
        for brick in self.brick_list:
            brick.render(self.display)

        # Render score
        score_display = self.text_font.render(
            "Score: " + self.current_score, True, WHITE
        )
        self.display.blit(score_display, (12, 12))

        # Render end game message
        if self.is_game_over:
            if self.player_won:
                end_message = self.text_font.render("You Win!", True, GREEN)
            else:
                end_message = self.text_font.render("Game Over!", True, RED)

            restart_message = self.text_font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            end_rect = end_message.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 25))
            restart_rect = restart_message.get_rect(
                center=(SCREEN_W // 2, SCREEN_H // 2 + 25)
            )

            self.display.blit(end_message, end_rect)
            self.display.blit(restart_message, restart_rect)

        pygame.display.flip()

    def run(self):
        active = True
        while active:
            active = self.handle_events()
            self.update_state()
            self.draw_screen()
            self.game_clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = BreakoutGame()
    game.run()
