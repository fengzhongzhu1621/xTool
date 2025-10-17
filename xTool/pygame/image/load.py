import pygame
from pygame.surface import Surface


def load_image(file_path: str, colorkey=None, scale: int = 1) -> Surface:
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
    # 从文件加载图片
    try:
        surface: Surface = pygame.image.load(file_path)  # 加载图像文件
    except pygame.error:
        raise SystemExit(f'无法加载图像 "{file_path}" {pygame.get_error()}')

    # 转换为显示格式以提高性能
    surface = surface.convert()

    # 使用transform.scale()函数将图像缩放到指定大小，以提高性能。
    if scale != 1:
        size = surface.get_size()
        size = (size[0] * scale, size[1] * scale)
        surface = pygame.transform.scale(surface, size)

    # 设置透明色
    if colorkey is not None:  # 检查是否设置了透明色
        if colorkey == -1:  # 如果透明色值为-1（特殊值）
            # 获取图像左上角(0,0)像素的颜色作为透明色
            colorkey = surface.get_at((0, 0))
        # 设置透明色并启用RLE加速
        surface.set_colorkey(colorkey, pygame.RLEACCEL)

    return surface
