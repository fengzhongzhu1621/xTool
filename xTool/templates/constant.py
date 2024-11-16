from typing import Any, List

from .template import Template


class ConstantTemplate(Template):
    def __init__(self, data: Any, template_validator=None):
        super().__init__(data, template_validator=template_validator)

    @classmethod
    def get_template_reference(cls, template: str) -> List[str]:
        """获得模版字符${value}中的value字符串 .

        Examples:

            ${a and b or c} -> ['c', 'b', 'a']
        """
        return cls._get_template_reference(template)

    def resolve_string(self, string: str, context: dict, raise_error: bool = False) -> Any:
        """使用参数的值填充模版字符串 ."""
        return self._render_string(string, context, raise_error=raise_error)

    @classmethod
    def resolve_template(cls, template: str, context: dict, raise_error: bool = False) -> str:
        return cls._render_template(template, context, raise_error=raise_error)
