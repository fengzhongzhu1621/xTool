from .hookimpl_marker import HookimplMarker

hookimpl = HookimplMarker("my_project")


@hookimpl(wrapper=True, tryfirst=True)
def my_hook_implementation(*args, **kwargs):
    # Your hook implementation logic here
    pass


def test_my_hook_attribute():
    my_hook_implementation()
    assert my_hook_implementation.my_project_impl == {
        'optionalhook': False,
        'specname': None,
        'tryfirst': True,
        'trylast': False,
        'wrapper': True,
    }
