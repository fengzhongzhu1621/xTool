# -*- coding: utf-8 -*-


class HealthzHandler:
    """
    HealthzHandler
    """

    @classmethod
    def healthz(cls) -> dict:
        result = {"healthy": True}
        return result
