import pygame
from pygame.mixer import Sound


def init_mixer(buffer=1024) -> None:
    if pygame.get_sdl_version()[0] == 2:
        pygame.mixer.pre_init(44100, 32, 2, buffer)  # SDL2音频预初始化

    # 初始化pygame，必须在mixer 之前初始化，否则mixer 无法初始化
    _ = pygame.init()

    if pygame.mixer and not pygame.mixer.get_init():  # 检查音频是否初始化成功
        print("警告，没有声音")
        pygame.mixer = None


def load_sound(file_path: str) -> Sound | None:
    """加载音效（因为pygame可能在没有mixer的情况下编译）"""
    if not pygame.mixer:
        return None
    try:
        sound = pygame.mixer.Sound(file_path)  # 加载音效
        return sound
    except pygame.error:
        print(f"警告，无法加载 {file_path}")
    return None


def play_background_sound(file_path: str) -> None:
    """播放背景音乐"""
    if pygame.mixer:
        pygame.mixer.music.load(file_path)  # 加载背景音乐
        pygame.mixer.music.play(-1)  # 循环播放背景音乐
