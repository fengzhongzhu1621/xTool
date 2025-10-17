from xTool.pygame import image, sound


def init_game(buffer: int = 1024) -> None:
    image.init_image()
    sound.init_mixer(buffer=buffer)
