from typing import Any, List, Literal, Optional, TypeVar

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic.alias_generators import to_camel

DataT = TypeVar("DataT")


class User(BaseModel):
    id: int
    name: str = "Jane Doe"


class Foo(BaseModel):
    count: int
    size: Optional[float] = None


class Bar(BaseModel):
    apple: str = "x"
    banana: str = "y"


class Spam(BaseModel):
    foo: Foo
    bars: List[Bar]


class Parent(BaseModel):
    """额外的属性,有三种处理方法。

    ignore，忽略。
    forbid，抛出异常。
    allow，保留。
    """

    model_config = ConfigDict(extra="allow")


class Model(Parent):
    x: str


class Voice(BaseModel):
    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include=None,
        exclude=None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
        return self.__pydantic_serializer__.to_python(
            self,
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=True,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=True,
            round_trip=round_trip,
            warnings=warnings,
        )

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    name: str = Field(alias="username")
    language_code: str = Field(
        alias="langcode",
    )


class TestBaseModel:
    def test_user(self):
        """测试验证错误抛出 ValidationError 异常 ."""
        user = User(id="123")
        assert user.id == 123
        assert isinstance(user.id, int)
        assert user.name == "Jane Doe"
        assert user.model_fields_set == {"id"}
        assert user.model_dump() == {"id": 123, "name": "Jane Doe"}
        assert user.dict() == {"id": 123, "name": "Jane Doe"}
        user.id = 321
        assert user.id == 321

        with pytest.raises(ValidationError):
            User()


class TestNestedModel:
    def test_spam(self):
        m = Spam(foo={"count": 4}, bars=[{"apple": "x1"}, {"apple": "x2"}])
        assert m.model_dump() == {
            "foo": {"count": 4, "size": None},
            "bars": [{"apple": "x1", "banana": "y"}, {"apple": "x2", "banana": "y"}],
        }


class TestConfigDict:
    def test_merge_parent(self):
        """子类和父类的model_config会合并 ."""
        m = Model(x="foo", y="bar")
        assert m.model_dump() == {"x": "foo", "y": "bar"}


class TestAlias:
    """
    alias_generator指定命名转换方式。
    默认情况下，指定alias_generator之后，输入的值也需要驼峰命名为key，populate_by_name=True表示同时支持原本属性名以及驼峰命名。
    默认情况下，Field的alias优先级高于alias_generator，如需设置后者的优先级更高，alias_priority=1。
    重写model_dump方法，设置alias为true。
    """

    def test_alias_generator(self):
        voice = Voice(username="Filiz", langcode="tr-TR")
        assert voice.language_code == "tr-TR"
        assert voice.model_dump() == {"username": "Filiz", "langcode": "tr-TR"}
