import inspect


def get_class_attrs_dict(component):
    """Gets the attributes of the component class, as a dict with name keys."""
    if not inspect.isclass(component):
        return None
    class_attrs_list = inspect.classify_class_attrs(component)
    return {class_attr.name: class_attr for class_attr in class_attrs_list}
