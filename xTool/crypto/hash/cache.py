def hash_key(*args):
    """计算的hash，用于缓冲的唯一性判断 ."""
    args = args[1:]
    return tuple(hash(k) for k in args)
