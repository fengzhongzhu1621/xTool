### 启动 Jaeger

```bash
docker run -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one
```

### 启动进程

```bash
OPEN_TELEMETRY_OTEL_SERVICE_NAME="server" python manage.py runserver --noreload
OPEN_TELEMETRY_OTEL_SERVICE_NAME="worker" celery worker -A config.celery -P threads -c 300 -l info
```

### 查看 trace 结果

```
http://localhost:16686/
```
