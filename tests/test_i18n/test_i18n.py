from xTool.i18n import lazy_gettext as _


def test_lazy_gettext():
    msg = _("Hello")
    assert msg == "Hello"
