#coding: utf-8

from __future__ import absolute_import


import sys
from datetime import datetime
from collections import namedtuple
import argparse
import getpass
import socket
import functools
import json
from argparse import Namespace


Arg = namedtuple(
    'Arg', ['flags', 'help', 'action', 'default', 'nargs', 'type', 'choices', 'metavar'])
Arg.__new__.__defaults__ = (None, None, None, None, None, None, None)


class BaseCLIFactory(object):
    args = {}
    subparsers = tuple()

    subparsers_dict = {sp['func'].__name__: sp for sp in subparsers}

    @classmethod
    def get_parser(cls):
        # 创建命令行解析器
        parser = argparse.ArgumentParser()
        # 添加子解析器
        subparsers = parser.add_subparsers(
            help='sub-command help', dest='subcommand')
        subparsers.required = True

        # 获得需要添加到子解析器的命令名
        subparser_name_list = cls.subparsers_dict.keys()
        # 遍历子解析器命令的名称
        for subparser_name in subparser_name_list:
            # 获得子解析器配置
            subparser_conf = cls.subparsers_dict[subparser_name]
            # 根据子命令名创建子解析器
            sp = subparsers.add_parser(subparser_conf['func'].__name__,
                                       help=subparser_conf['help'])
            # 遍历子命令参数
            for arg in subparser_conf['args']:
                # 根据参数名，从全局参数表中获取参数的详细配置
                arg_namedtuple = cls.args[arg]
                # 获得参数命名元组的值
                kwargs = {
                    f: getattr(arg_namedtuple, f)
                    for f in arg_namedtuple._fields if f != 'flags' and getattr(arg_namedtuple, f)}
                # 子解析器添加参数
                # flags：参数的短写和长写
                sp.add_argument(*arg_namedtuple.flags, **kwargs)
            # 设置参数的动作
            sp.set_defaults(func=subparser_conf['func'])
        return parser


def get_parser():
    return CLIFactory.get_parser()


def action_logging(f):
    """
    Decorates function to execute function at the same time submitting action_logging
    but in CLI context. It will call action logger callbacks twice,
    one for pre-execution and the other one for post-execution.

    :param f: function instance
    :return: wrapped function
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        """
        An wrapper for cli functions. It assumes to have Namespace instance
        at 1st positional argument
        :param args: Positional argument. It assumes to have Namespace instance
        at 1st positional argument
        :param kwargs: A passthrough keyword argument
        """
        # 第一个参数必须是argparse命名空间实例
        assert args
        assert isinstance(args[0], Namespace), \
            "1st positional argument should be argparse.Namespace instance, " \
            "but {}".format(args[0])
        # 创建命令行参数的上下文
        metrics = _build_metrics(f.__name__, args[0])
        cli_action_loggers.on_pre_execution(**metrics)
        # 执行命令行
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # 如果命令行抛出了异常，记录异常信息
            metrics['error'] = e
            raise
        finally:
            # 记录命令行结束时间
            metrics['end_datetime'] = datetime.now()
            cli_action_loggers.on_post_execution(**metrics)

    return wrapper


def _build_metrics(func_name, namespace):
    """
    Builds metrics dict from function args
    It assumes that function arguments is from airflow.bin.cli module's function
    and has Namespace instance where it optionally contains "dag_id", "task_id",
    and "execution_date".

    :param func_name: name of function
    :param namespace: Namespace instance from argparse
    :return: dict with metrics
    """

    metrics = {'sub_command': func_name, 'start_datetime': datetime.now(),
               'full_command': '{}'.format(list(sys.argv)), 'user': getpass.getuser()}

    assert isinstance(namespace, Namespace)
    tmp_dic = vars(namespace)
    metrics = dict(metrics)
    metrics['host_name'] = socket.gethostname()

    extra = json.dumps(dict((k, metrics[k]) for k in ('host_name', 'full_command')))

    # 构造需要记录在DB中的日志
    log = airflow.models.Log(
        event='cli_{}'.format(func_name),
        task_instance=None,
        owner=metrics['user'],
        extra=extra,
        task_id=metrics.get('task_id'),
        dag_id=metrics.get('dag_id'),
        execution_date=metrics.get('execution_date'))
    metrics['log'] = log
    return metrics

