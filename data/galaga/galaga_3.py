# CREATE: galaga

"""
Galaga - Classic shooter game

Control a ship to destroy waves of enemies. Enemies move in formation and
periodically attack. Implements limited ammo system with regeneration.
"""

import pygame
import random
import math

pygame.init()

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 600
FRAMERATE = 60

BG_COLOR = (0, 0, 0)
MAIN_COLOR = (0, 255, 65)
ALT_COLOR_1 = (0, 180, 255)
ALT_COLOR_2 = (255, 255, 100)

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Galaga")
timer = pygame.time.Clock()


def create_entry_trajectory(target_x, target_y):
    """Generate smooth entry path for enemies"""
    path = []
    start_x = target_x + random.choice([-220, 220])
    start_y = -45
    
    for i in range(76):
        t = i / 75
        spiral = math.sin(t * math.pi * 4) * 90 * (1 - t)
        x_pos = start_x + (target_x - start_x) * t + spiral
        y_pos = start_y + (target_y - start_y) * t
        path.append((x_pos, y_pos))
    path[-1] = (target_x, target_y)
    return path


def create_attack_trajectory(start_x, start_y, target_x, home_x, home_y, offset):
    """Generate swooping attack path"""
    path = []
    
    for i in range(105):
        t = i / 105
        theta = t * math.pi * 2.2
        x_pos = start_x + math.sin(theta * 1.8) * 160 + (target_x - start_x) * t + offset
        y_pos = start_y + t * 520 + math.cos(theta) * 45
        path.append((x_pos, y_pos))
    
    end_x, end_y = path[-1]
    for i in range(55):
        t = i / 55
        x_pos = end_x + (home_x - end_x) * t
        y_pos = end_y + (home_y - end_y) * t - math.sin(t * math.pi) * 105
        path.append((x_pos, y_pos))
    
    return path


class PlayerShip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(BG_COLOR)
        # Triangular design with base
        points = [(16, 2), (4, 28), (16, 22), (28, 28)]
        pygame.draw.polygon(self.image, MAIN_COLOR, points)
        pygame.draw.line(self.image, MAIN_COLOR, (4, 28), (28, 28), 3)
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 55))
        self.move_speed = 5
        
    def advance(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.move_speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.move_speed
        self.rect.clamp_ip(window.get_rect())


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((4, 14))
        self.image.fill(MAIN_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        
    def advance(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT:
            self.kill()


class EnemyShip(pygame.sprite.Sprite):
    def __init__(self, x, y, home_x, home_y, ship_type):
        super().__init__()
        self.ship_type = ship_type
        self.image = pygame.Surface((28, 28))
        self.image.fill(BG_COLOR)
        
        if ship_type == 0:
            self.ship_color = ALT_COLOR_2
            self.value = 160
            # Commander design
            pygame.draw.rect(self.image, self.ship_color, (3, 10, 22, 12), 2)
            pygame.draw.circle(self.image, self.ship_color, (9, 14), 3)
            pygame.draw.circle(self.image, self.ship_color, (19, 14), 3)
            pygame.draw.line(self.image, self.ship_color, (3, 16), (25, 16), 2)
        elif ship_type == 1:
            self.ship_color = ALT_COLOR_1
            self.value = 85
            # Officer design
            pygame.draw.ellipse(self.image, self.ship_color, (4, 8, 20, 12), 2)
            pygame.draw.line(self.image, self.ship_color, (8, 14), (20, 14), 2)
        else:
            self.ship_color = MAIN_COLOR
            self.value = 55
            # Soldier design
            pygame.draw.circle(self.image, self.ship_color, (14, 14), 11, 2)
            pygame.draw.circle(self.image, self.ship_color, (14, 14), 5)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.home_x = home_x
        self.home_y = home_y
        self.attacking = False
        self.entering = True
        self.path = []
        self.current_step = 0
        
        self.path = create_entry_trajectory(home_x, home_y)
        self.rect.center = self.path[0]
        
    def start_attack(self, player_x, lateral_offset=0):
        self.attacking = True
        self.current_step = 0
        self.path = create_attack_trajectory(
            self.rect.centerx, self.rect.centery,
            player_x, self.home_x, self.home_y, lateral_offset
        )
    
    def advance(self, formation_x_offset):
        result_bullet = None
        
        if self.entering:
            if self.current_step < len(self.path):
                self.rect.center = self.path[self.current_step]
                self.current_step += 1
            else:
                self.entering = False
                self.current_step = 0
        elif self.attacking:
            if self.current_step < len(self.path):
                self.rect.center = self.path[self.current_step]
                self.current_step += 1
                
                if self.current_step % 22 == 0:
                    result_bullet = Bullet(self.rect.centerx, self.rect.bottom, 6)
            else:
                self.attacking = False
        else:
            self.rect.centerx = self.home_x + formation_x_offset
            self.rect.centery = self.home_y
            
        return result_bullet


class Game:
    def __init__(self):
        self.setup()
        
    def setup(self):
        self.player = PlayerShip()
        self.player_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.entities = pygame.sprite.Group(self.player)
        
        for row in range(4):
            for col in range(7):
                x_pos = 100 + col * 75
                y_pos = 70 + row * 48
                ship_type = 0 if row == 0 else (1 if row == 1 else 2)
                enemy = EnemyShip(x_pos, y_pos, x_pos, y_pos, ship_type)
                self.enemies.add(enemy)
                self.entities.add(enemy)
        
        self.score = 0
        self.lives = 3
        self.over = False
        self.x_offset = 0
        self.offset_direction = 1
        self.attack_delay = 110
        self.fire_delay = 0
        self.ammo = 5
        self.ammo_regen = 0
        
    def new_wave(self):
        if len(self.enemies) == 0:
            for row in range(4):
                for col in range(7):
                    x_pos = 100 + col * 75
                    y_pos = 70 + row * 48
                    ship_type = 0 if row == 0 else (1 if row == 1 else 2)
                    enemy = EnemyShip(x_pos, y_pos, x_pos, y_pos, ship_type)
                    self.enemies.add(enemy)
                    self.entities.add(enemy)


def main():
    game = Game()
    active = True
    
    while active:
        timer.tick(FRAMERATE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            
            if event.type == pygame.KEYDOWN:
                if game.over:
                    if event.key == pygame.K_r:
                        game.setup()
                    elif event.key == pygame.K_q:
                        active = False
        
        if not game.over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and game.fire_delay <= 0 and game.ammo > 0:
                bullet = Bullet(game.player.rect.centerx, game.player.rect.top, -10)
                game.player_bullets.add(bullet)
                game.entities.add(bullet)
                game.fire_delay = 12
                game.ammo -= 1
            
            game.fire_delay -= 1
            
            # Ammo regeneration
            game.ammo_regen += 1
            if game.ammo_regen >= 35 and game.ammo < 5:
                game.ammo += 1
                game.ammo_regen = 0
            
            game.player.advance()
            
            for bullet in game.player_bullets:
                bullet.advance()
            for bullet in game.enemy_bullets:
                bullet.advance()
            
            game.x_offset += game.offset_direction * 0.55
            if abs(game.x_offset) > 55:
                game.offset_direction *= -1
            
            game.attack_delay -= 1
            if game.attack_delay <= 0 and len(game.enemies) > 0:
                game.attack_delay = random.randint(95, 175)
                available = [e for e in game.enemies if not e.attacking and not e.entering]
                if available:
                    count = min(random.randint(1, 3), len(available))
                    attackers = random.sample(available, count)
                    for i, attacker in enumerate(attackers):
                        attacker.start_attack(game.player.rect.centerx, (i - count // 2) * 45)
            
            for enemy in game.enemies:
                new_bullet = enemy.advance(game.x_offset)
                if new_bullet:
                    game.enemy_bullets.add(new_bullet)
            
            for bullet in game.player_bullets:
                hit = pygame.sprite.spritecollide(bullet, game.enemies, True)
                if hit:
                    bullet.kill()
                    game.score += hit[0].value
            
            if pygame.sprite.spritecollide(game.player, game.enemy_bullets, True):
                game.lives -= 1
                if game.lives <= 0:
                    game.over = True
            
            if pygame.sprite.spritecollide(game.player, game.enemies, True):
                game.lives -= 1
                if game.lives <= 0:
                    game.over = True
            
            for enemy in list(game.enemies):
                if enemy.rect.top > WINDOW_HEIGHT:
                    enemy.kill()
            
            game.new_wave()
        
        window.fill(BG_COLOR)
        game.entities.draw(window)
        game.player_bullets.draw(window)
        game.enemy_bullets.draw(window)
        
        ui_font = pygame.font.Font(None, 34)
        score_display = ui_font.render(f"Score: {game.score}", True, MAIN_COLOR)
        lives_display = ui_font.render(f"Lives: {game.lives}", True, MAIN_COLOR)
        ammo_display = ui_font.render(f"Ammo: {game.ammo}/5", True, MAIN_COLOR)
        window.blit(score_display, (12, 10))
        window.blit(lives_display, (12, 45))
        window.blit(ammo_display, (WINDOW_WIDTH - 130, 10))
        
        if game.over:
            title_font = pygame.font.Font(None, 76)
            over_display = title_font.render("GAME OVER", True, MAIN_COLOR)
            info_display = ui_font.render("Press R to Restart or Q to Quit", True, MAIN_COLOR)
            window.blit(over_display, (WINDOW_WIDTH // 2 - over_display.get_width() // 2, WINDOW_HEIGHT // 2 - 55))
            window.blit(info_display, (WINDOW_WIDTH // 2 - info_display.get_width() // 2, WINDOW_HEIGHT // 2 + 25))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()

