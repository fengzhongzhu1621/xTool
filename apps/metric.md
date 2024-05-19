### 安装 APP

确保 INSTALLED_APPS 中添加了如下应用：

```
INSTALLED_APPS += (
    ...
    "apps.opentelemetry_instrument",
)

OPEN_TELEMETRY_ENABLE_OTEL_METRICS = True

```

### 访问 endpoint

```
http://localhost:5001/
```
