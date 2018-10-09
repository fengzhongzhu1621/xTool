# coding: utf-8

import sys
import logging
from twisted.python import log


def _get_cur_info(number=1):
    """
        返回(调用函数名, 行号)
    """
    frame = sys._getframe(number)
    return (frame.f_code.co_filename, frame.f_code.co_name, frame.f_lineno)


class LinenoLogger(logging.getLoggerClass()):
    def makeRecord(self, *args, **kwargs):
        record = logging.Logger.makeRecord(self, *args, **kwargs)
        (f_filename, f_name, f_lineno) = _get_cur_info(7)
        record.filename = f_filename
        record.funcName = f_name
        record.lineno = f_lineno
        return record


LOG_FORMAT = ('%(asctime)s|%(levelname)s|%(name)s|%(filename)s|%(funcName)s|%(lineno)s|%(message)s')
LOGGER = logging.getLogger(__name__)
logging.setLoggerClass(LinenoLogger)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

LOG_MESSAGE_FORMAT = "%(name)s|%(time)s|%(username)s|%(param)s|%(action)s|%(object)s|%(content)s|%(result)s|%(extend)s"

observer = log.PythonLoggingObserver()
observer.start()
