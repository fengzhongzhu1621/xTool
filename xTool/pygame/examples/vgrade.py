"""pg.examples.vgrade

垂直渐变示例 - 使用numpy和pygame surfarray模块创建和显示图像

这个示例演示了如何使用numpy创建图像并通过SDL显示。
你可以查看导入numpy和pg.surfarray的方法，如果不可用，
该方法会"优雅地"失败。

我尝试在代码可能不够自解释的地方添加了很多注释，
尽管如此，它可能看起来仍然有点奇怪。学习像这样使用numpy处理图像
需要一些学习，但回报是极快的图像处理速度。

对于Pygame 1.9.2及以上版本，这个示例还展示了surfarray.blit_surface的
一个新特性：数组广播。如果源数组的宽度或高度为1，
数组会沿着该维度重复blit到表面以填充表面。实际上，
一个(1, 1)或(1, 1, 3)的数组会导致简单的表面颜色填充。

时间分配说明：对于每个时间采样，30%用于创建渐变，
30%用于blit数组，最后的40%用于翻转/更新显示表面。

窗口将没有边框装饰。

代码还演示了定时器事件的使用。
"""

import os

import pygame as pg

# 尝试导入numpy库，如果不可用则优雅地退出
try:
    import numpy as np
    import numpy.random as np_random
except ImportError:
    raise SystemExit("这个示例需要numpy和pygame surfarray模块")

# 全局计时器变量
timer = 0


def stopwatch(message=None):
    """简单的计时器函数，用于测量Python代码执行时间

    参数:
        message: 如果为None，则重置计时器；否则打印计时结果
    """
    global timer
    if not message:
        # 重置计时器
        timer = pg.time.get_ticks()
        return
    # 计算运行时间并打印结果
    now = pg.time.get_ticks()
    runtime = (now - timer) / 1000.0 + 0.001  # 转换为秒，避免除零
    print(f"{message} {runtime} 秒\t{(1.0 / runtime):.2f}帧/秒")
    timer = now  # 重置计时器


def VertGradientColumn(surf, topcolor, bottomcolor):
    """创建一个新的3D垂直渐变数组

    参数:
        surf: pygame表面对象
        topcolor: 顶部颜色 (RGB三元组)
        bottomcolor: 底部颜色 (RGB三元组)

    返回:
        映射到表面的渐变数组
    """
    # 将颜色转换为numpy数组
    topcolor = np.array(topcolor, copy=False)
    bottomcolor = np.array(bottomcolor, copy=False)

    # 计算颜色差值
    diff = bottomcolor - topcolor

    # 获取表面尺寸
    width, height = surf.get_size()

    # 创建从0.0到1.0的三元组数组
    # 生成高度范围内的浮点数组，并归一化到[0,1]
    column = np.arange(height, dtype="float") / height
    # 将一维数组转换为二维数组，并重复3次（对应RGB三个通道）
    column = np.repeat(column[:, np.newaxis], [3], 1)

    # 创建单个渐变列
    # 根据渐变比例计算每个像素的颜色值
    column = topcolor + (diff * column).astype("int")

    # 通过添加X维度将列转换为3D图像列
    column = column.astype("uint8")[np.newaxis, :, :]

    # 将3D数组映射到2D表面数组
    return pg.surfarray.map_array(surf, column)


def DisplayGradient(surf):
    """选择随机颜色并显示渐变

    参数:
        surf: 要显示渐变的表面对象
    """
    # 开始计时
    stopwatch()

    # 生成两个随机RGB颜色 (2行3列，值范围0-255)
    colors = np_random.randint(0, 255, (2, 3))

    # 创建垂直渐变列
    column = VertGradientColumn(surf, colors[0], colors[1])

    # 将渐变数组blit到表面
    pg.surfarray.blit_array(surf, column)

    # 更新显示
    pg.display.flip()

    # 结束计时并打印结果
    stopwatch("渐变:")


def main():
    """主函数 - 初始化pygame并运行渐变显示循环"""
    # 初始化pygame
    pg.init()
    # 关闭混音器以避免ALSA下溢消息（针对Debian squeeze）
    pg.mixer.quit()

    # 设置窗口尺寸
    size = 600, 400
    # 设置环境变量使窗口居中显示
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    # 创建无边框窗口
    screen = pg.display.set_mode(size, pg.NOFRAME, 0)

    # 阻止鼠标移动事件，保持事件队列更清洁
    pg.event.set_blocked(pg.MOUSEMOTION)
    # 设置定时器事件，每500毫秒触发一次USEREVENT
    pg.time.set_timer(pg.USEREVENT, 500)

    # 主事件循环
    while True:
        # 等待事件
        event = pg.event.wait()

        # 检查退出条件：退出事件、按键事件、鼠标点击事件
        if event.type in (pg.QUIT, pg.KEYDOWN, pg.MOUSEBUTTONDOWN):
            break
        # 如果是定时器事件，显示渐变
        elif event.type == pg.USEREVENT:
            DisplayGradient(screen)

    # 退出pygame
    pg.quit()


if __name__ == "__main__":
    main()
