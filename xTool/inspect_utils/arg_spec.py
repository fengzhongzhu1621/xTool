"""Inspection utility functions for Python Fire."""

import inspect
import sys
import types
from typing import Callable

import six

if six.PY34:
    pass


class FullArgSpec:
    """The arguments of a function, as in Python 3's inspect.FullArgSpec."""

    def __init__(
        self, args=None, varargs=None, varkw=None, defaults=None, kwonlyargs=None, kwonlydefaults=None, annotations=None
    ):
        """Constructs a FullArgSpec with each provided attribute, or the default.

        Args:
          args: A list of the argument names accepted by the function.
          varargs: The name of the *varargs argument or None if there isn't one.
          varkw: The name of the **kwargs argument or None if there isn't one.
          defaults: A tuple of the defaults for the arguments that accept defaults.
          kwonlyargs: A list of argument names that must be passed with a keyword.
          kwonlydefaults: A dictionary of keyword only arguments and their defaults.
          annotations: A dictionary of arguments and their annotated types.
        """
        self.args = args or []
        self.varargs = varargs
        self.varkw = varkw
        self.defaults = defaults or ()
        self.kwonlyargs = kwonlyargs or []
        self.kwonlydefaults = kwonlydefaults or {}
        self.annotations = annotations or {}


def _get_arg_spec_info(fn):
    """Gives information pertaining to computing the ArgSpec of fn.

    Determines if the first arg is supplied automatically when fn is called.
    This arg will be supplied automatically if fn is a bound method or a class
    with an __init__ method.

    Also returns the function who's ArgSpec should be used for determining the
    calling parameters for fn. This may be different from fn itself if fn is a
    class with an __init__ method.

    Args:
      fn: The function or class of interest.
    Returns:
      A tuple with the following two items:
        fn: The function to use for determining the arg spec of this function.
        skip_arg: Whether the first argument will be supplied automatically, and
          hence should be skipped when supplying args from a Fire command.
    """
    skip_arg = False
    if inspect.isclass(fn):
        # If the function is a class, we try to use its init method.
        skip_arg = True
        if six.PY2 and hasattr(fn, '__init__'):
            fn = fn.__init__
    elif inspect.ismethod(fn):
        # If the function is a bound method, we skip the `self` argument.
        skip_arg = fn.__self__ is not None
    elif inspect.isbuiltin(fn):
        # If the function is a bound builtin, we skip the `self` argument, unless
        # the function is from a standard library module in which case its __self__
        # attribute is that module.
        if not isinstance(fn.__self__, types.ModuleType):
            skip_arg = True
    elif not inspect.isfunction(fn):
        # The purpose of this else clause is to set skip_arg for callable objects.
        skip_arg = True
    return fn, skip_arg


def py2_get_arg_spec(fn):
    """A wrapper around getargspec that tries both fn and fn.__call__."""
    try:
        return inspect.getargspec(fn)  # pylint: disable=deprecated-method,no-member
    except TypeError:
        if hasattr(fn, '__call__'):
            return inspect.getargspec(fn.__call__)  # pylint: disable=deprecated-method,no-member
        raise


def py3_get_full_arg_spec(fn):
    """A alternative to the builtin getfullargspec.

    The builtin inspect.getfullargspec uses:
    `skip_bound_args=False, follow_wrapped_chains=False`
    in order to be backwards compatible.

    This function instead skips bound args (self) and follows wrapped chains.

    Args:
      fn: The function or class of interest.
    Returns:
      An inspect.FullArgSpec namedtuple with the full arg spec of the function.
    """
    # pylint: disable=no-member
    # pytype: disable=module-attr
    try:
        sig = inspect._signature_from_callable(  # pylint: disable=protected-access
            fn, skip_bound_arg=True, follow_wrapper_chains=True, sigcls=inspect.Signature
        )
    except Exception:
        # 'signature' can raise ValueError (most common), AttributeError, and
        # possibly others. We catch all exceptions here, and reraise a TypeError.
        raise TypeError('Unsupported callable.')

    args = []
    varargs = None
    varkw = None
    kwonlyargs = []
    defaults = ()
    annotations = {}
    defaults = ()
    kwdefaults = {}

    if sig.return_annotation is not sig.empty:
        annotations['return'] = sig.return_annotation

    for param in sig.parameters.values():
        kind = param.kind
        name = param.name

        # pylint: disable=protected-access
        if kind is inspect._POSITIONAL_ONLY:
            args.append(name)
        elif kind is inspect._POSITIONAL_OR_KEYWORD:
            args.append(name)
            if param.default is not param.empty:
                defaults += (param.default,)
        elif kind is inspect._VAR_POSITIONAL:
            varargs = name
        elif kind is inspect._KEYWORD_ONLY:
            kwonlyargs.append(name)
            if param.default is not param.empty:
                kwdefaults[name] = param.default
        elif kind is inspect._VAR_KEYWORD:
            varkw = name
        if param.annotation is not param.empty:
            annotations[name] = param.annotation
        # pylint: enable=protected-access

    if not kwdefaults:
        # compatibility with 'func.__kwdefaults__'
        kwdefaults = None

    if not defaults:
        # compatibility with 'func.__defaults__'
        defaults = None
    return inspect.FullArgSpec(args, varargs, varkw, defaults, kwonlyargs, kwdefaults, annotations)
    # pylint: enable=no-member
    # pytype: enable=module-attr


def get_full_arg_spec(fn):
    """Returns a FullArgSpec describing the given callable."""
    original_fn = fn
    fn, skip_arg = _get_arg_spec_info(fn)

    try:
        if sys.version_info[0:2] >= (3, 5):
            (args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations) = py3_get_full_arg_spec(fn)
        else:  # Specifically Python 3.4.
            (args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations) = inspect.getfullargspec(
                fn
            )  # pylint: disable=deprecated-method,no-member

    except TypeError:
        # If we can't get the argspec, how do we know if the fn should take args?
        # 1. If it's a builtin, it can take args.
        # 2. If it's an implicit __init__ function (a 'slot wrapper'), that comes
        # from a namedtuple, use _fields to determine the args.
        # 3. If it's another slot wrapper (that comes from not subclassing object in
        # Python 2), then there are no args.
        # Are there other cases? We just don't know.

        # Case 1: Builtins accept args.
        if inspect.isbuiltin(fn):
            # TODO(dbieber): Try parsing the docstring, if available.
            # TODO(dbieber): Use known argspecs, like set.add and namedtuple.count.
            return FullArgSpec(varargs='vars', varkw='kwargs')

        # Case 2: namedtuples store their args in their _fields attribute.
        # TODO(dbieber): Determine if there's a way to detect false positives.
        # In Python 2, a class that does not subclass anything, does not define
        # __init__, and has an attribute named _fields will cause Fire to think it
        # expects args for its constructor when in fact it does not.
        fields = getattr(original_fn, '_fields', None)
        if fields is not None:
            return FullArgSpec(args=list(fields))

        # Case 3: Other known slot wrappers do not accept args.
        return FullArgSpec()

    # In Python 3.5+ py3_get_full_arg_spec uses skip_bound_arg=True already.
    skip_arg_required = six.PY2 or sys.version_info[0:2] == (3, 4)
    if skip_arg_required and skip_arg and args:
        args.pop(0)  # Remove 'self' or 'cls' from the list of arguments.
    return FullArgSpec(args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations)


_PYPY = hasattr(sys, "pypy_version_info")


def varnames(func: object) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return tuple of positional and keywrord argument names for a function,
    method, class or callable. 用于获取函数、方法、类或可调用对象的参数名称.

    In case of a class, its ``__init__`` method is considered.
    For methods the ``self`` parameter is not included.
    """
    if inspect.isclass(func):
        try:
            func = func.__init__
        except AttributeError:
            return (), ()
    elif not inspect.isroutine(func):  # callable object?
        try:
            func = getattr(func, "__call__", func)
        except Exception:
            return (), ()

    try:
        # func MUST be a function or method here or we won't parse any args.
        sig = inspect.signature(
            func.__func__ if inspect.ismethod(func) else func  # type:ignore[arg-type]
        )
    except TypeError:
        return (), ()

    _valid_param_kinds = (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    )
    _valid_params = {name: param for name, param in sig.parameters.items() if param.kind in _valid_param_kinds}
    args = tuple(_valid_params)
    defaults = tuple(param.default for param in _valid_params.values() if param.default is not param.empty) or None

    if defaults:
        index = -len(defaults)
        args, kwargs = args[:index], tuple(args[index:])
    else:
        kwargs = ()

    # strip any implicit instance arg
    # pypy3 uses "obj" instead of "self" for default dunder methods
    if not _PYPY:
        implicit_names: tuple[str, ...] = ("self",)
    else:
        implicit_names = ("self", "obj")
    if args:
        qualname: str = getattr(func, "__qualname__", "")
        if inspect.ismethod(func) or ("." in qualname and args[0] in implicit_names):
            args = args[1:]

    return args, kwargs


def format_def(func: Callable[..., object]) -> str:
    """打印函数的签名 ."""
    return f"{func.__name__}{inspect.signature(func)}"
