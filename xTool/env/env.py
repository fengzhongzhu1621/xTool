import os

__all__ = [
    'get_env_or_raise',
]


def get_env_or_raise(key, default_value=None):
    """Get an environment variable, if it does not exist, raise an exception"""
    value = os.environ.get(key)
    if value:
        return value

    if default_value:
        return default_value

    raise RuntimeError(
        'Environment variable "{}" not found, you must set this variable to run this application.'.format(key)
    )
