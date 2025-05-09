import os

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOWED_ORIGINS = [origin for origin in str(os.getenv("BKAPP_CORS_ALLOWED_ORIGINS", "")).split(",") if origin]
CORS_ALLOW_HEADERS = os.getenv("BKAPP_CORS_ALLOW_HEADERS", "").split(",")
