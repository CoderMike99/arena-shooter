import pygame
from sprites.player import Player
from sprites.projectile import Projectile
from sprites.enemy import Enemy, Chaser, Shooter
from ui.ui import draw_text
from ui.hud import draw_hud
from ui.damage_number import DamageNumber
from settings import *
from utils import *
from spawn_manager import SpawnManager


pygame.init()

info = pygame.display.Info()
#screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
#screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
pygame.display.set_caption("Mein erstes Fenster")

clock = pygame.time.Clock()
running = True
score = 0
game_time = 0
state = "playing"

player1_controls = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
player1 = Player(controls=player1_controls)

pygame.joystick.init()
joysticks: list[pygame.joystick.JoystickType] = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
if joysticks is not None:
    joystick: pygame.joystick.JoystickType | None = joysticks[0]

projectiles = []
enemies: list[Enemy] = []
damage_numbers: list[DamageNumber] = []

font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 20)
game_over_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 40)
dmg_number_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 10)
debug_font = pygame.font.SysFont("Courier New", 14)

spawn_manager = SpawnManager()

def set_state(new_state):
    global state, previous_state
    previous_state = state
    state = new_state

def handle_global_events(events) -> bool:
    """Events die immer gelten, egal welcher State. Gibt False zurück wenn Spiel beendet werden soll."""
    global state
    for event in events:
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.JOYBUTTONDOWN and event.button == 7:
            set_state("paused") if state == "playing" else set_state("playing")
    return True

def handle_playing_events(events, input_state):
    global state, joystick, joysticks
    """Events die nur im playing State relevant sind."""
    
    
    if joystick and joystick.get_button(5):
            direction = joystick_direction(joystick)
            projectile = player1.shoot(direction)
            if projectile:
                projectiles.append(projectile)
    
    for event in events:
        if event.type == pygame.JOYDEVICEREMOVED:
            joystick = None
            state = "controller_disconnected"

        if event.type == pygame.JOYDEVICEADDED:
            joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            joystick = joysticks[0] if joysticks else None
            state = "playing"  # oder vorheriger state
        if event.type == pygame.JOYBUTTONDOWN and event.button == 2:
            input_state["dash_pressed"] = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            enemies.append(Chaser())
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            enemies.append(Shooter())

def handle_game_over_events(events):
    global player1, spawn_manager, state, score, enemies, projectiles, game_time
    for event in events:
        if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
            player1 = Player(controls=player1_controls)
            score = 0
            enemies = []
            projectiles = []
            game_time = 0
            state = "playing"
            spawn_manager = SpawnManager()


def update_game_logic(input_state):
    """Spiellogik – nur im playing State."""
    global state, enemies, projectiles, damage_numbers, game_time, score

    game_time += 1
    enemies += spawn_manager.update()

    keys = pygame.key.get_pressed()
    player1.move(keys, joystick)
    player1.update(input_state, joystick)

    for enemy in enemies:
        if isinstance(enemy, Shooter):
            projectiles += enemy.new_projectiles
            enemy.new_projectiles = []
        if isinstance(enemy, Chaser):
            if enemy.hitbox.colliderect(player1.hitbox) and enemy.attack_cooldown_remaining <= 0:
                enemy.attack_cooldown_remaining = enemy.attack_cooldown_max
                player1.take_damage(enemy.damage)
                damage_numbers.append(DamageNumber(font=dmg_number_font, position=player1.position, number=int(enemy.damage - player1.armor)))
            
    for projectile in projectiles:
        targets = enemies if projectile.faction == "player" else [player1]
        for target in targets:
            if target.hitbox.colliderect(projectile.hitbox) and target not in projectile.damaged_targets:
                projectile.piercing -= 1
                projectile.damaged_targets.append(target)
                target.take_damage(projectile.damage)
                damage_numbers.append(DamageNumber(font=dmg_number_font, position=target.position, number=int(projectile.damage - target.armor)))

    projectiles[:] = [p for p in projectiles if p.update()]
    damage_numbers[:] = [n for n in damage_numbers if n.update()]

    kills = len(enemies)
    enemies[:] = [e for e in enemies if e.update(player1.getPosition())]
    score += kills - len(enemies)

    if player1.health_points <= 0:
        state = "game_over"


def draw_playing():
    """Alles zeichnen im playing State."""
    screen.fill((30, 30, 30))
    
    draw_text(screen, font, f"Score: {score}", (255, 255, 255), WINDOW_WIDTH // 2, 20, anchor="midtop")
    draw_text(screen, debug_font, f"Enemies: {len(enemies)}", (150, 150, 150), 10, 10, anchor="topleft")
    draw_text(screen, debug_font, f"Difficulty: {spawn_manager.current_difficulty:.2f}", (150, 150, 150), 10, 30, anchor="topleft")
    draw_text(screen, debug_font, f"Max Spawn Interval Chaser: {int(CHASER_INITIAL_SPAWN_INTERVAL - spawn_manager.current_difficulty) / 60:.2f}s", (150, 150, 150), 10, 50, anchor="topleft")
    draw_text(screen, debug_font, f"Max Spawn Interval Shooter: {int(SHOOTER_INITIAL_SPAWN_INTERVAL - spawn_manager.current_difficulty * 10) / 60:.2f}s", (150, 150, 150), 10, 70, anchor="topleft")
    draw_text(screen, debug_font, f"Game State: {state}", (150, 150, 150), WINDOW_WIDTH - 10, 10, anchor="topright")
    draw_text(screen, debug_font, f"Game Time: {game_time // 3600}:{(game_time % 3600) // 60:02d}", (150, 150, 150), WINDOW_WIDTH - 10, 30, anchor="topright")
    draw_text(screen, debug_font, f"Player HP: {player1.health_points} / {player1.max_health_points}", (150, 150, 150), WINDOW_WIDTH - 10, 50, anchor="topright")

    player1.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    for p in projectiles:
        p.draw(screen)
    for number in damage_numbers:
        number.draw(screen)

    draw_hud(screen, player1, score, game_time, font, dmg_number_font)



def draw_overlay(text):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))
    draw_text(screen, font, text, (255,255,255), WINDOW_WIDTH//2, WINDOW_HEIGHT//2, anchor="center")


def draw_game_over():
    """Game over overlay."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    draw_text(screen, game_over_font, "GAME OVER", (255, 0, 0), WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, anchor="center")
    draw_text(screen, font, f"Score: {score}", (255,255,255), WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30, anchor="center")
    draw_text(screen, font, f"Press A to restart.", (255,255,255), WINDOW_WIDTH // 2, 30, anchor="center")

# Game Loop
while running:
    player1.current_projectile_count = len([p for p in projectiles if p.faction == "player"])
    player1_input_state = {"dash_pressed": False}

    events = pygame.event.get()
    running = handle_global_events(events)

    if state == "playing":
        handle_playing_events(events, player1_input_state)
        update_game_logic(player1_input_state)
        draw_playing()
    elif state == "paused":
        draw_overlay("GAME PAUSED")
    elif state == "controller_disconnected":
        draw_overlay("CONTROLLER DISCONNECTED")

    elif state == "game_over":
        handle_game_over_events(events)
        draw_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()