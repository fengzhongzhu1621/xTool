from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy

from apps.global_conf.resources import GetGlobalConfResource
from xTool.utils import register_choices


class TestGetGlobalConfResource:

    @register_choices("person_gender")
    class PersonGender(TextChoices):
        MALE = "MALE", _lazy("男")
        FEMALE = "FEMAIL", _lazy("女")

    def test_perform_request(self):
        actual = GetGlobalConfResource()()
        expect = {
            "person_gender": [
                {"id": "MALE", "name": "男"},
                {"id": "FEMAIL", "name": "女"},
            ]
        }
        assert actual == expect
