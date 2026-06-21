import pygame
from sprites.projectile import Projectile
from abc import ABC, abstractmethod
from settings import *
from utils import direction_to

class Entity(ABC):
    def __init__(self, health_points, max_health_points, position,  damage, armor, attack_speed, movement_speed, size, color):
        self.health_points = health_points
        self.max_health_points = max_health_points
        self.damage = damage
        self.armor = armor
        self.attack_speed = float(attack_speed)
        self.attack_cooldown_max = int(60 / attack_speed)
        self.attack_cooldown_remaining = 0 
        self.movement_speed = float(movement_speed)
        self.size = size
        self.color = color
        self.position = position
        self.hitbox = pygame.Rect(0, 0, self.size, self.size)
        self.hitbox.center = self.position
        
    
    def take_damage(self, amount):
        self.health_points -= max(0, amount - self.armor)
        return self.health_points > 0
    

    def draw_health_bar(self, screen):
        bar_width = self.hitbox.width + 10
        bar_height = 6
        bar_x = self.hitbox.centerx - bar_width // 2
        bar_y = self.hitbox.top - 10  # 10px über dem Enemy
        
        hp_percent = self.health_points / self.max_health_points

        if hp_percent > 0.8:
            color = (34, 139, 34)    # dunkelgrün
        elif hp_percent > 0.6:
            color = (154, 205, 50)   # hellgrün
        elif hp_percent > 0.4:
            color = (255, 255, 0)    # gelb
        elif hp_percent > 0.2:
            color = (255, 165, 0)    # orange
        else:
            color = (139, 0, 0)      # dunkelrot

        health_bar_background = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        health_bar_fill = pygame.Rect(bar_x, bar_y, bar_width * hp_percent, bar_height)
        
        pygame.draw.rect(screen, (0,0,0), health_bar_background)
        pygame.draw.rect(screen, color, health_bar_fill)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)
        self.draw_health_bar(screen)

    