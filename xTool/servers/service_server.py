# -*- coding: utf-8 -*-

import os
import asyncio
import signal
import logging
import errno

from xTool.servers.options import ServerOptions
from xTool.servers.service import Service, ServiceDesc
from xTool.servers.exceptions import ServiceNotFoundError
from xTool.servers.executor_process_manager import ExecutorProcessManager
from xTool.misc import OS_IS_WINDOWS
from xTool.utils.processes import ctrlc_workaround_for_windows


class ServiceServer:
    def __init__(self, server_options: ServerOptions,
                 register_sys_signals=True):
        self.server_options = server_options
        self.services = {}
        self.executor_process_manager = None
        self.register_sys_signals = register_sys_signals
        self.is_stopping = False
        self.loop = None

    def add_service(self, service_name: str, service: Service):
        self.services[service_name] = service

    def get_service(self, service_name: str):
        return self.services.get(service_name)

    def run_all_services(self):
        """运行所有的服务 。"""
        for service in self.services.values():
            service.run()

    def register(self, service_name: str, service_desc: ServiceDesc):
        """注册服务 ."""
        service = self.get_service(service_name)
        if service:
            service.register(service_desc)
        raise ServiceNotFoundError("service %s not found" % service_name)

    def add_task(self, task):
        """创建异步任务 。"""
        if callable(task):
            try:
                self.loop.create_task(task(self))
            except TypeError:
                self.loop.create_task(task())
        else:
            self.loop.create_task(task)

    def stop(self):
        if not self.is_stopping:
            try:
                self.executor_process_manager.close()
            except Exception as ex:
                logging.error("close server engine failure: %s", str(ex))

            service_close_rets = []
            for service in self.services.values():
                service_close_ret = service.close()
                if service_close_ret:
                    service_close_rets.append(service_close_ret)

            async def wait_closed(tasks):
                await asyncio.gather(*tasks)
                self.loop.stop()

            if service_close_rets:
                asyncio.ensure_future(wait_closed(service_close_rets), loop=self.loop)
            else:
                self.loop.stop()
            self.is_stopping = True

    def handle_stop_signal(self, signum, stackframe):
        """停止服务器 ."""
        logging.info("receive signal %s", signum)
        self.stop()

    def handle_child_process_exit(self):
        """子进程退出时系统会向父进程发送 SIGCHLD 信号，
        父进程可以通过注册 SIGCHLD 信号处理程序，
        在信号处理程序中调用 wait 系统调用来清理僵尸进程 ."""
        try:
            while not self.is_stopping:
                # -1 表示任意子进程
                # os.WNOHANG 表示如果没有可用的需要 wait 退出状态的子进程，立即返回不阻塞
                # os.waitpid 调用 wait 系统调用后阻止了子进程一直处于僵尸进程状态，从而实现了清除僵尸进程的效果
                cpid, status = os.waitpid(-1, os.WNOHANG)
                if cpid == 0:
                    logging.info('no child process was immediately available')
                    break
                exitcode = status >> 8
                logging.info('child process %s exit with exitcode %s', cpid, exitcode)
                # 子进程退出时，父进程重新拉起子进程
                if self.executor_process_manager.find_child_process(cpid):
                    self.executor_process_manager.restart_child_process(cpid)
        except ChildProcessError:
            exit()
        except OSError as e:
            if e.errno == errno.ECHILD:
                logging.warning('current process has no existing unwaited-for child processes.')
            else:
                exit()
        finally:
            logging.info('handle SIGCHLD end')

    def register_signal(self):
        """注册信号处理函数 ."""
        if not self.register_sys_signals:
            return
        if OS_IS_WINDOWS:
            ctrlc_workaround_for_windows(self)
        else:
            sigs = [signal.SIGTERM, signal.SIGINT, signal.SIGUSR2, signal.SIGSEGV]
            for sig in sigs:
                self.loop.add_signal_handler(sig, self.handle_stop_signal)
            self.loop.add_signal_handler(signal.SIGCHLD, self.handle_child_process_exit)

    def serve_forever(self, executor_process_manager=None):
        """启动服务器 ."""
        # 创建loop
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop

        # 创建engine
        self.executor_process_manager = executor_process_manager if executor_process_manager else ExecutorProcessManager(
            loop=loop,
            server_options=self.server_options)

        # 运行所有的服务
        self.run_all_services()

        # 启动执行引擎
        self.executor_process_manager.start_processes()

        # 获得主进程ID
        pid = os.getpid()

        try:
            # 注册信号处理函数
            self.register_signal()
            # 启动server
            logging.info("Starting worker [%s]", pid)
            self.loop.run_forever()
        except (SystemExit, KeyboardInterrupt):
            self.loop.stop()
        finally:
            logging.info("Stopping worker [%s]", pid)
