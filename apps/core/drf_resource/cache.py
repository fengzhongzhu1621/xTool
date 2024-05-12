class CacheTypeItem:
    """缓存类型 ."""

    def __init__(self, key, timeout, user_related=None, label=""):
        self.key = key
        self.timeout = timeout
        self.label = label
        self.user_related = user_related

    def __call__(self, timeout):
        """类装饰器 ."""
        return CacheTypeItem(self.key, timeout, self.user_related, self.label)
