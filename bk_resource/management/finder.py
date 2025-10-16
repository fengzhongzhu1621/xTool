import os

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder

from bk_resource.management.exceptions import ErrorSettingsWithResourceDirs
from bk_resource.settings import bk_resource_settings
from xTool.file.path import path_to_dotted

API_DIR = bk_resource_settings.DEFAULT_API_DIR
RESOURCE_DIRS = bk_resource_settings.DEFAULT_RESOURCE_DIRS
if API_DIR not in RESOURCE_DIRS:
    RESOURCE_DIRS.append(API_DIR)


class ResourceFinder(BaseFinder):
    def __init__(self, app_names=None, *args, **kwargs):
        # Mapping of app names to resource modules
        self.resource_path = []
        app_path_directories = []
        # 获得所有的 django 应用配置
        app_configs = apps.get_app_configs()
        if app_names:
            app_names = set(app_names)
            app_configs = [ac for ac in app_configs if ac.name in app_names]

        for app_config in app_configs:
            app_path = app_config.path
            root_path = os.path.dirname(app_path)
            self.resource_path += self.find(app_path, root_path=root_path)
            app_path_directories.append(app_path)

        for path in RESOURCE_DIRS:
            search_path = os.path.join(settings.BASE_DIR, path)
            if search_path in app_path_directories:
                continue

            self.resource_path += self.find(search_path, from_settings=True)

        self.resource_path.sort()
        self.found()

    def found(self) -> None:
        p_list = []
        for p in self.resource_path:
            p_list.append(ResourcePath(p))

        self.resource_path = p_list

    def list(self, ignore_patterns):
        """
        List all resource path.
        """
        for path in self.resource_path:
            yield path.path, path.status

    def find(self, path, root_path=None, from_settings=False):
        """
        Looks for resource module in the app directories.
        if recursive is True, recursive traversal directory
        """
        matches = set()
        base_dir = settings.BASE_DIR
        if not path.startswith(base_dir):
            if from_settings:
                raise ErrorSettingsWithResourceDirs("RESOURCE_DIRS settings error")
            return []
        # 忽略自己
        if path.startswith(os.path.join(base_dir, "bk_resource")):
            return []

        for root, dirs, files in sorted(os.walk(path)):
            # 搜索 resources 目录
            if os.path.basename(root) == "resources":
                relative_path = os.path.relpath(os.path.dirname(root), root_path or base_dir)
                matches.add(path_to_dotted(relative_path))
                continue

            # 搜索 default.py, resources.py 文件
            for file_path in files:
                file_name = os.path.basename(file_path)
                base_file_name, ext_name = os.path.splitext(file_name)
                if ext_name not in [".py", ".pyc", ".pyo"]:
                    continue

                if base_file_name in ["resources", "default"]:
                    relative_path = os.path.relpath(root, root_path or base_dir)
                    matches.add(path_to_dotted(relative_path))
                    continue

        return matches


class ResourceStatus:
    # 待加载
    unloaded = "unloaded"
    # 加载成功
    loaded = "loaded"
    # 忽略
    ignored = "ignored"
    # 加载错误
    error = "error"


class ResourcePath:
    """
    path = ResourcePath("api.xxx")
    path.loaded()
    path.ignored()
    path.error()
    """

    def __init__(self, path):
        status = ResourceStatus.unloaded
        path_info = path.split(":")
        if len(path_info) > 1:
            rspath, status = path_info[:2]
        else:
            rspath = path_info[0]

        self.path = rspath.strip()
        self.status = status.strip()

    def __getattr__(self, item):
        status = getattr(ResourceStatus, item, None)
        if status:
            return status_setter(status)(lambda: status, self)

    def __repr__(self):
        return "{}: {}".format(self.path, self.status)


def status_setter(status: str):
    """装饰器，用于给 ResourcePath 对象添加状态 ."""

    def setter(func, path: ResourcePath):
        path.status = status
        return func

    return setter
