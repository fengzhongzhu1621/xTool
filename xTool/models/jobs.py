#coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from past.builtins import basestring

import getpass

from sqlalchemy import (
    Column, Integer, DateTime, String, func, Index, or_, and_, not_)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.session import make_transient
from sqlalchemy_utc import UtcDateTime

from xTool.models import models
from xTool.decorators.db import create_session, provide_session
from xTool.exceptions import XToolException
from xTool.utils.log.logging_mixin import LoggingMixin
from xTool.utils.net import get_hostname
from xTool.utils import timezone
from xTool.utils import helpers
from xTool.utils.state import State

Base = models.Base
ID_LEN = models.ID_LEN


class BaseJob(Base, LoggingMixin):
    """
    Abstract class to be derived for jobs. Jobs are processing items with state
    and duration that aren't task instances. For instance a BackfillJob is
    a collection of task instance runs, but should have its own state, start
    and end time.
    """

    __tablename__ = "job"

    id = Column(Integer, primary_key=True)
    dag_id = Column(String(ID_LEN),)
    state = Column(String(20))
    job_type = Column(String(30))
    start_date = Column(DateTime())
    end_date = Column(DateTime())
    latest_heartbeat = Column(DateTime())
    executor_class = Column(String(500))
    hostname = Column(String(500))
    unixname = Column(String(1000))

    __mapper_args__ = {
        'polymorphic_on': job_type,
        'polymorphic_identity': 'BaseJob'
    }

    __table_args__ = (
        Index('job_type_heart', job_type, latest_heartbeat),
    )

    def __init__(
            self,
            executor,
            heartrate=5,
            max_tis_per_query=512,
            *args, **kwargs):
        # 当前机器的主机名
        self.hostname = get_hostname()
        # 执行器： 从任务队列中获取任务，并执行
        self.executor = executor
        # 获得执行器的类名
        self.executor_class = executor.__class__.__name__
        # 设置开始时间和心跳开始时间
        self.start_date = timezone.system_now()
        self.latest_heartbeat = self.start_date
        # job的心跳间隔时间，用于判断job是否存活
        self.heartrate = heartrate
        # 调度器进程所在机器的执行用户
        self.unixname = getpass.getuser()
        # 因为需要批量更新任务实例的状态，为了防止SQL过长
        # 需要设置每批更新的任务实例的数量
        self.max_tis_per_query = max_tis_per_query
        super(BaseJob, self).__init__(*args, **kwargs)

    def is_alive(self):
        """判断job是否存活 ."""
        # 如果job超过2个心跳周期都没有上报心跳，则认为job已经死亡
        return (
            (timezone.system_now() - self.latest_heartbeat).seconds <
            (heartrate * 2.1)
        )

    @provide_session
    def kill(self, session=None):
        """关闭job ."""
        job = session.query(BaseJob).filter(BaseJob.id == self.id).first()
        job.end_date = timezone.system_now()
        # 杀死job
        try:
            self.on_kill()
        except Exception as e:
            self.log.error('on_kill() method failed: {}'.format(e))
        # 保存job的关闭时间
        session.merge(job)
        session.commit()
        # 抛出异常
        raise XToolException("Job shut down externally.")

    def on_kill(self):
        """杀死job
        Will be called when an external kill command is received
        """
        pass

    def heartbeat_callback(self, session=None):
        pass

    def heartbeat(self):
        # 每次心跳获得最新的job状态
        with create_session() as session:
            # 如果只能查询到一个结果，返回它，否则抛出异常。 
            # 没有结果时抛sqlalchemy.orm.exc.NoResultFound，
            # 有超过一个结果时抛sqlalchemy.orm.exc.MultipleResultsFound。
            job = session.query(BaseJob).filter_by(id=self.id).one()
            # 将job复制，并去掉与sesion的关联
            # remove the association with any session
            # and remove its “identity key”
            make_transient(job)
            session.commit()

        # 如果job是关闭状态，则执行kill操作
        if job.state == State.SHUTDOWN:
            # 关闭job，抛出 AirflowException
            self.kill()

        # 获得到下一次心跳需要睡眠的时间间隔，并等待
        sleep_for = 0
        if job.latest_heartbeat:
            sleep_for = max(
                0,
                self.heartrate - (timezone.system_now() - job.latest_heartbeat).total_seconds())
        sleep(sleep_for)

        # 睡眠之后会重新连接DB
        with create_session() as session:
            # 更新最新的心跳时间
            job = session.query(BaseJob).filter(BaseJob.id == self.id).first()
            job.latest_heartbeat = timezone.system_now()
            session.merge(job)
            session.commit()
            # 执行心跳处理函数
            self.heartbeat_callback(session=session)
            self.log.debug('[heartbeat]')

    def run(self):
        """新增一个job，并执行job，状态从运行态->完成态 ."""
        with create_session() as session:
            # 新增job
            self.state = State.RUNNING
            session.add(self)
            session.commit()
            id_ = self.id
            make_transient(self)
            self.id = id_

            # 运行job
            self._execute()

            # job执行完成后，记录完成时间和状态
            self.end_date = timezone.system_now()
            self.state = State.SUCCESS
            session.merge(self)
            session.commit()

    def _execute(self):
        raise NotImplementedError("This method needs to be overridden")

    @provide_session
    def reset_state_for_orphaned_tasks(self, filter_by_dag_run=None, session=None):
        """验证是否存在孤儿任务实例，并将其状态设置为None
        This function checks if there are any tasks in the dagrun (or all)
        that have a scheduled state but are not known by the
        executor. If it finds those it will reset the state to None
        so they will get picked up again.
        The batch option is for performance reasons as the queries are made in
        sequence.

        :param filter_by_dag_run: the dag_run we want to process, None if all
        :type filter_by_dag_run: models.DagRun
        :return: the TIs reset (in expired SQLAlchemy state)
        :rtype: List(TaskInstance)
        """
        # 获得执行器等待执行队列中的任务实例
        queued_tis = self.executor.queued_tasks
        # 获得执行器中正在执行的任务实例
        running_tis = self.executor.running

        # 从DB中获取已调度和在队列中的任务实例
        # 根据 filter_by_dag_run 参数决定是否对dag_run的状态进行判断
        # TODO 全表扫描，SQL待优化
        resettable_states = [State.SCHEDULED, State.QUEUED]
        TI = models.TaskInstance
        DR = models.DagRun
        if filter_by_dag_run is None:
            # 获得正在运行的流程实例中，任务状态为 [State.SCHEDULED, State.QUEUED] 的任务实例
            resettable_tis = (
                session
                .query(TI)
                .join(
                    DR,
                    and_(
                        TI.dag_id == DR.dag_id,
                        TI.execution_date == DR.execution_date))
                .filter(
                    DR.state == State.RUNNING,
                    DR.run_id.notlike(BackfillJob.ID_PREFIX + '%'),  # 不是补录的流程实例
                    TI.state.in_(resettable_states))).all()
        else:
            # 获得指定dag_run中正在调度（任务状态为 [State.SCHEDULED, State.QUEUED]）的任务实例
            resettable_tis = filter_by_dag_run.get_task_instances(state=resettable_states,
                                                                  session=session)
        # 获得不在执行器队列（待执行队列和运行队列）中的任务实例
        tis_to_reset = []
        # Can't use an update here since it doesn't support joins
        for ti in resettable_tis:
            # 判断任务实例是否在调度器队列中
            # TODO 不知道什么情况下会发生
            if ti.key not in queued_tis and ti.key not in running_tis:
                tis_to_reset.append(ti)

        if len(tis_to_reset) == 0:
            return []

        # 将不在执行器队列（待执行队列和运行队列）中的任务实例状态设置为None
        # TODO 为什么不根据任务实例的ID来设置where添加呢？待优化！！！
        def query(result, items):
            filter_for_tis = ([and_(TI.dag_id == ti.dag_id,
                                    TI.task_id == ti.task_id,
                                    TI.execution_date == ti.execution_date)
                               for ti in items])
            reset_tis = (
                session
                .query(TI)
                .filter(or_(*filter_for_tis), TI.state.in_(resettable_states))
                .with_for_update()
                .all())
            for ti in reset_tis:
                ti.state = State.NONE
                session.merge(ti)
            return result + reset_tis

        # 将任务实例的状态批量改为None
        reset_tis = helpers.reduce_in_chunks(query,
                                             tis_to_reset,
                                             [],
                                             self.max_tis_per_query)

        task_instance_str = '\n\t'.join(
            ["{}".format(x) for x in reset_tis])
        session.commit()

        self.log.info(
            "Reset the following %s TaskInstances:\n\t%s",
            len(reset_tis), task_instance_str
        )
        # 返回设置状态为None之后的任务实例列表
        return reset_tis
