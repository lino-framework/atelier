# -*- coding: UTF-8 -*-
# python setup.py test -s tests.BasicTests.test_utils
# Copyright 2009-2020 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.

"""
Defines a series of utility classes and functions.

"""

# import six
# from six.moves import input
# from builtins import str
# from builtins import object
import re

from unipath import Path
from pprint import pprint

from rstgen.utils import *

def dict_py2(old_dict):
    """Convert the given `dict` so that it's `repr` is the same for both
    Python 2 and 3.

    Deprecated. Use :func:`rmu` instead.
    """
    from future.utils import viewitems
    new_dict = {}
    for (key, value) in viewitems(old_dict):
        if type(value) == dict:
            new_dict[str(key)] = dict_py2(value)
        elif type(value) == list:
            new_dict[str(key)] = list_py2(value)
        elif type(value) == tuple:
            new_dict[str(key)] = tuple_py2(value)
        else:
            if isinstance(value, bool):
                new_dict[str(key)] = value
            else:
                new_dict[str(key)] = str(value)
    return new_dict


def list_py2(old_list):
    """Convert the given `list` so that it's `repr` is the same for both
    Python 2 and 3.

    Deprecated. Use :func:`rmu` instead.

    """
    new_list = []
    for item in old_list:
        if type(item) == dict:
            new_list.append(dict_py2(item))
        elif type(item) == tuple:
            new_list.append(tuple_py2(item))
        else:
            new_list.append(str(item))
    return new_list


def tuple_py2(old_tuple):
    """Convert the given `tuple` so that it's `repr` is the same for both
    Python 2 and 3.

    Deprecated. Use :func:`rmu` instead.

    """
    lst = list(old_tuple)
    lst = list_py2(lst)
    return tuple(lst)


def rmu(x):
    u"""Remove the 'u' prefix from unicode strings under Python 2 in order
    to produce Python 3 compatible output in a doctested code snippet.

    >>> lst = [123, "123", u"Äöü"]
    >>> print(rmu(lst))
    [123, '123', '\\xc4\\xf6\\xfc']
    >>> print(rmu(tuple(lst)))
    (123, '123', '\\xc4\\xf6\\xfc')
    >>> dct = {i: i for i in lst}
    >>> print(rmu(dct)) #doctest: +ELLIPSIS
    {...'\\xc4\\xf6\\xfc': '\\xc4\\xf6\\xfc'...}

    """
    if isinstance(x, Path):
        return x
    # if isinstance(x, collections.namedtuple):
    #     return x
    if isinstance(x, list):
        return [rmu(i) for i in x]
    if isinstance(x, tuple):
        return tuple([rmu(i) for i in x])
    if isinstance(x, dict):
        return {rmu(k):rmu(v) for k,v in x.items()}
    if isinstance(x, str):
        return str(x)
    return x

def sixprint(*args):
    """Like print, but simulating PY3 output under PY2."""
    for x in args:
        # if six.PY2 and isinstance(x, set):
        #     print("{%s}" % ', '.join([str(rmu(i)) for i in x]))
        # else:
        pprint(rmu(x))

# def get_visual_editor():
#     """Returns the name of the visual editor, usually stored in the
#     `VISUAL` environment variable.  If `VISUAL` is not set, return the
#     value of `EDITOR`.

#     https://help.ubuntu.com/community/EnvironmentVariables

#     """
#     return os.environ.get('VISUAL') or os.environ.get('EDITOR')
