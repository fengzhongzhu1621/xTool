import pygame
from pygame.mixer import Sound

from xTool.file import filter_directory_files


class NoneSound:
    def play(self) -> None:
        pass


def load_sound(file_path: str) -> Sound | NoneSound:
    """加载音效（因为pygame可能在没有mixer的情况下编译）"""
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()

    try:
        sound: Sound = pygame.mixer.Sound(file_path)  # 加载音效
        return sound
    except pygame.error:
        print(f"警告，无法加载 {file_path}")

    return NoneSound()


def load_all_sound(directory: str, exts: list[str]) -> dict[str, Sound]:  # pyright: ignore[reportRedeclaration]
    return {name: pygame.mixer.Sound(path) for name, path in filter_directory_files(directory, exts=exts).items()}
