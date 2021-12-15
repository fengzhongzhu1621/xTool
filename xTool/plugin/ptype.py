from xTool.algorithms.collections.attrdict import FancyDict


class _PluginType(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            self[key] = key
            return self[key]

    def __delattr__(self, key):
        raise AttributeError(key)


PluginType = _PluginType()
