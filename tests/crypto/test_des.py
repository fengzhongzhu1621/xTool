# coding: utf8

import pytest
import unittest
from xTool.crypto import des


class TestDes(unittest.TestCase):
    """测试Des类 ."""
    def setUp(self):
        self.appkey = '8c6e8d92ad0f433fa5e54ada746d49c1'
        self.sysid = 2
        self.desAuthentication = des.DesAuthentication(self.appkey, self.sysid)

    def test_des_signature(self):
        rand_num = 1242
        time_stamp = 1375685363
        h_data = 'random%stimestamp%s' % (rand_num, time_stamp)
        # des加密
        signature = self.desAuthentication.des_signature(self.desAuthentication.getDeskey(), h_data)
        actualValue = b'041F03E83D85AD43B0BCE79FBB6841DAA87CC6C874BB71B45F5214DDF80BEB16'
        self.assertEqual(actualValue, signature)

    def test_build_header(self):
        desHeader = self.desAuthentication.build_header()
        self.assertEqual(desHeader.get('appkey'), self.appkey)
        self.assertEqual(len(desHeader.get('signature')), 64)
