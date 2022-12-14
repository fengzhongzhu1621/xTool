# -*- coding: utf-8 -*-
import logging
from os import path

from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from .render import CustomTemplateRenderer, Jinja2Renderer, CustomOperateTemplateRenderer

logger = logging.getLogger("notice")


class AlarmNoticeTemplate(object):
    """
    通知模板
    """

    Renderers = [
        CustomTemplateRenderer,
        Jinja2Renderer,
    ]

    def __init__(self, template_path=None, template_content=None):
        """
        :param template_path: 模板路径
        :type template_path: str or unicode
        """
        if template_path:
            self.template = self.get_template(template_path)
        elif template_content is not None:
            self.template = template_content
        else:
            self.template = ""

    def render(self, context):
        """
        模板渲染
        :param context: 上下文
        :return: 渲染后内容
        :rtype: str
        """
        template_message = self.template
        for renderer in self.Renderers:
            template_message = renderer.render(template_message, context)
        return template_message

    @staticmethod
    def get_template_source(template_path):
        """
        获取模板文本
        :param template_path: 模板路径
        :return: 模板消息
        """
        raw_template = get_template(template_path)
        with open(raw_template.template.filename, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def get_default_path(template_path):
        """
        获取默认模板路径
        :param template_path: 模板路径
        """
        dir_path, filename = path.split(template_path)
        name, ext = path.splitext(filename)
        names = name.split("_")
        name = f"default_{names[-1]}{ext}"
        return path.join(dir_path, name)

    @classmethod
    def get_template(cls, template_path):
        """
        查找模板
        :param template_path: 模板路径
        """
        if not template_path:
            return ""

        try:
            return cls.get_template_source(template_path)
        except TemplateDoesNotExist:
            logger.info("use empty template because {} not exists".format(template_path))
        except Exception as e:
            logger.info("use default template because {} load fail, {}".format(template_path, e))
        template_path = cls.get_default_path(template_path)

        try:
            return cls.get_template_source(template_path)
        except TemplateDoesNotExist:
            logger.info("use empty template because {} not exists".format(template_path))
        except Exception as e:
            logger.info("use empty template because {} load fail, {}".format(template_path, e))
        return ""


class AlarmOperateNoticeTemplate(AlarmNoticeTemplate):
    Renderers = [
        CustomTemplateRenderer,
        CustomOperateTemplateRenderer,
        Jinja2Renderer,
    ]
