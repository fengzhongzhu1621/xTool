def make_hashable(obj):
    if isinstance(obj, (list, tuple)):
        return tuple(make_hashable(x) for x in obj)
    elif isinstance(obj, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    else:
        return obj


def distinct_dict_list(dict_list: list):
    seen = set()
    result = []
    for d in dict_list:
        # 将字典转换为可哈希的形式
        hashable = {k: make_hashable(v) for k, v in d.items()}
        hash_tuple = tuple(sorted(hashable.items()))
        if hash_tuple not in seen:
            seen.add(hash_tuple)
            result.append(d)
    return result


def reverse_dict(dic):
    return {v: k for k, v in dic.items()}
