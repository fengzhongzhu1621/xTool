from .exceptions import MakoResultIsNotBoolTypeException
from .template import format_constant_key, deformat_constant_key, Template


def bool_mako_boolrule_result(evaluate, result):
    """将mako模版的渲染结果转化为bool类型 ."""
    if result in ["True", "1", 1, True]:
        return True
    if result in ["None", "False", "0", "0.0", 0, False]:
        return False
    raise MakoResultIsNotBoolTypeException("条件表达式的执行结果是 {}, 不是bool类型".format(result))


class MakoBoolRule:

    def __init__(self, evaluate):
        evaluate = evaluate.strip()
        if not evaluate.startswith("${"):
            self.verify_evaluate = evaluate
            evaluate = format_constant_key(evaluate)
        else:
            self.verify_evaluate = deformat_constant_key(evaluate)
        self.evaluate = evaluate

    def test(self, context=None):
        context = context if context else {}
        deformatted_data = {deformat_constant_key(key): value for key, value in context.items()}
        evaluate = self.evaluate
        for line_char in ["\r", "\n", "\t"]:
            if line_char in self.verify_evaluate:
                raise MakoResultIsNotBoolTypeException("条件表达式不能包含Tab、回车和换行字符")

        result = Template.resolve_template(evaluate, deformatted_data).strip()
        return bool_mako_boolrule_result(evaluate, result)
