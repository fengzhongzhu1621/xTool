import copy
import re
from typing import Any, List

from mako import codegen, lexer
from mako.exceptions import MakoException
from mako.template import Template as MakoTemplate

from xTool.log import logger
from xTool.templates.exceptions import ForbiddenMakoTemplateException

__all__ = [
    "Template",
]


# find mako template(format is ${xxx}，and ${}# not in xxx, # may raise
# memory error)
TEMPLATE_PATTERN = re.compile(r"\${[^${}#]+}")


def format_constant_key(key):
    return "${%s}" % key


format_var_key = format_constant_key


def deformat_constant_key(key):
    return key[2:-1]


deformat_var_key = deformat_constant_key


class Template:
    def __init__(self, data: Any, template_validator=None):
        self.data = data
        self.template_validator = template_validator

    def render(self, context: dict, raise_error: bool = False) -> Any:
        """渲染当前模板

        Examples:

            string = a ${b + c} d
            context = {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": 4,
            }
        """
        data = self.data
        if isinstance(data, str):
            return self._render_string(data, context, raise_error=raise_error)
        if isinstance(data, list):
            new_data = [""] * len(data)
            for index, item in enumerate(data):
                new_data[index] = Template(copy.deepcopy(item)).render(context)
            return new_data
        if isinstance(data, tuple):
            new_data = [""] * len(data)
            for index, item in enumerate(data):
                new_data[index] = Template(copy.deepcopy(item)).render(context)
            return tuple(new_data)
        if isinstance(data, dict):
            # TODO 改变了data的值
            for key, value in list(data.items()):
                data[key] = Template(copy.deepcopy(value)).render(context)
            return data
        return data

    @staticmethod
    def _get_string_templates(string: str) -> List[str]:
        """获得所有的模版字符串表达式${xxx} ."""
        return list(set(TEMPLATE_PATTERN.findall(string)))

    @staticmethod
    def _get_template_reference(template: str) -> List[str]:
        """获得模版字符${value}中的value字符串

        exmaples:

            ${a and b or c} -> ['c', 'b', 'a']
        """
        lex = lexer.Lexer(template)

        try:
            node = lex.parse()
        except MakoException as ex:
            logger.warning("pipeline get template[{}] reference error[{}]".format(template, ex))
            return []

        # Dummy compiler. _Identifiers class requires one
        # but only interested in the reserved_names field
        def compiler():
            return None

        compiler.reserved_names = set()
        identifiers = codegen._Identifiers(compiler, node)

        return list(identifiers.undeclared)

    def _render_string(self, string: str, context: dict, raise_error: bool = False) -> Any:
        """使用参数的值填充模版字符串 .

        Examples:

            string = a ${b + c} d
            context = {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": 4,
            }
        """
        if not isinstance(string, str):
            return string
        # 获得所有的模版字符串表达式${xxx}
        # a ${b + c} d => ["${b + c }"]
        templates = self.__class__._get_string_templates(string)

        # TODO keep render return object, here only process simple situation
        # 如果模版字符串只有一个单参数，即格式为 string为 ${a}，这种情况可能返回一个非字符串对象
        if len(templates) == 1 and templates[0] == string and deformat_var_key(string) in context:
            return context[deformat_var_key(string)]

        for tpl in templates:
            if self.template_validator:
                try:
                    self.template_validator(tpl)
                except ForbiddenMakoTemplateException as exec_info:
                    logger.error("forbidden template: {}, exception: {}".format(tpl, exec_info))
                    raise
                except Exception:  # pylint: disable=broad-except
                    logger.exception("{} safety check error.".format(tpl))
                    raise
            resolved = self.__class__._render_template(tpl, context, raise_error=raise_error)
            # 将模版字符串中的${xxx}，替换为真实的值
            string = string.replace(tpl, resolved)
        return string

    @classmethod
    def _render_template(cls, template: str, context: dict, raise_error: bool = False) -> str:
        """
        使用特定上下文渲染指定模板

        :param template: 模板
        :type template: Any
        :param context: 上下文
        :type context: dict
        :raises TypeError: [description]
        :return: [description]
        :rtype: str

        example:

            template = "${b + c }"
            context = {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": 4,
            }

        """
        data = {}
        data.update(context)
        if not isinstance(template, str):
            raise TypeError("constant resolve error, template[%s] is not a string" % template)
        try:
            # 添加允许的第三方库，注意库的安全性问题
            template_obj = MakoTemplate(template)
        except (MakoException, SyntaxError) as exc_info:
            err_message = "resolve template[{}] error[{}]".format(template, exc_info)
            logger.error(err_message)
            if raise_error:
                raise MakoException(exc_info)
            return template
        try:
            resolved = template_obj.render_unicode(**data)
        except (
            NameError,
            TypeError,
            KeyError,
        ) as exc_info:  # pylint: disable=broad-except
            err_message = "constant content({}) is invalid, error: {}".format(template, exc_info)
            logger.warning(err_message)
            if raise_error:
                raise MakoException(err_message)
            return template
        except AttributeError as exc_info:
            # lazy Variable resolve failed before execution
            err_message = "constant content is invalid with error [%s]" % exc_info
            logger.error(err_message)
            if raise_error:
                raise MakoException(err_message)
            return template
        else:
            return resolved
