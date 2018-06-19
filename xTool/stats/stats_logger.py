#coding: utf-8


class DummyStatsLogger(object):
    @classmethod
    def incr(cls, stat, count=1, rate=1):
        pass

    @classmethod
    def decr(cls, stat, count=1, rate=1):
        pass

    @classmethod
    def gauge(cls, stat, value, rate=1, delta=False):
        pass

    @classmethod
    def timing(cls, stat, dt):
        pass



def create_stats_client(host=None, port=None, prefix=None):
    """创建统计客户端 ."""
    if host:
        # 采集到的数据会走 UDP 协议发给 StatsD，
        # 由 StatsD 解析、提取、计算处理后，周期性地发送给 Graphite。
        from statsd import StatsClient
        statsd = StatsClient(
            host=conf.get('scheduler', 'statsd_host'),
            port=conf.getint('scheduler', 'statsd_port'),
            prefix=conf.get('scheduler', 'statsd_prefix'))
    else:
        statsd = DummyStatsLogger
    return statsd
