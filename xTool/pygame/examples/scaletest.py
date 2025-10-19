"""pygame.examples.scaletest

显示一个交互式图像缩放器。

"""

import sys
import time

import pygame as pg


def main(imagefile, convert_alpha=False, run_speed_test=False):
    """显示一个交互式图像缩放器

    参数:
        imagefile - 源图像文件名（必需）
        convert_alpha - 在表面上使用convert_alpha()（默认False）
        run_speed_test - 运行速度测试（默认False）
    """

    # 初始化显示
    pg.display.init()
    # 加载背景图像
    background = pg.image.load(imagefile)

    if run_speed_test:  # 如果运行速度测试模式
        if convert_alpha:
            # convert_alpha()需要设置显示模式
            pg.display.set_mode((1, 1))
            background = background.convert_alpha()

        SpeedTest(background)  # 运行速度测试
        return

    # 启动全屏模式
    screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN)
    if convert_alpha:
        background = background.convert_alpha()

    # 关闭鼠标指针
    pg.mouse.set_visible(0)
    # 主循环
    bRunning = True  # 程序运行标志
    bUp = False  # 上方向键按下状态
    bDown = False  # 下方向键按下状态
    bLeft = False  # 左方向键按下状态
    bRight = False  # 右方向键按下状态
    cursize = [background.get_width(), background.get_height()]  # 当前图像尺寸

    while bRunning:
        # 使用平滑缩放将图像缩放到当前尺寸
        image = pg.transform.smoothscale(background, cursize)
        # 计算图像位置（屏幕中心）
        imgpos = image.get_rect(centerx=512, centery=384)
        screen.fill((255, 255, 255))  # 用白色填充背景
        screen.blit(image, imgpos)  # 绘制图像
        pg.display.flip()  # 更新显示

        # 处理事件
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                bRunning = False  # 退出程序
            if event.type == pg.KEYDOWN:  # 按键按下事件
                if event.key == pg.K_UP:
                    bUp = True
                if event.key == pg.K_DOWN:
                    bDown = True
                if event.key == pg.K_LEFT:
                    bLeft = True
                if event.key == pg.K_RIGHT:
                    bRight = True
            if event.type == pg.KEYUP:  # 按键释放事件
                if event.key == pg.K_UP:
                    bUp = False
                if event.key == pg.K_DOWN:
                    bDown = False
                if event.key == pg.K_LEFT:
                    bLeft = False
                if event.key == pg.K_RIGHT:
                    bRight = False

        # 根据按键状态调整图像尺寸
        if bUp:  # 上键：减小高度
            cursize[1] -= 2
            if cursize[1] < 1:  # 确保高度不小于1
                cursize[1] = 1
        if bDown:  # 下键：增加高度
            cursize[1] += 2
        if bLeft:  # 左键：减小宽度
            cursize[0] -= 2
            if cursize[0] < 1:  # 确保宽度不小于1
                cursize[0] = 1
        if bRight:  # 右键：增加宽度
            cursize[0] += 2

    pg.quit()  # 退出Pygame


def SpeedTest(image):
    """图像缩放速度测试函数

    参数:
    image - 要测试的图像
    """
    print(f"\n图像缩放速度测试 - 图像尺寸 {str(image.get_size())}\n")

    imgsize = [image.get_width(), image.get_height()]  # 获取图像原始尺寸

    # 测试平滑缩放的缩小操作
    duration = 0.0
    for i in range(128):
        shrinkx = (imgsize[0] * i) // 128  # 计算缩小后的宽度
        shrinky = (imgsize[1] * i) // 128  # 计算缩小后的高度
        start = time.time()
        tempimg = pg.transform.smoothscale(image, (shrinkx, shrinky))  # 平滑缩放
        duration += time.time() - start  # 累计耗时
        del tempimg  # 释放临时图像

    print(f"平滑缩放缩小平均时间: {duration / 128 * 1000:.4f} 毫秒.")

    # 测试平滑缩放的放大操作
    duration = 0.0
    for i in range(128):
        expandx = (imgsize[0] * (i + 129)) // 128  # 计算放大后的宽度
        expandy = (imgsize[1] * (i + 129)) // 128  # 计算放大后的高度
        start = time.time()
        tempimg = pg.transform.smoothscale(image, (expandx, expandy))  # 平滑缩放
        duration += time.time() - start  # 累计耗时
        del tempimg  # 释放临时图像

    print(f"平滑缩放放大平均时间: {duration / 128 * 1000:.4f} 毫秒.")

    # 测试普通缩放的缩小操作
    duration = 0.0
    for i in range(128):
        shrinkx = (imgsize[0] * i) // 128  # 计算缩小后的宽度
        shrinky = (imgsize[1] * i) // 128  # 计算缩小后的高度
        start = time.time()
        tempimg = pg.transform.scale(image, (shrinkx, shrinky))  # 普通缩放
        duration += time.time() - start  # 累计耗时
        del tempimg  # 释放临时图像

    print(f"普通缩放缩小平均时间: {duration / 128 * 1000:.4f} 毫秒.")

    # 测试普通缩放的放大操作
    duration = 0.0
    for i in range(128):
        expandx = (imgsize[0] * (i + 129)) // 128  # 计算放大后的宽度
        expandy = (imgsize[1] * (i + 129)) // 128  # 计算放大后的高度
        start = time.time()
        tempimg = pg.transform.scale(image, (expandx, expandy))  # 普通缩放
        duration += time.time() - start  # 累计耗时
        del tempimg  # 释放临时图像

    print(f"普通缩放放大平均时间: {duration / 128 * 1000:.4f} 毫秒.")


if __name__ == "__main__":
    # 检查输入参数
    if len(sys.argv) < 2:  # 如果没有提供足够的参数
        print(f"\n用法: {sys.argv[0]} 图像文件 [-t] [-convert_alpha]")
        print("    图像文件       图像文件名（必需）")
        print("    -t             运行速度测试")
        print("    -convert_alpha  在图像表面上使用convert_alpha()\n")
    else:
        # 调用主函数，传入相应的参数
        main(
            sys.argv[1],  # 图像文件路径
            convert_alpha="-convert_alpha" in sys.argv,  # 是否使用convert_alpha
            run_speed_test="-t" in sys.argv,  # 是否运行速度测试
        )
