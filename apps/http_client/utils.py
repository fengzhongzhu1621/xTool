from typing import Dict

from apps.http_client.models import RequestApiConfig
from core.cache import cache_ten_minute


@cache_ten_minute("http_client:fetch_request_api_config:{}:{}")
def fetch_request_api_config(system_code: str, api_code: str) -> Dict:
    instance = (
        RequestApiConfig.objects.select_related("system")
        .filter(
            code=api_code,
            system__code=system_code,
        )
        .first()
    )
    if not instance:
        return {}
    config = instance.to_json()

    return config
