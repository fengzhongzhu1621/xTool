#coding: utf-8


from collections import namedtuple
import argparse


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
        # 遍历自解析器命令的名称
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
            sp.set_defaults(func=subparser_conf['func'])
        return parser
