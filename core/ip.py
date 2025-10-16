import requests
from django.conf import settings


def get_ip_analysis(ip: str):
    """
    获取ip详细概略
    """
    url = "https://ip.django-vue-admin.com/ip/analysis"

    data = {
        "continent": "",
        "country": "",
        "province": "",
        "city": "",
        "district": "",
        "isp": "",
        "area_code": "",
        "country_english": "",
        "country_code": "",
        "longitude": "",
        "latitude": "",
    }
    if not (ip and ip != "unknown"):
        return data

    if settings.ENABLE_LOGIN_ANALYSIS_LOG:
        try:
            res = requests.get(url, params={"ip": ip}, timeout=5)
            if res.status_code == 200:
                res_data = res.json()
                if res_data.get("code") == 0:
                    data = res_data.get("data")
            return data
        except Exception:
            pass

    return data
