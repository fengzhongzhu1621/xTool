# -*- coding: utf-8 -*-

from xTool.servers.executor_process import ExecutorProcess
from xTool.servers.worker_process import WorkerProcess
from xTool.servers.dispatcher_process import DispatcherProcess
from xTool.servers.socket_pair_pipeline import SocketPairPipeline


class ExecutorProcessManager:
    def __init__(self, loop, server_options):
        self.loop = loop
        self.server_options = server_options
        self.executor_processes = []
        self.worker_processes = []
        self.dispatcher_processes = []
        self.socket_pair_pipelines = []

        self.executor_enabled = False
        # 调度进程默认关闭
        self.dispatcher_enabled = False

    def close(self):
        pass

    def find_child_process(self, pid):
        pass

    def restart_child_process(self, pid):
        pass

    def create_dispatcher_process(self):
        dispatcher_process = DispatcherProcess(self.socket_pair_pipelines)
        self.dispatcher_processes.append(dispatcher_process)

    def create_executor_process(self):
        for worker_id in range(self.server_options.get_worker_num()):
            executor_process = ExecutorProcess()
            self.executor_processes.append(executor_process)

    def create_worker_process(self):
        for worker_id in range(self.server_options.get_worker_num()):
            socket_pair_pipeline = SocketPairPipeline()
            self.socket_pair_pipelines.append(socket_pair_pipeline)
            worker_process = WorkerProcess(socket_pair_pipeline)
            self.worker_processes.append(worker_process)

    def start_dispatcher_process(self):
        for dispatcher_process in self.dispatcher_processes:
            dispatcher_process.start()

    def start_worker_process(self):
        for worker_process in self.worker_processes:
            worker_process.start()

    def start_executor_process(self):
        for executor_process in self.executor_processes:
            executor_process.start()

    def start_processes(self):
        self.start_dispatcher_process()
        self.start_worker_process()
        self.start_executor_process()
