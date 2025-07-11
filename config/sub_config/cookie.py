import os

SESSION_COOKIE_DOMAIN = os.getenv("BKAPP_SESSION_COOKIE_DOMAIN")
CSRF_COOKIE_DOMAIN = os.getenv("BKAPP_CSRF_COOKIE_DOMAIN", SESSION_COOKIE_DOMAIN)
AUTH_BACKEND_DOMAIN = os.getenv("BKAPP_AUTH_BACKEND_DOMAIN", SESSION_COOKIE_DOMAIN)
LANGUAGE_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
AUTH_BACKEND_TYPE = os.getenv("BKAPP_AUTH_BACKEND_TYPE", "bk_token")
OAUTH_COOKIES_PARAMS = {AUTH_BACKEND_TYPE: AUTH_BACKEND_TYPE}
