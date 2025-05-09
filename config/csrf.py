import os

CSRF_EXEMPT_PATHS = []

APP_CODE = os.environ.get("BKPAAS_APP_ID")

CSRF_TRUSTED_ORIGINS = [origin for origin in str(os.getenv("BKAPP_CSRF_TRUSTED_ORIGINS", "")).split(",") if origin]
CSRF_COOKIE_NAME = f"{APP_CODE}_csrftoken"
CSRF_EXEMPT_PATHS = []
