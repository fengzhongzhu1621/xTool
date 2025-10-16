import logging
import random
import re
import string
import sys
import uuid
from pathlib import Path

from xTool.testing.pytest_plugin import append_pytest_fixture_plugins

# 导入其它的 fixtures
path = Path(__file__).parent / "fixtures"
root_path = Path(__file__).parent.parent
pytest_plugins = append_pytest_fixture_plugins(root_path, path)

logging_format = """module: %(module)s; \
function: %(funcName)s(); \
message: %(message)s"""

logging.basicConfig(format=logging_format, level=logging.INFO)

random.seed("Pack my box with five dozen liquor jugs.")

if sys.platform in ["win32", "cygwin"]:
    collect_ignore = ["test_worker.py"]

TYPE_TO_GENERATOR_MAP = {
    "string": lambda: "".join([random.choice(string.ascii_letters + string.digits) for _ in range(4)]),
    "int": lambda: random.choice(range(1000000)),
    "number": lambda: random.random(),
    "alpha": lambda: "".join([random.choice(string.ascii_letters) for _ in range(4)]),
    "uuid": lambda: str(uuid.uuid1()),
}


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
