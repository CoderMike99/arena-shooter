import pygame
from random import randint
from ui.ui import draw_text



class DamageNumber:
    def __init__(self, font, position, number, color=(255,255,255), lifetime=60, isCrit=False):
        self.font = font
        self.position = pygame.Vector2(position)
        self.lifetime = lifetime
        self.lifetime_remaining = lifetime
        self.alpha = 255
        self.isCrit = isCrit
        self.text = str(number) + "!" if self.isCrit else str(number) 
        self.color = (255,0,0) if self.isCrit else color

    def update(self):
        self.position -= pygame.math.Vector2(0, 1)
        self.alpha = int(255 * (self.lifetime_remaining / self.lifetime))
        self.lifetime_remaining -= 1
        
        return self.lifetime_remaining > 0

    def draw(self, screen):
        draw_text(screen, font=self.font, text=str(self.text), color=self.color, x=self.position.x, y=self.position.y, alpha=self.alpha)