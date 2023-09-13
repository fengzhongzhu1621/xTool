# -*- coding: utf-8 -*-

import json
import re
from typing import Dict, List, Union

from django.utils import translation
from jinja2 import Environment, FileSystemLoader


def jinja2_environment(**options: Dict) -> Environment:
    """创建jinja2的环境执行环境 ."""
    env = Environment(extensions=["jinja2.ext.i18n"], **options)
    env.install_gettext_translations(translation, newstyle=True)
    return env


class Jinja2Renderer:
    """
    Jinja2渲染器
    """

    @staticmethod
    def render(template_value: str, context: dict) -> str:
        """
        只支持json和re函数
        """
        return (
            jinja2_environment()
            .from_string(template_value)
            .render({"json": json, "re": re, **context})
        )


def jinja_render(template_value, context) -> Union[str, Dict, List]:
    """使用jinja渲染对象 ."""
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


class Jinja2FileTemplateRenderer:
    """
    Jinja2文件渲染器
    """

    def __init__(self, template_dir: str, **options) -> None:
        self.template_dir = template_dir
        self.env = jinja2_environment(**options)
        self.env.loader = FileSystemLoader(self.template_dir, encoding="utf-8")

    def render(self, template_file: str, context: dict) -> str:
        """渲染文件内容 ."""
        template = self.env.get_template(template_file)
        render_value = template.render({"json": json, "re": re, **context})
        return render_value
