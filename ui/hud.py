import pygame
from settings import WINDOW_WIDTH, DASH_COOLDOWN_MAX, HUD_HEIGHT, PLAY_AREA_HEIGHT

# HUD Konstanten

HUD_BG_COLOR = (8, 8, 18)
HUD_BORDER_COLOR = (40, 40, 60)
BAR_BG_COLOR = (30, 30, 45)

# Ability Slot Konstanten
ABILITY_SLOT_WIDTH = 60
ABILITY_SLOT_HEIGHT = 72
ABILITY_SLOT_GAP = 8

# Farben Buttons (Xbox)
BTN_COLORS = {
    "A": (39, 174, 96),
    "B": (231, 76, 60),
    "X": (52, 152, 219),
    "Y": (241, 196, 15),
}


def draw_bar(screen, x, y, width, height, value, max_value, fill_color, label, label_color, font):
    """Zeichnet eine gefüllte Leiste mit Label."""
    # Hintergrund
    pygame.draw.rect(screen, BAR_BG_COLOR, (x, y, width, height), border_radius=4)
    # Füllung
    fill_width = int(width * max(0, value) / max_value)
    if fill_width > 0:
        pygame.draw.rect(screen, fill_color, (x, y, fill_width, height), border_radius=4)
    # Label links
    label_surf = font.render(label, True, label_color)
    screen.blit(label_surf, (x - label_surf.get_width() - 8, y + height // 2 - label_surf.get_height() // 2))
    # Wert rechts
    val_text = f"{int(value)}/{int(max_value)}"
    val_surf = font.render(val_text, True, (120, 120, 140))
    screen.blit(val_surf, (x + width + 6, y + height // 2 - val_surf.get_height() // 2))


def draw_ability_slot(screen, x, y, label, icon_text, cooldown_remaining, cooldown_max, btn_color, font_small):
    """Zeichnet einen Ability-Slot mit Cooldown-Overlay."""
    btn_color_dim = tuple(max(0, c - 180) for c in btn_color)
    bg_color = tuple(min(255, c + 15) for c in btn_color_dim)

    # Hintergrund
    pygame.draw.rect(screen, bg_color, (x, y, ABILITY_SLOT_WIDTH, ABILITY_SLOT_HEIGHT), border_radius=8)
    # Rahmen
    border_alpha = 180 if cooldown_remaining <= 0 else 60
    border_color = tuple(min(255, int(c * border_alpha / 180)) for c in btn_color)
    pygame.draw.rect(screen, border_color, (x, y, ABILITY_SLOT_WIDTH, ABILITY_SLOT_HEIGHT), width=2, border_radius=8)

    # Button Label oben
    key_surf = font_small.render(label, True, btn_color)
    screen.blit(key_surf, (x + ABILITY_SLOT_WIDTH // 2 - key_surf.get_width() // 2, y + 5))

    # Icon Mitte
    icon_surf = font_small.render(icon_text, True, (220, 220, 220))
    screen.blit(icon_surf, (x + ABILITY_SLOT_WIDTH // 2 - icon_surf.get_width() // 2, y + ABILITY_SLOT_HEIGHT // 2 - icon_surf.get_height() // 2 + 4))

    # Cooldown Overlay
    if cooldown_remaining > 0:
        cd_height = int(ABILITY_SLOT_HEIGHT * cooldown_remaining / cooldown_max)
        overlay = pygame.Surface((ABILITY_SLOT_WIDTH, cd_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (x, y + ABILITY_SLOT_HEIGHT - cd_height))

        cd_sec = cooldown_remaining / 60
        cd_text = f"{cd_sec:.1f}s" if cd_sec >= 1 else f"{int(cooldown_remaining * 1000 / 60)}ms"
        cd_surf = font_small.render(cd_text, True, (200, 200, 200))
        screen.blit(cd_surf, (x + ABILITY_SLOT_WIDTH // 2 - cd_surf.get_width() // 2, y + ABILITY_SLOT_HEIGHT - 16))


def draw_hud(screen, player, score, game_time, font, font_small):
    """
    Hauptfunktion – zeichnet die komplette HUD.
    
    Parameters:
        screen:      pygame Surface
        player:      Player Instanz
        score:       aktueller Score (int)
        game_time:   vergangene Frames (int)
        font:        normale Schrift
        font_small:  kleine Schrift für Labels und Ability Slots
    """

    # ── Hintergrund ──────────────────────────────────────────
    pygame.draw.rect(screen, HUD_BG_COLOR, (0, PLAY_AREA_HEIGHT, WINDOW_WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, HUD_BORDER_COLOR, (0, PLAY_AREA_HEIGHT), (WINDOW_WIDTH, PLAY_AREA_HEIGHT), 2)

    # ── Linke Sektion: HP + XP Leisten ───────────────────────
    left_x = 60
    bar_width = 220
    bar_height = 12

    hp_color = (46, 204, 113) if player.health_points > 50 else (243, 156, 18) if player.health_points > 25 else (231, 76, 60)
    draw_bar(screen, left_x, PLAY_AREA_HEIGHT + 28, bar_width, bar_height,
             player.health_points, player.max_health_points,
             hp_color, "HP", (231, 76, 60), font_small)

    # XP Platzhalter (später durch echte Werte ersetzen)
    xp_placeholder = 60
    xp_max_placeholder = 100
    draw_bar(screen, left_x, PLAY_AREA_HEIGHT + 58, bar_width, bar_height,
             xp_placeholder, xp_max_placeholder,
             (155, 89, 182), "XP", (155, 89, 182), font_small)

    # Level Platzhalter
    level_surf = font_small.render("LVL 1", True, (180, 130, 220))
    screen.blit(level_surf, (left_x, PLAY_AREA_HEIGHT + 82))

    # ── Mittlere Sektion: Score + Timer ───────────────────────
    center_x = WINDOW_WIDTH // 2

    score_surf = font.render(f"{score:,}", True, (255, 215, 0))
    screen.blit(score_surf, (center_x - score_surf.get_width() // 2, PLAY_AREA_HEIGHT + 20))

    score_label = font_small.render("SCORE", True, (80, 80, 100))
    screen.blit(score_label, (center_x - score_label.get_width() // 2, PLAY_AREA_HEIGHT + 55))

    minutes = game_time // 3600
    seconds = (game_time % 3600) // 60
    time_surf = font_small.render(f"{minutes:02d}:{seconds:02d}", True, (140, 140, 160))
    screen.blit(time_surf, (center_x - time_surf.get_width() // 2, PLAY_AREA_HEIGHT + 80))

    # ── Rechte Sektion: Ability Slots ─────────────────────────
    # 4 Slots: X (Shoot), A (Dash), B (–), Y (–)
    abilities = [
    ("RT", "SHOOT", player.attack_cooldown_remaining, player.attack_cooldown_max, (255, 255, 255)),
    ("X",  "DASH",  player.dash_cooldown_remaining,   DASH_COOLDOWN_MAX,          BTN_COLORS["X"]),
    ("A",  "–",     0,                                1,                          BTN_COLORS["A"]),
    ("B",  "–",     0,                                1,                          BTN_COLORS["B"]),
    ("Y",  "–",     0,                                1,                          BTN_COLORS["Y"])]


    total_width = len(abilities) * ABILITY_SLOT_WIDTH + (len(abilities) - 1) * ABILITY_SLOT_GAP
    slots_x = WINDOW_WIDTH - total_width - 24
    slots_y = PLAY_AREA_HEIGHT + (HUD_HEIGHT - ABILITY_SLOT_HEIGHT) // 2

    for i, (label, icon, cd_remaining, cd_max, color) in enumerate(abilities):
        slot_x = slots_x + i * (ABILITY_SLOT_WIDTH + ABILITY_SLOT_GAP)
        draw_ability_slot(screen, slot_x, slots_y, label, icon, cd_remaining, cd_max, color, font_small)