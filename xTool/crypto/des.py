# -*- coding: utf8 -*-
"""
一个基于DES的头部签名加密算法
"""

import binascii
import random
import time

import pyDes


class DesAuthentication(object):
    def __init__(self, appkey, sysid):
        """初始化

        Args:
            appkey(string): 申请的appkey
            deskey(string): des加密key
        """
        self._appkey = str(appkey).strip()
        self._sysid = str(sysid).strip()
        self._deskey = str(self._sysid).ljust(8, '-')

    def getDeskey(self):
        return self._deskey

    @staticmethod
    def des_signature(key, text):
        """构造签名

        Args:
            summary: des加密
            param key: 加密key
            text: 明文

        Returns:
            返回十六进制大写密文
        """
        k = pyDes.des(key, pyDes.CBC, key, pad=None, padmode=pyDes.PAD_PKCS5)
        d = k.encrypt(text)
        # 加密后的字母需要大写
        return binascii.hexlify(d).upper()

    def build_header(self, content_type='application/x-www-form-urlencoded'):
        '''获取HTTP头部消息内容

        Args
            appkey: 申请的appkey
            random: 随机数
            timestamp: 客户端请求时，当前时间的时间戳（只要到秒即可）
            signature:
                    以appkey对应的sysid为密钥，random ,timestamp拼接的字符串为
                    data进行DES算法加密后生成的字符串（需要转换成大写字母）。
                    例如：
                    random=1799,timestamp= 1356419423
                    sting data= “random1799timestamp1356419423”;
                    string signature= DESEncrypt(data, sysid.ToString())
                    DES的密钥要求为8位，不足的用“-”补齐，多余的需截断。

        Notes:
            服务器端验证权限的条件：

            1、验证请求时间的有效性：timestamp参数在服务器端的时间窗口内
            （目前设置时间窗口的长度是3分钟）。

            2、验证签名：根据appkey对应的sysid，random, timestamp进行DES加密，
               生成的签名与客户端传入的签名是否相等。

            3、验证权限：appkey有调用该接口的权限。
        '''
        # 假定4位随机数
        rand_num = str(random.randint(1000, 9999))
        # 当前时间戳取整
        time_stamp = int(time.time())
        time_stamp = str(time_stamp)[:10]
        # 加密的明文
        h_data = 'random%stimestamp%s' % (rand_num, time_stamp)
        # des加密
        signature = self.des_signature(self._deskey, h_data)
        headers = {
            'appkey': self._appkey,
            'random': rand_num,
            'timestamp': time_stamp,  # 注意只要10位数
            'signature': signature,
            'Content-Type': content_type,
        }
        return headers
