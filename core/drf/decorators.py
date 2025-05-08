try:
    from rest_framework.decorators import detail_route, list_route
except ImportError:
    # 兼容新版本 DRF 缺失 list_route, detail_route 的情况
    from rest_framework.decorators import action as viewset_action

    def list_route(**kwargs):
        kwargs["detail"] = False
        return viewset_action(**kwargs)

    def detail_route(**kwargs):
        kwargs["detail"] = True
        return viewset_action(**kwargs)
