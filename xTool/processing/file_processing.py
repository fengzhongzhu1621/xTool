# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import time
import zipfile
from abc import ABCMeta, abstractmethod
from collections import defaultdict

from xTool.utils import timezone
from xTool.utils.log.logging_mixin import LoggingMixin


class AbstractFileProcessor(object):
    """文件处理器抽象类 ."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self):
        """启动处理器 ."""
        raise NotImplementedError()

    @abstractmethod
    def terminate(self, sigkill=False):
        """终止处理器 ."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def pid(self):
        """获得处理器的进程ID ."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def exit_code(self):
        """获得处理器进程退出码 ."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def done(self):
        """判断处理器进程是否执行完成 ."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def result(self):
        """获得处理器执行结果 ."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def start_time(self):
        """获得处理器进程的开始时间 ."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def file_path(self):
        """获得处理器处理的文件路径 ."""
        raise NotImplementedError()


class FileProcessorManager(LoggingMixin):
    """文件处理器进程管理类

    :type _file_path_queue: list[unicode]
    :type _processors: dict[unicode, AbstractDagFileProcessor]
    :type _last_runtime: dict[unicode, float]
    :type _last_finish_time: dict[unicode, datetime]
    """

    def __init__(self,
                 file_directory,
                 file_paths,
                 parallelism,
                 process_file_interval,
                 max_runs,
                 processor_factory):
        """
        :param processor_factory: function that creates processors for file
        definition files. Arguments are (dag_definition_path)
        :type processor_factory: (unicode, unicode) -> (AbstractFileProcessor)
        """
        # 文件的目录
        self._file_directory = file_directory
        # 需要处理的文件，每个文件启动一个文件处理器进程
        # file_paths 是 file_directory 目录下的有效文件路径
        self._file_paths = file_paths
        # 文件队列
        self._file_path_queue = []
        # 文件处理器进程的最大数量，即能够同时处理多少个文件
        self._parallelism = parallelism
        # job运行的最大次数，默认是-1
        # 如果是>0，则运行指定次数后，调用进程就会停止
        self._max_runs = max_runs
        # 同一个文件在被处理器处理时的间隔
        self._process_file_interval = process_file_interval
        # 每次心跳的休眠时间
        self._min_file_parsing_loop_time = min_file_parsing_loop_time
        # 文件处理进程
        self._processor_factory = processor_factory
        # 记录正在运行的处理器
        self._processors = {}
        # 记录文件处理器执行完成后的执行时长
        self._last_runtime = {}
        # 记录文件处理器执行完成后的结束时间
        self._last_finish_time = {}
        # 处理器运行次数
        self._run_count = defaultdict(int)
        # Scheduler heartbeat key.
        # 记录心跳的次数
        self._heart_beat_key = 'heart-beat'

    @property
    def file_paths(self):
        """返回需要处理的文件列表 ."""
        return self._file_paths

    def get_pid(self, file_path):
        """获得文件所在处理器的进程ID ."""
        if file_path in self._processors:
            return self._processors[file_path].pid
        return None

    def get_all_pids(self):
        """获得所有文件处理器的进程ID列表 ."""
        return [x.pid for x in self._processors.values()]

    def get_runtime(self, file_path):
        """获得文件处理器的运行时长，单位是秒 ."""
        if file_path in self._processors:
            return (timezone.system_now() - self._processors[file_path].start_time)\
                .total_seconds()
        return None

    def get_last_runtime(self, file_path):
        """文件处理器执行完成后，获得执行的时长，单位是秒 ."""
        return self._last_runtime.get(file_path)

    def get_last_finish_time(self, file_path):
        """文件处理器执行完成后，获得的执行完成时间，单位是秒 ."""
        return self._last_finish_time.get(file_path)

    def get_start_time(self, file_path):
        """获得文件处理器的开始时间 ."""
        if file_path in self._processors:
            return self._processors[file_path].start_time
        return None

    def set_file_paths(self, new_file_paths):
        """根据文件处理器需要处理的新的文件列表 ."""
        # 设置目录下最新的文件路径数组
        self._file_paths = new_file_paths
        # 获得 self._file_path_queue 和  new_file_paths的交集
        # 即从文件队列中删除不存在的文件
        self._file_path_queue = [x for x in self._file_path_queue
                                 if x in new_file_paths]
        # 已删除的文件关联的处理器停止运行
        filtered_processors = {}
        for file_path, processor in self._processors.items():
            if file_path in new_file_paths:
                filtered_processors[file_path] = processor
            else:
                # 如果正在执行的处理器文件不存在，则停止处理器
                self.log.warning("Stopping processor for %s", file_path)
                # 将被删除的文件关联的文件处理器进程，停止执行
                processor.terminate()
        self._processors = filtered_processors

    def processing_count(self):
        """获得文件处理器的数量 ."""
        return len(self._processors)

    def wait_until_finished(self):
        """阻塞等待所有的文件处理器执行完成 ."""
        for file_path, processor in self._processors.items():
            while not processor.done:
                time.sleep(0.1)

    def heartbeat(self):
        """心跳
        
        - 处理执行完毕的处理器
        - 将任务加入队列
        - 执行队列中的进程
        """
        # 已完成的文件处理器
        # :type : dict[unicode, AbstractDagFileProcessor]
        finished_processors = {}
        # 正在运行的文件处理器
        # :type : dict[unicode, AbstractDagFileProcessor]
        running_processors = {}

        # 遍历所有的文件处理器
        result = []
        for file_path, processor in self._processors.items():
            if processor.done:
                self.log.info("Processor for %s finished", file_path)
                # 获得已完成的文件处理器进程
                finished_processors[file_path] = processor
                # 文件处理器运行时间
                now = timezone.system_now()
                # 记录文件处理器的的执行时长
                self._last_runtime[file_path] = (now -
                                                 processor.start_time).total_seconds()
                # 记录文件处理器的结束时间
                self._last_finish_time[file_path] = now
                # 记录文件被处理的次数
                self._run_count[file_path] += 1
                # 收集已完成处理器的执行结果
                if processor.result is None:
                    self.log.warning(
                        "Processor for %s exited with return code %s.",
                        processor.file_path, processor.exit_code
                    )
                else:
                    for value in processor.result:
                        result.append(value)
            else:
                # 记录正在运行的文件处理器进程
                running_processors[file_path] = processor

        # 每一次心跳，剔除已完成的处理器
        self._processors = running_processors

        self.log.debug("%s/%s scheduler processes running",
                       len(self._processors), self._parallelism)

        self.log.debug("%s file paths queued for processing",
                       len(self._file_path_queue))

        # 如果队列为空，设置需要入队的文件
        if not self._file_path_queue:
            # 可能存在正在运行的文件处理器进程尚未执行完成
            # 在下一次心跳处理
            file_paths_in_progress = self._processors.keys()

            # 记录下尚未到调度时间的文件
            file_paths_recently_processed = []
            longest_parse_duration = 0
            now = timezone.system_now()

            # 遍历需要处理的文件列表
            for file_path in self._file_paths:
                # 获得文件处理器上一次执行完成的时间
                last_finish_time = self.get_last_finish_time(file_path)
                # 如果文件曾经处理过
                if last_finish_time is not None:
                    duration = now - last_finish_time
                    # 如果文件尚未到调度时间，则记录在指定数组中
                    if duration.total_seconds() < self._process_file_interval:
                        file_paths_recently_processed.append(file_path)
                    # 获得所有文件中最长的等待时间
                    longest_parse_duration = max(duration.total_seconds(),
                                                 longest_parse_duration)

            # 获得每次心跳的休眠时间
            sleep_length = max(self._min_file_parsing_loop_time - longest_parse_duration,
                               0)
            # 休眠
            if sleep_length > 0:
                self.log.debug("Sleeping for %.2f seconds to prevent excessive "
                               "logging",
                               sleep_length)
                time.sleep(sleep_length)

            # 获得处理器已经执行完成的文件列表，且这些文件的执行次数已经达到了最大阈值
            files_paths_at_run_limit = [file_path
                                        for file_path, num_runs in self._run_count.items()
                                        if num_runs == self._max_runs]

            # 获得需要入队的文件，新增的文件在此入库
            # 去掉正在运行的文件
            # 去掉最近需要运行的文件
            # 去掉运行次数已经达到阈值的文件
            files_paths_to_queue = list(set(self._file_paths) -
                                        set(file_paths_in_progress) -
                                        set(file_paths_recently_processed) -
                                        set(files_paths_at_run_limit))

            # 遍历正在运行的处理器进程
            for file_path, processor in self._processors.items():
                self.log.debug(
                    "File path %s is still being processed (started: %s)",
                    processor.file_path, processor.start_time.isoformat()
                )
            self.log.debug(
                "Queuing the following files for processing:\n\t%s",
                "\n\t".join(files_paths_to_queue)
            )

            # 将任务加入队列
            self._file_path_queue.extend(files_paths_to_queue)

        # 处理器并发性阈值验证
        while (self._parallelism - len(self._processors) > 0 and
               self._file_path_queue):
            # 从队列中出队一个文件
            file_path = self._file_path_queue.pop(0)
            # 创建文件处理器子进程
            processor = self._processor_factory(file_path)
            # 启动文件处理器子进程
            processor.start()
            self.log.info(
                "Started a process (PID: %s) to generate tasks for %s",
                processor.pid, file_path
            )
            # 记录文件子进程
            self._processors[file_path] = processor

        # 记录心跳的次数
        self._run_count[self._heart_beat_key] += 1

        # 返回已完成处理器的执行结果
        return result

    def max_runs_reached(self):
        """
        :return: whether all file paths have been processed max_runs times
        """
        if self._max_runs == -1:  # Unlimited runs.
            return False
        # 如果有任意一个文件都没有达到执行次数，也认为没有到达最大阈值
        for file_path in self._file_paths:
            if self._run_count[file_path] != self._max_runs:
                return False
        # 心跳总数大于等于最大运行次数时，也会停止调度
        if self._run_count[self._heart_beat_key] < self._max_runs:
            return False
        return True

    def terminate(self):
        """停止所有处理器 ."""
        for processor in self._processors.values():
            processor.terminate()
