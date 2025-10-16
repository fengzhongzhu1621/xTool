import asyncio
import errno
import logging
import os

from xTool.asynchronous.aiomisc import cancel_tasks
from xTool.asynchronous.servers.context import Context, get_context
from xTool.misc import OS_IS_WINDOWS
from xTool.net.servers.signal import register_signal_hander
from xTool.utils.processes import ctrlc_workaround_for_windows


class ServiceMeta(type):
    """在对象中添加变量__async_required__和__required__ ."""

    def __new__(cls, name, bases, namespace, **kwds):
        instance = type.__new__(cls, name, bases, dict(namespace))

        for key in ("__async_required__", "__required__"):
            setattr(instance, key, frozenset(getattr(instance, key, ())))

        check_instance = all(
            asyncio.iscoroutinefunction(getattr(instance, method)) for method in instance.__async_required__
        )

        if not check_instance:
            raise TypeError(
                "Following methods must be coroutine functions",
                tuple("{}.{}".format(name, m) for m in instance.__async_required__),
            )

        return instance


class Service(metaclass=ServiceMeta):
    # 协程
    __async_required__ = "start", "stop"
    # 必填参数
    __required__ = ()

    def __init__(self, **kwargs):
        lost_kw = self.__required__ - kwargs.keys()
        if lost_kw:
            raise AttributeError("Absent attributes", lost_kw)

        self.loop = None
        self._set_params(**kwargs)
        self.__context = None
        self.start_event = None  # type: asyncio.Event

    @property
    def context(self) -> Context:
        if self.__context is None:
            self.__context = get_context()
        return self.__context

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.start_event = asyncio.Event()

    def _set_params(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    async def start(self):
        raise NotImplementedError

    async def stop(self, exception: Exception = None):
        pass


class SimpleServer(Service):
    def __init__(self, **kwargs):
        self.server = None
        self.tasks = set()
        self.is_stopping = False
        super().__init__(**kwargs)

    def create_task(self, coro):
        task = self.loop.create_task(coro)
        self.tasks.add(task)
        # 任务执行完成后从集合中删除
        task.add_done_callback(self.tasks.remove)
        return task

    async def start(self):
        raise NotImplementedError

    async def stop(self, exc: Exception = None):
        await cancel_tasks(self.tasks)
        self.server.close()


class BaseServiceServer:
    def __init__(self, *args, **kwargs):
        self.services = {}
        self.is_stopping = False
        self.loop = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    def add_service(self, service_name: str, service: Service):
        self.services[service_name] = service

    def get_service(self, service_name: str):
        return self.services.get(service_name)

    def run_services(self):
        """运行所有的服务 。"""
        for service in self.services.values():
            service.run()

    def close_services(self):
        close_futures = []
        for service in self.services.values():
            future = service.close()
            if future:
                close_futures.append(future)
        return close_futures

    def add_task(self, task):
        """创建异步任务 。"""
        if callable(task):
            try:
                self.loop.create_task(task(self))
            except TypeError:
                self.loop.create_task(task())
        else:
            self.loop.create_task(task)

    async def _wait_closed(self, tasks):
        await asyncio.gather(*tasks)
        self.loop.stop()

    def stop(self):
        if not self.is_stopping:
            close_futures = self.close_services()
            if close_futures:
                asyncio.ensure_future(self._wait_closed(close_futures), loop=self.loop)
            else:
                self.loop.stop()
            self.is_stopping = True

    def handle_stop_signal(self, signum, stackframe):
        """停止服务器 ."""
        logging.info("receive signal %s", signum)
        self.stop()

    def find_child_process(self, child_pid):
        raise NotImplementedError("Method not implemented")

    def restart_child_process(self, child_pid):
        raise NotImplementedError("Method not implemented")

    def handle_child_process_exit(self):
        """子进程退出时系统会向父进程发送 SIGCHLD 信号，
        父进程可以通过注册 SIGCHLD 信号处理程序，
        在信号处理程序中调用 wait 系统调用来清理僵尸进程 ."""
        try:
            while not self.is_stopping:
                # -1 表示任意子进程
                # os.WNOHANG 表示如果没有可用的需要 wait 退出状态的子进程，立即返回不阻塞
                # os.waitpid 调用 wait 系统调用后阻止了子进程一直处于僵尸进程状态，从而实现了清除僵尸进程的效果
                child_pid, status = os.waitpid(-1, os.WNOHANG)
                if child_pid == 0:
                    logging.info("no child process was immediately available")
                    break
                exitcode = status >> 8
                logging.info("child process %s exit with exitcode %s", child_pid, exitcode)
                # 子进程退出时，父进程重新拉起子进程
                if self.find_child_process(child_pid):
                    self.restart_child_process(child_pid)
        except ChildProcessError:
            exit()
        except OSError as e:
            if e.errno == errno.ECHILD:
                logging.warning("current process has no existing unwaited-for child processes.")
            else:
                exit()
        finally:
            logging.info("handle SIGCHLD end")

    def _register_signal_handler(self):
        if OS_IS_WINDOWS:
            ctrlc_workaround_for_windows(self)
        else:
            register_signal_hander(self.loop, self.handle_stop_signal, self.handle_child_process_exit)

    def serve(self):
        # 注册信号处理函数
        self._register_signal_handler()
        try:
            self.loop.run_forever()
        except (SystemExit, KeyboardInterrupt):
            self.loop.stop()
