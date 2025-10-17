import pygame


def init_image() -> None:
    # see if we can load more than standard BMP
    if not pygame.image.get_extended():
        raise SystemExit("Sorry, extended image module required")
