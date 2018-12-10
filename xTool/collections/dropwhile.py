from __future__ import absolute_import

from builtins import next
from itertools import dropwhile


def rindex( l, v ):
    """
    Like l.index(v) but finds last occurrence of value v in sequence l.

    :type l: anything

    >>> rindex( [0], 0 )
    0
    >>> rindex( [0,0], 0 )
    1
    >>> rindex( [0,1], 0 )
    0
    >>> rindex( [0,1,0,1], 0 )
    2
    >>> rindex( [0,1,0,1], 1 )
    3
    >>> rindex( [0], 1 )
    Traceback (most recent call last):
    ...
    ValueError: 1
    >>> rindex( [None], None )
    0
    >>> rindex( [], None )
    Traceback (most recent call last):
    ...
    ValueError: None
    >>> rindex( "0101", '0')
    2
    >>> rindex( (0,1,0,1), 0 )
    2
    >>> from builtins import range
    >>> rindex( range(3), 2 )
    2
    """
    try:
        n = next( dropwhile( lambda i_x: v != i_x[1], enumerate( reversed( l ), 1 ) ) )[ 0 ]
    except StopIteration:
        raise ValueError( v )
    else:
        return len( l ) - n
