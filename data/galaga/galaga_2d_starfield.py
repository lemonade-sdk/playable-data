# SOURCE: galaga_2d_movement.py
# REMIX: add star field background

"""
Galaga - 2D Movement with Star Field

Combines free 2D player movement with animated star field background.
Player can move in all directions through the bottom half of the screen
while traveling through space with parallax scrolling stars.
"""

import pygame
import random
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 800
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 6
FORMATION_Y = 100

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
BLUE = (0, 200, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)

# Game setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaga")
clock = pygame.time.Clock()


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.choice([0.5, 1, 1.5, 2])
        if self.speed >= 2:
            self.color = WHITE
            self.size = 2
        elif self.speed >= 1.5:
            self.color = GRAY
            self.size = 2
        elif self.speed >= 1:
            self.color = GRAY
            self.size = 1
        else:
            self.color = DARK_GRAY
            self.size = 1
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLACK)
        pygame.draw.polygon(self.image, GREEN, [(15, 0), (0, 30), (30, 30)])
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = PLAYER_SPEED
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(HEIGHT // 2, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((3, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, formation_x, formation_y, enemy_type=0):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLACK)
        
        if enemy_type == 0:
            self.color = YELLOW
            self.points = 150
            pygame.draw.rect(self.image, self.color, (5, 8, 20, 14), 2)
            pygame.draw.circle(self.image, self.color, (10, 15), 4)
            pygame.draw.circle(self.image, self.color, (20, 15), 4)
        elif enemy_type == 1:
            self.color = BLUE
            self.points = 80
            pygame.draw.polygon(self.image, self.color, [(15, 10), (5, 20), (15, 18), (25, 20)], 2)
            pygame.draw.circle(self.image, self.color, (15, 15), 5, 2)
        else:
            self.color = GREEN
            self.points = 50
            pygame.draw.circle(self.image, self.color, (15, 15), 10, 2)
            pygame.draw.line(self.image, self.color, (8, 15), (22, 15), 2)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.formation_x = formation_x
        self.formation_y = formation_y
        self.attacking = False
        self.entering = True
        self.attack_path = []
        self.entry_path = []
        self.path_index = 0
        self.shoot_timer = random.randint(120, 300)
        
        self.create_entry_path(formation_x, formation_y)
        
    def create_entry_path(self, target_x, target_y):
        start_x = target_x + random.choice([-200, 200])
        start_y = -50
        self.entry_path = []
        
        for i in range(81):
            t = i / 80
            x = start_x + (target_x - start_x) * t + math.sin(t * math.pi * 3) * 100 * (1 - t)
            y = start_y + (target_y - start_y) * t
            self.entry_path.append((x, y))
        self.entry_path[-1] = (target_x, target_y)
        self.rect.center = self.entry_path[0]
        
    def start_attack(self, player_x, offset=0):
        self.attacking = True
        self.path_index = 0
        start_x, start_y = self.rect.centerx, self.rect.centery
        self.attack_path = []
        
        for i in range(100):
            t = i / 100
            angle = t * math.pi * 2
            x = start_x + math.sin(angle * 2) * 150 + (player_x - start_x) * t + offset
            y = start_y + t * 500 + math.cos(angle * 3) * 50
            self.attack_path.append((x, y))
        
        last_x, last_y = self.attack_path[-1]
        for i in range(60):
            t = i / 60
            x = last_x + (self.formation_x - last_x) * t
            y = last_y + (self.formation_y - last_y) * t - math.sin(t * math.pi) * 100
            self.attack_path.append((x, y))
    
    def update(self, formation_offset_x, enemies):
        if self.entering:
            if self.path_index < len(self.entry_path):
                self.rect.center = self.entry_path[self.path_index]
                self.path_index += 1
            else:
                self.entering = False
                self.path_index = 0
        elif self.attacking:
            if self.path_index < len(self.attack_path):
                self.rect.center = self.attack_path[self.path_index]
                self.path_index += 1
                
                if self.path_index % 20 == 0:
                    bullet = Bullet(self.rect.centerx, self.rect.bottom, ENEMY_BULLET_SPEED)
                    enemies.add(bullet)
                    return bullet
            else:
                self.attacking = False
        else:
            target_x = self.formation_x + formation_offset_x
            self.rect.centerx = target_x
            self.rect.centery = self.formation_y
            
        return None


class Game:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.player = Player()
        self.player_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.stars = [Star() for _ in range(100)]
        
        for row in range(4):
            for col in range(8):
                x = 100 + col * 60
                y = FORMATION_Y + row * 50
                if row == 0:
                    enemy_type = 0
                elif row == 1:
                    enemy_type = 1
                else:
                    enemy_type = 2
                enemy = Enemy(x, y, x, y, enemy_type)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
        
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.formation_offset = 0
        self.formation_direction = 1
        self.attack_timer = 120
        self.shoot_cooldown = 0
        
    def spawn_wave(self):
        if len(self.enemies) == 0:
            for row in range(4):
                for col in range(8):
                    x = 100 + col * 60
                    y = FORMATION_Y + row * 50
                    if row == 0:
                        enemy_type = 0
                    elif row == 1:
                        enemy_type = 1
                    else:
                        enemy_type = 2
                    enemy = Enemy(x, y, x, y, enemy_type)
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)


def main():
    game = Game()
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_r:
                        game.reset()
                    elif event.key == pygame.K_q:
                        running = False
        
        if not game.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and game.shoot_cooldown <= 0:
                bullet = Bullet(game.player.rect.centerx, game.player.rect.top, -BULLET_SPEED)
                game.player_bullets.add(bullet)
                game.all_sprites.add(bullet)
                game.shoot_cooldown = 15
            game.shoot_cooldown -= 1
            
            for star in game.stars:
                star.update()
            
            game.player.update()
            game.player_bullets.update()
            game.enemy_bullets.update()
            
            game.formation_offset += game.formation_direction * 0.5
            if abs(game.formation_offset) > 50:
                game.formation_direction *= -1
            
            game.attack_timer -= 1
            if game.attack_timer <= 0 and len(game.enemies) > 0:
                game.attack_timer = random.randint(90, 180)
                available = [e for e in game.enemies if not e.attacking and not e.entering]
                if available:
                    group_size = min(random.randint(1, 3), len(available))
                    attackers = random.sample(available, group_size)
                    for i, attacker in enumerate(attackers):
                        attacker.start_attack(game.player.rect.centerx, i * 40 - 40)
            
            for enemy in game.enemies:
                new_bullet = enemy.update(game.formation_offset, game.all_sprites)
                if new_bullet:
                    game.enemy_bullets.add(new_bullet)
            
            for bullet in game.player_bullets:
                hit = pygame.sprite.spritecollide(bullet, game.enemies, True)
                if hit:
                    bullet.kill()
                    game.score += hit[0].points
            
            if pygame.sprite.spritecollide(game.player, game.enemy_bullets, True):
                game.lives -= 1
                if game.lives <= 0:
                    game.game_over = True
            
            if pygame.sprite.spritecollide(game.player, game.enemies, True):
                game.lives -= 1
                if game.lives <= 0:
                    game.game_over = True
            
            for enemy in list(game.enemies):
                if enemy.rect.top > HEIGHT:
                    enemy.kill()
            
            game.spawn_wave()
        
        screen.fill(BLACK)
        
        for star in game.stars:
            star.draw(screen)
        
        pygame.draw.line(screen, (50, 50, 50), (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 1)
        
        game.all_sprites.draw(screen)
        game.player_bullets.draw(screen)
        game.enemy_bullets.draw(screen)
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {game.score}", True, GREEN)
        lives_text = font.render(f"Lives: {game.lives}", True, GREEN)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        
        if game.game_over:
            font_large = pygame.font.Font(None, 72)
            game_over_text = font_large.render("GAME OVER", True, GREEN)
            restart_text = font.render("Press R to Restart or Q to Quit", True, GREEN)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()

