import pytest

from rest_framework import serializers
from rest_framework.fields import empty


class SerializerRequiredIsTrueAndAllowBlankIsFlse(serializers.Serializer):
    field = serializers.CharField(required=True, allow_blank=False)


class SerializerRequiredIsTrueAndAllowBlankIsTrue(serializers.Serializer):
    field = serializers.CharField(required=True, allow_blank=True)


class SerializerRequiredIsFalseAndAllowBlankIsTrue(serializers.Serializer):
    field = serializers.CharField(required=False, allow_blank=True)


class SerializerRequiredIsFalseAndAllowBlankIsFalse(serializers.Serializer):
    field = serializers.CharField(required=False, allow_blank=False)


class SerializerRequiredIsTrueAndAllowNoneIsFlse(serializers.Serializer):
    field = serializers.CharField(required=True, allow_null=False)


class SerializerRequiredIsTrueAndAllowNoneIsTrue(serializers.Serializer):
    field = serializers.CharField(required=True, allow_null=True)


class SerializerRequiredIsFalseAndAllowNoneIsTrue(serializers.Serializer):
    field = serializers.CharField(required=False, allow_null=True)


class SerializerRequiredIsFalseAndAllowNoneIsFalse(serializers.Serializer):
    field = serializers.CharField(required=False, allow_null=False)


class TestSerializer:

    def test_field(self):
        field = serializers.IntegerField()
        assert field.read_only is False
        assert field.required is True
        assert field.allow_null is False
        with pytest.raises(AttributeError):
            assert field.allow_blank
        assert field.default == empty

        field = serializers.CharField()
        assert field.read_only is False
        assert field.required is True
        assert field.allow_null is False
        assert field.allow_blank is False
        assert field.default == empty

    def test_read_only(self):
        class Serializer(serializers.Serializer):
            field = serializers.IntegerField(read_only=True)

        data = {
            "field": 1
        }

        serializer = Serializer(data=data)
        assert serializer.initial_data == data

        assert serializer.is_valid()
        assert serializer.data == {}

        serializer.field = 2
        assert serializer.data == {}

    @pytest.mark.parametrize("data,output,is_valid", [
        [{"field": 1}, {'field': '1'}, True],
        [{"field": 0}, {"field": '0'}, True],
        [{}, {}, False],
        [{"field": None}, {"field": None}, False],
        [{"field": ""}, {"field": ""}, False],
    ])
    def test_char_field_required(self, data, output, is_valid):
        class Serializer(serializers.Serializer):
            field = serializers.CharField(required=True)

        serializer = Serializer(data=data)
        assert serializer.initial_data == data
        assert serializer.is_valid() is is_valid
        assert serializer.data == output

    @pytest.mark.parametrize("data,output,is_valid", [
        [{"field": 1}, {'field': 1}, True],
        [{"field": 0}, {"field": 0}, True],
        [{"field": '0'}, {"field": 0}, True],
        [{}, {}, False],
        [{"field": None}, {"field": None}, False],
        [{"field": ""}, {"field": ""}, False],
    ])
    def test_int_field_required(self, data, output, is_valid):
        class Serializer(serializers.Serializer):
            field = serializers.IntegerField(required=True)

        serializer = Serializer(data=data)
        assert serializer.is_valid() is is_valid
        assert serializer.data == output

    @pytest.mark.parametrize("serializer_cls,data,output,is_valid", [
        [SerializerRequiredIsTrueAndAllowBlankIsFlse, {"field": 1}, {'field': '1'}, True],
        [SerializerRequiredIsTrueAndAllowBlankIsFlse, {"field": 0}, {"field": '0'}, True],
        [SerializerRequiredIsTrueAndAllowBlankIsFlse, {"field": ""}, {"field": ""}, False],
        [SerializerRequiredIsTrueAndAllowBlankIsFlse, {}, {}, False],
        [SerializerRequiredIsTrueAndAllowBlankIsFlse, {"field": None}, {"field": None}, False],

        [SerializerRequiredIsTrueAndAllowBlankIsTrue, {"field": 1}, {'field': '1'}, True],
        [SerializerRequiredIsTrueAndAllowBlankIsTrue, {"field": 0}, {"field": '0'}, True],
        [SerializerRequiredIsTrueAndAllowBlankIsTrue, {"field": ""}, {"field": ""}, True],
        [SerializerRequiredIsTrueAndAllowBlankIsTrue, {}, {}, False],
        [SerializerRequiredIsTrueAndAllowBlankIsTrue, {"field": None}, {"field": None}, False],

        [SerializerRequiredIsFalseAndAllowBlankIsTrue, {"field": 1}, {'field': '1'}, True],
        [SerializerRequiredIsFalseAndAllowBlankIsTrue, {"field": 0}, {"field": '0'}, True],
        [SerializerRequiredIsFalseAndAllowBlankIsTrue, {"field": ""}, {"field": ""}, True],
        [SerializerRequiredIsFalseAndAllowBlankIsTrue, {}, {}, True],
        [SerializerRequiredIsFalseAndAllowBlankIsTrue, {"field": None}, {"field": None}, False],

        [SerializerRequiredIsFalseAndAllowBlankIsFalse, {"field": 1}, {'field': '1'}, True],
        [SerializerRequiredIsFalseAndAllowBlankIsFalse, {"field": 0}, {"field": '0'}, True],
        [SerializerRequiredIsFalseAndAllowBlankIsFalse, {"field": ""}, {"field": ""}, False],
        [SerializerRequiredIsFalseAndAllowBlankIsFalse, {}, {}, True],
        [SerializerRequiredIsFalseAndAllowBlankIsFalse, {"field": None}, {"field": None}, False],
    ])
    def test_allow_blank(self, serializer_cls, data, output, is_valid):
        serializer = serializer_cls(data=data)
        assert serializer.is_valid() is is_valid
        assert serializer.data == output

    @pytest.mark.parametrize("serializer_cls,data,output,is_valid", [
        [SerializerRequiredIsTrueAndAllowNoneIsFlse, {"field": 1}, {'field': '1'}, True],
        [SerializerRequiredIsTrueAndAllowNoneIsFlse, {"field": 0}, {"field": '0'}, True],
        [SerializerRequiredIsTrueAndAllowNoneIsFlse, {"field": ""}, {"field": ""}, False],
        [SerializerRequiredIsTrueAndAllowNoneIsFlse, {}, {}, False],
        [SerializerRequiredIsTrueAndAllowNoneIsFlse, {"field": None}, {"field": None}, False],

        [SerializerRequiredIsTrueAndAllowNoneIsTrue, {"field": 1}, {'field': '1'}, True],
        [SerializerRequiredIsTrueAndAllowNoneIsTrue, {"field": 0}, {"field": '0'}, True],
        [SerializerRequiredIsTrueAndAllowNoneIsTrue, {"field": ""}, {"field": ""}, False],
        [SerializerRequiredIsTrueAndAllowNoneIsTrue, {}, {}, False],
        [SerializerRequiredIsTrueAndAllowNoneIsTrue, {"field": None}, {"field": None}, True],

        [SerializerRequiredIsFalseAndAllowNoneIsTrue, {"field": 1}, {'field': '1'}, True],
        [SerializerRequiredIsFalseAndAllowNoneIsTrue, {"field": 0}, {"field": '0'}, True],
        [SerializerRequiredIsFalseAndAllowNoneIsTrue, {"field": ""}, {"field": ""}, False],
        [SerializerRequiredIsFalseAndAllowNoneIsTrue, {}, {"field": None}, True],
        [SerializerRequiredIsFalseAndAllowNoneIsTrue, {"field": None}, {"field": None}, True],

        [SerializerRequiredIsFalseAndAllowNoneIsFalse, {"field": 1}, {'field': '1'}, True],
        [SerializerRequiredIsFalseAndAllowNoneIsFalse, {"field": 0}, {"field": '0'}, True],
        [SerializerRequiredIsFalseAndAllowNoneIsFalse, {"field": ""}, {"field": ""}, False],
        [SerializerRequiredIsFalseAndAllowNoneIsFalse, {}, {}, True],
        [SerializerRequiredIsFalseAndAllowNoneIsFalse, {"field": None}, {"field": None}, False],
    ])
    def test_allow_null(self, serializer_cls, data, output, is_valid):
        serializer = serializer_cls(data=data)
        assert serializer.is_valid() is is_valid
        assert serializer.data == output
