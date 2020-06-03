# -*- coding: utf-8 -*-

import random
import string
import uuid

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
