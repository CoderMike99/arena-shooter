import pygame
from settings import WINDOW_HEIGHT, WINDOW_WIDTH, PLAYER_SIZE
from utils import apply_deadzone

class Player:
    def __init__(self, x_position, y_position, controls, health_points, max_health_points, armor, size=PLAYER_SIZE, color=(255, 0, 0)):
        self.health_points = health_points
        self.max_health_points = max_health_points
        self.armor = armor
        self.size = size
        self.color = color
        self.controls = controls
        self.hitbox = pygame.Rect(x_position, y_position, size, size)

    def take_damage(self, amount):
        self.health_points -= max(0, amount - self.armor)
    
    def getPosition(self):
        return pygame.math.Vector2(self.hitbox.centerx, self.hitbox.centery)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)

    def move(self, keys, joystick=None):
        if keys[self.controls["right"]] and self.hitbox.x < WINDOW_WIDTH - self.size:
            self.hitbox.x += 5
        if keys[self.controls["left"]] and self.hitbox.x > 0:
            self.hitbox.x -= 5
        if keys[self.controls["up"]] and self.hitbox.y > 0:
            self.hitbox.y -= 5
        if keys[self.controls["down"]] and self.hitbox.y < WINDOW_HEIGHT - self.size:
            self.hitbox.y += 5

        if joystick:
            axis_x = apply_deadzone(joystick.get_axis(0))
            axis_y = apply_deadzone(joystick.get_axis(1))

            self.hitbox.x = max(0, min(self.hitbox.x + round(axis_x * 5), WINDOW_WIDTH - self.size))
            self.hitbox.y = max(0, min(self.hitbox.y + round(axis_y * 5), WINDOW_HEIGHT - self.size))
