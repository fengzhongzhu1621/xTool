import functools

from .keys import hash_key, method_key


def cached(cache, key=hash_key, lock=None):
    """Decorator to wrap a function with a memoizing callable that saves
    results in a cache.

    """

    def decorator(func):
        if cache is None:

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            def clear():
                pass

        elif lock is None:

            def wrapper(*args, **kwargs):
                # 计算hash值
                k = key(*args, **kwargs)
                # 优先从缓存获取结果
                try:
                    return cache[k]
                except KeyError:
                    pass  # key not found
                # 缓存结果
                v = func(*args, **kwargs)
                try:
                    cache[k] = v
                except ValueError:
                    pass  # value too large
                return v

            def clear():
                cache.clear()

        else:

            def wrapper(*args, **kwargs):
                k = key(*args, **kwargs)
                try:
                    with lock:
                        return cache[k]
                except KeyError:
                    pass  # key not found
                v = func(*args, **kwargs)
                # in case of a race, prefer the item already in the cache
                try:
                    with lock:
                        return cache.setdefault(k, v)
                except ValueError:
                    return v  # value too large

            def clear():
                with lock:
                    cache.clear()

        wrapper.cache = cache
        wrapper.cache_key = key
        wrapper.cache_lock = lock
        wrapper.cache_clear = clear

        return functools.update_wrapper(wrapper, func)

    return decorator


def cachedmethod(cache, key=method_key, lock=None):
    """Decorator to wrap a class or instance method with a memoizing
    callable that saves results in a cache.

    """

    def decorator(method):
        if lock is None:

            def wrapper(self, *args, **kwargs):
                c = cache(self)
                if c is None:
                    return method(self, *args, **kwargs)
                k = key(self, *args, **kwargs)
                try:
                    return c[k]
                except KeyError:
                    pass  # key not found
                v = method(self, *args, **kwargs)
                try:
                    c[k] = v
                except ValueError:
                    pass  # value too large
                return v

            def clear(self):
                c = cache(self)
                if c is not None:
                    c.clear()

        else:

            def wrapper(self, *args, **kwargs):
                c = cache(self)
                if c is None:
                    return method(self, *args, **kwargs)
                k = key(self, *args, **kwargs)
                try:
                    with lock(self):
                        return c[k]
                except KeyError:
                    pass  # key not found
                v = method(self, *args, **kwargs)
                # in case of a race, prefer the item already in the cache
                try:
                    with lock(self):
                        return c.setdefault(k, v)
                except ValueError:
                    return v  # value too large

            def clear(self):
                c = cache(self)
                if c is not None:
                    with lock(self):
                        c.clear()

        wrapper.cache = cache
        wrapper.cache_key = key
        wrapper.cache_lock = lock
        wrapper.cache_clear = clear

        return functools.update_wrapper(wrapper, method)

    return decorator
