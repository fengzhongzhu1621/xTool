import pygame


def quit_game() -> None:
    # 背景音乐淡出
    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)

    pygame.quit()
