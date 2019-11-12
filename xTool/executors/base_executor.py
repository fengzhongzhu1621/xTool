# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from builtins import range

from xTool.utils.log.logging_mixin import LoggingMixin
from xTool.utils.state import State


class BaseExecutor(LoggingMixin):

    def __init__(self, parallelism):
        """
        Class to derive in order to interface with executor-type systems
        like Celery, Mesos, Yarn and the likes.

        :param parallelism: how many jobs should run at one time. Set to
            ``0`` for infinity
        :type parallelism: int
        """
        # 同一时间运行多少个job，0表示无限多
        # 整个集群中同时运行的任务实例的总量
        self.parallelism = parallelism
        # 准备入队的缓存任务队列
        self.queued_tasks = {}
        # 已经入队的正在运行的任务队列
        self.running = {}
        # 记录任务完成的状态
        self.event_buffer = {}

    def start(self):  # pragma: no cover
        """
        Executors may need to get things started. For example LocalExecutor
        starts N workers.
        """
        pass

    def queue_command(self, task_instance, command, priority=1, queue=None):
        """将任务实例放到本地缓存队列中 ."""
        # 每个任务实例都有一个唯一key
        key = task_instance.key
        # 判断任务实例是否已经在队列中或正在运行
        if not self.has_task(task_instance):
            self.log.info("Adding to queue: %s", command)
            # 将任务加入到缓冲队列
            self.queued_tasks[key] = (command, priority, queue, task_instance)
        else:
            self.log.info("could not queue task {}".format(key))

    def has_task(self, task_instance):
        """判断任务实例是否已经在队列中或正在运行 ."""
        if task_instance.key in self.queued_tasks or task_instance.key in self.running:
            return True

    def sync(self):
        """每次心跳都会调用
        Sync will get called periodically by the heartbeat method.
        Executors should override this to perform gather statuses.
        """
        pass

    def heartbeat(self):
        # Triggering new jobs
        # 获得剩余可运行job的数量
        if not self.parallelism:
            open_slots = len(self.queued_tasks)
        else:
            open_slots = self.parallelism - len(self.running)

        self.log.debug("%s running task instances", len(self.running))
        self.log.debug("%s in queue", len(self.queued_tasks))
        self.log.debug("%s open slots", open_slots)

        # 按优先级逆序，优先级大的放在前面，优先执行；优先级默认为1
        sorted_queue = sorted(
            [(k, v) for k, v in self.queued_tasks.items()],
            key=lambda x: x[1][1],
            reverse=True)

        # 执行任务实例
        for i in range(min((open_slots, len(self.queued_tasks)))):
            # 从缓冲队列中取出一个任务
            key, (command, _, queue, ti) = sorted_queue.pop(0)
            # TODO(jlowin) without a way to know what Job ran which tasks,
            # there is a danger that another Job started running a task
            # that was also queued to this executor. This is the last chance
            # to check if that happened. The most probable way is that a
            # Scheduler tried to run a task that was originally queued by a
            # Backfill. This fix reduces the probability of a collision but
            # does NOT eliminate it.
            self.queued_tasks.pop(key)
            # 从DB中获取最新的任务实例参数，因为任务实例的状态可能有变化
            ti.refresh_from_db()
            # 将未运行的任务实例放入执行队列，并发给执行器处理
            if ti.state != State.RUNNING:
                self.running[key] = command
                self.execute_async(key=key,
                                   command=command,
                                   queue=queue,
                                   executor_config=ti.executor_config)
            else:
                # 正在运行的任务是不会重新执行的
                self.logger.info(
                    'Task is already running, not sending to '
                    'executor: {}'.format(key))

        # Calling child class sync method
        # 如果是本地或顺序调度器，则是阻塞操作，同步任务实例执行结果
        # 如果是celery等分布式调度器，则是非阻塞操作，异步获取任务实例执行结果
        self.log.debug("Calling the %s sync method", self.__class__)
        self.sync()

    def change_state(self, key, state):
        self.log.debug("Changing state: {}".format(key))
        self.running.pop(key)
        self.event_buffer[key] = state

    def fail(self, key):
        self.change_state(key, State.FAILED)

    def success(self, key):
        self.change_state(key, State.SUCCESS)

    def get_event_buffer(self, dag_ids=None):
        """获得celery worker执行完毕的任务实例
        Returns and flush the event buffer. In case dag_ids is specified
        it will only return and flush events for the given dag_ids. Otherwise
        it returns and flushes all

        :param dag_ids: to dag_ids to return events for, if None returns all
        :return: a dict of events
        """
        cleared_events = dict()
        if dag_ids is None:
            cleared_events = self.event_buffer
            self.event_buffer = dict()
        else:
            for key in self.event_buffer:
                dag_id, _, _, _ = key
                if dag_id in dag_ids:
                    cleared_events[key] = self.event_buffer.pop(key)
        return cleared_events

    def execute_async(self,
                      key,
                      command,
                      queue=None,
                      executor_config=None):  # pragma: no cover
        """
        This method will execute the command asynchronously.
        """
        raise NotImplementedError()

    def end(self):  # pragma: no cover
        """
        This method is called when the caller is done submitting job and is
        wants to wait synchronously for the job submitted previously to be
        all done.
        """
        raise NotImplementedError()

    def terminate(self):
        """
        This method is called when the daemon receives a SIGTERM
        """
        raise NotImplementedError()
