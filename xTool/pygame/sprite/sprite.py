import pygame
from pygame import Rect, Surface

from xTool.pygame import image


class Sprite(pygame.sprite.Sprite):

    def __init__(self, *groups) -> None:
        super().__init__(*groups)

        # 基类变量
        self.image: Surface
        self.rect: Rect

        self.original_image: Surface
        self.images: list[Surface] = []

        # 获取当前显示表面（游戏窗口）
        self.screen: Surface = self.get_screen()
        # 保存屏幕的矩形区域，用于边界检测
        self.screen_rect: Rect = self.screen.get_rect()

        # 初始速度
        self.speed: int = 0
        # 初始旋转角度
        self.spin_angle: int = 0
        self.facing: int = -1  # 面向方向（-1左，1右）

    def get_rect(self) -> Rect:
        return self.rect

    def get_image(self) -> Surface:
        return self.image

    def get_screen(self) -> Surface:
        """获取当前显示表面（游戏窗口）"""
        return pygame.display.get_surface()

    def load_image(self, file_path: str, colorkey=None, scale: int = 1) -> Surface:
        return image.load_image(file_path, colorkey=colorkey, scale=scale)

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

    def get_rect_center(self, actor: Rect | tuple[int, int]) -> Rect:
        """将玩家放置在屏幕中央"""
        if isinstance(actor, Rect):
            center = actor.center
        else:
            center = actor
        return self.image.get_rect(center=center)

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

    def move_with_mouse(self) -> Rect:
        """跟随鼠标移动"""
        # 返回鼠标当前的(x, y)坐标
        pos = pygame.mouse.get_pos()
        # 设置拳头位置：将拳头的矩形区域左上角对齐到鼠标位置
        self.rect.topleft = pos
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

    def walk_horizontal(self) -> None:
        """先移动，再转向"""
        # 移动到新的位置
        newpos = self.rect.move((self.speed, 0))
        # 检查新位置是否超出屏幕边界
        if not self.screen_rect.contains(newpos):
            # 如果超出屏幕边界，则反转移动方向，并重新计算新位置
            if self.rect.left < self.screen_rect.left or self.rect.right > self.screen_rect.right:
                self.speed = -self.speed  # 反转移动方向
                newpos = self.rect.move((self.speed, 0))  # 重新计算新位置
                self.image = pygame.transform.flip(self.image, True, False)  # 水平翻转图像

        # 更新矩形位置
        self.rect = newpos

    def set_walk_speed(self, speed: int) -> None:
        self.speed = speed

    def spin(self, offset: int, max_angle: int = 0) -> bool:
        """旋转"""
        stop = False
        # 增加旋转角度
        self.spin_angle = self.spin_angle + offset
        if self.spin_angle >= 360:  # 如果完成一圈旋转
            if max_angle > 0 and self.spin_angle >= max_angle:
                # 标记停止选择
                stop = True
            self.spin_angle = 0  # 重置选择角度
            # 恢复原始图像
            self.image = self.original_image
        else:
            # 旋转原始图像
            self.image = pygame.transform.rotate(self.original_image, self.spin_angle)

        # 保持中心点不变
        center = self.rect.center
        self.rect = self.get_rect_center(center)

        return stop

    def in_screen(self, screen_rect: Rect) -> bool:
        """判断是否在屏幕内，是否碰到屏幕边缘"""
        return screen_rect.contains(self.rect)

    def move_next_line(self, screen_rect: Rect) -> Rect:
        """下一一行"""
        self.rect.top = self.rect.bottom + 1  # 下移一行
        self.rect = self.rect.clamp(screen_rect)  # 确保在屏幕内
        return self.rect

    def simple_colliderect(self, target) -> bool:
        """简单的碰撞检测"""
        # 创建稍小的碰撞检测框
        hitbox = self.rect.inflate(-5, -5)
        # 检查是否与目标矩形相交
        return hitbox.colliderect(target.rect)
