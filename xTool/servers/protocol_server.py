# -*- coding: utf-8 -*-


class ProtocolServer:
    def __init__(self, loop, server_coroutine):
        self.loop = loop
        self.server_coroutine = server_coroutine

    def close(self):
        pass

    def find_child_process(self, pid):
        pass

    def restart_child_process(self, pid):
        pass

    def start_process(self):
        pass
