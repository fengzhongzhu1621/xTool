import pygame
from pygame import Rect, Surface

from xTool.pygame import image


class Sprite(pygame.sprite.Sprite):

    def __init__(self, *groups) -> None:
        super().__init__(*groups)

        # 基类变量
        self.image: Surface
        self.rect: Rect

        self.images: list[Surface] = []

        self.facing: int = -1  # 面向方向（-1左，1右）

    def get_rect(self) -> Rect:
        return self.rect

    def get_image(self) -> Surface:
        return self.image

    def load_images(self, file_paths: list[str]) -> list[Surface]:
        """加载多个图像"""
        return [image.load_image(file_path) for file_path in file_paths]

    def load_flipx_images(self, file_path: str) -> list[Surface]:
        """加载水平翻转图像"""
        img = image.load_image(file_path)
        return [img, pygame.transform.flip(img, 1, 0)]  # 玩家左右图像

    def load_flipxy_iamges(self, file_path: str) -> list[Surface]:
        """同时进行水平和垂直翻转，相当于180度旋转"""
        img = image.load_image(file_path)
        return [img, pygame.transform.flip(img, 1, 1)]

    def get_rect_midbottom(self, actor: Rect | tuple[int, int]) -> Rect:
        """将玩家放置在屏幕底部中央"""
        if isinstance(actor, Rect):
            midbottom = actor.midbottom
        else:
            midbottom = actor
        return self.image.get_rect(midbottom=midbottom)

    def get_rect_center(self, actor: Rect) -> Rect:
        """将玩家放置在屏幕中央"""
        return self.image.get_rect(center=actor.center)

    def move_up(self, speed: int) -> Rect:
        """向上移动"""
        speed = -speed if speed > 0 else speed
        self.rect.move_ip(0, speed)
        if self.rect.top <= 0:
            self.kill()
        return self.rect

    def move_down(self, speed: int) -> Rect:
        """向下移动"""
        speed = -speed if speed < 0 else speed
        self.rect.move_ip(0, speed)
        return self.rect

    def move_horizontal(
        self,
        direction: int,
        origtop: int,  # 原始顶部位置
        screen_rect: Rect | None,
        speed: int = 10,  # 移动速度
        bounce: int = 24,  # 弹跳效果
    ) -> Rect:
        """水平移动，支持弹跳"""
        if direction:
            self.facing = direction  # 更新面向方向

        # 根据方向移动玩家
        self.rect.move_ip(direction * speed, 0)
        # 确保玩家不会移出屏幕
        if screen_rect:
            self.rect = self.rect.clamp(screen_rect)

        # 根据移动方向切换图像（左右镜像）
        if direction < 0:
            self.image = self.images[0]  # 向左的图像
        elif direction > 0:
            self.image = self.images[1]  # 向右的图像

        # 添加弹跳效果
        self.rect.top = origtop - (self.rect.left // bounce % 2)

        return self.rect

    def in_screen(self, screen_rect: Rect) -> bool:
        """判断是否在屏幕内，是否碰到屏幕边缘"""
        return screen_rect.contains(self.rect)

    def move_next_line(self, screen_rect: Rect) -> Rect:
        """下一一行"""
        self.rect.top = self.rect.bottom + 1  # 下移一行
        self.rect = self.rect.clamp(screen_rect)  # 确保在屏幕内
        return self.rect
