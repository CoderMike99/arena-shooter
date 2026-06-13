def draw_text(screen, font, text, color, x, y, alpha=255, anchor="topleft"):
    surface = font.render(text, True, color)
    surface.set_alpha(alpha)
    rect = surface.get_rect()
    setattr(rect, anchor, (x, y))
    screen.blit(surface, rect)