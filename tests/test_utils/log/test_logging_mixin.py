#coding: utf-8

import sys
import logging
from xTool.utils.log.logging_mixin import *


class A(LoggingMixin):
	pass
		
		
def test_LoggingMixin():	
	assert A.log is not None
	
	
def test_StreamLogWriter():
	a = A()
	logger = a.log
	stream = StreamLogWriter(logger, logging.INFO)
	stream.write('test')
	stream.write(u'test')
	stream.write(u'你好')
	stream.write('你好\n')
	
def test_RedirectStdHandler():
	handler = RedirectStdHandler('stdout')
	assert handler.stream == sys.stdout
	handler = RedirectStdHandler('stderr')
	assert handler.stream == sys.stderr
	handler = RedirectStdHandler('other')
	assert handler.stream == sys.stderr

	
def test_redirect():
	a = A()
	logger = a.log
	with redirect_stdout(logger, logging.INFO),\
			redirect_stderr(logger, logging.WARN):
		pass
	logging.shutdown()

	
def test_set_context():
	a = A()
	logger = a.log
	set_context(logger, {'a': 1})
	logger.info('test')