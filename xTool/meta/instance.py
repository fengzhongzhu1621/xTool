class NoInstance(type):
    """不能实例化的类，用于创建只有静态方法的类 ."""

    def __call__(cls, *args, **kwargs):
        raise TypeError("Can't create instance of this class")
