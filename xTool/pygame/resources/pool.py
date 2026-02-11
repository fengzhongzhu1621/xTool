import os

import pygame
from pygame.font import Font
from pygame.mixer import Sound
from pygame.surface import Surface

from xTool.pygame.image import load_all_image
from xTool.pygame.image import load_image as load_pygame_image
from xTool.pygame.sound import NoneSound, load_all_sound
from xTool.pygame.sound import load_sound as load_mixer_sound

__all__ = [
    "ResourcePool",
    "get_default_resource_pool",
    "set_colorkey",
    "load_image",
    "load_sound",
    "load_music",
    "play_music",
]


class ResourcePool:
    def __init__(self) -> None:
        self.colorkey: tuple[int, int, int] | None = None

        self.font_paths: dict[str, str] = {}
        self.music_paths: dict[str, str] = {}
        self.image_paths: dict[str, str] = {}
        self.sound_paths: dict[str, str] = {}

        self.fonts: dict[str, Font] = {}
        self.music: dict[str, Sound] = {}
        self.images: dict[str, Surface] = {}
        self.sounds: dict[str, Sound | NoneSound] = {}

    def update_font_paths(self, paths: dict[str, str]) -> None:
        self.font_paths.update(paths)

    def update_music_paths(self, paths: dict[str, str]) -> None:
        self.music_paths.update(paths)

    def update_image_paths(self, paths: dict[str, str]) -> None:
        self.image_paths.update(paths)

    def update_sound_paths(self, paths: dict[str, str]) -> None:
        self.sound_paths.update(paths)

    def load_sound(self, file_path: str) -> Sound | NoneSound:
        name = os.path.basename(file_path)
        if name in self.sounds:
            return self.sounds[name]

        sound = load_mixer_sound(file_path)
        self.sounds[name] = sound
        self.sound_paths[name] = file_path
        return sound

    def load_sounds(self, resource_dir: str, exts: list[str] | None = None) -> None:
        """加载所有音效资源"""
        if exts is None:
            allowed_exts: list[str] = ['.wav', '.mpe', '.ogg', '.mdi']
        else:
            allowed_exts = exts
        self.sounds.update(load_all_sound(resource_dir, allowed_exts))

    def get_sound(self, name: str) -> Sound | NoneSound:
        if name in self.sounds:
            return self.sounds[name]

        if name in self.sound_paths:
            return self.load_sound(self.sound_paths[name])

        return NoneSound()

    def set_colorkey(self, colorkey: tuple[int, int, int] | None) -> None:
        self.colorkey = colorkey

    def load_image(self, file_path: str) -> Surface:
        name = os.path.basename(file_path)
        if name in self.images:
            return self.images[name]

        img = load_pygame_image(file_path, self.colorkey)
        self.images[name] = img
        self.image_paths[name] = file_path
        return img

    def load_images(self, resource_dir: str, exts: list[str] | None = None) -> None:
        """加载所有图形资源"""
        if exts is None:
            allowed_exts: list[str] = ['.png', '.jpg', '.bmp']
        else:
            allowed_exts = exts
        self.images.update(load_all_image(resource_dir, self.colorkey, allowed_exts))

    def get_image(self, name: str) -> Surface:
        if name in self.images:
            return self.images[name]

        if name in self.image_paths:
            return self.load_image(self.image_paths[name])

        raise KeyError(f'图像资源 "{name}" 不存在')

    def load_music(self, name: str):
        if name in self.music_paths:
            music_path = self.music_paths[name]
            pygame.mixer.music.load(music_path)

    def play_music(self, name: str) -> None:
        self.load_music(name)
        pygame.mixer.music.play()


def create_default_resource_pool() -> ResourcePool:
    return ResourcePool()


default_resource_pool = create_default_resource_pool()


def get_default_resource_pool() -> ResourcePool:
    return default_resource_pool


def set_colorkey(colorkey: tuple[int, int, int] | None) -> None:
    default_resource_pool.set_colorkey(colorkey)


def load_image(name: str) -> Surface:
    return default_resource_pool.get_image(name)


def load_sound(name: str) -> Sound | NoneSound:
    return default_resource_pool.get_sound(name)


def load_music(name: str) -> None:
    default_resource_pool.load_music(name)


def play_music(name: str) -> None:
    default_resource_pool.play_music(name)
