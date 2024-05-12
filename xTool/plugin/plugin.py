class Plugin:
    def __init__(
        self,
        cls,
        plugin_type: str,
        plugin_name: str,
        version: str = "",
        can_init_instance: bool = True,
        *args,
        **kwargs
    ):
        # 需要转换为插件的类
        self._cls = cls
        # 插件名称
        self.name = plugin_name
        # 插件类型
        self.type = plugin_type
        # 插件的版本
        self.version = version
        # 对象可以初始化
        self.can_init_instance = can_init_instance
        self.args = args
        self.kwargs = kwargs

    def create_instance(self):
        """创建插件实例 ."""
        return self._cls(*self.args, **self.kwargs)
