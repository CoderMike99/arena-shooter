import pygame
import random
from sprites.entity import Entity
from sprites.projectile import Projectile
from abc import ABC, abstractmethod
from settings import *
from utils import direction_to, normalize_angle

class Enemy(Entity):
    def __init__(self, damage, health_points, max_health_points, position, armor, attack_speed, movement_speed, size, color):
        super().__init__(damage=damage,
                         health_points=health_points,
                         max_health_points=max_health_points,
                         position=position,
                         armor=armor,
                         attack_speed=attack_speed,
                         movement_speed=movement_speed,
                         size=size,
                         color=color)

    @staticmethod
    def get_random_spawn_position(size=0) -> pygame.math.Vector2:
        side = random.choice(["left", "right", "top", "bottom"])

        match side:
            case "left":
                return pygame.math.Vector2(-40, random.randint(0, PLAY_AREA_HEIGHT))
            case "right":
                return pygame.math.Vector2(WINDOW_WIDTH + size // 2, random.randint(0, PLAY_AREA_HEIGHT))
            case "top":
                return pygame.math.Vector2(random.randint(0, WINDOW_WIDTH), -40)
            case "bottom":
                return pygame.math.Vector2(random.randint(0, WINDOW_WIDTH), PLAY_AREA_HEIGHT + size // 2)
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
                         attack_speed=CHASER_ATTACK_SPEED,
                         movement_speed=CHASER_MOVEMENT_SPEED,
                         size=CHASER_SIZE,
                         color=CHASER_COLOR)
        
        self.image = pygame.image.load("assets/images/enemy_chaser_160.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (CHASER_SIZE*3.5, CHASER_SIZE*3.5))

    def update(self, player_pos):
        direction = direction_to(self.position, player_pos)
        if direction:
            self.position += direction * float(self.movement_speed)
            self.hitbox.center = self.position

        if self.attack_cooldown_remaining > 0:
            self.attack_cooldown_remaining -= 1

        return self.health_points > 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)
        self.draw_health_bar(screen)
        rect = self.image.get_rect(center=self.hitbox.center)
        screen.blit(self.image, rect)

class Shooter(Enemy):
    def __init__(self, shoot_interval = SHOOTER_SHOOT_INTERVAL):
        super().__init__(damage=SHOOTER_DAMAGE,
                         health_points=SHOOTER_HEALTH_POINTS,
                         max_health_points=SHOOTER_MAX_HEALTH_POINTS,
                         position=Enemy.get_random_spawn_position(SHOOTER_SIZE),
                         armor=SHOOTER_ARMOR,
                         attack_speed=SHOOTER_ATTACK_SPEED,
                         movement_speed=SHOOTER_MOVEMENT_SPEED,
                         size=SHOOTER_SIZE,
                         color=SHOOTER_COLOR)
        
        self.image = pygame.image.load("assets/images/enemy_shooter_160.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (SHOOTER_SIZE*3.5, SHOOTER_SIZE*3.5))
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
            self.position.y > PLAY_AREA_HEIGHT - vertical_border_buff:
            # Move on if not in position
                if direction:
                    self.position += direction * float(self.movement_speed)
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
        rect = self.image.get_rect(center=self.hitbox.center)
        screen.blit(self.image, rect)

    def shoot(self, direction):
        self.new_projectiles = []   # Jeden Frame leeren      
        if self.attack_cooldown_remaining > 0:
            self.attack_cooldown_remaining -= 1
        else:
            self.new_projectiles.append(Projectile(position=pygame.math.Vector2(self.position),
                                                   velocity=direction,
                                                   faction="enemy",
                                                   damage=self.damage,
                                                   color=SHOOTER_COLOR))
            self.attack_cooldown_remaining = self.attack_cooldown_max

class Seeker(Enemy):
    def __init__(self,
                 slowdown_radius = SEEKER_SLOWDOWN_RADIUS,
                 min_speed = SEEKER_MIN_SPEED,
                 max_speed = SEEKER_MAX_SPEED,
                 acceleration = SEEKER_ACCELERATION,
                 max_turn_angle = SEEKER_MAX_TURN_DEGREES_PER_FRAME):
        super().__init__(damage=SEEKER_DAMAGE,
                         health_points=SEEKER_HEALTH_POINTS,
                         max_health_points=SEEKER_MAX_HEALTH_POINTS,
                         position=Enemy.get_random_spawn_position(SEEKER_SIZE),
                         armor=SEEKER_ARMOR,
                         attack_speed=SEEKER_ATTACK_SPEED,
                         movement_speed=SEEKER_MAX_SPEED,
                         size=SEEKER_SIZE,
                         color=SEEKER_COLOR)
        

        self.original_image = pygame.image.load("assets/images/enemy_seeker_schweif_160.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (SEEKER_SIZE*6, SEEKER_SIZE*6))
        self.image = self.original_image
        self.slowdown_radius = slowdown_radius
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.velocity = pygame.math.Vector2(self.movement_speed, 0).rotate(random.uniform(0, 360))
        self.max_turn_angle = max_turn_angle
        self.current_speed = min_speed

    def update(self, player_pos):
        # 1. Wo soll ich hin?
        target_direction = direction_to(self.position, player_pos)
        
        # 2. Wie weit muss ich mich drehen, um dorthin zu zeigen?
        self.angle_to_target = self.velocity.angle_to(target_direction)
        self.angle_to_target = normalize_angle(self.angle_to_target)  # auslagern!
        
        # 3. Wie nah bin ich am Ziel?
        distance = (player_pos - self.position).length()
        
        # 4. Wie aggressiv darf ich JETZT drehen? (langsamer wenn nah)
        if distance < self.slowdown_radius:
            effective_max_turn = self.max_turn_angle * (distance / self.slowdown_radius)
        else:
            effective_max_turn = self.max_turn_angle
        
        # 5. Tatsächlicher Drehwinkel diesen Frame (begrenzt)
        turn_this_frame = max(-effective_max_turn, min(effective_max_turn, self.angle_to_target))
        
        # 6. Wie schnell will ich fliegen? (langsamer in scharfen Kurven)
        turn_severity = 0.5 * abs(turn_this_frame) / self.max_turn_angle  # 0 = gerade, 1 = max Kurve
        target_speed = self.max_speed - (self.max_speed - self.min_speed) * turn_severity
        
        # 7. Geschwindigkeit graduell anpassen (keine Sprünge)
        if self.current_speed < target_speed:
            self.current_speed = min(target_speed, self.current_speed + self.acceleration)
        else:
            self.current_speed = max(target_speed, self.current_speed - self.acceleration)
        
        # 8. Velocity aktualisieren: drehen + neue Geschwindigkeit
        self.velocity = self.velocity.rotate(turn_this_frame).normalize() * self.current_speed
        
        # 9. Bewegen
        self.position += self.velocity
        self.hitbox.center = self.position
        
        return self.health_points > 0

    def draw(self, screen):
        #pygame.draw.rect(screen, self.color, self.hitbox)
        self.draw_health_bar(screen)
        angle = self.velocity.angle_to(pygame.math.Vector2(0, -1))  # Winkel zur "rechts" Richtung
        self.image = pygame.transform.rotate(self.original_image, angle)
        rect = self.image.get_rect(center=self.hitbox.center)
        screen.blit(self.image, rect)

   