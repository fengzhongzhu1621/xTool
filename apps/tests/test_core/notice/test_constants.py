from core.constants import NoticeWay


class TestNoticeWay:
    def test_names(self):
        actual = NoticeWay.names
        expect = ["SMS", "EMAIL", "WECHAT", "WECOM", "VOICE", "WECOM_BOT"]
        assert actual == expect

    def test_choices(self):
        actual = NoticeWay.choices
        expect = [
            ("sms", "短信"),
            ("email", "邮件"),
            ("wechat", "微信"),
            ("wecom", "企业微信"),
            ("voice", "电话"),
            ("wecom_bot", "企业微信机器人"),
        ]
        assert actual == expect

    def test_labels(self):
        actual = NoticeWay.labels
        expect = ["短信", "邮件", "微信", "企业微信", "电话", "企业微信机器人"]
        assert actual == expect

    def test_values(self):
        actual = NoticeWay.values
        expect = ["sms", "email", "wechat", "wecom", "voice", "wecom_bot"]
        assert actual == expect
