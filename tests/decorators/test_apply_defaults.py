#coding: utf-8

from xTool.decorators.apply_defaults import apply_defaults

class Model(object):
    pass

class BashOperator(object):
    template_fields = ('bash_command', 'env')
    template_ext = ('.sh', '.bash',)
    ui_color = '#f0ede4'

    @apply_defaults
    def __init__(
            self,
            bash_command,
            xcom_push=False,
            env=None,
            output_encoding='utf-8',
            *args, **kwargs):

        self.bash_command = bash_command
        self.env = env
        self.xcom_push_flag = xcom_push
        self.output_encoding = output_encoding
        self.args = args
        self.kwargs = kwargs

def test_apply_defaults():
    bash_operator = BashOperator(bash_command="ls")
    assert bash_operator.args == ()
    assert bash_operator.kwargs == {'params': {}}

    model = Model()
    model.default_args = {
        'a': 1,
        'env': 2,
    }
    model.params = {
        'c': 3,
    }
    args = ()
    kwargs = {
        'model': model,
        'default_args': {
            'params': {
                'b': 22,
                'c': 4
            },
            'e': 5,
            'env': 8
        },
        'params': {
            'g': 7,
            'c': 5,
        }
    }

    bash_operator = BashOperator(
        bash_command="ls", 
        *args, **kwargs)
    assert bash_operator.args == ()
    """{
        'model': <test_apply_defaults.Model object at 0x027CA170>, 
        'default_args': {'e': 5, 'env': 8}, 
        'bash_command': 'ls', 
        'params': {'g': 7, 'b': 22, 'c': 4}, 
        'env': 8}
    """
    kwargs = bash_operator.kwargs
    assert kwargs['params'] == {'b': 22, 'c': 4, 'g': 7}
    assert kwargs['default_args'] == {'env': 8, 'e': 5}
    assert bash_operator.env == 8
    assert bash_operator.bash_command == 'ls'
