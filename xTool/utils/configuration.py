# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import os
import json
from tempfile import mkstemp


def tmp_configuration_copy(conf):
    """将配置转换为json写入到临时文件
    Returns a path for a temporary file including a full copy of the configuration
    settings.
    :return: a path to a temporary file
    """
    cfg_dict = conf.as_dict(display_sensitive=True)
    temp_fd, cfg_path = mkstemp()

    # fdopen用于在一个已经打开的文件描述符上打开一个流，返回文件指针
    with os.fdopen(temp_fd, 'w') as temp_file:
        json.dump(cfg_dict, temp_file)

    return cfg_path
