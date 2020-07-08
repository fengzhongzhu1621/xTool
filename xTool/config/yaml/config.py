# -*- coding: utf-8 -*-

class Config:
    def __init__(self,
                 global_config: Global = None,
                 server: Server = None,
                 client: Client = None):
        self.global_config = global_config
        self.server = server
        self.client = client

