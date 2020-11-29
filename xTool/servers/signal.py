# -*- coding: utf-8 -*-

import signal


class Signal:
    stopped = False


def register_signal_hander(loop, handle_stop_signal, handle_child_process_exit):
    """添加信号处理函数 ."""
    # multiprocessing模块，其中的terminate函数，发送的是SIGTERM信号；命令行数据 kill pid 时的信号
    # Ctrl-c会发送SIGINT(这在Python中其实被封装成了KeyboardInterrupt异常)；键盘中断（如break键被按下）
    # SIGUSR2 31,12,17 A 用户自定义信号2
    # SIGSEGV 11 C 无效的内存引用
    # SIGCHLD 20,17,18 B 子进程结束信号；每当子进程终止的时候，它会向父进程发送SIGCHLD信号。父进程可以设置一个信号处理程序来接受SIGCHLD和整理已经终止的子进程。
    sigs = [signal.SIGTERM, signal.SIGINT, signal.SIGUSR2, signal.SIGSEGV]
    for sig in sigs:
        loop.add_signal_handler(sig, handle_stop_signal)
    if handle_child_process_exit:
        loop.add_signal_handler(signal.SIGCHLD, handle_child_process_exit)
