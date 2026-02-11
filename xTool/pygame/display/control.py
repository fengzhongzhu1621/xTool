import pygame

from xTool.pygame.state import State

from .display import DisplayWindow


class ControlCenter:
    """
    游戏主控制器类

    负责整个项目的控制，包含游戏主循环和事件循环，
    事件循环根据需要将事件传递给各个状态，
    状态切换的逻辑也在这里实现。
    """

    def __init__(self, window: DisplayWindow):
        """初始化控制器"""
        self.window = window

        # 游戏是否结束
        self.done = False
        # 当前按下的键
        self.keys = pygame.key.get_pressed()
        # 当前状态对象
        self.state: State

    def change_state(self, state: State) -> None:
        """设置游戏状态"""
        self.state = state

    def update(self):
        """更新游戏逻辑"""
        if self.state.quit:
            # 如果状态要求退出，则结束游戏
            self.done = True
        elif self.state.done:
            # 如果状态完成，切换到下一个状态
            self.change_state(self.state.flip_next())

        # 更新当前状态
        self.state.update(self.window.get_screen(), self.keys)

    def event_loop(self):
        """事件循环处理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True  # 处理退出事件
            elif event.type == pygame.KEYDOWN:
                self.keys = pygame.key.get_pressed()  # 更新按键状态
                self.window.toggle_show_fps(event.key)  # 切换FPS显示
            elif event.type == pygame.KEYUP:
                self.keys = pygame.key.get_pressed()  # 更新按键状态

            # 给状态发送需要处理的事件
            self.state.handle_event(event)

    def main(self):
        """游戏主循环"""
        while not self.done:
            # 处理事件
            self.event_loop()

            # 更新游戏逻辑
            self.update()

            # 更新显示
            pygame.display.update()

            # 控制帧率
            self.window.set_fps()
