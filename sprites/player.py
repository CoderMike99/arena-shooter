import pygame
from sprites.entity import Entity
from sprites.projectile import Projectile
from settings import PLAY_AREA_HEIGHT, WINDOW_WIDTH, PLAYER_MAX_HEALTH_POINTS, PLAYER_DAMAGE, PLAYER_SIZE, PLAYER_ARMOR, PLAYER_ATTACK_SPEED, PLAYER_MOVEMENT_SPEED, PLAYER_PROJECTILE_SIZE, PLAYER_PROJECTILE_SPEED, PLAYER_COLOR, DASH_COOLDOWN_MAX, DASH_DURATION, DASH_RANGE
from utils import normalize_vector, apply_deadzone, dash_delta
from animation import Animation

class Player(Entity):
    def __init__(self, 
                 controls,
                 position=pygame.math.Vector2(WINDOW_WIDTH // 2, PLAY_AREA_HEIGHT // 2),
                 damage = PLAYER_DAMAGE, 
                 health_points=PLAYER_MAX_HEALTH_POINTS, 
                 max_health_points=PLAYER_MAX_HEALTH_POINTS, 
                 armor=PLAYER_ARMOR, speed=PLAYER_MOVEMENT_SPEED,
                 attack_speed=PLAYER_ATTACK_SPEED,
                 size=PLAYER_SIZE, 
                 color=PLAYER_COLOR):
        super().__init__(damage=damage,
                         health_points=health_points,
                         max_health_points=max_health_points,
                         position=position,
                         armor=armor,
                         attack_speed=attack_speed,
                         movement_speed=speed,
                         size=size,
                         color=color)

        self.current_projectile_count = 0
        self.controls = controls
        self.position = position
        self.hitbox = pygame.Rect(self.position.x, self.position.y, size, size)
        self.xp = 0
        self.level = 0
        self.xp_to_next_level = 30

        # Abilities
        self.dash_active = False
        self.dash_progress = 0
        self.dash_direction = pygame.math.Vector2(0, 0)
        self.dash_cooldown_max = DASH_COOLDOWN_MAX
        self.dash_cooldown_remaining = 0

        # Animation
        self.load_animations()
        self.animations = Animation(self.idle_frames, 30)
    
    def update(self, input_state: dict, joystick=None):
        self.hitbox.center = self.position
        if self.attack_cooldown_remaining > 0:
            self.attack_cooldown_remaining -= 1
        if self.dash_cooldown_remaining > 0:
            self.dash_cooldown_remaining -= 1

        # Starts dash if controller input is given and no dash active
        if input_state["dash_pressed"] and not self.dash_active:
            self.dash(joystick)
        # Continues ongoing dash
        if self.dash_active:
            self.dash(joystick)

        self.animations.update()
        


    def getPosition(self):
        return pygame.math.Vector2(self.hitbox.centerx, self.hitbox.centery)

    def get_xp(self, xp_value):
        self.xp += xp_value
        #print(f"XP erhöht um {xp_value} auf {self.xp}")

    """ def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)
        self.draw_health_bar(screen) """

    def draw(self, screen):
        if self.animations:  # nur wenn überhaupt Animationen vorhanden sind
            image = self.animations.get_current_frame()
            image = pygame.transform.scale(image, (self.size*3, self.size*3))  # oder eigene Breite/Höhe
            screen.blit(image, self.hitbox)
        else:
            pygame.draw.rect(screen, self.color, self.hitbox)

    def move(self, keys, joystick=None):
        if keys[self.controls["right"]] and self.position.x < WINDOW_WIDTH - self.size:
            self.position.x += 5
        if keys[self.controls["left"]] and self.position.x > 0:
            self.position.x -= 5
        if keys[self.controls["up"]] and self.position.y > 0:
            self.position.y -= 5
        if keys[self.controls["down"]] and self.position.y < PLAY_AREA_HEIGHT - self.size:
            self.position.y += 5

        if joystick and (self.dash_progress >= DASH_DURATION * 0.3 or not self.dash_active):
            axis_x = apply_deadzone(joystick.get_axis(0))
            axis_y = apply_deadzone(joystick.get_axis(1))

            self.position.x = max(self.size // 2, min(self.position.x + round(axis_x * self.movement_speed), WINDOW_WIDTH - self.size // 2))
            self.position.y = max(self.size // 2, min(self.position.y + round(axis_y * self.movement_speed), PLAY_AREA_HEIGHT - self.size // 2))

    def shoot(self, direction) -> Projectile | None:
        if self.attack_cooldown_remaining <= 0 and direction is not None:
            self.attack_cooldown_remaining = self.attack_cooldown_max
            return Projectile(self.getPosition(), velocity=direction, 
                            faction="player", damage=self.damage, color=(255,165,0), size=PLAYER_PROJECTILE_SIZE, speed=PLAYER_PROJECTILE_SPEED)
        return None

    def dash(self, joystick=None):
        # First Frame of Dash Ability: Set dash direction, dash_active flag and manage cooldown
        if self.dash_cooldown_remaining == 0 and joystick:
            self.dash_cooldown_remaining = DASH_COOLDOWN_MAX
            self.dash_direction = pygame.math.Vector2(normalize_vector(apply_deadzone(joystick.get_axis(0)), apply_deadzone(joystick.get_axis(1))))
            if self.dash_direction != pygame.math.Vector2(0,0):
                self.dash_active = True                                         
        
        # Change position and continue progress
        if self.dash_active:
            step = self.dash_direction * dash_delta(self.dash_progress, DASH_DURATION) * DASH_RANGE
            self.position += step
            self.dash_progress += 1

        # Reset flag and timer at last frame of dash
        if self.dash_progress >= DASH_DURATION:
            self.dash_active = False
            self.dash_progress = 0


    def load_animations(self):
        self.idle_frames = self._load_spritesheet("assets/images/office_guy_black_front_idle.png", 18, 24)
