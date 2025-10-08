# CREATE: galaga
# ERROR: Traceback (most recent call last):
# ERROR:   File "C:\work\lsdk\playable-data\data\galaga\bugs\galaga_4_bug.py", line 345, in <module>
# ERROR:     execute_game()
# ERROR:   File "C:\work\lsdk\playable-data\data\galaga\bugs\galaga_4_bug.py", line 325, in execute_game
# ERROR:     lives_label = text_font.render(f"Lives: {lives_remaining}", True, COLOR_SHIP)
# ERROR:                                                ^^^^^^^^^^^^^^^^
# ERROR: NameError: name 'lives_remaining' is not defined

"""
Galaga - Space combat game

Player ship vs alien formations. Aliens enter in animated sequences, form up,
then launch coordinated attacks. Uses OOP design with sprite groups for collision.
"""

import pygame
import random
import math

# Game constants
FPS_TARGET = 60
SCREEN_W = 600
SCREEN_H = 750

# Color palette
COLOR_BACKGROUND = (0, 0, 0)
COLOR_SHIP = (0, 255, 65)
COLOR_ENEMY_A = (255, 200, 50)
COLOR_ENEMY_B = (100, 180, 255)
COLOR_ENEMY_C = (0, 255, 65)

pygame.init()
display_surface = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Galaga")
frame_clock = pygame.time.Clock()


class PlayerVessel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((36, 36))
        self.image.fill(COLOR_BACKGROUND)
        # Pentagon style ship
        points = [(18, 0), (36, 12), (30, 36), (6, 36), (0, 12)]
        pygame.draw.polygon(self.image, COLOR_SHIP, points, 0)
        pygame.draw.polygon(self.image, COLOR_BACKGROUND, points, 2)
        pygame.draw.circle(self.image, COLOR_SHIP, (18, 18), 6)
        self.rect = self.image.get_rect(center=(SCREEN_W // 2, SCREEN_H - 60))
        self.movement_speed = 4
        
    def update_position(self):
        key_state = pygame.key.get_pressed()
        if key_state[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.movement_speed
        if key_state[pygame.K_RIGHT] and self.rect.right < SCREEN_W:
            self.rect.x += self.movement_speed


class LaserBolt(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, velocity_y):
        super().__init__()
        self.image = pygame.Surface((2, 16))
        self.image.fill(COLOR_SHIP)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.velocity_y = velocity_y
        
    def update_position(self):
        self.rect.y += self.velocity_y
        if self.rect.bottom < -10 or self.rect.top > SCREEN_H + 10:
            self.kill()


class HostileShip(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, formation_x, formation_y, class_type):
        super().__init__()
        self.class_type = class_type
        self.image = pygame.Surface((30, 30))
        self.image.fill(COLOR_BACKGROUND)
        
        if class_type == 0:
            self.color = COLOR_ENEMY_A
            self.point_value = 140
            # Boss design - oval with eyes
            pygame.draw.ellipse(self.image, self.color, (2, 10, 26, 12), 2)
            pygame.draw.circle(self.image, self.color, (10, 15), 4)
            pygame.draw.circle(self.image, self.color, (20, 15), 4)
            pygame.draw.line(self.image, self.color, (2, 16), (28, 16), 2)
        elif class_type == 1:
            self.color = COLOR_ENEMY_B
            self.point_value = 70
            # Mid-tier - angular design
            points = [(15, 6), (6, 15), (15, 24), (24, 15)]
            pygame.draw.polygon(self.image, self.color, points, 2)
            pygame.draw.circle(self.image, self.color, (15, 15), 4)
        else:
            self.color = COLOR_ENEMY_C
            self.point_value = 40
            # Basic - simple circle
            pygame.draw.circle(self.image, self.color, (15, 15), 12, 2)
            pygame.draw.line(self.image, self.color, (6, 15), (24, 15), 2)
            pygame.draw.line(self.image, self.color, (15, 6), (15, 24), 2)
            
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.formation_x = formation_x
        self.formation_y = formation_y
        self.state_attacking = False
        self.state_entering = True
        self.movement_path = []
        self.path_position = 0
        
        self.generate_entry_sequence(formation_x, formation_y)
        
    def generate_entry_sequence(self, target_x, target_y):
        spawn_side = random.choice([-1, 1])
        spawn_x = target_x + spawn_side * 200
        spawn_y = -35
        
        self.movement_path = []
        num_steps = 85
        
        for step in range(num_steps + 1):
            progress = step / num_steps
            wave_amplitude = 70 * (1 - progress)
            wave_frequency = 3.5
            
            x = spawn_x + (target_x - spawn_x) * progress
            x += math.sin(progress * math.pi * wave_frequency) * wave_amplitude
            y = spawn_y + (target_y - spawn_y) * progress
            
            self.movement_path.append((x, y))
        
        self.movement_path[-1] = (target_x, target_y)
        self.rect.center = self.movement_path[0]
        
    def generate_attack_sequence(self, player_x, offset_x=0):
        self.state_attacking = True
        self.path_position = 0
        
        origin_x = self.rect.centerx
        origin_y = self.rect.centery
        self.movement_path = []
        
        dive_steps = 100
        for step in range(dive_steps):
            progress = step / dive_steps
            angle_param = progress * math.pi * 2.8
            
            x = origin_x + math.sin(angle_param * 1.5) * 145
            x += (player_x - origin_x) * progress + offset_x
            y = origin_y + progress * 500 + math.cos(angle_param) * 55
            
            self.movement_path.append((x, y))
        
        return_x, return_y = self.movement_path[-1]
        return_steps = 68
        
        for step in range(return_steps):
            progress = step / return_steps
            arc_height = math.sin(progress * math.pi) * 110
            
            x = return_x + (self.formation_x - return_x) * progress
            y = return_y + (self.formation_y - return_y) * progress - arc_height
            
            self.movement_path.append((x, y))
    
    def update_position(self, offset_formation):
        projectile_result = None
        
        if self.state_entering:
            if self.path_position < len(self.movement_path):
                self.rect.center = self.movement_path[self.path_position]
                self.path_position += 1
            else:
                self.state_entering = False
                self.path_position = 0
                
        elif self.state_attacking:
            if self.path_position < len(self.movement_path):
                self.rect.center = self.movement_path[self.path_position]
                self.path_position += 1
                
                if self.path_position % 24 == 0:
                    projectile_result = LaserBolt(self.rect.centerx, self.rect.bottom, 5)
            else:
                self.state_attacking = False
                
        else:
            self.rect.centerx = self.formation_x + offset_formation
            self.rect.centery = self.formation_y
            
        return projectile_result


class GameSession:
    def __init__(self):
        self.initialize_game()
        
    def initialize_game(self):
        self.vessel = PlayerVessel()
        self.player_projectiles = pygame.sprite.Group()
        self.hostile_ships = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.all_game_sprites = pygame.sprite.Group(self.vessel)
        
        self.setup_enemy_formation()
        
        self.current_score = 0
        self.lives_remaining = 3
        self.game_over_state = False
        self.formation_sway = 0
        self.sway_velocity = 0.45
        self.next_attack_timer = 130
        self.weapon_cooldown = 0
        
    def setup_enemy_formation(self):
        rows = 4
        cols = 8
        
        for row_index in range(rows):
            for col_index in range(cols):
                x_position = 90 + col_index * 65
                y_position = 95 + row_index * 52
                
                if row_index == 0:
                    enemy_class = 0
                elif row_index <= 1:
                    enemy_class = 1
                else:
                    enemy_class = 2
                    
                enemy = HostileShip(x_position, y_position, x_position, y_position, enemy_class)
                self.hostile_ships.add(enemy)
                self.all_game_sprites.add(enemy)
        
    def spawn_new_wave(self):
        if len(self.hostile_ships) == 0:
            self.setup_enemy_formation()


def execute_game():
    session = GameSession()
    is_running = True
    
    while is_running:
        frame_clock.tick(FPS_TARGET)
        
        for game_event in pygame.event.get():
            if game_event.type == pygame.QUIT:
                is_running = False
            
            if game_event.type == pygame.KEYDOWN:
                if session.game_over_state:
                    if game_event.key == pygame.K_r:
                        session.initialize_game()
                    elif game_event.key == pygame.K_q:
                        is_running = False
        
        if not session.game_over_state:
            key_state = pygame.key.get_pressed()
            if key_state[pygame.K_SPACE] and session.weapon_cooldown <= 0:
                bolt = LaserBolt(session.vessel.rect.centerx, session.vessel.rect.top, -9)
                session.player_projectiles.add(bolt)
                session.all_game_sprites.add(bolt)
                session.weapon_cooldown = 13
            
            session.weapon_cooldown -= 1
            
            session.vessel.update_position()
            
            for proj in session.player_projectiles:
                proj.update_position()
            for proj in session.enemy_projectiles:
                proj.update_position()
            
            session.formation_sway += session.sway_velocity
            if abs(session.formation_sway) > 48:
                session.sway_velocity *= -1
            
            session.next_attack_timer -= 1
            if session.next_attack_timer <= 0 and len(session.hostile_ships) > 0:
                session.next_attack_timer = random.randint(85, 165)
                
                ready_enemies = [e for e in session.hostile_ships 
                               if not e.state_attacking and not e.state_entering]
                
                if ready_enemies:
                    attack_group_size = min(random.randint(1, 3), len(ready_enemies))
                    attackers = random.sample(ready_enemies, attack_group_size)
                    
                    for attacker_index, attacker in enumerate(attackers):
                        lateral_offset = (attacker_index - attack_group_size // 2) * 50
                        attacker.generate_attack_sequence(session.vessel.rect.centerx, lateral_offset)
            
            for enemy in session.hostile_ships:
                new_projectile = enemy.update_position(session.formation_sway)
                if new_projectile:
                    session.enemy_projectiles.add(new_projectile)
            
            for projectile in session.player_projectiles:
                destroyed_enemies = pygame.sprite.spritecollide(projectile, session.hostile_ships, True)
                if destroyed_enemies:
                    projectile.kill()
                    session.current_score += destroyed_enemies[0].point_value
            
            if pygame.sprite.spritecollide(session.vessel, session.enemy_projectiles, True):
                session.lives_remaining -= 1
                if session.lives_remaining <= 0:
                    session.game_over_state = True
            
            if pygame.sprite.spritecollide(session.vessel, session.hostile_ships, True):
                session.lives_remaining -= 1
                if session.lives_remaining <= 0:
                    session.game_over_state = True
            
            for enemy in list(session.hostile_ships):
                if enemy.rect.top > SCREEN_H:
                    enemy.kill()
            
            session.spawn_new_wave()
        
        display_surface.fill(COLOR_BACKGROUND)
        session.all_game_sprites.draw(display_surface)
        session.player_projectiles.draw(display_surface)
        session.enemy_projectiles.draw(display_surface)
        
        text_font = pygame.font.Font(None, 36)
        score_label = text_font.render(f"Score: {session.current_score}", True, COLOR_SHIP)
        lives_label = text_font.render(f"Lives: {lives_remaining}", True, COLOR_SHIP)
        display_surface.blit(score_label, (14, 14))
        display_surface.blit(lives_label, (14, 52))
        
        if session.game_over_state:
            large_text_font = pygame.font.Font(None, 74)
            game_over_label = large_text_font.render("GAME OVER", True, COLOR_SHIP)
            instruction_label = text_font.render("Press R to Restart or Q to Quit", True, COLOR_SHIP)
            
            game_over_x = SCREEN_W // 2 - game_over_label.get_width() // 2
            game_over_y = SCREEN_H // 2 - 58
            instruction_x = SCREEN_W // 2 - instruction_label.get_width() // 2
            instruction_y = SCREEN_H // 2 + 28
            
            display_surface.blit(game_over_label, (game_over_x, game_over_y))
            display_surface.blit(instruction_label, (instruction_x, instruction_y))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    execute_game()

