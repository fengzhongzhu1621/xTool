import inspect
import time
import traceback
from functools import wraps

from xTool.log import logger

try:
    from raven.contrib.django.raven_compat.models import sentry_exception_handler
except ImportError:
    sentry_exception_handler = None


def notify_sentry(func_name: str, log_enabled: bool = True):
    """通知 sentry"""
    if log_enabled:
        logger.error(f"[{func_name}] execute error: {traceback.format_exc()}")
    if sentry_exception_handler is not None:
        sentry_exception_handler(request=None)


def log(f):
    """方法参数日志记录"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        params = []
        arg_spec = inspect.getfullargspec(f)
        # arg_spec.args = (1, 2, 3, 4, 5)
        for index, arg in enumerate(arg_spec.args):
            try:
                params.append(f"{arg}={args[index]}")
            except IndexError:
                pass

        params.extend([f"args{index}={value}" for index, value in enumerate(args[len(params) :])])

        d = kwargs.copy()
        # arg_spec.kwonlyargs = ["d", "e"]
        # arg_spec.kwonlydefaults = {"e": 3}}
        for kw_only_arg in arg_spec.kwonlyargs:
            if kw_only_arg in kwargs:
                value = kwargs[kw_only_arg]
                d.pop(kw_only_arg)
            else:
                value = arg_spec.kwonlydefaults[kw_only_arg]

            params.append(f"{kw_only_arg}={value}")

        params.extend([f"(kwargs){t}={value}" for t, value in d.items()])

        # 执行函数，并记录耗时
        begin_time = time.time()
        try:
            logger.info(f"[{f.__name__}] execute begin: {', '.join(params)}")
            try:
                result = f(*args, **kwargs)
                return result
            except Exception:  # pylint: disable=broad-except
                notify_sentry(f.__name__)
                raise

        finally:
            end_time = time.time()
            cost = end_time - begin_time
            logger.info(f"[{f.__name__}] execute end: {', '.join(params)}, cost is {cost}")

        return result

    return wrapper


if __name__ == "__main__":

    @log
    def run_task(a, b=2, *c, d, e=3, **f) -> str:
        print(f"a={a}, b={b}, c={c}, d={d}, e={e}, f={f}")

    def test_run_task():
        run_task(1, 2, 3, 4, 5, d=6, attr1="v1", attr2="v2")
