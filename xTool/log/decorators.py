import inspect
from functools import wraps
from xTool.log import logger


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

        # 执行函数前打印函数的执行参数
        logger.info("%s(%s)", f.__name__, ', '.join(params))

        return f(*args, **kwargs)

    return wrapper


if __name__ == "__main__":
    @log
    def run_task(a, b=2, *c, d, e=3, **f) -> str:
        print(f"a={a}, b={b}, c={c}, d={d}, e={e}, f={f}")


    def test_run_task():
        run_task(1, 2, 3, 4, 5, d=6, attr1="v1", attr2="v2")
