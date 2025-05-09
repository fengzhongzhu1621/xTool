from prometheus_client import CollectorRegistry

REGISTRY = CollectorRegistry(auto_describe=True)
