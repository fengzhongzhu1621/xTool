class Default:
    """
    It is used to replace `None` or `object()` as a sentinel
    that represents a default value. Sometimes we want to set
    a value to `None` so we cannot use `None` to represent the
    default value, and `object()` is hard to be typed.
    """

    pass


DefaultValue = Default()
