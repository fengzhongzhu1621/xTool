import os

import pygame


def get_font_list(dir_path: str) -> list[str]:
    """
    Generate a font list using font.get_fonts() for system fonts or
    from a path from the command line.
    """
    if os.path.exists(dir_path):
        fonts = [font for font in os.listdir(dir_path) if font.endswith(".ttf")]
    else:
        fonts = pygame.font.get_fonts()

    return fonts
