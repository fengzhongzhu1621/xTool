# -*- coding: utf-8 -*-

from django.http.response import JsonResponse


def fail_response(code, message, request_id):
    """带request_id的失败响应 ."""
    response = JsonResponse(
        {"code": code, "result": False, "message": message, "data": None}
    )
    response["X-Request-Id"] = request_id
    return response


def success_response(data, request_id):
    """带request_id的成功响应 ."""
    response = JsonResponse({"code": 0, "result": True, "message": "", "data": data})
    response["X-Request-Id"] = request_id
    return response
