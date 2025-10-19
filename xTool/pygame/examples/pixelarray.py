"""pygame.examples.pixelarray

PixelArray用于像素的数组处理。
类似于另一个数组处理器'numpy' - 但专门用于像素。

    翻转它，
            条纹化它，
                      旋转它。

控制方式
--------

要查看不同的效果 - 按任意键或点击鼠标。
"""

import os

import pygame as pg

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")


def show(image):
    """
    显示图像并等待用户交互

    此函数将图像显示在屏幕上，然后等待用户按下任意键或点击鼠标
    用于在演示不同效果时暂停程序

    参数:
    image - 要显示的图像表面
    """
    screen = pg.display.get_surface()  # 获取显示表面
    screen.fill((255, 255, 255))  # 用白色填充背景
    screen.blit(image, (0, 0))  # 在(0,0)位置绘制图像

    pg.display.flip()  # 更新屏幕显示

    # 等待用户交互
    while True:
        event = pg.event.wait()  # 等待事件
        if event.type == pg.QUIT:  # 如果点击关闭按钮
            pg.quit()
            raise SystemExit  # 退出程序
        if event.type in [pg.MOUSEBUTTONDOWN, pg.KEYDOWN]:  # 如果按下鼠标或键盘
            break  # 继续下一个效果


def main():
    """
    主函数 - 演示PixelArray的各种操作

    这个函数展示了PixelArray的多种用法：
    1. 创建渐变效果
    2. 图像翻转
    3. 条纹效果
    4. 旋转操作
    5. 缩放处理
    6. 颜色替换
    7. 颜色提取
    8. 图像比较
    """
    pg.init()  # 初始化Pygame

    # 创建255x255像素的显示窗口和表面
    pg.display.set_mode((255, 255))
    surface = pg.Surface((255, 255))

    pg.display.flip()  # 更新显示

    # 演示1: 创建渐变效果
    # 创建PixelArray对象
    ar = pg.PixelArray(surface)

    # 创建简单的灰度渐变效果
    # 从黑色(0,0,0)渐变到白色(255,255,255)
    for y in range(255):
        r, g, b = y, y, y  # RGB值相同，创建灰度
        ar[:, y] = (r, g, b)  # 设置整列像素的颜色  # pyright: ignore[reportIndexIssue]
    del ar  # 删除PixelArray对象以解锁表面
    show(surface)  # 显示渐变效果

    # 演示2: 垂直翻转渐变
    # 我们创建了渐变效果，现在垂直翻转它
    ar = pg.PixelArray(surface)
    ar[:] = ar[:, ::-1]  # 使用切片[::-1]实现垂直翻转  # pyright: ignore[reportIndexIssue]
    del ar
    show(surface)

    # 演示3: 创建蓝色条纹效果
    # 每隔一列设置为蓝色
    ar = pg.PixelArray(surface)
    ar[::2] = (0, 0, 255)  # [::2]选择每隔一列，设置为蓝色  # pyright: ignore[reportIndexIssue]
    del ar
    show(surface)

    # 演示4: 创建绿色条纹效果
    # 每隔一行设置为绿色
    ar = pg.PixelArray(surface)
    ar[:, ::2] = (0, 255, 0)  # [:, ::2]选择每隔一行，设置为绿色  # pyright: ignore[reportIndexIssue]
    del ar
    show(surface)

    # 演示5: 加载图像并垂直翻转
    # 操作真实图像，围绕Y轴翻转
    surface = pg.image.load(os.path.join(data_dir, "arraydemo.bmp"))
    ar = pg.PixelArray(surface)
    ar[:] = ar[:, ::-1]  # 垂直翻转图像  # pyright: ignore[reportIndexIssue]
    del ar
    show(surface)

    # 演示6: 水平翻转图像
    # 围绕X轴翻转图像
    ar = pg.PixelArray(surface)
    ar[:] = ar[::-1, :]  # [::-1, :]实现水平翻转  # pyright: ignore[reportIndexIssue]
    del ar
    show(surface)

    # 演示7: 创建白色条纹效果
    # 每隔一列设置为白色
    ar = pg.PixelArray(surface)
    ar[::2] = (255, 255, 255)  # 白色条纹  # pyright: ignore[reportIndexIssue]
    del ar
    show(surface)

    # 演示8: 同时翻转两个轴，恢复原始布局
    # 因为之前翻转了两次，再次翻转两个轴会恢复原状
    ar = pg.PixelArray(surface)
    ar[:] = ar[::-1, ::-1]  # 同时水平和垂直翻转  # pyright: ignore[reportIndexIssue]
    del ar
    show(surface)

    # 演示9: 顺时针旋转90度
    # 使用转置和翻转实现90度旋转
    w, h = surface.get_size()  # 获取原始图像的宽度和高度
    # 创建新的表面，尺寸为(h, w) - 交换宽高
    surface2 = pg.Surface((h, w), surface.get_flags(), surface)
    ar = pg.PixelArray(surface)
    ar2 = pg.PixelArray(surface2)
    # 转置后水平翻转实现90度顺时针旋转
    ar2[...] = ar.transpose()[::-1, :]  # pyright: ignore[reportIndexIssue]
    del ar, ar2
    show(surface2)

    # 演示10: 通过丢弃每隔一个像素来缩放图像
    # 实现2倍缩小效果
    surface = pg.image.load(os.path.join(data_dir, "arraydemo.bmp"))
    ar = pg.PixelArray(surface)
    # [::2, ::2]选择每隔一个像素，创建缩放后的表面
    sf2 = ar[::2, ::2].make_surface()  # pyright: ignore[reportIndexIssue]
    del ar
    show(sf2)

    # 演示11: 颜色替换
    # 将文本中的蓝色替换为绿色
    ar = pg.PixelArray(surface)
    # replace()方法替换相似颜色，0.06是容差参数
    ar.replace((60, 60, 255), (0, 255, 0), 0.06)
    del ar
    show(surface)

    # 演示12: 颜色提取
    # 提取图像中可能是黑色的部分
    surface = pg.image.load(os.path.join(data_dir, "arraydemo.bmp"))
    ar = pg.PixelArray(surface)
    # extract()方法提取相似颜色，0.07是容差参数
    ar2 = ar.extract((0, 0, 0), 0.07)
    sf2 = ar2.surface  # 获取提取后的表面
    del ar, ar2
    show(sf2)

    # 演示13: 图像比较
    # 比较两个外星人图像的差异
    surface = pg.image.load(os.path.join(data_dir, "alien1.gif"))
    surface2 = pg.image.load(os.path.join(data_dir, "alien2.gif"))
    ar1 = pg.PixelArray(surface)
    ar2 = pg.PixelArray(surface2)
    # compare()方法比较两个图像的差异，0.07是容差参数
    ar3 = ar1.compare(ar2, 0.07)
    sf3 = ar3.surface  # 获取比较结果的表面
    del ar1, ar2, ar3
    show(sf3)


if __name__ == "__main__":
    main()  # 运行主函数
    pg.quit()  # 退出Pygame
