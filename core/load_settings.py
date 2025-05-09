from importlib import import_module


def get_settings_from_module(module, is_upper=True):
    setting_items = {}
    for _setting in dir(module):
        if is_upper and not _setting.isupper():
            continue
        setting_items[_setting] = getattr(module, _setting)
    return setting_items


def load_settings(module_path: str, settings_for_merge=None, raise_exception=True):
    if not settings_for_merge:
        settings_for_merge = {}
    setting_items = {}

    # 加载模块
    try:
        module = import_module(module_path)
    except ImportError:
        if not raise_exception:
            return {}
        raise

    # 遍历模块中的配置选项
    for _setting in dir(module):
        if not _setting.isupper():
            continue

        if _setting in settings_for_merge:
            new_setting_item_value = getattr(module, _setting)
            if not isinstance(new_setting_item_value, (tuple, list)):
                # 配置覆盖
                setting_items[_setting] = new_setting_item_value
                continue
            # 配置追加
            old_setting_item_value = settings_for_merge.get(_setting, [])
            setting_items[_setting] = (
                *old_setting_item_value,
                *(_s for _s in new_setting_item_value if _s not in old_setting_item_value),
            )
        else:
            # 配置覆盖
            setting_items[_setting] = getattr(module, _setting)

    return setting_items
