class HealthzHandler:
    """用于拨测 ."""

    @classmethod
    def healthz(cls) -> dict:
        result = {"healthy": True}
        return result
