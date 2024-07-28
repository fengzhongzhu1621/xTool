"""
cipher rot13 'Hello world!'  # Uryyb jbeyq!
cipher rot13 'Uryyb jbeyq!'  # Hello world!
cipher caesar-encode 1 'Hello world!'  # Ifmmp xpsme!
cipher caesar-decode 1 'Ifmmp xpsme!'  # Hello world!
"""

import fire


def caesar_encode(n=0, text=''):
    return ''.join(_caesar_shift_char(n, char) for char in text)


def caesar_decode(n=0, text=''):
    return caesar_encode(-n, text)


def rot13(text):
    return caesar_encode(13, text)


def _caesar_shift_char(n=0, char=' '):
    if not char.isalpha():
        return char
    if char.isupper():
        return chr((ord(char) - ord('A') + n) % 26 + ord('A'))
    return chr((ord(char) - ord('a') + n) % 26 + ord('a'))


def main():
    fire.Fire(name='cipher')


if __name__ == '__main__':
    main()
