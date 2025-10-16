PASSWORD_POLICY = {
    "name": "password",
    "rule": {
        "max_length": 25,
        "min_length": 6,
        "include_rule": {
            "numbers": True,  # 是否包含数字
            "symbols": True,  # 是否包含特殊符号
            "lowercase": True,  # 是否包含小写字符
            "uppercase": True,  # 是否包含大写字符
        },
        "exclude_continuous_rule": {
            "limit": 3,  # 最大连续长度
            "letters": True,  # 连续字母
            "numbers": True,  # 连续数字
            "repeats": True,  # 连续重复字符
            "symbols": True,  # 连续特殊字符
            "keyboards": True,  # 连续键盘序
        },
    },
}

VERIFY_PASSWORD_DATA = {
    "is_strength": False,
    "password_verify_info": {
        "lowercase_valid": False,
        "uppercase_valid": False,
        "numbers_valid": False,
        "symbols_valid": False,
        "repeats_valid": True,
        "follow_letters_valid": True,
        "follow_symbols_valid": True,
        "follow_keyboards_valid": True,
        "follow_numbers_valid": True,
        "min_length_valid": True,
        "max_length_valid": True,
    },
}
