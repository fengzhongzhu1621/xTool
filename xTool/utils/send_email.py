# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str
from past.builtins import basestring

import importlib
import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate

from xTool.exceptions import XToolConfigException
from xTool.utils.log.logging_mixin import LoggingMixin


def send_email(e_from, to, subject, html_content,
               files=None, dryrun=False, cc=None, bcc=None,
               mime_subtype='mixed', mime_charset='us-ascii',
               conf=None,
               **kwargs):
    """
    Send email using backend specified in EMAIL_BACKEND.

    :param dryrun: true表示测试邮件配置，不会发送邮件
    """
    # 动态加载模块发送函数
    # 可以通过插件的方式自定义邮件发送函数
    # e.g. email_backend = xTool.utils.send_email.send_email_smtp
    if conf:
        path, attr = conf.get_email_backend().rsplit('.', 1)
        module = importlib.import_module(path)
        backend = getattr(module, attr)
    else:
        backend = send_email_smtp
    return backend(e_from, to, subject, html_content, files=files,
                   dryrun=dryrun, cc=cc, bcc=bcc,
                   mime_subtype=mime_subtype, mime_charset=mime_charset, **kwargs)


def send_email_smtp(e_from, to, subject, html_content,
                    files=None,
                    host=None, port=None,
                    ssl=None, starttls=None,
                    user=None, password=None,
                    dryrun=False, cc=None, bcc=None,
                    mime_subtype='mixed', mime_charset='us-ascii',
                    **kwargs):
    """
    Send an email with html content

    >>> send_email('test@example.com', 'foo', '<b>Foo</b> bar', ['/dev/null'], dryrun=True)
    """
    # 收件人格式化
    to = get_email_address_list(to)

    # 构建混合邮件体
    msg = MIMEMultipart(mime_subtype)
    msg['Subject'] = subject
    msg['From'] = e_from
    msg['To'] = ", ".join(to)
    recipients = to
    if cc:
        cc = get_email_address_list(cc)
        msg['CC'] = ", ".join(cc)
        recipients = recipients + cc

    if bcc:
        # don't add bcc in header
        bcc = get_email_address_list(bcc)
        recipients = recipients + bcc
    
    # 添加邮件内容
    msg['Date'] = formatdate(localtime=True)
    mime_text = MIMEText(html_content, 'html', mime_charset)
    msg.attach(mime_text)

    # 添加附件
    for fname in files or []:
        # 注意：获得文件名，文件路径在调用的当前路径下
        basename = os.path.basename(fname)
        with open(fname, "rb") as f:
            part = MIMEApplication(
                f.read(),
                Name=basename
            )
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename
            part['Content-ID'] = '<%s>' % basename
            msg.attach(part)

    # 发送邮件
    send_MIME_email(e_from, recipients, msg,
                    host, port,
                    ssl, starttls,
                    user, password,
                    dryrun)


def send_MIME_email(e_from, e_to, mime_msg,
                    host, port,
                    ssl=False, starttls=False,
                    user=None, password=None,
                    dryrun=False):
    """发送邮件 ."""
    log = LoggingMixin().log

    if not user or not password:
        log.debug("No user/password found for SMTP, so logging in with no authentication.")

    if not dryrun:
        s = smtplib.SMTP_SSL(host, port) if ssl else smtplib.SMTP(host, port)
        if starttls:
            s.starttls()
        s.login(user, password)
        log.info("Sent an alert email to %s", e_to)
        s.sendmail(e_from, e_to, mime_msg.as_string())
        s.quit()


def get_email_address_list(address_string):
    """多个收件人用逗号或分号分隔，并转化为数组 ."""
    if isinstance(address_string, basestring):
        if ',' in address_string:
            address_string = address_string.split(',')
        elif ';' in address_string:
            address_string = address_string.split(';')
        else:
            address_string = [address_string]

    return address_string
