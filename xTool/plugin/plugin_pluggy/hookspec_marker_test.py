from .hookspec_marker import HookspecMarker

hookspec = HookspecMarker("my_project")


@hookspec
def my_hook() -> str:
    """A simple hook specification."""


def test_my_hook_attribute():
    my_hook()
    assert my_hook.my_project_spec == {
        "firstresult": False,
        "historic": False,
        "warn_on_impl": None,
        "warn_on_impl_args": None,
    }
