import uuid

from django.conf import settings
from django.dispatch import Signal
from django.utils.deprecation import MiddlewareMixin

from core.exceptions import AccessForbidden, ServerBlueException
from core.utils.local import inject_request_id, release_request_local, request_local

# since each thread has its own greenlet we can just use those as identifiers
# for the context.  If greenlets are not available we fall back to the
# current thread ident depending on where it is.
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class AccessorSignal(Signal):
    """"""

    allowed_receivers = [
        "core.utils.request_provider.RequestProvider",
    ]

    def __init__(self, providing_args=None):
        super().__init__(providing_args)

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        """注册一个观察者，观察者必须在白名单内 .

        params receiver: 观察者执行的方法
        """
        # 指定观察者必须是
        receiver_name = ".".join([receiver.__class__.__module__, receiver.__class__.__name__])
        if receiver_name not in self.allowed_receivers:
            raise AccessForbidden("%s is not allowed to connect" % receiver_name)
        super().connect(receiver, sender, weak, dispatch_uid)


request_accessor = AccessorSignal()


class RequestProvider(MiddlewareMixin):
    """
    @summary: request事件接收者
    """

    _instance = None

    def __new__(cls, get_response):
        """实现一个单例模式 ."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, get_response):
        super().__init__(get_response)
        self._request_pool = {}
        # 将中间件注册为观察者
        request_accessor.connect(self)

    def process_request(self, request):
        # 判断请求的来源
        request.is_mobile = lambda: bool(settings.RE_MOBILE.search(request.META.get("HTTP_USER_AGENT", "")))

        # 是否为合法的RIO请求
        request.is_rio = lambda: bool(
            request.META.get("HTTP_STAFFNAME", "")
            and getattr(settings, "RIO_TOKEN", None)
            and settings.RE_WECHAT.search(request.META.get("HTTP_USER_AGENT", ""))
        )

        # 是否为合法 WEIXIN 请求，必须符合两个条件，wx 客户端 & WX PAAS 域名
        request_origin_url = "{}://{}".format(request.scheme, request.get_host())
        request.is_wechat = lambda: (
            bool(settings.RE_WECHAT.search(request.META.get("HTTP_USER_AGENT", "")))
            and request_origin_url == settings.WEIXIN_BK_URL
            and not request.is_rio()
        )

        # JWT请求
        request.is_bk_jwt = lambda: bool(request.META.get("HTTP_X_BKAPI_JWT", ""))

        # 将当前请求加入到线程变量中，并生成 request_id
        self._request_pool[get_ident()] = request
        request_local.request = request
        inject_request_id(request_local, request)
        return None

    def process_response(self, request, response):
        # 释放线程变量
        assert request is self._request_pool.pop(get_ident())
        release_request_local()
        return response

    def __call__(self, *args, **kwargs):
        """
        1）接受 signal 请求响应，
        2）继承 MiddlewareMixin.__call__ 兼容 djagno 1.10 之前中间件
        """
        from_signal = kwargs.get("from_signal", False)
        if from_signal:
            return self.get_request(**kwargs)
        else:
            return super().__call__(args[0])

    def get_request(self, **kwargs):
        sender = kwargs.get("sender")
        if sender is None:
            sender = get_ident()
        if sender not in self._request_pool:
            raise ServerBlueException("get_request can't be called in a new thread.")
        # 获得当前线程的 request 对象
        return self._request_pool[sender]


def get_request():
    """通知所有的观察者，执行中间件的 RequestProvider.__call__(*args, **kwargs) ."""
    return request_accessor.send(get_ident(), from_signal=True)[0][1]


def get_x_request_id():
    x_request_id = ""
    http_request = get_request()
    if hasattr(http_request, "META"):
        meta = http_request.META
        x_request_id = meta.get("HTTP_X_REQUEST_ID", "") if isinstance(meta, dict) else ""
    return x_request_id


def get_local_request():
    return getattr(request_local, "request", None)


def get_local_request_id():
    return getattr(request_local, "request_id", str(uuid.uuid4()))


def get_or_create_local_request_id():
    if not hasattr(request_local, "request_id"):
        request_local.request_id = str(uuid.uuid4())
    return request_local.request_id


def get_request_username():
    operator = None
    try:
        operator = get_local_request().user.username
    except (IndexError, AttributeError):
        if getattr(settings, "NON_REQUEST_USERNAME_PROVIDER"):
            operator = settings.NON_REQUEST_USERNAME_PROVIDER()

    return operator
