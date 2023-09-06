import pygame

pygame.init()
font = pygame.font.Font(None, 30)


def debug(text, row: int = 0):
    display_suface = pygame.display.get_surface()
    debug_surf = font.render(str(text), True, "White")
    debug_rect = debug_surf.get_rect(topleft=[10, 30*row])
    display_suface.blit(debug_surf, debug_rect)
