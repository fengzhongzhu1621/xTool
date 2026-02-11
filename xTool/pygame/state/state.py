from typing import Any

import pygame
from pygame import Surface
from pygame.event import Event


class State:
    """
    游戏状态机模式的基础实现类

    该类实现了游戏状态机模式，用于管理游戏中的不同状态（如主菜单、游戏关卡、暂停界面等）。
    每个状态都有完整的生命周期：启动、运行、清理。
    """

    name: str

    def __init__(self) -> None:
        """初始化状态对象"""
        self.start_time: float = 0.0  # 状态开始时间（用于计时和状态持续时间计算）
        self.current_time: float = 0.0  # 当前时间（用于更新逻辑）（毫秒）

        self.done: bool = False  # 状态是否完成（True时切换到下一个状态）
        self.quit: bool = False  # 是否退出游戏（True时退出整个游戏）

        self.next: State  # 下一个状态对象（状态切换时使用）
        self.previous: State  # 上一个状态对象（用于返回上一状态）

        self.persist: dict = {}  # 持久化数据字典（用于状态间传递数据，如玩家分数、关卡信息等）

    def handle_event(self, event: Event):
        """
        处理用户输入事件

        参数:
            event: pygame事件对象（如键盘、鼠标事件）

        说明:
            子类需要重写此方法来实现具体的事件处理逻辑
        """
        return NotImplemented

    def startup(self, persistant: dict[str, Any]) -> None:
        """
        状态启动时的初始化方法

        参数:
            current_time: 当前游戏时间
            persistant: 从上一个状态传递过来的持久化数据

        说明:
            在状态开始运行时调用，用于设置初始状态
        """
        self.start_time = pygame.time.get_ticks()
        self.persist = persistant

    def cleanup(self) -> Any | dict[str, Any]:
        """
        状态结束时的清理方法

        返回值:
            返回持久化数据给下一个状态

        说明:
            在状态结束时调用，重置状态标志并返回需要传递的数据
        """
        self.done = False
        return self.persist

    def update(self, surface: Surface, keys) -> None:
        """
        状态的主更新逻辑

        参数:
            surface: 绘制表面（用于渲染游戏画面）
            keys: 当前按下的键位状态

        说明:
            子类需要重写此方法来实现具体的游戏逻辑更新和渲染
        """
        self.current_time = pygame.time.get_ticks()

    def set_next(self, next: "State") -> None:
        self.next = next

    def set_previous(self, previous: "State") -> None:
        self.previous = previous

    def next_state(self) -> "State":
        return NotImplemented

    def flip_next(self) -> "State":
        """切换游戏状态"""
        next = self.next_state()

        # 清理当前状态并获取持久化数据
        persist = self.cleanup()

        # 启动新状态
        next.startup(persist)
        next.previous = self

        return next
