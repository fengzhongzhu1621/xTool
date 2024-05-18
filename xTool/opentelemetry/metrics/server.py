def start_metrics_http_server():
    from prometheus_client import start_http_server  # noqa

    print("start metrics http server listen :5001")
    start_http_server(port=5001)
