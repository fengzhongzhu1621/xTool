
# target
Prometheus 监控一个指标

* 服务发现，确认要监控的对象（targets）。
* 定期找各个 target 采集数据样本（samples），写入时序数据库（本地 or 远程）。
* 把 samples 从数据库里读出：添加时间轴生成仪表盘；配进告警规则发送告警。

# job
其值来自配置文件中定义的 job_name，用于区分来自不同 job 的指标， 特别是当多个 job 可能抓取相同 target 时

# instance
默认情况下，这个标签包含 target 的 <host>:<port>，用于标识具体的被监控实例。这对于区分同一个 job 下的不同实例非常有用。

# up
表明抓取操作是否成功。如果最近的抓取成功，up 的值为 1；如果失败，值为 0。

# scrape_duration_seconds

