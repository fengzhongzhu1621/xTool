import pygame

from xTool.pygame import image, sound


def init_game(buffer: int = 1024) -> None:
    image.init_image()
    # 初始化声音
    sound.init_mixer(buffer=buffer)
    # 初始化字体模块
    pygame.font.init()
