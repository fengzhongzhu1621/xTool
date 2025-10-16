class LabelHandleMixin:
    def labels(self, *label_values, **label_kwargs):
        """处理标签中的异常数据 ."""
        label_values = (type(value).__name__ if isinstance(value, Exception) else value for value in label_values)
        label_values = [value if value is not None else "" for value in label_values]
        label_kwargs = {
            key: type(value).__name__ if isinstance(value, Exception) else value for key, value in label_kwargs.items()
        }
        return super().labels(*label_values, **label_kwargs)
