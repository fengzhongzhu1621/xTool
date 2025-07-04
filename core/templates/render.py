import json
import re
from typing import Dict, List, Union

from django.utils import translation
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment as Environment


def jinja2_environment(**options: Dict) -> Environment:
    """
    创建并配置Jinja2环境

    参数:
        **options: 传递给Jinja2环境的额外选项

    返回:
        配置好的Jinja2环境实例

    功能:
        - 添加i18n扩展支持国际化
        - 安装Django的翻译功能
        - 启用新的gettext样式
    """
    env = Environment(extensions=["jinja2.ext.i18n"], **options)
    env.install_gettext_translations(translation, newstyle=True)
    return env


class Jinja2Renderer:
    """
    Jinja2字符串模板渲染器

    提供简单的字符串模板渲染功能，支持JSON和re模块的使用
    """

    @staticmethod
    def render(template_value: str, context: dict) -> str:
        """
        渲染Jinja2字符串模板

        参数:
            template_value: 要渲染的Jinja2模板字符串
            context: 渲染上下文变量字典

        返回:
            渲染后的字符串

        注意:
            此方法仅支持在模板中使用json和re模块
        """
        # 创建基础环境并添加必要的模块到全局变量
        env = jinja2_environment()
        # 渲染模板，将json和re模块以及用户提供的上下文一起传入
        return env.from_string(template_value).render({"json": json, "re": re, **context})


def jinja_render(template_value, context) -> Union[str, Dict, List]:
    """
    递归渲染Jinja2模板

    支持渲染字符串、字典和列表类型的模板值，递归处理嵌套结构

    参数:
        template_value: 要渲染的模板值(可以是字符串、字典或列表)
        context: 渲染上下文变量字典

    返回:
        渲染后的值(保持原始类型)

    处理逻辑:
        - 如果是字符串: 使用Jinja2Renderer渲染
        - 如果是字典: 递归渲染每个值
        - 如果是列表: 递归渲染每个元素
        - 其他类型: 直接返回原值
    """
    if isinstance(template_value, str):
        # 渲染字符串模板，如果渲染结果为None则返回原模板值
        return Jinja2Renderer.render(template_value, context) or template_value
    if isinstance(template_value, dict):
        # 递归渲染字典中的每个值
        render_value = {}
        for key, value in template_value.items():
            render_value[key] = jinja_render(value, context)
        return render_value
    if isinstance(template_value, list):
        # 递归渲染列表中的每个元素
        return [jinja_render(value, context) for value in template_value]
    # 非字符串、字典或列表类型直接返回
    return template_value


class Jinja2FileTemplateRenderer:
    """
    Jinja2文件模板渲染器

    从文件系统加载模板文件并进行渲染
    """

    def __init__(self, template_dir: str, **options) -> None:
        """
        初始化文件模板渲染器

        参数:
            template_dir: 模板文件所在的目录路径
            **options: 传递给Jinja2环境的额外选项
        """
        self.template_dir = template_dir
        # 创建Jinja2环境
        self.env = jinja2_environment(**options)
        # 配置文件系统加载器，指定模板目录和编码
        self.env.loader = FileSystemLoader(self.template_dir, encoding="utf-8")

    def render(self, template_file: str, context: dict) -> str:
        """
        渲染指定模板文件

        参数:
            template_file: 模板文件名(相对于template_dir)
            context: 渲染上下文变量字典

        返回:
            渲染后的字符串
        """
        # 从环境加载模板文件
        template = self.env.get_template(template_file)
        # 渲染模板，将json和re模块以及用户提供的上下文一起传入
        render_value = template.render({"json": json, "re": re, **context})
        return render_value
