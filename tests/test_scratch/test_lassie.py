"""
lassie 从网页中智能提取关键信息

* 标题 title
* 描述 description
* 图像 images
* 视频 videos
* 链接 links

"""

import lassie

from xTool.tests.testing import assert_dict_contains

url = "https://www.baidu.com"


def test_fetch_title():
    actual = lassie.fetch(url)
    expect = {
        "description": "全球领先的中文搜索引擎、致力于让网民更便捷地获取信息，找到所求。百度超过千亿的中文网页数据库，可以瞬间找到相关的搜索结果。",
        "images": [
            {"src": "https://www.baidu.com/favicon.ico", "type": "favicon"},
            {"src": "https://www.baidu.com/favicon.ico", "type": "favicon"},
        ],
        "status_code": 200,
        "title": "百度一下，你就知道",
        "url": "https://www.baidu.com",
        "videos": [],
    }

    assert_dict_contains(actual, expect)
