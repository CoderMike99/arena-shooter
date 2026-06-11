import pygame
import random
from sprites.entity import Entity
from sprites.projectile import Projectile
from abc import ABC, abstractmethod
from settings import *
from utils import direction_to

class Enemy(Entity):
    def __init__(self, health_points, max_health_points, armor, speed, size, color):
        super().__init__(health_points=health_points,
                         max_health_points=max_health_points,
                         armor=armor,
                         speed=speed,
                         size=size,
                         color=color)

    @staticmethod
    def get_random_spawn_position(size=0) -> pygame.math.Vector2:
        side = random.choice(["left", "right", "top", "bottom"])

        match side:
            case "left":
                return pygame.math.Vector2(-40, random.randint(0, WINDOW_HEIGHT))
            case "right":
                return pygame.math.Vector2(WINDOW_WIDTH + size // 2, random.randint(0, WINDOW_HEIGHT))
            case "top":
                return pygame.math.Vector2(random.randint(0, WINDOW_WIDTH), -40)
            case "bottom":
                return pygame.math.Vector2(random.randint(0, WINDOW_WIDTH), WINDOW_HEIGHT + size // 2)
            case default:
                return pygame.math.Vector2(0,0)
        


class Chaser(Enemy):
    def __init__(self):
        super().__init__(health_points=CHASER_HEALTH_POINTS,
                         max_health_points=CHASER_MAX_HEALTH_POINTS,
                         armor=CHASER_ARMOR,
                         speed=CHASER_SPEED,
                         size=CHASER_SIZE,
                         color=CHASER_COLOR)
        
        self.pos = self.get_random_spawn_position(CHASER_SIZE)
        self.hitbox = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.hitbox.center = self.pos

    def update(self, player_pos):
        direction = direction_to(self.pos, player_pos)
        if direction:
            self.pos += direction * float(self.speed)
            self.hitbox.center = self.pos

        return self.health_points > 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)
        self.draw_health_bar(screen)


class Shooter(Enemy):
    def __init__(self, shoot_interval = SHOOTER_SHOOT_INTERVAL):
        super().__init__(health_points=SHOOTER_HEALTH_POINTS,
                         max_health_points=SHOOTER_MAX_HEALTH_POINTS,
                         armor=SHOOTER_ARMOR,
                         speed=SHOOTER_SPEED,
                         size=SHOOTER_SIZE,
                         color=SHOOTER_COLOR)
        
        self.shoot_timer = 0
        self.shooter_interval = shoot_interval # how many frames between each shot
        self.new_projectiles = []   # newly generated projectiles
        self.in_position = False # if shooter in position and ready to shoot
        self.pos = self.get_random_spawn_position(SHOOTER_SIZE)
        self.hitbox = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.hitbox.center = self.pos

    def update(self, player_pos):
        direction = direction_to(self.pos, player_pos)
        horizontal_border_buff = 30
        vertical_border_buff = 30
        self.new_projectiles = []   # Jeden Frame leeren
        
        # Checking if shooter in position (on border)
        if not self.in_position:
            if self.pos.x < horizontal_border_buff or \
            self.pos.x > WINDOW_WIDTH - horizontal_border_buff or \
            self.pos.y < vertical_border_buff or \
            self.pos.y > WINDOW_HEIGHT - vertical_border_buff:
            # Move on if not in position
                if direction:
                    self.pos += direction * float(self.speed)
                    self.hitbox.center = self.pos
            # Set "in_position" to true if in position
            else:
                self.in_position = True
        # Shoot if in position
        else:
            self.shoot_timer += 1
            if self.shoot_timer >= self.shooter_interval:
                self.new_projectiles.append(Projectile(self.pos.x,
                                                       self.pos.y,
                                                       velocity=direction,
                                                       faction="enemy",
                                                       damage=SHOOTER_DAMAGE,
                                                       color=SHOOTER_COLOR))
                self.shoot_timer = 0
            

        return self.health_points > 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)
        self.draw_health_bar(screen)

    def shoot(self, player_pos):
        pass