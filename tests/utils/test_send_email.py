# -*- coding: utf-8 -*-

import unittest
from xTool.utils.send_email import *


def test_send_email():
    e_from = 'sender@example.com'
    to = "receiver@example.com"
    subject="email title"
    html_content = "email body"
    files=None
    dryrun=True

    send_email(e_from, to, subject, html_content,
              files, dryrun)

    class Configutration(object):
        def get_email_backend(self):
            return "xTool.utils.send_email.send_email_smtp"
    conf = Configutration()
    send_email(e_from, to, subject, html_content,
              files, dryrun,
              conf=conf)
