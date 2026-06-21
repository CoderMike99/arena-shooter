import pygame
from utils import direction_to
from ui.ui import draw_text

def draw_debug_angle(screen, enemy, angle_value, font):
    draw_text(screen, font, f"{angle_value:.0f}°", (255, 255, 0), 
              enemy.position.x, enemy.position.y - 30, anchor="center")

def draw_debug_vectors(screen, enemy, player_pos, length=50):
    # Velocity-Richtung (wohin er sich bewegt)
    velocity_end = enemy.position + enemy.velocity.normalize() * length
    pygame.draw.line(screen, (0, 255, 0), enemy.position, velocity_end, 2)
    
    # Richtung zum Spieler
    target_dir = direction_to(enemy.position, player_pos)
    target_end = enemy.position + target_dir * length
    pygame.draw.line(screen, (255, 0, 0), enemy.position, target_end, 2)