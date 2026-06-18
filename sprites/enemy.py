import pygame
import random
from sprites.entity import Entity
from sprites.projectile import Projectile
from abc import ABC, abstractmethod
from settings import *
from utils import direction_to

class Enemy(Entity):
    def __init__(self, damage, health_points, max_health_points, position, armor, attack_speed, movement_speed, size, color):
        super().__init__(damage=damage,
                         health_points=health_points,
                         max_health_points=max_health_points,
                         position=position,
                         armor=armor,
                         attack_speed=attack_speed,
                         movement_speed=movement_speed,
                         size=size,
                         color=color)

    @staticmethod
    def get_random_spawn_position(size=0) -> pygame.math.Vector2:
        side = random.choice(["left", "right", "top", "bottom"])

        match side:
            case "left":
                return pygame.math.Vector2(-40, random.randint(0, PLAY_AREA_HEIGHT))
            case "right":
                return pygame.math.Vector2(WINDOW_WIDTH + size // 2, random.randint(0, PLAY_AREA_HEIGHT))
            case "top":
                return pygame.math.Vector2(random.randint(0, WINDOW_WIDTH), -40)
            case "bottom":
                return pygame.math.Vector2(random.randint(0, WINDOW_WIDTH), PLAY_AREA_HEIGHT + size // 2)
            case default:
                return pygame.math.Vector2(0,0)
        
    @abstractmethod
    def update(self, player_pos: pygame.math.Vector2):
        pass

class Chaser(Enemy):
    def __init__(self):
        super().__init__(damage=CHASER_DAMAGE,
                         health_points=CHASER_HEALTH_POINTS,
                         max_health_points=CHASER_MAX_HEALTH_POINTS,
                         position = Enemy.get_random_spawn_position(CHASER_SIZE),
                         armor=CHASER_ARMOR,
                         attack_speed=CHASER_ATTACK_SPEED,
                         movement_speed=CHASER_MOVEMENT_SPEED,
                         size=CHASER_SIZE,
                         color=CHASER_COLOR)

    def update(self, player_pos):
        direction = direction_to(self.position, player_pos)
        if direction:
            self.position += direction * float(self.movement_speed)
            self.hitbox.center = self.position

        if self.attack_cooldown_remaining > 0:
            self.attack_cooldown_remaining -= 1

        return self.health_points > 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)
        self.draw_health_bar(screen)


class Shooter(Enemy):
    def __init__(self, shoot_interval = SHOOTER_SHOOT_INTERVAL):
        super().__init__(damage=SHOOTER_DAMAGE,
                         health_points=SHOOTER_HEALTH_POINTS,
                         max_health_points=SHOOTER_MAX_HEALTH_POINTS,
                         position=Enemy.get_random_spawn_position(SHOOTER_SIZE),
                         armor=SHOOTER_ARMOR,
                         attack_speed=SHOOTER_ATTACK_SPEED,
                         movement_speed=SHOOTER_MOVEMENT_SPEED,
                         size=SHOOTER_SIZE,
                         color=SHOOTER_COLOR)
        
        self.new_projectiles = []   # newly generated projectiles
        self.in_position = False # if shooter in position and ready to shoot

    def update(self, player_pos):
        direction = direction_to(self.position, player_pos)
        horizontal_border_buff = 30
        vertical_border_buff = 30
        
        
        # Checking if shooter in position (on border)
        if not self.in_position:
            if self.position.x < horizontal_border_buff or \
            self.position.x > WINDOW_WIDTH - horizontal_border_buff or \
            self.position.y < vertical_border_buff or \
            self.position.y > PLAY_AREA_HEIGHT - vertical_border_buff:
            # Move on if not in position
                if direction:
                    self.position += direction * float(self.movement_speed)
                    self.hitbox.center = self.position
            # Set "in_position" to true if in position
            else:
                self.in_position = True
        # Shoot if in position
        else:
            self.shoot(direction)
            

        return self.health_points > 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)
        self.draw_health_bar(screen)

    def shoot(self, direction):
        self.new_projectiles = []   # Jeden Frame leeren      
        if self.attack_cooldown_remaining > 0:
            self.attack_cooldown_remaining -= 1
        else:
            self.new_projectiles.append(Projectile(position=pygame.math.Vector2(self.position),
                                                   velocity=direction,
                                                   faction="enemy",
                                                   damage=self.damage,
                                                   color=SHOOTER_COLOR))
            self.attack_cooldown_remaining = self.attack_cooldown_max

class Seeker(Enemy):
    def __init__(self,
                 max_turn_angle=SEEKER_MAX_TURN_ANGLE,
                 min_movement_speed = SEEKER_MIN_MOVEMENT_SPEED):
        super().__init__(damage=SEEKER_DAMAGE,
                         health_points=SEEKER_HEALTH_POINTS,
                         max_health_points=SEEKER_MAX_HEALTH_POINTS,
                         position=Enemy.get_random_spawn_position(SEEKER_SIZE),
                         armor=SEEKER_ARMOR,
                         attack_speed=SEEKER_ATTACK_SPEED,
                         movement_speed=SEEKER_MOVEMENT_SPEED,
                         size=SEEKER_SIZE,
                         color=SEEKER_COLOR)
        
        self.velocity = pygame.math.Vector2(self.movement_speed, 0).rotate(random.uniform(0, 360))
        self.max_turn_angle = max_turn_angle
        self.current_speed = min_movement_speed

    def update(self, player_pos):
        target_direction = direction_to(self.position, player_pos)
        angle_to_target = self.velocity.angle_to(target_direction)
        angle = max(-self.max_turn_angle, min(self.max_turn_angle, angle_to_target))


        # in update():
        # Zielgeschwindigkeit basierend auf Kurve
        target_speed = self.movement_speed * (1 - (abs(angle) / self.max_turn_angle) * 0.5)

        # Geschwindigkeit nur langsam anpassen
        max_accel = 0.1  # z.B. 0.1 px/frame²
        if self.current_speed < target_speed:
            self.current_speed = min(target_speed, self.current_speed + max_accel)
        else:
            self.current_speed = max(target_speed, self.current_speed - max_accel)

        self.velocity = self.velocity.rotate(angle).normalize() * self.current_speed
        
        self.position += self.velocity

        self.hitbox.center = self.position

        return self.health_points > 0
    

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)
        self.draw_health_bar(screen)