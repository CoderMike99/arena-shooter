import pygame
import random
from sprites.player import Player
from sprites.projectile import Projectile
from sprites.enemy import Enemy, Chaser, Shooter
from ui import draw_text
from settings import *
from utils import *


pygame.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Mein erstes Fenster")

clock = pygame.time.Clock()
running = True

score = 0

player1_controls = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
player1 = Player(0, 0, player1_controls, health_points=100, max_health_points=100, armor=10, color=(255, 0, 0))

""" player2_controls = {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT}
player2 = Player(200, 200, player2_controls, color=(0, 0, 255)) """

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
joystick = joysticks[0] if joysticks else None

projectiles = []
enemies: list[Enemy] = []

spawn_timer = {"Chaser": 0, "Shooter": 0}
spawn_interval = random.randint(60,120)
game_time = 0

font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 20)

state = "playing"

while running:

    # Time
    game_time += 1
    #spawn_timer["Chaser"] += 1
    #spawn_timer["Shooter"] += 1
    

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.JOYBUTTONDOWN and event.button == 5:
            direction = joystick_direction(joystick)
            if direction is not None:
                projectiles.append(Projectile(*player1.getPosition(), velocity=direction, faction="player", damage=PLAYER_DAMAGE, color=(255,165,0)))
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            enemies.append(Chaser())
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            enemies.append(Shooter())

    # Gegner spawnen
    if spawn_timer["Chaser"] == spawn_interval:
        spawn_timer["Chaser"] = 0
        spawn_interval = random.randint(30, max(30, 120 - score))
        enemies.append(Chaser())



    # Input
    keys = pygame.key.get_pressed()
    player1.move(keys, joystick)

    # Neue Projektile erzeugen
    for enemy in enemies:
        if isinstance(enemy, Shooter):
            projectiles += enemy.new_projectiles
            enemy.new_projectiles = [] # sofort leeren nach dem Erstellen

    # Kollisionen von Projektilen und Gegnern überprüfen
    for projectile in projectiles:
        if projectile.faction == "player":
            targets = enemies
        else:
            targets = [player1]
        
        for target in targets:
            if target.hitbox.colliderect(projectile.hitbox):
                projectile.piercing -= 1
                target.take_damage(projectile.damage)

    

    projectiles = [p for p in projectiles if p.update()]

    # Tracking kills by adding length difference of active enemies
    kills = len(enemies)
    enemies = [enemy for enemy in enemies if enemy.update(player1.getPosition())]    
    kills -= len(enemies)
    score += kills

    #shooter_projectiles = [p for p in projectiles if p.update()]

    
    # Zeichnen
    screen.fill((30, 30, 30))
    draw_text(screen, font, f"Score: {score}", (255,255,255), WINDOW_WIDTH//2, 20, anchor="midtop")
    

    player1.draw(screen)
    #player2.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)

    for p in projectiles:
        p.draw(screen)
    
    # Neuer Frame
    pygame.display.flip()
    clock.tick(60)

pygame.quit()