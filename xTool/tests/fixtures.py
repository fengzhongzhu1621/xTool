# -*- coding: utf-8 -*-

import random
import string
import uuid
import time
import subprocess
import shlex
from contextlib import contextmanager

import pytest


TYPE_TO_GENERATOR_MAP = {
    "string": lambda: "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(4)]
    ),
    "int": lambda: random.choice(range(1000000)),
    "number": lambda: random.random(),
    "alpha": lambda: "".join(
        [random.choice(string.ascii_letters) for _ in range(4)]
    ),
    "uuid": lambda: str(uuid.uuid1()),
}


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
