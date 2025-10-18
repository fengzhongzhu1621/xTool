import pygame
from pygame.rect import Rect
from pygame.surface import Surface

from xTool.pygame import image, sound


class DisplayWindow:
    def __init__(self, rect: pygame.Rect, winstyle: int = 0, depth: int = 32):
        self.rect: Rect = rect
        self.winstyle: int = winstyle
        self.depth: int = depth
        self.bestdepth: int = 0

        self.fullscreen: bool = False  # 全屏状态
        self.screen: Surface = self.set_model()
        self.background: Surface = pygame.Surface(self.screen.get_size())

    def set_model(self, size: pygame.Rect | None = None, flags: int | None = None, depth: int | None = None) -> Surface:
        if size is not None:
            self.rect = size
        if flags is not None:
            self.winstyle = flags
        if depth is not None:
            self.depth = depth

        self.bestdepth = pygame.display.mode_ok(self.rect.size, self.winstyle, self.depth)  # 获取最佳颜色深度
        screen_surface = pygame.display.set_mode(self.rect.size, self.winstyle, self.bestdepth)  # 创建显示窗口

        return screen_surface

    def switch_screen(self) -> Surface:
        if not self.fullscreen:
            self.screen = self.change_to_fullscreen()
        else:
            self.screen = self.change_to_winscreen()

        return self.screen

    def change_to_fullscreen(self) -> Surface:
        """切换到全屏模式"""
        if self.fullscreen:
            return self.screen

        screen_backup = self.screen.copy()
        self.winstyle = self.winstyle | pygame.FULLSCREEN

        screen = pygame.display.set_mode(self.rect.size, self.winstyle, self.bestdepth)
        _ = screen.blit(screen_backup, (0, 0))

        # 更新显示
        pygame.display.flip()

        self.fullscreen = not self.fullscreen
        self.screen = screen
        return self.screen

    def change_to_winscreen(self) -> Surface:
        """切换到窗口模式"""
        if not self.fullscreen:
            return self.screen

        screen_backup = self.screen.copy()
        self.winstyle = self.winstyle & ~pygame.FULLSCREEN

        screen = pygame.display.set_mode(self.rect.size, self.winstyle, self.bestdepth)
        _ = screen.blit(screen_backup, (0, 0))

        # 更新显示
        pygame.display.flip()

        self.fullscreen = not self.fullscreen
        self.screen = screen
        return self.screen

    def get_screen(self) -> Surface:
        return self.screen

    def get_screen_width(self) -> int:
        return self.screen.get_width()

    def get_screen_height(self) -> int:
        return self.screen.get_height()

    def fill_color(self, color, rect=None) -> Surface:
        _ = self.screen.fill(color, rect)
        return self.screen

    def draw_circle(self, color, center, radius: float) -> Rect:
        """绘制圆形 ."""
        return pygame.draw.circle(self.screen, color, center, radius)

    def draw_rect(self, color, rect) -> Rect:
        return pygame.draw.rect(self.screen, color, rect)

    def set_icon(self, surface: Surface, size: tuple[int, int]) -> None:
        """设置窗口图标"""
        icon = pygame.transform.scale(surface, size)
        pygame.display.set_icon(icon)

    def set_caption(self, title: str) -> None:
        """设置窗口标题"""
        pygame.display.set_caption(title)

    def hide_mouse(self) -> None:
        """隐藏鼠标光标"""
        _ = pygame.mouse.set_visible(0)

    def blit_background(self, file_path: str) -> Surface:
        # 加载背景图片
        bgdtile = image.load_image(file_path)
        # 创建背景表面
        background = pygame.Surface(self.rect.size)
        # 平铺背景图像
        for x in range(0, self.rect.width, bgdtile.get_width()):
            _ = background.blit(bgdtile, (x, 0))

        # 绘制背景到屏幕
        _ = self.screen.blit(background, (0, 0))

        self.background = background
        return background

    def blit_background_color(self, color) -> Surface:
        # 创建与屏幕相同尺寸的表面
        background: Surface = pygame.Surface(self.screen.get_size())
        # 转换为显示格式
        background = background.convert()
        # 填充背景色
        _ = background.fill(color)

        # 绘制背景到屏幕
        _ = self.screen.blit(background, (0, 0))

        self.background = background
        return background

    def play_background_sound(self, file_path: str) -> None:
        """播放背景音乐"""
        sound.play_background_sound(file_path)

    def blit(self, source: Surface, dest) -> Rect:
        """绘制到屏幕"""
        return self.screen.blit(source, dest)

    def flip(self) -> None:
        """更新显示"""
        pygame.display.flip()
