import pygame
from pygame.surface import Surface


def load_image(file_path: str) -> Surface:
    """
    加载图像并准备用于游戏

    参数:
        file_path: 图像文件路径

    返回:
        Surface: 转换后的图像表面

    说明:
        使用convert()函数将图像转换为与显示格式兼容的Surface，这样可以显著提高绘制性能。
        convert()会将图像转换为与显示表面相同的像素格式，避免每次绘制时的格式转换开销。
    """
    try:
        surface: Surface = pygame.image.load(file_path)  # 加载图像文件
    except pygame.error:
        raise SystemExit(f'无法加载图像 "{file_path}" {pygame.get_error()}')

    # 转换为显示格式以提高性能
    return surface.convert()
