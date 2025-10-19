"""pygame.examples.headless_no_windows_needed

如何在无窗口系统（如无头服务器）中使用pygame。

图像缩放生成缩略图是pygame可以完成的一个示例。
注意：pygame缩放函数如果可用会使用mmx/sse指令集，并且可以在多线程中运行。
"""

import os
import sys

import pygame as pg

usage = """-scale inputimage outputimage new_width new_height
eg.  -scale in.png out.png 50 50

使用说明：
-scale 输入图像 输出图像 新宽度 新高度
示例：-scale in.png out.png 50 50

"""

# 设置SDL使用虚拟NULL视频驱动，这样就不需要窗口系统了
os.environ["SDL_VIDEODRIVER"] = "dummy"


# 某些平台需要初始化显示才能使用pygame的部分功能
pg.display.init()
# 创建一个最小尺寸的显示表面（1x1像素），虽然我们不需要显示窗口
screen = pg.display.set_mode((1, 1))


def scaleit(fin, fout, w, h):
    """缩放图像并保存

    Args:
        fin: 输入图像文件路径
        fout: 输出图像文件路径
        w: 新宽度
        h: 新高度
    """
    # 加载输入图像
    i = pg.image.load(fin)

    # 检查是否支持平滑缩放（smoothscale），如果支持则使用平滑缩放
    if hasattr(pg.transform, "smoothscale"):
        scaled_image = pg.transform.smoothscale(i, (w, h))
    else:
        # 如果不支持平滑缩放，使用普通缩放
        scaled_image = pg.transform.scale(i, (w, h))

    # 保存缩放后的图像
    pg.image.save(scaled_image, fout)


def main(fin, fout, w, h):
    """将名为fin的图像文件平滑缩放到新尺寸(w,h)并保存为fout"""
    scaleit(fin, fout, w, h)


if __name__ == "__main__":
    # 检查命令行参数是否包含-scale选项
    if "-scale" in sys.argv:
        # 从命令行参数中提取输入文件、输出文件、宽度和高度
        fin, fout, w, h = sys.argv[2:]
        # 将宽度和高度转换为整数
        w, h = map(int, [w, h])
        # 执行缩放操作
        main(fin, fout, w, h)
    else:
        # 如果没有正确的参数，显示使用说明
        print(usage)
