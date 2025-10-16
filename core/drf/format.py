import json

from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.settings import api_settings

from apps.logger import logger
from core.exceptions import ParamValidationError


def format_serializer_errors(serializer):
    try:
        __message, cn_message = _format_serializer_errors_core(
            serializer.errors, serializer.fields, serializer.get_initial()
        )
    except Exception as exc_info:  # pylint: disable=broad-except
        logger.warning(gettext("序列化器错误信息格式化失败，原因: %s"), exc_info)
        return serializer.errors
    else:
        return cn_message


def _format_serializer_errors_core(  # pylint: disable=too-many-locals,too-many-branches
    errors, fields, params, prefix="", return_all_errors=True
):
    """
    格式化序列化器的错误，对前端显示更为友好
    :param errors: serializer_errors
    :param fields: 校验的字段
    :param params: 参数
    :param prefix: 错误消息前缀
    :param return_all_errors: 是否返回所有错误消息
    :return:
    """
    message = {}
    cn_message = {}
    for key, field_errors in list(errors.items()):  # pylint: disable=too-many-nested-blocks
        sub_message = []
        try:
            label = fields[key].label
        except (KeyError, AttributeError):
            label = key

        if key == api_settings.NON_FIELD_ERRORS_KEY:
            sub_message.append(";".join(field_errors))
        elif key not in fields:
            sub_message.append(json.dumps(field_errors, ensure_ascii=False))
        else:
            field = fields[key]
            if (
                hasattr(field, "child")
                and isinstance(field_errors, list)
                and len(field_errors) > 0
                and not isinstance(field_errors[0], str)
            ):
                for index, sub_errors in enumerate(field_errors):
                    if sub_errors:
                        sub_format = format_serializer_errors(sub_errors, field.child.fields, params, prefix=prefix)
                        if not return_all_errors:
                            return f"{label}: {sub_format}"
                        temp_message = f"{prefix}第{index + 1}项:"
                        sub_message.append(
                            temp_message + sub_format[0] if isinstance(sub_format, tuple) else sub_format
                        )
            else:
                if isinstance(field_errors, dict):
                    if hasattr(field, "child"):
                        sub_format = format_serializer_errors(field_errors, field.child.fields, params, prefix=prefix)
                    else:
                        sub_format = format_serializer_errors(field_errors, field.fields, params, prefix=prefix)
                    if not return_all_errors:
                        return f"{label}: {sub_format}"
                    sub_message.append(sub_format)
                elif isinstance(field_errors, list):
                    for index, error in enumerate(field_errors):
                        error = error.format(**{key: params.get(key, "")})
                        if len(field_errors) > 1:
                            sub_message.append("{index}.{error}".format(index=index + 1, error=error))
                        else:
                            sub_message.append("{error}".format(error=error))
                        if not return_all_errors:
                            sub_message = ",".join(sub_message)
                            return f"{label}: {sub_message}"
        cn_message[str(label)] = ",".join(
            [str(message[1]) if isinstance(message, tuple) else str(message) for message in sub_message]
        )
        message[key] = sub_message
        break

    message = json.dumps(message, ensure_ascii=False)
    cn_message = json.dumps(cn_message, ensure_ascii=False)
    return message, cn_message


def custom_params_valid(serializer, params, instance=None, many=False, partial=False):
    """序列化器自定义数据校验"""
    _serializer = serializer(data=params, many=many, instance=instance, partial=partial)
    try:
        _serializer.is_valid(raise_exception=True)
    except serializers.ValidationError:
        msg_tuple = format_serializer_errors(_serializer.errors, _serializer.fields, params)
        raise ParamValidationError(msg_tuple)
    if many:
        return list(_serializer.validated_data)

    return dict(_serializer.validated_data)
