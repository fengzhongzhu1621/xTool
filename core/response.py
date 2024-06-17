from django.http.response import JsonResponse
from rest_framework.response import Response


def fail_response(code, message, request_id):
    """带request_id的失败响应 ."""
    response = JsonResponse({"code": code, "result": False, "message": message, "data": None})
    response["X-Request-Id"] = request_id
    return response


def success_response(data, request_id):
    """带request_id的成功响应 ."""
    response = JsonResponse({"code": 0, "result": True, "message": "", "data": data})
    response["X-Request-Id"] = request_id
    return response


class SuccessResponse(Response):
    """
    标准响应成功的返回, SuccessResponse(data)或者SuccessResponse(data=data)
    (1)默认code返回2000, 不支持指定其他返回码
    """

    def __init__(
        self,
        data=None,
        msg="success",
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        page=1,
        limit=1,
        total=1,
    ):
        std_data = {"code": 2000, "page": page, "limit": limit, "total": total, "data": data, "msg": msg}
        super().__init__(std_data, status, template_name, headers, exception, content_type)


class DetailResponse(Response):
    """
    不包含分页信息的接口返回,主要用于单条数据查询
    (1)默认code返回2000, 不支持指定其他返回码
    """

    def __init__(
        self,
        data=None,
        msg="success",
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        std_data = {"code": 2000, "data": data, "msg": msg}
        super().__init__(std_data, status, template_name, headers, exception, content_type)


class ErrorResponse(Response):
    """
    标准响应错误的返回,ErrorResponse(msg='xxx')
    (1)默认错误码返回400, 也可以指定其他返回码:ErrorResponse(code=xxx)
    """

    def __init__(
        self,
        data=None,
        msg="error",
        code=400,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        std_data = {"code": code, "data": data, "msg": msg}
        super().__init__(std_data, status, template_name, headers, exception, content_type)
