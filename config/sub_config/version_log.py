from django.utils.translation import gettext_lazy as _lazy

VERSION_LOG = {
    # 版本日志 Markdown 文件存放的目录
    'MD_FILES_DIR': 'version_logs_md',
    # 多语言文件名后缀的分隔符，例如version_v1.0_en.md，其中 _en 表示英语版本
    'LANGUAGE_POSTFIX_SEPARATION': "_",
    # 语言映射字典，用于指定不同语言的文件名后缀
    # 'LANGUAGE_MAPPINGS': {
    #     'en': '_en',
    #     'zh': '_zh'
    # }
    'LANGUAGE_MAPPINGS': {},
    # 版本日志文件名的正则表达式模式
    # 表示文件名以 v 或 V 开头，后面跟着 2 到 4 个数字和点，最后以 .md 结尾。例如 v1.0.0.md 或 V2.3.4.5.md。
    'NAME_PATTERN': r'[vV](\d+\.){2,4}md',  # noqa
    # 文件时间的格式
    'FILE_TIME_FORMAT': '%Y%m%d',
    # 是否显示最新版本信息
    'LATEST_VERSION_INFORM': False,
    # 显示最新版本信息的方式（如重定向）
    'LATEST_VERSION_INFORM_TYPE': 'redirect',
    # 版本日志的入口 URL
    'ENTRANCE_URL': 'version_log/',
    # 页面标题
    'PAGE_HEAD_TITLE': _lazy('版本日志'),
    # 页面展示样式（如对话框）
    'PAGE_STYLE': 'dialog',
    # 是否使用哈希 URL
    'USE_HASH_URL': True,
}
