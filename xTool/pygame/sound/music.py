import pygame


def play_background_sound(file_path: str) -> None:
    """播放背景音乐"""
    if pygame.mixer:
        pygame.mixer.music.load(file_path)  # 加载背景音乐
        pygame.mixer.music.play(-1)  # 循环播放背景音乐
