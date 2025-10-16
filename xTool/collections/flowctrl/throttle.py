import threading
import time

from xTool.compat import PY3

if PY3:
    from threading import BoundedSemaphore
else:
    from threading import _BoundedSemaphore as BoundedSemaphore


__all__ = [
    "BoundedEmptySemaphore",
    "GlobalThrottle",
    "LocalThrottle",
    "throttle",
]


class BoundedEmptySemaphore(BoundedSemaphore):
    """
    A bounded semaphore that is initially empty.
    """

    def __init__(self, value=1):
        super().__init__(value)
        # 如果从令牌桶算法算法角度出发，即令牌桶算法在初始化时使用完所有的令牌
        # value：是令牌桶中初始的令牌数量
        for i in range(value):
            assert self.acquire(blocking=False)


class GlobalThrottle:
    """一个线程安全的全局限速器，用于访问全局资源；可以应用到所有的线程上。

    也可以认为是一个令牌桶算法，BoundedEmptySemaphore就是一个令牌桶。

    A thread-safe rate limiter that throttles all threads globally. This should be used to
    regulate access to a global resource. It can be used as a function/method decorator or as a
    simple object, using the throttle() method. The token generation starts with the first call
    to throttle() or the decorated function. Each subsequent call to throttle() will then acquire
    a token, possibly having to wait until one becomes available. The number of unused tokens
    will not exceed a limit given at construction time. This is a very basic mechanism to
    prevent the resource from becoming swamped after longer pauses.
    """

    def __init__(self, min_interval, max_unused):
        """
        :param min_interval: 资源探测的间隔时间，也即令牌的生成间隔
        :param max_unused: 信号量的大小，即资源的数量，也即令牌的数量
        """
        # 线程的间隔时间
        self.min_interval = min_interval
        # 创建信号量，并调用acquire使其内部计数器等于0，阻塞进程
        self.semaphore = BoundedEmptySemaphore(max_unused)
        # 创建线程锁
        self.thread_start_lock = threading.Lock()
        # 默认不启动线程
        self.thread_started = False
        # 创建线程
        self.thread = threading.Thread(target=self.generator)
        # 主线程结束时，子线程也随之结束
        self.thread.daemon = True

    def generator(self):
        while True:
            try:
                # 随着时间流逝,系统会按恒定1/QPS时间间隔(如果QPS=100,则间隔是10ms)往桶里加入Token
                # (想象和漏洞漏水相反,有个水龙头在不断的加水),如果桶已经满了就不再加了.
                # 新请求来临时,会各自拿走一个Token,如果没有Token可拿了就阻塞或者拒绝服务.
                self.semaphore.release()
            except ValueError:
                pass
            time.sleep(self.min_interval)

    def throttle(self, wait=True):
        """
        If the wait parameter is True, this method returns True after suspending the current
        thread as necessary to ensure that no less than the configured minimum interval passed
        since the most recent time an invocation of this method returned True in any thread.

        If the wait parameter is False, this method immediatly returns True if at least the
        configured minimum interval has passed since the most recent time this method returned
        True in any thread, or False otherwise.
        """
        # I think there is a race in Thread.start(), hence the lock
        with self.thread_start_lock:
            # 启动子线程，不停地释放信号量
            if not self.thread_started:
                self.thread.start()
                self.thread_started = True
        # 新请求来临时,会各自拿走一个Token, 如果没有Token可拿了就阻塞或者拒绝服务.
        return self.semaphore.acquire(blocking=wait)

    def __call__(self, function):
        def wrapper(*args, **kwargs):
            self.throttle()
            return function(*args, **kwargs)

        return wrapper


class LocalThrottle:
    """一个线程安全的单个线程限速器，在指定时间间隔后才会运行
    A thread-safe rate limiter that throttles each thread independently. Can be used as a
    function or method decorator or as a simple object, via its .throttle() method.

    The use as a decorator is deprecated in favor of throttle().
    """

    def __init__(self, min_interval):
        """
        Initialize this local throttle.

        :param min_interval: The minimum interval in seconds between invocations of the throttle
        method or, if this throttle is used as a decorator, invocations of the decorated method.
        """
        self.min_interval = min_interval
        # 线程局部变量
        self.per_thread = threading.local()
        self.per_thread.last_invocation = None

    def throttle(self, wait=True):
        """
        If the wait parameter is True, this method returns True after suspending the current
        thread as necessary to ensure that no less than the configured minimum interval has
        passed since the last invocation of this method in the current thread returned True.

        If the wait parameter is False, this method immediatly returns True (if at least the
        configured minimum interval has passed since the last time this method returned True in
        the current thread) or False otherwise.
        """
        now = time.time()
        last_invocation = self.per_thread.last_invocation
        if last_invocation is not None:
            # 计算时间过了多久
            interval = now - last_invocation
            # 时间未过期，继续等待；到期后执行函数
            if interval < self.min_interval:
                if wait:
                    remainder = self.min_interval - interval
                    time.sleep(remainder)
                else:
                    return False
        self.per_thread.last_invocation = time.time()
        return True

    def __call__(self, function):
        def wrapper(*args, **kwargs):
            self.throttle()
            return function(*args, **kwargs)

        return wrapper


class throttle:  # pylint: disable=invalid-name
    """在函数执行之后等待，直到超时；如果有异常不等待
    A context manager for ensuring that the execution of its body takes at least a given amount
    of time, sleeping if necessary. It is a simpler version of LocalThrottle if used as a
    decorator.

    Ensures that body takes at least the given amount of time.
    """

    def __init__(self, min_interval):
        self.min_interval = min_interval

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # 计算执行时间
            duration = time.time() - self.start
            # 如果函数执行完之后，还未超时，则继续等待
            remainder = self.min_interval - duration
            if remainder > 0:
                time.sleep(remainder)

    def __call__(self, function):
        def wrapper(*args, **kwargs):
            with self:
                return function(*args, **kwargs)

        return wrapper
