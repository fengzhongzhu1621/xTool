import hashlib
import inspect

from .bytes import tob


def count_md5(content, dict_sort=True, list_sort=True):
    if dict_sort and isinstance(content, dict):
        content = [(str(k), count_md5(content[k], dict_sort, list_sort)) for k in sorted(content.keys())]
        return count_md5(content, dict_sort, list_sort)
    elif isinstance(content, (list, tuple)):
        content = (
            sorted([count_md5(k, dict_sort, list_sort=True) for k in content])
            if list_sort
            else [count_md5(k, dict_sort, list_sort) for k in content]
        )
        return md5(str(content))
    elif callable(content):
        return make_callable_hash(content)
    return md5(str(content))


def make_callable_hash(content):
    """
    计算callable的hash
    """
    if inspect.isclass(content):
        h = []
        for attr in [i for i in sorted(dir(content)) if not i.startswith("__")]:
            v = getattr(content, attr)
            h.append(count_md5(v))

        return md5("".join(h))
    try:
        return md5(content.__name__)
    except AttributeError:
        try:
            return md5(content.func.__name__)
        except AttributeError:
            return md5(str(content))


def get_md5(content):
    if isinstance(content, list):
        return [count_md5(c) for c in content]
    else:
        return count_md5(content)


def file_md5sum(file):
    file.seek(0, 0)

    m = hashlib.md5()
    for chunk in file.chunks():
        m.update(chunk)

    file.seek(0, 0)
    return m.hexdigest()


def md5(src):
    if not src:
        return None
    m = hashlib.md5()
    m.update(tob(src))
    return m.hexdigest()
