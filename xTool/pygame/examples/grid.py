from typing import Literal

import pygame as pg
from pygame.surface import Surface
from pygame.time import Clock

# 游戏常量定义
TITLE = "Grid"  # 窗口标题
TILES_HORIZONTAL = 10  # 水平方向瓦片数量
TILES_VERTICAL = 10  # 垂直方向瓦片数量
TILE_SIZE = 80  # 每个瓦片的大小（像素）
WINDOW_WIDTH = 800  # 窗口宽度
WINDOW_HEIGHT = 800  # 窗口高度


class Player:
    """玩家类，表示网格上的玩家角色"""

    def __init__(self, surface) -> None:
        self.surface = surface  # 绘制表面
        self.pos: tuple[Literal[40], Literal[40]] = (40, 40)  # 玩家初始位置

    def draw(self):
        """绘制玩家角色（白色圆圈）"""
        _ = pg.draw.circle(self.surface, (255, 255, 255), self.pos, 40)

    def move(self, target):
        """移动玩家到网格位置

        Args:
            target: 目标坐标，玩家会移动到最近的网格中心
        """
        # 计算网格对齐的位置
        x = (80 * (target[0] // 80)) + 40  # 将x坐标对齐到网格中心
        y = (80 * (target[1] // 80)) + 40  # 将y坐标对齐到网格中心

        self.pos = (x, y)  # 更新玩家位置


class Game:
    """游戏主类，管理游戏循环和状态"""

    def __init__(self):
        _ = pg.init()  # 初始化Pygame
        self.clock: Clock = pg.time.Clock()  # 游戏时钟，用于控制帧率
        pg.display.set_caption(TITLE)  # 设置窗口标题
        self.surface: Surface = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # 创建游戏窗口
        self.loop: bool = True  # 游戏循环控制标志
        self.player: Player = Player(self.surface)  # 创建玩家对象

    def main(self):
        """游戏主循环"""
        while self.loop:
            self.grid_loop()  # 执行每一帧的游戏逻辑
        pg.quit()  # 退出Pygame

    def grid_loop(self):
        """网格游戏循环，处理每一帧的渲染和事件"""

        # 填充黑色背景
        self.surface.fill((0, 0, 0))

        # 绘制棋盘格背景
        for row in range(TILES_HORIZONTAL):
            # 交错绘制瓦片，创建棋盘效果
            for col in range(row % 2, TILES_HORIZONTAL, 2):
                pg.draw.rect(
                    self.surface,
                    (40, 40, 40),  # 深灰色瓦片
                    (row * TILE_SIZE, col * TILE_SIZE, TILE_SIZE, TILE_SIZE),  # 瓦片位置和大小
                )

        # 绘制玩家角色
        self.player.draw()

        # 处理事件
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.loop = False  # 窗口关闭事件
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.loop = False  # ESC键退出
            elif event.type == pg.MOUSEBUTTONUP:
                # 鼠标点击事件：移动玩家到点击位置
                pos = pg.mouse.get_pos()
                self.player.move(pos)

        # 更新显示
        pg.display.update()


if __name__ == "__main__":
    mygame = Game()
    mygame.main()
