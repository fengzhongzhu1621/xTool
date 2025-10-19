import pygame


def scaleit(fin: str, fout: str, w: int, h: int) -> None:
    """缩放图像并保存

    Args:
        fin: 输入图像文件路径
        fout: 输出图像文件路径
        w: 新宽度
        h: 新高度
    """
    # 加载输入图像
    i = pygame.image.load(fin)

    # 检查是否支持平滑缩放（smoothscale），如果支持则使用平滑缩放
    if hasattr(pygame.transform, "smoothscale"):
        scaled_image = pygame.transform.smoothscale(i, (w, h))
    else:
        # 如果不支持平滑缩放，使用普通缩放
        scaled_image = pygame.transform.scale(i, (w, h))

    # 保存缩放后的图像
    pygame.image.save(scaled_image, fout)
