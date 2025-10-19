"""pygame.examples.liquid

这个示例演示了一个简单的图像水波纹效果。它尝试创建一个可以使用页面翻转进行更快更新的硬件显示表面。
注意，加载的GIF图像的调色板被复制到显示表面的调色板中。

这个示例基于Freedom2000的Brad Graham制作的名为F2KWarp的演示，使用BlitzBasic编写。
我只是将BlitzBasic代码翻译成pygame来比较结果。我没有移植文本和声音部分，
这对读者来说是一个足够简单的挑战 :]
"""

import os
import time

import pygame as pg

from xTool.pygame.image.liquid import liquid

# 获取当前脚本所在目录
main_dir = os.path.split(os.path.abspath(__file__))[0]


def main():
    """主函数，实现液体效果演示"""

    # 初始化并设置屏幕
    pg.init()
    # 创建硬件加速的双缓冲显示表面
    screen = pg.display.set_mode((640, 480), pg.HWSURFACE | pg.DOUBLEBUF)

    # 加载图像并进行四倍放大
    imagename = os.path.join(main_dir, "data", "liquid.bmp")
    bitmap = pg.image.load(imagename)
    bitmap = pg.transform.scale2x(bitmap)  # 第一次2倍放大
    bitmap = pg.transform.scale2x(bitmap)  # 第二次2倍放大（总共4倍）

    # 确保图像和屏幕使用相同的格式
    if screen.get_bitsize() == 8:
        # 如果是8位色深，设置屏幕调色板与图像一致
        screen.set_palette(bitmap.get_palette())
    else:
        # 否则将图像转换为屏幕格式
        bitmap = bitmap.convert()

    # 准备一些变量
    anim = 0.0  # 动画计数器，用于控制波纹效果

    # 定义停止事件：退出、按键、鼠标点击
    stopevents = pg.QUIT, pg.KEYDOWN, pg.MOUSEBUTTONDOWN

    while True:
        for e in pg.event.get():
            if e.type in stopevents:
                return

        # 图片显示为流水效果
        anim = anim + 0.02
        liquid(screen, bitmap, anim)

        # 更新显示（双缓冲翻转）
        pg.display.flip()

        # 控制帧率，每帧暂停10毫秒
        time.sleep(0.01)


if __name__ == "__main__":
    main()
    pg.quit()


"""BTW, here is the code from the BlitzBasic example this was derived
from. i've snipped the sound and text stuff out.
-----------------------------------------------------------------
; Brad@freedom2000.com

; Load a bmp pic (800x600) and slice it into 1600 squares
Graphics 640,480
SetBuffer BackBuffer()
bitmap$="f2kwarp.bmp"
pic=LoadAnimImage(bitmap$,20,15,0,1600)

; use SIN to move all 1600 squares around to give liquid effect
Repeat
f=0:w=w+10:If w=360 Then w=0
For y=0 To 599 Step 15
For x = 0 To 799 Step 20
f=f+1:If f=1600 Then f=0
DrawBlock pic,(x+(Sin(w+x)*40))/1.7+80,(y+(Sin(w+y)*40))/1.7+60,f
Next:Next:Flip:Cls
Until KeyDown(1)
"""
