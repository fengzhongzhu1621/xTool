import os

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOWED_ORIGINS = [origin for origin in str(os.getenv("BKAPP_CORS_ALLOWED_ORIGINS", "")).split(",") if origin]

# 跨域允许的header
CORS_ALLOW_HEADERS = os.getenv("BKAPP_CORS_ALLOW_HEADERS", "").split(",")
if not CORS_ALLOW_HEADERS:
    CORS_ALLOW_HEADERS = (
        "referer",
        "accept",
        "authorization",
        "content-type",
        "user-agent",
        "x-requested-with",
        "x-csrftoken",
        "HTTP_X_REQUESTED_WITH",
    )
