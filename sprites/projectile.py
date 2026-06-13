import pygame
from settings import *

class Projectile:
    def __init__(self, position, velocity, faction, damage, speed=PROJECTILE_SPEED, piercing=PROJECTILE_PIERCING, size=PROJECTILE_SIZE, color=(255, 255, 0)):
        self.position = position
        self.velocity = pygame.math.Vector2(velocity)  # (vel_x, vel_y) normalisierter Vektor
        self.faction = faction
        self.speed = speed
        self.damage = damage
        self.piercing = piercing # How many enemies a projectile can pass through
        self.size = size
        self.color = color
        self.hitbox = pygame.Rect(
            self.position.x - self.size,
            self.position.y - self.size,
            self.size * 2,
            self.size * 2
        )
        self.hitbox.center = self.position

    def update(self):    
        self.position += self.velocity * self.speed
        self.hitbox.center = self.position
        buff = self.size // 2
        in_bounds = -buff < self.position.x < WINDOW_WIDTH + buff and -buff < self.position.y < WINDOW_HEIGHT + buff
        
        return in_bounds and self.piercing > 0
            
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.size)