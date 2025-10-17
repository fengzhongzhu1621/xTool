import asyncio
import logging
import random
import re
import shlex
import string
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager, suppress
from pathlib import Path

import fakeredis
import pytest

from xTool.cache import Cache
from xTool.cache.constants import CacheBackendType, CacheInstanceType
from xTool.concurrency import thread_pool
from xTool.decorators import Signal

TYPE_TO_GENERATOR_MAP = {
    "string": lambda: "".join([random.choice(string.ascii_letters + string.digits) for _ in range(4)]),
    "int": lambda: random.choice(range(1000000)),
    "number": lambda: random.random(),
    "alpha": lambda: "".join([random.choice(string.ascii_letters) for _ in range(4)]),
    "uuid": lambda: str(uuid.uuid1()),
}

# 导入其它的 fixtures
path = Path(__file__).parent / "fixtures"
root_path = Path(__file__).parent.parent

logging_format = """module: %(module)s; \
function: %(funcName)s(); \
message: %(message)s"""

logging.basicConfig(format=logging_format, level=logging.INFO)

random.seed("Pack my box with five dozen liquor jugs.")

if sys.platform in ["win32", "cygwin"]:
    collect_ignore = ["test_worker.py"]


class RouteStringGenerator:
    ROUTE_COUNT_PER_DEPTH = 100
    HTTP_METHODS = ["GET", "PUT", "POST", "PATCH", "DELETE", "OPTION"]
    ROUTE_PARAM_TYPES = ["string", "int", "number", "alpha", "uuid"]

    def generate_random_direct_route(self, max_route_depth=4):
        routes = []
        for depth in range(1, max_route_depth + 1):
            for _ in range(self.ROUTE_COUNT_PER_DEPTH):
                route = "/".join([TYPE_TO_GENERATOR_MAP.get("string")() for _ in range(depth)])
                route = route.replace(".", "", -1)
                route_detail = (random.choice(self.HTTP_METHODS), route)

                if route_detail not in routes:
                    routes.append(route_detail)
        return routes

    def add_typed_parameters(self, current_routes, max_route_depth=8):
        routes = []
        for method, route in current_routes:
            current_length = len(route.split("/"))
            new_route_part = "/".join(
                [
                    "<{}:{}>".format(
                        TYPE_TO_GENERATOR_MAP.get("string")(),
                        random.choice(self.ROUTE_PARAM_TYPES),
                    )
                    for _ in range(max_route_depth - current_length)
                ]
            )
            route = "/".join([route, new_route_part])
            route = route.replace(".", "", -1)
            routes.append((method, route))
        return routes

    @staticmethod
    def generate_url_for_template(template):
        url = template
        for pattern, param_type in re.findall(
            re.compile(r"((?:<\w+:(string|int|number|alpha|uuid)>)+)"),
            template,
        ):
            value = TYPE_TO_GENERATOR_MAP.get(param_type)()
            url = url.replace(pattern, str(value), -1)
        return url


@pytest.fixture
def cache():
    connection_conf = {
        "host": "localhost",
        "port": "6379",
        "db": 0,
        "password": "",
    }
    cache = Cache(
        CacheBackendType.CELERY,
        CacheInstanceType.RedisCache,
        redis_class=fakeredis.FakeStrictRedis,
        connection_conf=connection_conf,
    )
    return cache


@pytest.fixture(scope="function")
def url_param_generator():
    return TYPE_TO_GENERATOR_MAP


@pytest.fixture(scope="module")
def gunicorn_worker():
    command = (
        "gunicorn "
        "--bind 127.0.0.1:1337 "
        "--worker-class xTool.workers.worker.GunicornWorker "
        "examples.simple_server:app"
    )
    worker = subprocess.Popen(shlex.split(command))
    time.sleep(3)
    yield
    worker.kill()


@pytest.fixture(scope="module")
def gunicorn_worker_with_access_logs():
    command = (
        "gunicorn "
        "--bind 127.0.0.1:1338 "
        "--worker-class xTool.workers.worker.GunicornWorker "
        "examples.simple_server:app"
    )
    worker = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    time.sleep(2)
    return worker


@pytest.fixture(scope="module")
def gunicorn_worker_with_env_var():
    command = (
        'env XTOOL_ACCESS_LOG="False" '
        "gunicorn "
        "--bind 127.0.0.1:1339 "
        "--worker-class xTool.workers.worker.GunicornWorker "
        "--log-level info "
        "examples.simple_server:app"
    )
    worker = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    time.sleep(2)
    return worker


@pytest.fixture
def timer():
    @contextmanager
    def timer(expected_time=0, dispersion=0.5):
        expected_time = float(expected_time)
        dispersion_value = expected_time * dispersion

        now = time.monotonic()

        yield

        delta = time.monotonic() - now

        lower_bound = expected_time - dispersion_value
        upper_bound = expected_time + dispersion_value

        assert lower_bound < delta < upper_bound

    return timer


@pytest.fixture
def aiomisc_unused_port():
    from xTool.net import get_unused_port

    return get_unused_port()


@pytest.fixture
def signal():
    return Signal()


@pytest.fixture(params=(thread_pool.threaded, thread_pool.threaded_separate))
def threaded_decorator(request, executor: thread_pool.ThreadPoolExecutor):
    assert executor
    return request.param


@pytest.fixture
def executor(loop: asyncio.AbstractEventLoop):
    pool = thread_pool.ThreadPoolExecutor(8)
    loop.set_default_executor(pool)
    try:
        yield pool
    finally:
        with suppress(Exception):
            pool.shutdown(wait=True)

        pool.shutdown(wait=True)


gen_decos = (
    thread_pool.threaded_iterable,
    thread_pool.threaded_iterable_separate,
)


@pytest.fixture(params=gen_decos)
def iterator_decorator(request):
    return request.param
