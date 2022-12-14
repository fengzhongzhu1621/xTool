# -*- coding: utf-8 -*-

from apps.core.notice.constants import NoticeWay
from apps.core.notice.render import NoticeRowRenderer, CustomTemplateRenderer, CustomOperateTemplateRenderer
from xTool.algorithms.collections import FancyDict


class TestNoticeRowRenderer:
    def test_format(self):
        notice_way = NoticeWay.WECHAT
        title = "Hi"
        content = "I'm OK"
        actual = NoticeRowRenderer.format(notice_way, title, content)
        expect = "Hi: I'm OK"
        assert actual == expect

    def test_render_line(self):
        line = "#Hi#I'm OK"
        context = {
            "notice_way": NoticeWay.WECHAT,
        }
        actual = NoticeRowRenderer.render_line(line, context)
        expect = "Hi: I'm OK"
        assert actual == expect

    def test_render(self):
        content = """
            #title_a#content_a
            #title_b#content_b
        """
        context = {
            "notice_way": NoticeWay.WECHAT,
        }
        actual = NoticeRowRenderer.render(content, context)
        expect = """title_a: content_a
title_b: content_b"""
        assert actual == expect


class TestCustomTemplateRenderer:
    def test_render(self):
        content = "content"
        context = {
            "notice_way": NoticeWay.WECHAT,
            "action": FancyDict({"id": 1}),
            "a": "value_a",
            "b": "value_b",
            "title": "I'm title",
            "title_template": "[{{action.id}}] {{title}}",
            "default_title_template": "",
            "content_template": """
                #title_a#content_a {{a}}
                #title_b#content_b {{b}}
            """,
            "default_content_template": "{{action.id}}",
        }
        CustomTemplateRenderer.render(content, context)
        assert context["user_title"] == "[1] I'm title"
        assert context["user_content"] == """title_a: content_a value_a
title_b: content_b value_b"""


class TestCustomOperateTemplateRenderer:
    def test_render(self):
        content = ""
        context = {
            "notice_way": NoticeWay.WECHAT,
            "a": "value_a",
            "b": "value_b",
            "action_instance": FancyDict({"content_template": """
                                    #title_a#content_a {{a}}
                                    #title_b#content_b {{b}}
                                """})
        }
        CustomOperateTemplateRenderer.render(content, context)
        assert context["operate_content"] == """title_a: content_a value_a
title_b: content_b value_b"""
