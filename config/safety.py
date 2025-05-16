ALLOWED_HOSTS = ["*"]

# 敏感参数,记录请求参数时需剔除
SENSITIVE_PARAMS = ["app_code", "app_secret", "bk_app_code", "bk_app_secret"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
