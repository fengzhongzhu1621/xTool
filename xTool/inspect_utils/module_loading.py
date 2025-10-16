import imp
import importlib
import os
import sys
import warnings
from inspect import ismodule
from types import ModuleType
from typing import Callable

from xTool.exceptions import XToolException
from xTool.log import logger
from xTool.utils.log.logging_mixin import LoggingMixin

log = LoggingMixin().log


def prepare_classpath(dir_path):
    """将路径加入python系统路径 ."""
    dir_path = os.path.abspath(os.path.expanduser(dir_path))
    if dir_path not in sys.path:
        sys.path.append(dir_path)


def make_module(name, objects):
    """动态创建模块 .

    - name: 模块名称
    - objects: 模块中需要包含的对象列表

    Examples:
        make_module('airflow.operators.' + p.name, p.operators + p.sensors))
    """
    log.debug("Creating module %s", name)
    # 创建模块
    module = imp.new_module(name)
    # 给模块设置_name属性 （插件名），即p.name
    module._name = name.split(".")[-1]
    # 给模块设置_object属性（插件中所有的类名）
    module._objects = objects
    # 给模块设置属性 （类名 => 类）
    module.__dict__.update((o.__name__, o) for o in objects)
    # 返回新创建的模块
    return module


def integrate_plugins(modules):
    """Integrate plugins to the context."""
    # 将模块加入到系统模块变量中
    for module in modules:
        sys.modules[module.__name__] = module
        globals()[module._name] = module


def create_object_from_plugin_module(name, *args, **kwargs):
    """从插件模块中获取类实例 .

    Args:
        name: plugin_module.class_name
    """
    items = name.split(".")
    if len(items) != 2:
        raise XToolException(
            "Executor {} not supported: " "please specify in format plugin_module.executor".format(name)
        )
    # items[0]：表示插件名
    # items[1]：表示插件中的类名
    plugin_module_name = items[0]
    class_name = items[1]
    if plugin_module_name in globals():
        # 根据插件中的类名创建对象
        return globals()[plugin_module_name].__dict__[class_name](*args, **kwargs)
    else:
        raise XToolException("Executor {} not supported.".format(name))


def load_backend_module_from_conf(section, key, default_backend, conf=None):
    """从配置文件中加载模块 .

    Args:
        section: 配置文件中的section
        key: section中的key
        default_backend: 默认后端模块配置
        conf: 配置对象

    Returns:
        返回加载的模块
    """
    module = None
    # 从配置文件中获取配置的后端模块
    if conf is None:
        backend = default_backend
    else:
        try:
            backend = conf.get(section, key)
        except conf.XToolConfigException:
            # 没有配置
            backend = default_backend

    # 加载模块，加载失败抛出异常
    try:
        module = importlib.import_module(backend)
    except ImportError as err:
        log.critical("Cannot import %s for %s %s due to: %s", backend, section, key, err)
        raise XToolException(err)

    return module


def import_string(dotted_path: str) -> Callable:
    """根据点分割的字符串，加载类
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.

    Args:
        dotted_path: 字符串表示的模块类，module.class
    Returns:
        返回加载的模块中的对象
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError:
        raise ImportError("{} doesn't look like a module path".format(dotted_path))

    module: ModuleType = importlib.import_module(module_path)

    try:
        # 返回模块中的类
        return getattr(module, class_name)
    except AttributeError:
        raise ImportError('Module "{}" does not define a "{}" attribute/class'.format(module_path, class_name))


def import_string_from_package(module_name, package=None):
    """
    Import a module or class by string path.

    :module_name: str with path of module or path to import and
    instanciate a class
    :returns: a module object or one instance from class if
    module_name is a valid path to class

    """
    module, klass = module_name.rsplit(".", 1)
    module = importlib.import_module(module, package=package)
    obj = getattr(module, klass)
    if ismodule(obj):
        return obj
    return obj()


def re_import_modules(path, module_path):
    """递归导入文件下的模块，通常用于触发注册器逻辑"""
    for name in os.listdir(path):
        # 忽略无效文件
        if name.endswith(".pyc") or name in ["__init__.py", "__pycache__"]:
            continue

        if os.path.isdir(os.path.join(path, name)):
            re_import_modules(os.path.join(path, name), ".".join([module_path, name]))
        else:
            try:
                module_name = name.replace(".py", "")
                import_path = ".".join([module_path, module_name])
                importlib.import_module(import_path)
            except ModuleNotFoundError as e:
                logger.warning(e)


class XToolImporter:
    """
    Importer that dynamically loads a class and module from its parent. This
    allows Airflow to support ``from airflow.operators import BashOperator``
    even though BashOperator is actually in
    ``airflow.operators.bash_operator``.

    The importer also takes over for the parent_module by wrapping it. This is
    required to support attribute-based usage:

    .. code:: python

        from xTool import operators
        operators.BashOperator(...)
        _operators = {
            'bash_operator': ['BashOperator'],
        }
        importer = XToolImporter(sys.modules[__name__], _operators)
    """

    def __init__(self, parent_module, module_attributes):
        """
        :param parent_module: The string package name of the parent module. For
            example, 'airflow.operators'
        :type parent_module: string
        :param module_attributes: The file to class mappings for all importable
            classes.
        :type module_attributes: string
        """
        self._parent_module = parent_module
        self._attribute_modules = self._build_attribute_modules(module_attributes)
        self._loaded_modules = {}

        # Wrap the module so we can take over __getattr__.
        sys.modules[parent_module.__name__] = self

    @staticmethod
    def _build_attribute_modules(module_attributes):
        """遍历模块的属性，返回属性和模块名称的映射关系
        Flips and flattens the module_attributes dictionary from:

            module => [Attribute, ...]

        To:

            Attribute => module

        This is useful so that we can find the module to use, given an
        attribute.
        """
        attribute_modules = {}

        for module, attributes in module_attributes.items():
            for attribute in attributes:
                attribute_modules[attribute] = module

        return attribute_modules

    def _load_attribute(self, attribute):
        """
        Load the class attribute if it hasn't been loaded yet, and return it.
        """
        # 根据属性获得模块名称
        module = self._attribute_modules.get(attribute, False)

        # 如果模块不存在，则抛出导入错误
        if not module:
            # This shouldn't happen. The check happens in find_modules, too.
            raise ImportError(attribute)
        elif module not in self._loaded_modules:
            # 保证模块只加载一次
            # Note that it's very important to only load a given modules once.
            # If they are loaded more than once, the memory reference to the
            # class objects changes, and Python thinks that an object of type
            # Foo that was declared before Foo's module was reloaded is no
            # longer the same type as Foo after it's reloaded.
            # 获得父模块所在的目录
            path = os.path.realpath(self._parent_module.__file__)
            folder = os.path.dirname(path)
            # 在父模块的目录下所有的文件中查找指定的module
            f, filename, description = imp.find_module(module, [folder])
            self._loaded_modules[module] = imp.load_module(module, f, filename, description)

            # This functionality is deprecated
            warnings.warn(
                "Importing '{i}' directly from '{m}' has been "
                "deprecated. Please import from "
                "'{m}.[operator_module]' instead. Support for direct "
                "imports will be dropped entirely in future version.".format(
                    i=attribute, m=self._parent_module.__name__
                ),
                DeprecationWarning,
            )

        loaded_module = self._loaded_modules[module]

        # 从动态加载后的模块中获取属性
        return getattr(loaded_module, attribute)

    def __getattr__(self, attribute):
        """
        Get an attribute from the wrapped module. If the attribute doesn't
        exist, try and import it as a class from a submodule.

        This is a Python trick that allows the class to pretend it's a module,
        so that attribute-based usage works:

            from airflow import operators
            operators.BashOperator(...)

        It also allows normal from imports to work:

            from airflow.operators.bash_operator import BashOperator
        """
        # 如果模块包含指定的属性
        if hasattr(self._parent_module, attribute):
            # Always default to the parent module if the attribute exists.
            return getattr(self._parent_module, attribute)
        # 如果模块不包含指定的属性
        elif attribute in self._attribute_modules:
            # 动态加载模块，并获取属性
            # Try and import the attribute if it's got a module defined.
            loaded_attribute = self._load_attribute(attribute)
            setattr(self, attribute, loaded_attribute)
            return loaded_attribute

        raise AttributeError


def import_from_file_path(path):
    """Performs a module import given the filename.

    Args:
      path (str): the path to the file to be imported.

    Raises:
      IOError: if the given file does not exist or importlib fails to load it.

    Returns:
      Tuple[ModuleType, str]: returns the imported module and the module name,
        usually extracted from the path itself.
    """

    if not os.path.exists(path):
        raise OSError('Given file path does not exist.')

    module_name = os.path.basename(path)

    if sys.version_info.major == 3 and sys.version_info.minor < 5:
        loader = importlib.machinery.SourceFileLoader(  # pylint: disable=no-member
            fullname=module_name,
            path=path,
        )

        module = loader.load_module(module_name)  # pylint: disable=deprecated-method

    else:
        from importlib import util  # pylint: disable=g-import-not-at-top,import-outside-toplevel,no-name-in-module

        spec = util.spec_from_file_location(module_name, path)

        if spec is None:
            raise OSError('Unable to load module from specified path.')

        module = util.module_from_spec(spec)  # pylint: disable=no-member
        spec.loader.exec_module(module)  # pytype: disable=attribute-error

    return module, module_name


def import_from_module_name(module_name: str):
    """Imports a module and returns it and its name."""
    module = importlib.import_module(module_name)
    return module, module_name


def import_module(module_or_filename):
    """Imports a given module or filename.

    If the module_or_filename exists in the file system and ends with .py, we
    attempt to import it. If that import fails, try to import it as a module.

    Args:
      module_or_filename (str): string name of path or module.

    Raises:
      ValueError: if the given file is invalid.
      IOError: if the file or module can not be found or imported.

    Returns:
      Tuple[ModuleType, str]: returns the imported module and the module name,
        usually extracted from the path itself.
    """

    if os.path.exists(module_or_filename):
        # importlib.util.spec_from_file_location requires .py
        if not module_or_filename.endswith('.py'):
            try:  # try as module instead
                return import_from_module_name(module_or_filename)
            except ImportError:
                raise ValueError('Fire can only be called on .py files.')

        return import_from_file_path(module_or_filename)

    if os.path.sep in module_or_filename:  # Use / to detect if it was a filename.
        raise OSError('Fire was passed a filename which could not be found.')

    return import_from_module_name(module_or_filename)  # Assume it's a module.
