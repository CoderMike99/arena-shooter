import pygame
import random
from sprites.entity import Entity
from sprites.projectile import Projectile
from abc import ABC, abstractmethod
from settings import *
from utils import direction_to

class Enemy(Entity):
    def __init__(self, damage, health_points, max_health_points, position, armor, speed, size, color):
        super().__init__(damage=damage,
                         health_points=health_points,
                         max_health_points=max_health_points,
                         position=position,
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
                         speed=CHASER_SPEED,
                         size=CHASER_SIZE,
                         color=CHASER_COLOR)

    def update(self, player_pos):
        direction = direction_to(self.position, player_pos)
        if direction:
            self.position += direction * float(self.speed)
            self.hitbox.center = self.position

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
                         speed=SHOOTER_SPEED,
                         size=SHOOTER_SIZE,
                         color=SHOOTER_COLOR)
        
        self.shoot_timer = 0
        self.shooter_interval = shoot_interval # how many frames between each shot
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
            self.position.y > WINDOW_HEIGHT - vertical_border_buff:
            # Move on if not in position
                if direction:
                    self.position += direction * float(self.speed)
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
        self.shoot_timer += 1
        if self.shoot_timer >= self.shooter_interval:
            self.new_projectiles.append(Projectile(position=pygame.math.Vector2(self.position),
                                                   velocity=direction,
                                                   faction="enemy",
                                                   damage=self.damage,
                                                   color=SHOOTER_COLOR))
            self.shoot_timer = 0