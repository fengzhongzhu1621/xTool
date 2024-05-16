import re

__all_ = ["RE_MOBILE", "RE_WECHAT"]

RE_MOBILE = re.compile(r"Mobile|Android|iPhone|iPad|iPod", re.IGNORECASE)
RE_WECHAT = re.compile(r"MicroMessenger", re.IGNORECASE)
