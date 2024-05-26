from typing import Tuple

from django.conf import settings


def inject_logging_trace_info(
    logging: dict,
    inject_formatters: Tuple[str] = ("verbose",),
    trace_format: str = settings.OPEN_TELEMETRY_OTEL_LOGGING_TRACE_FORMAT,
    format_keywords: Tuple[str] = ("format", "fmt"),
):
    """往logging配置中动态注入trace信息，直接修改logging数据"""
    formatters = {name: formatter for name, formatter in logging["formatters"].items() if name in inject_formatters}
    for name, formatter in formatters.items():
        matched_keywords = set(format_keywords) & set(formatter.keys())
        for keyword in matched_keywords:
            # 日志格式化器打印时追加 trace 信息
            formatter.update({keyword: formatter[keyword].strip() + f" {trace_format}\n"})
