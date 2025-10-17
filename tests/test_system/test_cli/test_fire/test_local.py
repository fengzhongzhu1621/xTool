"""
$ python test_local.py english
Hello World

$ python test_local.py spanish
Hola Mundo
"""

import fire

if __name__ == '__main__':
    english = 'Hello World'
    spanish = 'Hola Mundo'
    fire.Fire()
