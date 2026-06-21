import pygame
from utils import random_unit_vector, direction_to
from settings import XP_SHARD_WIDTH, XP_SHARD_HEIGHT, XP_SHARD_COLOR, XP_SHARD_SCATTER_RANGE, XP_SHARD_SCATTER_TIME, XP_SHARD_PICKUP_RANGE, XP_SHARD_DROP_MOVEMENT_SPEED, XP_SHARD_COLLECT_MOVEMENT_SPEED


class XPShard():
    def __init__(self,
                value,
                position=pygame.math.Vector2(0,0),
                color = XP_SHARD_COLOR,
                drop_movement_speed = XP_SHARD_DROP_MOVEMENT_SPEED,
                collect_movement_speed = XP_SHARD_COLLECT_MOVEMENT_SPEED,
                pickup_range = XP_SHARD_PICKUP_RANGE,
                scatter_range = XP_SHARD_SCATTER_RANGE,
                scatter_time = XP_SHARD_SCATTER_TIME):
        self.hitbox = pygame.Rect(0, 0, XP_SHARD_WIDTH, XP_SHARD_HEIGHT)
        self.value = value
        self.position = position
        self.color = color
        self.drop_movement_speed = drop_movement_speed
        self.collect_movement_speed = collect_movement_speed
        self.pickup_range = pickup_range
        self.is_scattering = True
        self.is_collected = False
        self.scatter_time = scatter_time
        self.scatter_velocity = random_unit_vector() * scatter_range / scatter_time
    
    def update(self, player_pos):
        distance = (player_pos - self.position).length()
        direction = direction_to(self.position, player_pos)
        
        if distance <= self.pickup_range:
            self.is_collected = True
            self.is_scattering = False
            self.drop_movement_speed = self.collect_movement_speed
        elif self.is_scattering:
            self.position += self.scatter_velocity
            self.scatter_time -= 1
            self.is_scattering = False if self.scatter_time <= 0 else True

        if self.is_collected:
            self.position += direction * self.collect_movement_speed
            self.collect_movement_speed += 0.05

        self.hitbox.center = self.position
        
        return distance > 20       


    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)