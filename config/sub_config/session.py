from config import APP_CODE

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2
SESSION_COOKIE_NAME = f"{APP_CODE}_sessionid"
# The module to store session data
SESSION_ENGINE = "django.contrib.sessions.backends.db"
# Whether to save the session data on every request.
SESSION_SAVE_EVERY_REQUEST = False
# Whether to set the flag restricting cookie leaks on cross-site requests.
# This can be 'Lax', 'Strict', 'None', or False to disable the flag.
# SameSite 属性是一个安全特性，用于防止跨站请求伪造（CSRF）攻击。它决定了浏览器如何处理跨站点请求中的 cookie。
# 1. Lax（默认值）：对于 GET 请求，浏览器将在跨站点请求中发送 cookie。对于其他类型的请求（如 POST、PUT 或 DELETE），
# 浏览器将仅在请求是从顶级窗口发起的且满足一定条件时发送 cookie。
# 2. Strict：浏览器仅在请求是从同一站点发起时才发送 cookie。这提供了更严格的安全保护，但也可能导致某些合法请求无法正常工作。
# 3. None：浏览器将在所有跨站点请求中发送 cookie。这可能会增加 CSRF 攻击的风险。
SESSION_COOKIE_SAMESITE = "Lax"
