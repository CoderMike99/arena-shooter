import pygame
from settings import WINDOW_HEIGHT, WINDOW_WIDTH, PLAYER_SIZE, PLAYER_SPEED, PLAYER_MAX_PROJECTILE_COUNT, DASH_COOLDOWN_MAX, DASH_DURATION, DASH_RANGE
from utils import normalize_vector, apply_deadzone, dash_delta

class Player:
    def __init__(self, x_position, y_position, controls, health_points, max_health_points, armor, max_projectile_count=PLAYER_MAX_PROJECTILE_COUNT, size=PLAYER_SIZE, color=(255, 0, 0)):
        self.health_points = health_points
        self.max_health_points = max_health_points
        self.armor = armor
        self.max_projectile_count = max_projectile_count
        self.current_projectile_count = 0
        self.size = size
        self.color = color
        self.controls = controls
        self.pos = pygame.math.Vector2(x_position, y_position)
        self.hitbox = pygame.Rect(self.pos.x, self.pos.y, size, size)
        

        # Abilities
        self.dash_active = False
        self.dash_progress = 0
        self.dash_direction = pygame.math.Vector2(0, 0)
        self.dash_cooldown_max = DASH_COOLDOWN_MAX
        self.dash_cooldown_remaining = 0


    def take_damage(self, amount):
        self.health_points -= max(0, amount - self.armor)
    
    def update(self, input_state: dict, joystick=None):
        self.hitbox.center = self.pos
        
        if self.dash_cooldown_remaining > 0:
            self.dash_cooldown_remaining -= 1

        # Starts dash if controller input is given and no dash active
        if input_state["dash_pressed"] and not self.dash_active:
            self.dash(joystick)
        # Continues ongoing dash
        if self.dash_active:
            self.dash(joystick)
        


    def getPosition(self):
        return pygame.math.Vector2(self.hitbox.centerx, self.hitbox.centery)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)

    def move(self, keys, joystick=None):
        if keys[self.controls["right"]] and self.pos.x < WINDOW_WIDTH - self.size:
            self.pos.x += 5
        if keys[self.controls["left"]] and self.pos.x > 0:
            self.pos.x -= 5
        if keys[self.controls["up"]] and self.pos.y > 0:
            self.pos.y -= 5
        if keys[self.controls["down"]] and self.pos.y < WINDOW_HEIGHT - self.size:
            self.pos.y += 5

        if joystick and (self.dash_progress >= DASH_DURATION * 0.3 or not self.dash_active):
            axis_x = apply_deadzone(joystick.get_axis(0))
            axis_y = apply_deadzone(joystick.get_axis(1))

            self.pos.x = max(0, min(self.pos.x + round(axis_x * PLAYER_SPEED), WINDOW_WIDTH - self.size))
            self.pos.y = max(0, min(self.pos.y + round(axis_y * PLAYER_SPEED), WINDOW_HEIGHT - self.size))


    def dash(self, joystick=None):
        # First Frame of Dash Ability: Set dash direction, dash_active flag and manage cooldown
        if self.dash_cooldown_remaining == 0 and joystick:
            self.dash_cooldown_remaining = DASH_COOLDOWN_MAX
            self.dash_direction = pygame.math.Vector2(normalize_vector(apply_deadzone(joystick.get_axis(0)), apply_deadzone(joystick.get_axis(1))))
            self.dash_active = True                                         
        
        # Change position and continue progress
        if self.dash_active:
            step = self.dash_direction * dash_delta(self.dash_progress, DASH_DURATION) * DASH_RANGE
            self.pos += step
            self.dash_progress += 1

        # Reset flag and timer at last frame of dash
        if self.dash_progress >= DASH_DURATION:
            self.dash_active = False
            self.dash_progress = 0
