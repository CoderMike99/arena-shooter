import pygame
import random
from sprites.player import Player
from sprites.projectile import Projectile
from sprites.enemy import Enemy, Chaser, Shooter
from ui import draw_text
from settings import *
from utils import *
from spawn_manager import SpawnManager


pygame.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Mein erstes Fenster")

clock = pygame.time.Clock()
running = True

score = 0

player1_controls = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
player1 = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, player1_controls, health_points=100, max_health_points=100, armor=10, color=(255, 0, 0))

""" player2_controls = {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT}
player2 = Player(200, 200, player2_controls, color=(0, 0, 255)) """

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
joystick = joysticks[0] if joysticks else None
print(joystick)

projectiles = []
enemies: list[Enemy] = []
game_time = 0

font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 20)
debug_font = pygame.font.SysFont("Courier New", 14)

state = "playing"

spawn_manager = SpawnManager()

while running:
    
    
    player1.current_projectile_count = len([p for p in projectiles if p.faction == "player"])
    player1_input_state = {"dash_pressed": False}

    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN and event.button == 7:
            if state == "playing":
                state = "paused"
            elif state == "paused":
                state = "playing"

        if event.type == pygame.QUIT:
                running = False

        if event.type == pygame.JOYBUTTONDOWN:
                    print(event.button)

        if state == "playing":        
                if event.type == pygame.JOYBUTTONDOWN and event.button == 2:
                    player1_input_state["dash_pressed"] = True

                if event.type == pygame.JOYBUTTONDOWN and event.button == 5:
                    direction = joystick_direction(joystick)
                    if direction is not None and player1.current_projectile_count < player1.max_projectile_count:
                        projectiles.append(Projectile(*player1.getPosition(), velocity=direction, faction="player", damage=PLAYER_DAMAGE, color=(255,165,0)))
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    enemies.append(Chaser())
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    enemies.append(Shooter())


    if state == "playing":
        # Time
        game_time += 1

        # Gegner spawnen
        enemies += spawn_manager.update()

        # Input
        keys = pygame.key.get_pressed()
        player1.move(keys, joystick)
        player1.update(player1_input_state, joystick)

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

        
        # Zeichnen
        screen.fill((30, 30, 30))
        draw_text(screen, font, f"Score: {score}", (255,255,255), WINDOW_WIDTH//2, 20, anchor="midtop")
        
        # Debug-Info
        draw_text(screen, debug_font, f"Enemies: {len(enemies)}", (150,150,150), 10, 10, anchor="topleft")
        draw_text(screen, debug_font, f"Difficulty: {spawn_manager.current_difficulty:.2f}", (150,150,150), 10, 30, anchor="topleft")
        draw_text(screen, debug_font, f"Max Spawn Interval Chaser: {int(CHASER_INITIAL_SPAWN_INTERVAL - spawn_manager.current_difficulty)/60:.2f}s", (150,150,150), 10, 50, anchor="topleft")
        draw_text(screen, debug_font, f"Max Spawn Interval Shooter: {int(SHOOTER_INITIAL_SPAWN_INTERVAL - spawn_manager.current_difficulty * 10)/60:.2f}s", (150,150,150), 10, 70, anchor="topleft")
        draw_text(screen, debug_font, f"Game Time: {game_time // 3600}:{(game_time % 3600)//60:02d}", (150,150,150), WINDOW_WIDTH-10, 10, anchor="topright")
        draw_text(screen, debug_font, f"Bullets: {player1.max_projectile_count - player1.current_projectile_count}", (150,150,150), WINDOW_WIDTH-10, 30, anchor="topright")

        player1.draw(screen)
        #player2.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        for p in projectiles:
            p.draw(screen)
        
        # Neuer Frame
    
    
    if state == "paused":
        draw_text(screen, font, "GAME PAUSED", (255,255,255), WINDOW_WIDTH//2, WINDOW_HEIGHT//2, anchor="center")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()