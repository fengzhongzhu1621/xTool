import base64
import os
import re

# pip install pycryptodome
from Crypto.Cipher import AES


class OpensslAes256CbcCipher:
    """
    兼容bash openssl加解密
    echo $plaintext | openssl enc -salt -aes-256-cbc -e -a -k $password
    encrypted=`echo $plaintext | openssl enc -salt -aes-256-cbc -e -a -k $password`
    echo $encrypted | openssl enc -salt -aes-256-cbc -d -a -k $password
    """

    def __init__(self, password, msgdgst='md5'):
        password = password.encode('ascii', 'ignore')  # convert to ASCII
        self.password = password
        self.msgdgst = msgdgst

    def get_key_and_iv(self, salt, klen=32, ilen=16):
        '''
        Derive the key and the IV from the given password and salt.

        This is a niftier implementation than my direct transliteration of
        the C++ code although I modified to support different digests.

        CITATION: http://stackoverflow.com/questions/13907841/implement-openssl-aes-encryption-in-python

        @param password  The password to use as the seed.
        @param salt      The salt.
        @param klen      The key length.
        @param ilen      The initialization vector length.
        @param msgdgst   The message digest algorithm to use.
        '''
        # equivalent to:
        #   from hashlib import <mdi> as mdf
        #   from hashlib import md5 as mdf
        #   from hashlib import sha512 as mdf
        mdf = getattr(__import__('hashlib', fromlist=[self.msgdgst]), self.msgdgst)

        try:
            maxlen = klen + ilen
            keyiv = mdf(self.password + salt).digest()
            tmp = [keyiv]
            while len(tmp) < maxlen:
                tmp.append(mdf(tmp[-1] + self.password + salt).digest())
                keyiv += tmp[-1]  # append the last byte
            key = keyiv[:klen]
            iv = keyiv[klen : klen + ilen]
            return key, iv
        except UnicodeDecodeError:
            return None, None

    def encrypt(self, plaintext, chunkit=True, salt=None):
        '''
        Encrypt the plaintext using the password using an openssl
        compatible encryption algorithm. It is the same as creating a file
        with plaintext contents and running openssl like this:

        $ cat plaintext
        <plaintext>
        $ openssl enc -e -aes-256-cbc -base64 -salt \\
            -pass pass:<password> -n plaintext

        @param password  The password.
        @param plaintext The plaintext to encrypt.
        @param chunkit   Flag that tells encrypt to split the ciphertext
                         into 64 character (MIME encoded) lines.
                         This does not affect the decrypt operation.
        @param msgdgst   The message digest algorithm.
        '''
        if not salt:
            salt = os.urandom(8)
        key, iv = self.get_key_and_iv(salt)
        if key is None:
            return None

        # PKCS#7 padding
        padding_len = 16 - (len(plaintext) % 16)
        if isinstance(plaintext, str):
            padded_plaintext = plaintext + (chr(padding_len) * padding_len)
        else:  # assume bytes
            padded_plaintext = plaintext + (bytearray([padding_len] * padding_len))

        # Encrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(padded_plaintext)

        # Make openssl compatible.
        # I first discovered this when I wrote the C++ Cipher class.
        # CITATION: http://projects.joelinoff.com/cipher-1.1/doxydocs/html/
        openssl_ciphertext = b'Salted__' + salt + ciphertext
        b64 = base64.b64encode(openssl_ciphertext)
        if not chunkit:
            return b64

        line_len = 64

        def chunk(s):
            return b'\n'.join(s[i : min(i + line_len, len(s))] for i in range(0, len(s), line_len))

        return chunk(b64)

    def decrypt(self, ciphertext):
        '''
        Decrypt the ciphertext using the password using an openssl
        compatible decryption algorithm. It is the same as creating a file
        with ciphertext contents and running openssl like this:

        $ cat ciphertext
        # ENCRYPTED
        <ciphertext>
        $ egrep -v '^#|^$' | \\
            openssl enc -d -aes-256-cbc -base64 -salt -pass pass:<password> -in ciphertext
        @param password   The password.
        @param ciphertext The ciphertext to decrypt.
        @param msgdgst    The message digest algorithm.
        @returns the decrypted data.
        '''

        # unfilter -- ignore blank lines and comments
        if isinstance(ciphertext, str):
            filtered = ''
            nl = '\n'
            re1 = r'^\s*$'
            re2 = r'^\s*#'
        else:
            filtered = b''
            nl = b'\n'
            re1 = b'^\\s*$'
            re2 = b'^\\s*#'

        for line in ciphertext.split(nl):
            line = line.strip()
            if re.search(re1, line) or re.search(re2, line):
                continue
            filtered += line + nl

        # Base64 decode
        raw = base64.b64decode(filtered)
        assert raw[:8] == b'Salted__'
        salt = raw[8:16]  # get the salt

        # Now create the key and iv.
        key, iv = self.get_key_and_iv(salt)
        if key is None:
            return None

        # The original ciphertext
        ciphertext = raw[16:]

        # Decrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(ciphertext)

        if isinstance(padded_plaintext, str):
            padding_len = ord(padded_plaintext[-1])
        else:
            padding_len = padded_plaintext[-1]
        plaintext = padded_plaintext[:-padding_len]
        return plaintext.rstrip(b'\n')
