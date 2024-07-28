def is_named_tuple(component):
    """Return true if the component is a namedtuple.

    Unfortunately, Python offers no native way to check for a namedtuple type.
    Instead, we need to use a simple hack which should suffice for our case.
    namedtuples are internally implemented as tuples, therefore we need to:
      1. Check if the component is an instance of tuple.
      2. Check if the component has a _fields attribute which regular tuples do
         not have.

    Args:
      component: The component to analyze.
    Returns:
      True if the component is a namedtuple or False otherwise.
    """
    if not isinstance(component, tuple):
        return False

    has_fields = bool(getattr(component, '_fields', None))
    return has_fields
