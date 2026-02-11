import pygame
from pygame.surface import Surface

from xTool.file import filter_directory_files


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
    # 检查pygame.display是否已初始化
    if not pygame.display.get_init():
        raise SystemExit('错误：请先初始化pygame.display（调用pygame.display.set_mode()）')

    # 从文件加载图片
    try:
        img: Surface = pygame.image.load(file_path)  # 加载图像文件
    except pygame.error:
        raise SystemExit(f'无法加载图像 "{file_path}" {pygame.get_error()}')

    if img.get_alpha():
        img = img.convert_alpha()
    else:
        # 转换为显示格式以提高性能
        img = img.convert()

        # 设置透明色
        if colorkey is not None:  # 检查是否设置了透明色
            if colorkey == -1:  # 如果透明色值为-1（特殊值）
                # 获取图像左上角(0,0)像素的颜色作为透明色
                colorkey = img.get_at((0, 0))
            # 设置透明色并启用RLE加速
            img.set_colorkey(colorkey, pygame.RLEACCEL)

    # 使用transform.scale()函数将图像缩放到指定大小，以提高性能。
    if scale != 1:
        size = img.get_size()
        size = (size[0] * scale, size[1] * scale)
        img = pygame.transform.scale(img, size)

    return img


def load_all_image(directory: str, colorkey: tuple[int, int, int] | None, exts: list[str]) -> dict[str, Surface]:
    graphics: dict[str, Surface] = {}
    for name, path in filter_directory_files(directory, exts=exts).items():
        img = pygame.image.load(path)
        if img.get_alpha():
            img = img.convert_alpha()
        else:
            img = img.convert()
            img.set_colorkey(colorkey, pygame.RLEACCEL)

        graphics[name] = img

    return graphics
