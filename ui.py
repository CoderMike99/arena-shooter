def draw_text(screen, font, text, color, x, y, anchor="topleft"):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    setattr(rect, anchor, (x, y))
    screen.blit(surface, rect)