import pygame
from settings import *

class Projectile:
    def __init__(self, x_position, y_position, velocity, faction, damage, speed=PROJECTILE_SPEED, piercing=PROJECTILE_PIERCING, size=PROJECTILE_SIZE, color=(255, 255, 0)):
        self.pos = pygame.math.Vector2(x_position, y_position)
        self.velocity = pygame.math.Vector2(velocity)  # (vel_x, vel_y) normalisierter Vektor
        self.faction = faction
        self.speed = speed
        self.damage = damage
        self.piercing = piercing # How many enemies a projectile can pass through
        self.size = size
        self.color = color
        self.hitbox = pygame.Rect(
            self.pos.x - self.size,
            self.pos.y - self.size,
            self.size * 2,
            self.size * 2
        )
        self.hitbox.center = self.pos

    def update(self):    
        self.pos += self.velocity * self.speed
        self.hitbox.center = self.pos
        buff = self.size // 2
        in_bounds = -buff < self.pos.x < WINDOW_WIDTH + buff and -buff < self.pos.y < WINDOW_HEIGHT + buff
        
        return in_bounds and self.piercing > 0
            
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.size)