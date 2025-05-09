import os
import sys

__all__ = ["is_backend"]


def is_backend() -> bool:
    """判断进程是否是后台运行的 ."""
    basename = os.path.basename(sys.argv[0])

    # 非web请求
    if any(
        [
            "manage.py" == basename and "runserver" not in sys.argv,
            "celery" in sys.argv,
            "test" in sys.argv,
            "migrate" in sys.argv,
            basename in ["pytest", "py.test", "django_test_manage.py", "pydevconsole.py"],
            basename.find("pytest") != -1,
        ]
    ):
        return True

    return False
