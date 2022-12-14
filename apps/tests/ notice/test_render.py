# -*- coding: utf-8 -*-

from apps.core.notice.constants import NoticeWay
from apps.core.notice.render import NoticeRowRenderer


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
