from .attrs import get_class_attrs_dict


def has_custom_str(component):
    """Determines if a component has a custom __str__ method.

    Uses inspect.classify_class_attrs to determine the origin of the object's
    __str__ method, if one is present. If it defined by `object` itself, then
    it is not considered custom. Otherwise it is. This means that the __str__
    methods of primitives like ints and floats are considered custom.

    Objects with custom __str__ methods are treated as values and can be
    serialized in places where more complex objects would have their help screen
    shown instead.

    Args:
      component: The object to check for a custom __str__ method.
    Returns:
      Whether `component` has a custom __str__ method.
    """
    if hasattr(component, '__str__'):
        class_attrs = get_class_attrs_dict(type(component)) or {}
        str_attr = class_attrs.get('__str__')
        if str_attr and str_attr.defining_class is not object:
            return True
    return False
