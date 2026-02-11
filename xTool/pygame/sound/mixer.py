import pygame


def init_mixer(buffer=1024) -> None:
    if pygame.get_sdl_version()[0] == 2:
        pygame.mixer.pre_init(44100, 32, 2, buffer)  # SDL2音频预初始化

    # 初始化pygame，必须在mixer 之前初始化，否则mixer 无法初始化
    _ = pygame.init()

    if pygame.mixer and not pygame.mixer.get_init():  # 检查音频是否初始化成功
        print("警告，没有声音")
        pygame.mixer = None
