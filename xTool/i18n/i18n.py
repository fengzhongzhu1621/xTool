#  -*- coding: utf-8 -*-

import gettext

from speaklater import make_lazy_gettext


def translate(message):
    return message


def gettext_from_po_file(
        message,
        domain="messages",
        languages=None,
        class_=None,
        fallback=False):
    """模块 gettext 将使用路径 (在 Unix 系统中): localedir/language/LC_MESSAGES/domain.mo 查找二进制 .mo 文件，
    此处对应地查找 language 的位置是环境变量 LANGUAGE, LC_ALL, LC_MESSAGES 和 LANG 中
    """
    localedir = gettext._localedirs.get(domain, None)
    codeset = gettext._localecodesets.get(domain, None)
    try:
        t = gettext.translation(
            domain,
            localedir=localedir,
            languages=languages,
            class_=class_,
            fallback=fallback,
            codeset=codeset)
    except OSError:
        return message
    return t.gettext(message)


lazy_gettext = make_lazy_gettext(lambda: translate)
