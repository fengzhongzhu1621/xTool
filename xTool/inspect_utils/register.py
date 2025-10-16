import logging
import os
import pkgutil
import sys
from importlib import import_module
from types import ModuleType
from typing import List

logger = logging.getLogger(__name__)


def autodiscover_items(module: ModuleType) -> None:
    """
    Given a path to discover, auto register all items
    """
    # Workaround for a Python 3.2 bug with pkgutil.iter_modules
    # 列出指定目录下的所有非包、非下划线开头的子模块名称
    module_dir = module.__path__[0]
    sys.path_importer_cache.pop(module_dir, None)
    modules = [
        name for _, name, is_pkg in pkgutil.iter_modules([module_dir]) if not is_pkg and not name.startswith('_')
    ]
    # 动态导入子模块
    for name in modules:
        module_path = "{}.{}".format(module.__name__, name)
        __import__(module_path)

    for root, _, files in os.walk(module_dir, followlinks=False):
        if "__pycache__" in root:
            continue
        for file in files:
            if file == "__init__.py":
                continue
            # 获得文件的绝对路径
            file_path = os.path.join(root, file)
            # 只处理文件
            if not os.path.isfile(file_path):
                continue
            if module_dir == root:
                continue
            # 只处理后缀为.py的文件
            _, file_ext = os.path.splitext(os.path.split(file_path)[-1])
            if file_ext != '.py':
                continue
            # 获得子模块路径
            sub_path = root[root.index(module_dir) + len(module_dir) :]
            sub_module = sub_path.strip("/").strip("\\").replace("/", ".").replace("\\", ".")
            module_path = "{}.{}".format(module.__name__, sub_module)
            actual_module = import_module(module_path)
            actual_module_dir = actual_module.__path__[0]
            sys.path_importer_cache.pop(actual_module_dir, None)
            modules = [
                name
                for _, name, is_pkg in pkgutil.iter_modules([actual_module_dir])
                if not is_pkg and not name.startswith('_')
            ]
            for name in modules:
                module_path = "{}.{}".format(actual_module.__name__, name)
                try:
                    __import__(module_path)
                except Exception as exc_info:  # pylint: disable=broad-except
                    logging.exception(exc_info)


def autodiscover_collections(path: str, app_configs: List) -> None:
    """
    Auto-discover INSTALLED_APPS modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """

    for app_config in app_configs:
        try:
            # 根据路径导入模块
            module_path = '{}.{}'.format(app_config.get("name"), path)
            _module = import_module(module_path)
            # 搜索模块路径，导入模块中的子模块
            autodiscover_items(_module)
        except ImportError as exc_info:  # pylint: disable=broad-except
            # 忽略模块导入错误
            if not str(exc_info) == 'No module named %s' % path:
                pass
