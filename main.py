import pygame
from sprites.player import Player
from sprites.projectile import Projectile
from sprites.enemy import Enemy, Chaser, Shooter
from ui.ui import draw_text
from ui.damage_number import DamageNumber
from settings import *
from utils import *
from spawn_manager import SpawnManager


pygame.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Mein erstes Fenster")

clock = pygame.time.Clock()
running = True
score = 0
game_time = 0
state = "playing"

player1_controls = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
player1 = Player(controls=player1_controls)

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
joystick = joysticks[0] if joysticks else None

projectiles = []
enemies: list[Enemy] = []
damage_numbers: list[DamageNumber] = []

font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 20)
dmg_number_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 10)
debug_font = pygame.font.SysFont("Courier New", 14)

spawn_manager = SpawnManager()


def handle_global_events(events) -> bool:
    """Events die immer gelten, egal welcher State. Gibt False zurück wenn Spiel beendet werden soll."""
    global state
    for event in events:
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.JOYBUTTONDOWN and event.button == 7:
            state = "paused" if state == "playing" else "playing"
    return True


def handle_playing_events(events, input_state):
    """Events die nur im playing State relevant sind."""
    for event in events:
        if event.type == pygame.JOYBUTTONDOWN and event.button == 2:
            input_state["dash_pressed"] = True

        if event.type == pygame.JOYBUTTONDOWN and event.button == 5:
            direction = joystick_direction(joystick)
            if direction is not None and player1.attack_cooldown_remaining <= 0:
                projectiles.append(Projectile(player1.getPosition(), velocity=direction, faction="player", damage=player1.damage, color=(255, 165, 0)))
                player1.attack_cooldown_remaining = player1.attack_cooldown_max
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            enemies.append(Chaser())
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            enemies.append(Shooter())


def update_game_logic(input_state):
    """Spiellogik – nur im playing State."""
    global enemies, projectiles, damage_numbers, game_time, score

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


def draw_playing():
    """Alles zeichnen im playing State."""
    screen.fill((30, 30, 30))

    draw_text(screen, font, f"Score: {score}", (255, 255, 255), WINDOW_WIDTH // 2, 20, anchor="midtop")
    draw_text(screen, debug_font, f"Enemies: {len(enemies)}", (150, 150, 150), 10, 10, anchor="topleft")
    draw_text(screen, debug_font, f"Difficulty: {spawn_manager.current_difficulty:.2f}", (150, 150, 150), 10, 30, anchor="topleft")
    draw_text(screen, debug_font, f"Max Spawn Interval Chaser: {int(CHASER_INITIAL_SPAWN_INTERVAL - spawn_manager.current_difficulty) / 60:.2f}s", (150, 150, 150), 10, 50, anchor="topleft")
    draw_text(screen, debug_font, f"Max Spawn Interval Shooter: {int(SHOOTER_INITIAL_SPAWN_INTERVAL - spawn_manager.current_difficulty * 10) / 60:.2f}s", (150, 150, 150), 10, 70, anchor="topleft")
    draw_text(screen, debug_font, f"Game Time: {game_time // 3600}:{(game_time % 3600) // 60:02d}", (150, 150, 150), WINDOW_WIDTH - 10, 10, anchor="topright")
    draw_text(screen, debug_font, f"Player HP: {player1.health_points} / {player1.max_health_points}", (150, 150, 150), WINDOW_WIDTH - 10, 30, anchor="topright")

    player1.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    for p in projectiles:
        p.draw(screen)
    for number in damage_numbers:
        number.draw(screen)


def draw_paused():
    """Pause overlay."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    draw_text(screen, font, "GAME PAUSED", (255, 255, 255), WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, anchor="center")


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
        draw_paused()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()