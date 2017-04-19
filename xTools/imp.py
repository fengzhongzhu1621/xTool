#coding: utf-8

def make_module(name, objects):
    """动态创建模块 .

    - name: 模块名称
    - objects: 模块中需要包含的对象列表
    """
    name = name.lower()
    module = imp.new_module(name)
    module._name = name.split('.')[-1]
    module._objects = objects
    module.__dict__.update((o.__name__, o) for o in objects)
    return module
