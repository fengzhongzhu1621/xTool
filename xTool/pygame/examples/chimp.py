"""pygame.examples.chimp
猩猩拳击游戏示例

这个简单的示例用于Pygame的逐行教程，基于一个"流行"的网页横幅游戏。
玩家需要用拳头击打移动的猩猩，击中后猩猩会旋转。

游戏说明：
- 移动鼠标控制拳头
- 点击鼠标左键出拳
- 击中猩猩会使其旋转并播放音效
- 按ESC键或关闭窗口退出游戏
"""

# 导入模块
import os
from typing import Any, override

import pygame
import pygame as pg
from pygame.surface import Surface

from xTool.pygame import display, sound, sprite

# 检查字体和音频模块是否可用
if not pg.font:
    print("警告：字体功能已禁用")
if not pg.mixer:
    print("警告：音频功能已禁用")

# 获取数据文件目录路径
main_dir = os.path.split(os.path.abspath(__file__))[0]  # 获取当前文件所在目录
data_dir = os.path.join(main_dir, "data")  # 数据文件目录


# 游戏对象类
class Fist(sprite.Sprite):
    """拳头类 - 在屏幕上移动紧握的拳头，跟随鼠标"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.image = self.load_image(os.path.join(data_dir, "fist.png"), colorkey=-1)
        self.rect = self.image.get_rect()
        self.fist_offset = (-235, -80)
        self.punching = False

    @override
    def update(self) -> Any:
        """根据鼠标位置移动拳头"""
        # 跟随鼠标移动
        self.rect = self.move_with_mouse()
        # 将拳头图像调整到合适位置（可能是为了视觉对齐）
        self.rect.move_ip(self.fist_offset)

        if self.punching:
            # 出拳动画：拳头会额外向右下方向移动(15, 25)像素，模拟出拳的动作效果
            self.rect.move_ip(15, 25)

    def punch(self, target):
        """出拳并检查是否击中目标

        参数:
            target: 目标精灵对象

        返回:
            bool: 如果拳头与目标碰撞返回True，否则返回False
        """
        if not self.punching:
            # 设置出拳状态
            self.punching = True
            # 检测与猩猩的碰撞
            return self.simple_colliderect(target)

    def unpunch(self) -> None:
        """收回拳头"""
        self.punching = False  # 重置出拳状态


class Chimp(sprite.Sprite):
    """猩猩类 - 在屏幕上移动猴子角色，被击中时会旋转"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.image = self.load_image(os.path.join(data_dir, "chimp.png"), -1, 4)
        self.rect = self.image.get_rect()

        # 获取当前显示表面（游戏窗口）
        screen = self.get_screen()
        # 保存屏幕的矩形区域，用于边界检测
        self.area = screen.get_rect()

        # 设置猩猩初始位置为屏幕左上角附近
        self.rect.topleft = 10, 90
        # 设置猩猩每次移动的像素距离
        self.set_walk_speed(18)
        # 初始状态为不眩晕（未被击中）
        self.dizzy = False

    @override
    def update(self) -> None:
        """根据猩猩的状态决定行走或旋转"""
        if self.dizzy:
            self._spin()  # 如果眩晕状态，执行旋转
        else:
            self._walk()  # 否则执行行走

    def _walk(self) -> None:
        """让猩猩在屏幕上移动，到达边界时转向"""
        self.walk_horizontal()

    def _spin(self) -> None:
        """旋转猩猩图像"""
        # 旋转最大一周，然后重置旋转角度为0
        stop_flag = self.spin(12, max_angle=360)
        if stop_flag:
            # 取消眩晕状态
            self.dizzy = False

    def punched(self):
        """被击中时触发猩猩旋转"""
        if not self.dizzy:  # 如果当前不在眩晕状态
            self.dizzy = True  # 设置眩晕状态
            self.original_image = self.image  # 保存当前图像作为旋转基准


def blit_text(background: Surface):
    if pg.font:
        font = pg.font.Font(None, 64)  # 创建字体对象
        text = font.render("Pummel The Chimp, And Win $$$", True, (10, 10, 10))  # 渲染文本
        textpos = text.get_rect(centerx=background.get_width() / 2, y=10)  # 计算文本位置
        background.blit(text, textpos)  # 将文本绘制到背景上


def main():
    """主函数 - 程序启动时调用

    初始化所有需要的资源，然后进入游戏循环直到函数返回
    """
    # 初始化所有内容
    pg.init()

    # 创建窗口
    screen_rect = pygame.Rect(0, 0, 1280, 480)
    window = display.DisplayWindow(screen_rect, pg.SCALED, 0)
    window.set_caption("Monkey Fever")
    window.hide_mouse()

    # 创建背填充浅绿色背景景
    background: Surface = window.blit_background_color((170, 238, 187))

    # 在背景上居中放置文本
    blit_text(background)

    # 显示背景
    window.flip()

    # 加载声音
    whiff_sound = sound.load_sound(os.path.join(data_dir, "whiff.wav"))  # 加载挥空音效
    punch_sound = sound.load_sound(os.path.join(data_dir, "punch.wav"))  # 加载击中音效

    # 准备游戏对象
    chimp = Chimp()  # 创建猩猩对象
    fist = Fist()  # 创建拳头对象
    allsprites = pg.sprite.RenderPlain(
        [chimp, fist]  # pyright: ignore[reportArgumentType]
    )  # 创建精灵组，包含所有游戏对象
    clock = pg.time.Clock()  # 创建时钟对象用于控制帧率

    # 主循环
    going = True
    while going:
        clock.tick(60)  # 限制帧率为60FPS

        # 处理输入事件
        for event in pg.event.get():
            if event.type == pg.QUIT:  # 窗口关闭事件
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:  # ESC键退出
                going = False
            elif event.type == pg.MOUSEBUTTONDOWN:  # 鼠标按下事件
                if fist.punch(chimp):  # 如果击中猩猩
                    # 播放击中音效
                    _ = punch_sound.play()
                    # 触发猩猩旋转
                    chimp.punched()
                else:
                    # 播放挥空音效
                    _ = whiff_sound.play()
            elif event.type == pg.MOUSEBUTTONUP:  # 鼠标释放事件
                # 收回拳头
                fist.unpunch()

        # 更新所有精灵状态
        allsprites.update()

        # 绘制所有内容
        window.screen.blit(background, (0, 0))  # 重绘背景
        allsprites.draw(window.screen)  # 绘制所有精灵

        # 更新显示
        window.flip

    pg.quit()


# 游戏结束


# 当脚本被执行时调用'main'函数
if __name__ == "__main__":
    main()
