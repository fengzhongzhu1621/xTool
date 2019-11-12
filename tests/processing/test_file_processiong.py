#coding: utf-8

import os
import logging

from xTool.utils.file import list_py_file_paths
from xTool.utils.file_processing import FileProcessorManager
from xTool.utils.file_processing import BaseMultiprocessFileProcessor


#logging.basicConfig(level=logging.INFO)


file_directory = os.path.dirname(__file__)


class PrintMultiprocessFileProcessor(BaseMultiprocessFileProcessor):
    def terminate(self):
        pass

    def process_file(self, file_path):
        if file_path == '1.txt':
            raise Exception("I'm 1.txt")
        return [file_path]


def processor_factory(file_path):
    return PrintMultiprocessFileProcessor(file_path)


class TestFileProcessorManager:
    def test_heartbeat(self):
        file_paths = list_py_file_paths(file_directory)
        parallelism = 1
        process_file_interval = 1
        min_file_parsing_loop_time = 1
        max_runs = 1
        process_manager = FileProcessorManager(file_directory,
                             file_paths[:1],
                             parallelism,
                             process_file_interval,
                             min_file_parsing_loop_time,
                             max_runs,
                             processor_factory)
        result = process_manager.heartbeat()
        assert result == []
        assert process_manager.processing_count() == 1

        process_manager.wait_until_finished()
        result = process_manager.heartbeat()
        assert process_manager.processing_count() == 0
        assert result == file_paths[:1]

    def test_subprocess_exception(self):
        file_paths = ['1.txt', '2.txt']
        parallelism = 2
        process_file_interval = 1
        min_file_parsing_loop_time = 1
        max_runs = 3
        process_manager = FileProcessorManager(file_directory,
                             file_paths,
                             parallelism,
                             process_file_interval,
                             min_file_parsing_loop_time,
                             max_runs,
                             processor_factory)
        result = process_manager.heartbeat()
        assert result == []
        assert process_manager.processing_count() == 2

        process_manager.wait_until_finished()
        result = process_manager.heartbeat()
        assert process_manager.processing_count() == 0
        assert result == ['2.txt']
