import os

try:
    import grp
    import pwd
except ImportError:
    pass
import asyncio
import logging
import signal
from typing import Protocol

import psutil

from xTool.misc import USE_WINDOWS

# the prefix to append to gunicorn worker processes after ini
GUNICORN_WORKER_READY_PREFIX = "[ready] "


def uid_to_name(uid):
    """用户ID转换为用户名称 ."""
    return pwd.getpwuid(uid).pw_name


def gid_to_name(gid):
    """组ID转换为组名 。"""
    return grp.getgrgid(gid).gr_name


def name_to_uid(name):
    """用户名转换为用户ID ."""
    return pwd.getpwnam(name).pw_uid


def name_to_gid(name):
    """组名转换为组ID ."""
    return grp.getgrnam(name).gr_gid


def which(name, path=None):
    """
    从指定路径或环境变量PATH中遍历所有的目录，判断文件名name是否在PATH目录下且可访问
    Look for an executable file of the given name in the given list of directories,
    or the directories listed in the PATH variable of the current environment. Roughly the
    equivalent of the `which` program. Does not work on Windows.

    :type name: str
    :param name: the name of the program

    :type path: Iterable
    :param path: the directory paths to consider or None if the directories referenced in the
    PATH environment variable should be used instead

    :returns: an iterator yielding the full path to every occurrance of an executable file of the
    given name in a directory on the given path or the PATH environment variable if no path was
    passed

    >>> next( which('ls') )
    '/bin/ls'
    >>> list( which('asdalskhvxjvkjhsdasdnbmfiewwewe') )
    []
    >>> list( which('ls', path=()) )
    []
    """
    if path is None:
        path = os.environ.get("PATH")
        if path is None:
            return
        path = path.split(os.pathsep)
    for bin_dir in path:
        executable_path = os.path.join(bin_dir, name)
        if os.access(executable_path, os.X_OK):
            yield executable_path


def get_num_ready_workers_running(gunicorn_master_proc):
    """获得进程状态为ready的gunicorn的子进程的数量 ."""
    # 获得进程的所有子进程
    workers = psutil.Process(gunicorn_master_proc.pid).children()

    def ready_prefix_on_cmdline(proc):
        try:
            # 获得启动进程的命令行
            cmdline = proc.cmdline()
            # 判断是用gunicorn启动的进程，且进程状态为ready
            if cmdline:
                return GUNICORN_WORKER_READY_PREFIX in cmdline[0]
        except psutil.NoSuchProcess:
            pass
        return False

    # 获得状态为ready的gunicorn子进程
    ready_workers = [proc for proc in workers if ready_prefix_on_cmdline(proc)]
    # 返回子进程的数量
    return len(ready_workers)


def get_num_workers_running(gunicorn_master_proc):
    """获得gunicorn的子进程的数量 ."""
    workers = psutil.Process(gunicorn_master_proc.pid).children()
    return len(workers)


def kill_children_processes(pids_to_kill, timeout=5, log=None):
    """杀掉当前进程的所有子进程 ."""
    if pids_to_kill:
        # 获得主进程
        this_process = psutil.Process(os.getpid())
        # Only check child processes to ensure that we don't have a case
        # where we kill the wrong process because a child process died
        # but the PID got reused.
        # 获得存活的子进程
        child_processes = [x for x in this_process.children(recursive=True) if x.is_running() and x.pid in pids_to_kill]
        # 终止多个DAG处理子进程
        # First try SIGTERM
        for child in child_processes:
            log.info("Terminating child PID: %s", child.pid)
            child.terminate()
        # TODO: Remove magic number
        # 等待多个DAG处理子进程结束
        log.info("Waiting up to %s seconds for processes to exit...", timeout)
        try:
            psutil.wait_procs(child_processes, timeout=timeout, callback=lambda x: log.info("Terminated PID %s", x.pid))
        except psutil.TimeoutExpired:
            log.debug("Ran out of time while waiting for processes to exit")

        # 判断子进程是否结束
        # Then SIGKILL
        child_processes = [x for x in this_process.children(recursive=True) if x.is_running() and x.pid in pids_to_kill]
        if child_processes:
            log.info("SIGKILL processes that did not terminate gracefully")
            for child in child_processes:
                log.info("Killing child PID: %s", child.pid)
                child.kill()
                child.wait()


def reap_process_group(pid, log, sig=signal.SIGTERM, timeout=60):
    """终止进程id为pid的子进程（包括进程id的所有子进程）
    Tries really hard to terminate all children (including grandchildren). Will send
    sig (SIGTERM) to the process group of pid. If any process is alive after timeout
    a SIGKILL will be send.

    :param log: log handler
    :param pid: pid to kill
    :param sig: signal type 软件终止信号
    :param timeout: how much time a process has to terminate 杀死进程后的等待超时时间
    """
    if USE_WINDOWS:
        return True

    def on_terminate(p):
        """进程被关闭时的回调，打印进程ID和返回码 ."""
        log.info("Process %s (%s) terminated with exit code %s", p, p.pid, p.returncode)

    # 不允许杀死自己，pid必须是子进程
    if pid == os.getpid():
        raise RuntimeError("I refuse to kill myself")

    # 创建进程对象
    parent = psutil.Process(pid)

    # 根据进程ID，递归获得所有子进程和当前进程
    children = parent.children(recursive=True)
    children.append(parent)

    # 杀掉进程组
    # 程序结束(terminate)信号, 与SIGKILL不同的是该信号可以被阻塞和处理。
    # 通常用来要求程序自己正常退出，shell命令kill缺省产生这个信号。
    # 如果进程终止不了，我们才会尝试SIGKILL。
    log.info("Sending %s to GPID %s", sig, os.getpgid(pid))
    # getpgid 返回pid进程的group id.
    # 如果pid为0,返回当前进程的group id。在unix中有效
    os.killpg(os.getpgid(pid), sig)

    # 等待正在被杀死的进程结束
    gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)

    # 如果仍然有进程存活
    if alive:
        # 打印存活的进程
        for p in alive:
            log.warn("process %s (%s) did not respond to SIGTERM. Trying SIGKILL", p, pid)

        # 如果子进程仍然存活，则调用SIGKILL信号重新杀死
        os.killpg(os.getpgid(pid), signal.SIGKILL)

        # 等待子进程结束
        gone, alive = psutil.wait_procs(alive, timeout=timeout, callback=on_terminate)

        # 如果子进程仍然存活，则记录错误日志
        if alive:
            for p in alive:
                log.error("Process %s (%s) could not be killed. Giving up.", p, p.pid)


class AppProtocol(Protocol):

    def stop(self): ...

    def add_task(self, task) -> None: ...


def ctrlc_workaround_for_windows(app: AppProtocol):
    """在windows下重启进程 ."""

    async def stay_active(app: AppProtocol):
        """Asyncio wakeups to allow receiving SIGINT in Python"""
        while not die:
            # If someone else stopped the app, just exit
            # 判断程序是否终止
            if app.is_stopping:
                return
            # Windows Python blocks signal handlers while the event loop is
            # waiting for I/O. Frequent wakeups keep interrupts flowing.
            await asyncio.sleep(0.1)
        # Can't be called from signal handler, so call it from here
        # 收到SIGINIT信号，则停止APP，实现了graceful stop
        app.stop()

    def ctrlc_handler(sig, frame):
        """SIGINT信号处理函数 ."""
        logging.info("receive signal %s", sig)
        nonlocal die
        if die:
            # 如果收到重复的SIGINT信号，则抛出异常
            raise KeyboardInterrupt("Non-graceful Ctrl+C")
        die = True

    die = False
    # 程序终止(interrupt)信号, 在用户键入INTR字符(通常是Ctrl-C)时发出，用于通知前台进程组终止进程
    signal.signal(signal.SIGINT, ctrlc_handler)
    # 注册一个监控协程，每0.1秒检测一次APP的状态
    app.add_task(stay_active)
