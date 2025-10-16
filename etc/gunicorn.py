"""
一个为 高并发 Web 应用 优化的 Gunicorn 配置文件
"""

import os

from gevent import monkey  # noqa

# Gevent 的猴子补丁（Monkey Patch），用于将标准库（如 socket、threading）替换为异步版本，使 Gunicorn 能高效处理并发请求。
monkey.patch_all()

# 服务器监听的 IP 地址，默认为 127.0.0.1（仅本地访问）。可通过环境变量 HOST 修改（如 "0.0.0.0" 允许外部访问）。
HOST = os.environ.get("HOST", "127.0.0.1")
# 服务器监听的端口，默认为 8000。可通过环境变量 PORT 修改（如 80 或 443）。
PORT = os.environ.get("PORT", 8000)
# 工作进程数（Worker Processes），默认为 2。可通过环境变量 NUMPROCS 修改。
# 通常设置为 CPU 核心数 × 2 + 1（如 4 核 CPU 设置为 9），但需根据实际负载调整。
workers = int(os.environ.get("NUM_PROCS", 2))

bind = "{}:{}".format(HOST, PORT)
# 设置 TCP 监听队列的最大长度（即等待 Gunicorn 接受的连接数）。默认值为 2048，适用于高并发场景。
backlog = 2048

# 指定工作进程的类型，默认是 "sync"（同步阻塞）。
# 这里改为 "gevent"，表示使用 Gevent 的异步协程模型，适合高并发 I/O 密集型应用（如 Web API、微服务）。
# worker_class = 'sync'
worker_class = "gevent"
# 仅对 gevent 或 gthread 模式有效，表示每个工作进程能同时处理的最大连接数（默认 1000）。
worker_connections = 1000
# 设置工作进程处理请求的超时时间（秒）。如果请求超过此时间未完成，Gunicorn 会终止该进程并重启。默认值为 30 秒，这里设置为 60 秒。
timeout = 60
# 设置 HTTP Keep-Alive 连接的保持时间（秒）。客户端可以在该时间内复用连接发送多个请求。默认值为 2 秒。
keepalive = 2
# 每个工作进程在处理 max_requests 个请求后会自动重启，防止内存泄漏。默认值为 0（不重启）。
max_requests = 2000
# 限制 HTTP 请求行的最大长度（字节）。默认值为 4094，这里设置为 8190（接近 HTTP 标准最大值 8192），适用于长 URL 或复杂请求头。
limit_request_line = 8190

# 是否开启调试模式（打印所有执行的代码）。默认为 False，开启后会严重影响性能。
spew = False

# 是否以守护进程（后台进程）运行 Gunicorn。默认为 False（前台运行），生产环境通常设为 True。
daemon = False

# logging
# 指定错误日志的输出位置。"-" 表示输出到标准错误（stderr），通常重定向到文件或日志服务。
errorlog = "-"
# 设置日志级别（debug、info、warning、error、critical）。这里为 info，记录常规运行信息。
loglevel = "info"
# 指定访问日志的输出位置。"-" 表示输出到标准输出（stdout）。
accesslog = "-"
# 自定义访问日志的格式，字段含义如下：
# %(h)s：客户端 IP 地址。
# %(t)s：请求时间。
# %(r)s：HTTP 请求行（如 GET / HTTP/1.1）。
# %(s)s：HTTP 状态码。
# %(b)s：响应大小（字节）。
# %(f)s：Referer 头。
# %(a)s：User-Agent 头。
# %({X-Request-Id}i)s：自定义请求头 X-Request-Id 的值。
# %(L)s：请求处理时间（秒）。
access_log_format = '%(h)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%({X-Request-Id}i)s" in %(L)s seconds'
