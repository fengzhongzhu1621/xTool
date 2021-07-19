# -*- coding: utf-8 -*-

from typing import Dict, List

import sys
from xTool.type_hint import get_class_object_init_type


class DictConfigConverter:
    def __init__(self, dict_config: Dict):
        self.dict_config = dict_config

    def marshal(self):
        "将配置对象转换为Dict配置 ."""
        pass

    def unmarshal(self, key: str, target_object: object) -> object:
        if not key:
            # 将字典的所有成员转换为一个指定对象
            dict_config = self.dict_config
        else:
            # 将字典的部分转换一个指定对象
            dict_config = self.dict_config.get(key)
        return self.unmarshal_dict_to_object(dict_config, target_object)

    @classmethod
    def unmarshal_dict_to_object(cls, dict_config: Dict,  target_object: object):
        """将dict类型的配置转换为配置对象 ."""
        for name, value in dict_config.items():
            # 判断对象中属性是否存在
            if not hasattr(target_object, name):
                continue
            # 获得对象中属性的类型
            attr_type = get_class_object_init_type(target_object, name)
            py_version = sys.version_info
            if py_version.major == 3 and py_version.minor == 6:
                attr_type_class = getattr(attr_type, '__extra__', attr_type)
            elif py_version.version_info > (3, 6):
                attr_type_class = getattr(attr_type, '__origin__', attr_type)
            else:
                attr_type_class = attr_type
            # 类型转换
            if value is None:
                value = attr_type_class()
                setattr(target_object, name, value)
            elif isinstance(value, dict):
                if attr_type == List:
                    setattr(target_object, name, value)
                elif attr_type_class == dict:
                    # TOOD 字典中还有对象
                    setattr(target_object, name, value)
                else:
                    value_object = attr_type_class()
                    setattr(target_object, name, value_object)
                    cls.unmarshal_dict_to_object(value, value_object)
            elif isinstance(value, list):
                if attr_type == List:
                    setattr(target_object, name, value)
                elif attr_type_class == list:
                    sub_object_list = []
                    setattr(target_object, name, sub_object_list)
                    for sub_value in value:
                        sub_value_object = getattr(attr_type, '__args__')[0]()
                        sub_object_list.append(sub_value_object)
                        cls.unmarshal_dict_to_object(sub_value, sub_value_object)
            else:
                setattr(target_object, name, attr_type(value))
        return target_object
