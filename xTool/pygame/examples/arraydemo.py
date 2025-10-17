"""pygame.examples.arraydemo

Welcome to the arraydemo!

Use the numpy array package to manipulate pixels.

This demo will show you a few things:

* scale up, scale down, flip,
* cross fade
* soften
* put stripes on it!

"""

import os

import pygame as pg
from pygame import surfarray

main_dir = os.path.split(os.path.abspath(__file__))[0]


def surfdemo_show(array_img, name):
    """displays a surface, waits for user to continue"""
    # 创建一个窗口，大小为数组的形状，深度为32位，显示 np.zeros((128, 128), int32) 颜色是黑色
    screen = pg.display.set_mode(array_img.shape[:2], 0, 32)
    surfarray.blit_array(screen, array_img)
    pg.display.flip()
    pg.display.set_caption(name)

    while True:
        e = pg.event.wait()
        # Force application to only advance when main button is released
        if e.type == pg.MOUSEBUTTONUP and e.button == pg.BUTTON_LEFT:
            break
        elif e.type == pg.KEYDOWN and e.key == pg.K_s:
            pg.image.save(screen, name + ".png")
        elif e.type == pg.QUIT:
            pg.quit()
            raise SystemExit()


def main():
    """show various surfarray effects"""
    import numpy as np
    from numpy import int32, uint

    pg.init()

    print("Using Numpy")
    print("Press the left mouse button to advance image.")
    print('Press the "s" key to save the current image.')

    # 创建一个全黑的窗口
    # allblack
    allblack = np.zeros((128, 128), int32)
    surfdemo_show(allblack, "allblack")

    # striped
    # the element type is required for np.zeros in numpy else
    # an array of float is returned.
    # 创建一个全零的三维数组，所有像素初始为黑色 [0, 0, 0]
    # (128, 128, 3)：数组形状（128高×128宽×3个颜色通道）
    striped = np.zeros((128, 128, 3), int32)
    # [:] 表示选择所有元素 (255, 0, 0) 是RGB颜色值（红色=255，绿色=0，蓝色=0） 整个图像变为纯红色
    striped[:] = (255, 0, 0)
    # 选择所有行(:)，每3列选择一列(::3)，即选择第0列、第3列、第6列...（从0开始，步长为3）(0, 255, 255) 是青色（红色=0，绿色=255，蓝色=255）
    # 第一个索引 : 表示选择所有行。
    # 第二个索引 ::3 表示在列方向上以步长 3 进行选择：
    # ::3 等价于 0:128:3，即从第 0 列开始，每隔 3 列取一列（索引为 0, 3, 6, 9, ... 的列）
    striped[:, ::3] = (0, 255, 255)
    # 在红色背景上创建间隔的青色横条纹
    surfdemo_show(striped, "striped")

    # rgbarray
    imagename = os.path.join(main_dir, "data", "arraydemo.bmp")
    imgsurface = pg.image.load(imagename)
    rgbarray = surfarray.array3d(imgsurface)
    surfdemo_show(rgbarray, "rgbarray")

    # flipped 相当于将图像进行水平镜像翻转
    # : 表示选择所有行（保持高度不变）
    # ::-1 表示在宽度维度上进行反转
    flipped = rgbarray[:, ::-1]
    surfdemo_show(flipped, "flipped")

    # scaledown 图像尺寸缩小为原来的1/4（高度和宽度都减半）
    # [::2, ::2] 是NumPy的切片操作：
    # ::2 在高度维度：从第0行开始，每隔1行取1行（步长为2）
    # ::2 在宽度维度：从第0列开始，每隔1列取1列（步长为2）
    scaledown = rgbarray[::2, ::2]
    surfdemo_show(scaledown, "scaledown")

    # scaleup
    # 获取原始图像的尺寸信息（高度、宽度、通道数）
    shape = rgbarray.shape
    # 创建一个新的全零数组，尺寸是原始图像的2倍（高度×2，宽度×2）
    # 例如：原始图像100×100 → 新图像200×200
    scaleup = np.zeros((shape[0] * 2, shape[1] * 2, shape[2]), int32)
    # 将原始图像的像素复制到放大图像的偶数行、偶数列位置
    # 相当于在放大图像的网格中，每个2×2块的左上角放置原始像素
    scaleup[::2, ::2, :] = rgbarray
    # 将原始图像的像素复制到放大图像的奇数行、偶数列位置
    # 相当于在2×2块的左下角也放置相同的原始像素
    scaleup[1::2, ::2, :] = rgbarray
    # 将偶数列的像素值复制到奇数列
    # 完成水平方向的像素复制，使图像在宽度方向上也连续
    scaleup[:, 1::2] = scaleup[:, ::2]
    surfdemo_show(scaleup, "scaleup")

    # redimg
    redimg = np.array(rgbarray)
    # 前两个 : 表示选择所有行和所有列（整个图像）
    # 1: 表示从第1个颜色通道开始到末尾（Python索引从0开始）
    # 颜色通道索引：0=红色(R)，1=绿色(G)，2=蓝色(B)
    # 1: 对应绿色和蓝色通道（索引1和2）
    # = 0 将绿色和蓝色通道的值全部设为0
    # 最终效果：
    # 保留红色通道不变
    # 将绿色和蓝色通道清零
    # 结果是图像中只显示红色成分，其他颜色都被移除
    # 原本彩色的图像会变成不同深浅的红色调图像
    redimg[:, :, 1:] = 0
    surfdemo_show(redimg, "redimg")

    # soften
    # 这是一个简化的均值滤波或模糊滤波，每个像素的新值计算为
    # 新像素 = (中心像素 + 8×上方像素 + 8×下方像素 + 8×左侧像素 + 8×右侧像素) / 33
    # having factor as an array forces integer upgrade during multiplication
    # of rgbarray, even for numpy.
    # 创建权重因子数组，值为8，用于控制相邻像素的贡献程度
    factor = np.array((8,), int32)
    # 创建原始图像的副本，转换为int32类型以容纳更大的数值
    soften = np.array(rgbarray, int32)
    # 四个方向的邻域像素加权累加
    soften[1:, :] += rgbarray[:-1, :] * factor  # 上方像素的贡献
    soften[:-1, :] += rgbarray[1:, :] * factor  # 下方像素的贡献
    soften[:, 1:] += rgbarray[:, :-1] * factor  # 左侧像素的贡献
    soften[:, :-1] += rgbarray[:, 1:] * factor  # 右侧像素的贡献
    # 对累加结果进行归一化（整除33）
    # 33 = 1(中心像素) + 8×4(四个方向的权重)
    # 通过将每个像素与其四个相邻像素进行加权平均
    # 产生柔化（模糊）效果，减少图像的锐利边缘
    soften //= 33
    surfdemo_show(soften, "soften")

    # crossfade (50%)
    # 创建原始图像的副本作为源图像
    src = np.array(rgbarray)
    # 创建与源图像相同尺寸的全零数组作为目标图像
    dest = np.zeros(rgbarray.shape)  # dest is float64 by default.
    # 将目标图像填充为统一的RGB颜色 (20, 50, 100)
    # 这是一个深蓝绿色调，作为淡入效果的目标颜色
    dest[:] = 20, 50, 100
    # 计算源图像和目标图像之间的差异
    # 乘以0.50表示进行50%的淡入淡出
    # 结果：每个像素取源图像和目标图像差异的一半
    diff = (dest - src) * 0.50
    # 将差异值加到源图像上，完成交叉淡入淡出
    # .astype(uint) 将浮点数转换回无符号整数类型（像素值范围0-255）
    xfade = src + diff.astype(uint)
    surfdemo_show(xfade, "xfade")

    # all done
    pg.quit()


if __name__ == "__main__":
    main()
