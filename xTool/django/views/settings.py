# -*- coding: utf-8 -*-

import json
from django.conf import settings
from django.http import HttpResponseForbidden
from django.http.response import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder


def settings(request):
    """
    查看所有的settings配置内容
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    data = {}
    for key in sorted(dir(settings)):
        if not key or key.startswith("_"):
            continue
        value = getattr(settings, key)
        try:
            json.dumps(value, cls=DjangoJSONEncoder)
        except Exception:  # noqa
            continue
        data[key] = value

    return JsonResponse({"code": 0, "result": True, "message": "", "data": data})
