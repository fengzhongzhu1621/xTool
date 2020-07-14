# -*- coding: utf-8 -*-


class WorkerProcessManager:
    def __init__(self, loop, server_options):
        self.loop = loop
        self.server_options = server_options

    def close(self):
        pass

    def find_child_process(self, pid):
        pass

    def restart_child_process(self, pid):
        pass

    def run_worker_process(self):
        """启动工作进程 ."""
        pass

