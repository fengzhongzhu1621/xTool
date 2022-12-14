# -*- coding: utf-8 -*-

import json
import logging
import re
from collections import defaultdict

from django.utils import translation
from jinja2 import Environment, Undefined
from jinja2.exceptions import TemplateSyntaxError

from .constants import NoticeWay

logger = logging.getLogger(__name__)


class UndefinedSilently(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return UndefinedSilently()

    def __unicode__(self):
        return ""

    def __str__(self):
        return ""

    __add__ = (
        __radd__
    ) = (
        __mul__
    ) = (
        __rmul__
    ) = (
        __div__
    ) = (
        __rdiv__
    ) = (
        __truediv__
    ) = (
        __rtruediv__
    ) = (
        __floordiv__
    ) = (
        __rfloordiv__
    ) = (
        __mod__
    ) = (
        __rmod__
    ) = (
        __pos__
    ) = (
        __neg__
    ) = (
        __call__
    ) = (
        __getitem__
    ) = (
        __lt__
    ) = (
        __le__
    ) = (
        __gt__
    ) = (
        __ge__
    ) = __int__ = __float__ = __complex__ = __pow__ = __rpow__ = __sub__ = __rsub__ = _fail_with_undefined_error


def jinja2_environment(**options):
    env = Environment(undefined=UndefinedSilently, extensions=["jinja2.ext.i18n"], **options)
    env.install_gettext_translations(translation, newstyle=True)
    return env


class Jinja2Renderer(object):
    """
    Jinja2渲染器
    """

    @staticmethod
    def render(template_value: str, context: dict):
        """
        只支持json和re函数
        """
        return jinja2_environment().from_string(template_value).render({"json": json, "re": re, **context})


def jinja_render(template_value, context):
    """
    支持object的jinja2渲染
    :param context: 上下文
    :param template_value:渲染模板
    :return:
    """
    if isinstance(template_value, str):
        return Jinja2Renderer.render(template_value, context) or template_value
    if isinstance(template_value, dict):
        render_value = {}
        for key, value in template_value.items():
            render_value[key] = jinja_render(value, context)
        return render_value
    if isinstance(template_value, list):
        return [jinja_render(value, context) for value in template_value]
    return template_value


class NoticeRowRenderer:
    """
    行渲染器
    """

    LineTemplateMapping = defaultdict(
        lambda: "{title}{content}",
        {
            "email": '<tr style="background: #FFFFFF;"><td style="color: #979BA5; font-size: 14px; height: 19px; '
                     'vertical-align: text-top;">{title}</td><td style="color: #63656E; font-size: 14px; '
                     'vertical-align: text-top;">{content}</td></tr><tr style="background: #FFFFFF;">'
                     '<td colspan="4" style="height: 20px;"></td></tr>'
        },
    )

    @classmethod
    def format(cls, notice_way: NoticeWay, title: str, content: str) -> str:
        """
        格式化
        :param notice_way: 通知方式
        :param title: 标题
        :param content: 文本
        """
        title = str(title).strip()
        content = str(content).strip()
        if title:
            title += ": "
        if not title and not content:
            return ""
        return cls.LineTemplateMapping[notice_way].format(title=title, content=content)

    @classmethod
    def render_line(cls, line, context):
        """
        使用行模板渲染一行渲染一行
        :param line:
        :param context:
        :return:
        """
        # 是否符合行模板格式
        line = line.strip()
        if not re.match(r"^#.*#", line):
            return line

        title, content = line[1:].split("#", 1)
        return cls.format(context.get("notice_way").value, title=title, content=content)

    @classmethod
    def render(cls, content, context):
        lines = []
        for line in content.splitlines():
            if not line.strip():
                continue
            new_line = cls.render_line(line, context)
            if not new_line.strip():
                continue
            lines.append(new_line)

        return "\n".join(lines)


class CustomTemplateRenderer:
    """
    自定义模板渲染器
    """

    @staticmethod
    def render(content, context):
        action_id = context.get("action").id if context.get("action") else None
        try:
            content_template = Jinja2Renderer.render(context.get("content_template") or "", context)
        except TemplateSyntaxError as error:
            logger.error(
                "$%s render content failed :%s, content_template %s",
                action_id,
                str(error),
                context.get("content_template"),
            )
            content_template = Jinja2Renderer.render(context.get("default_content_template") or "", context)

        alarm_content = NoticeRowRenderer.render(content_template, context)
        if context.get("notice_way") == NoticeWay.EMAIL:
            content = content.replace("\n", "")
        context["user_content"] = alarm_content
        title_content = ""
        try:
            title_content = Jinja2Renderer.render(context.get("title_template") or "", context)
        except TemplateSyntaxError as error:
            logger.error(
                "$%s render title failed :%s, title_template %s", action_id, str(error), context.get("title_template")
            )
        if not title_content:
            # 没有自定义通知标题，用默认模板
            title_content = Jinja2Renderer.render(context.get("default_title_template") or "", context)
        context["user_title"] = title_content
        return content


class CustomOperateTemplateRenderer:
    """
    自定义处理记录模板渲染器
    """

    @staticmethod
    def render(content, context):
        content_template = Jinja2Renderer.render(getattr(context["action_instance"], "content_template", ""), context)
        action_content = NoticeRowRenderer.render(content_template, context)
        context["operate_content"] = action_content
        return content
