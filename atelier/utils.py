# -*- coding: UTF-8 -*-
# Copyright 2009-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.

"""
Defines a series of utility classes and functions.

$ python setup.py test -s tests.BasicTests.test_utils

"""

from __future__ import print_function

import six
from six.moves import input
from builtins import str
from builtins import object
from future.types import newstr
from future.utils import python_2_unicode_compatible
import re

# from __future__ import unicode_literals
# causes problems on Windows where `subprocess.Popen` wants only plain strings

import os
import sys
import locale
import datetime
import subprocess
# import collections
from dateutil import parser as dateparser
from dateutil.relativedelta import relativedelta
from contextlib import contextmanager
from unipath import Path
from pprint import pprint


@python_2_unicode_compatible
class AttrDict(dict):

    """
    Dictionary-like helper object.
    
    Usage example:
    
    >>> from atelier.utils import AttrDict
    >>> a = AttrDict()
    >>> a.define('foo', 1)
    >>> a.define('bar', 'baz', 2)
    >>> a == {"bar": {"baz": 2}, "foo": 1}
    True
    >>> print(a.foo)
    1
    >>> print(a.bar.baz)
    2
    >>> print(a.resolve('bar.baz'))
    2
    >>> print(a.bar)
    {'baz': 2}
    
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                "AttrDict instance has no key '%s' (keys are %s)" % (
                    name, ', '.join(list(self.keys()))))

    def define2(self, name, value):
        return self.define(*name.split('.') + [value])

    def define(self, *args):
        "args must be a series of names followed by the value"
        assert len(args) >= 2
        d = s = self
        for n in args[:-2]:
            d = s.get(n, None)
            if d is None:
                d = AttrDict()
                s[n] = d
            s = d
        oldvalue = d.get(args[-2], None)
        d[args[-2]] = args[-1]
        return oldvalue

    def resolve(self, name, default=None):
        """
        return an attribute with dotted name
        """
        o = self
        for part in name.split('.'):
            o = getattr(o, part, default)
            # o = o.__getattr__(part)
        return o


def iif(condition, true_value, false_value=None):
    """
    "Inline If" : an ``if`` statement as a function.

    Examples:

    >>> from atelier.utils import iif
    >>> print("Hello, %s world!" % iif(1+1==2, "real", "imaginary"))
    Hello, real world!
    >>> iif(True, "true")
    'true'
    >>> iif(False, "true")

    """
    if condition:
        return true_value
    return false_value


def i2d(i):
    """
    Convert `int` to `date`. Examples:

    >>> i2d(20121224)
    datetime.date(2012, 12, 24)

    """
    s = str(i)
    if len(s) != 8:
        raise Exception("Invalid date specification {0}.".format(i))
    d = dateparser.parse(s)
    d = datetime.date(d.year, d.month, d.day)
    # print(i, "->", v)
    return d


def i2t(s):
    """
    Convert `int` to `time`. Examples:
    
    >>> i2t(815)
    datetime.time(8, 15)
    
    >>> i2t(1230)
    datetime.time(12, 30)
    
    >>> i2t(12)
    datetime.time(12, 0)
    
    >>> i2t(1)
    datetime.time(1, 0)
    
    """
    s = str(s)
    if len(s) == 4:
        return datetime.time(int(s[:2]), int(s[2:]))
    if len(s) == 3:
        return datetime.time(int(s[:1]), int(s[1:]))
    if len(s) <= 2:
        return datetime.time(int(s), 0)
    raise ValueError(s)


def last_day_of_month(d):
    """Return the last day of the month of the given date.

    >>> from atelier.utils import i2d
    >>> last_day_of_month(i2d(20160212))
    datetime.date(2016, 2, 29)
    >>> last_day_of_month(i2d(20161201))
    datetime.date(2016, 12, 31)
    >>> last_day_of_month(i2d(20160123))
    datetime.date(2016, 1, 31)
    >>> last_day_of_month(i2d(20161123))
    datetime.date(2016, 11, 30)

    Thanks to `stackoverflow.com
    <http://stackoverflow.com/questions/42950/get-last-day-of-the-month-in-python>`_.

    """
    return d + relativedelta(day=31)
    # d = datetime.date(d.year, d.month + 1, 1)
    # return relativedelta(d, days=-1)


def isiterable(x):
    "Returns `True` if the specified object is iterable."
    try:
        iter(x)
    except TypeError:
        return False
    return True


def is_string(s):
    """Return True if the specified value is a string.
    """
    if six.PY2:
        return isinstance(s, six.string_types) or isinstance(s, newstr)
    return isinstance(s, six.string_types)
   
def isidentifier(s):
    """
    Check whether the given string can be used as a Python identifier.
    """
    if six.PY2:
        return re.match("[_A-Za-z][_a-zA-Z0-9]*$", s)
    return s.isidentifier()


def ispure(s):
    """Returns `True` if the specified string `s` is either None, or
    contains only ASCII characters, or is a validly encoded unicode
    string.

    """
    if s is None:
        return True
    if isinstance(s, (six.text_type, newstr)):
        return True
    if type(s) == bytes:
        try:
            s.decode('ascii')
        except UnicodeDecodeError:
            return False
        return True
    return False


def assert_pure(s):
    """
    raise an Exception if the given string is not :func:`ispure`.
    """
    #~ assert ispure(s), "%r: not pure" % s
    if s is None:
        return
    if isinstance(s, str):
        return True
    try:
        s.decode('ascii')
    except UnicodeDecodeError as e:
        raise Exception("%r is not pure : %s" % (s, e))


def confirm(prompt=None, default="y"):
    """
    Ask for user confirmation from the console.
    """
    if six.PY2:
        prompt = prompt.encode(
            sys.stdin.encoding or locale.getpreferredencoding(True))
    # print(20160324, type(prompt))
    prompt += " [Y,n]?"
    while True:
        ln = input(prompt)
        if not ln:
            ln = default
        if ln.lower() in ('y', 'j', 'o'):
            return True
        if ln.lower() == 'n':
            return False
        print("Please answer Y or N")


def indentation(s):
    r"""
    Examples:
    
    >>> from atelier.utils import indentation
    >>> indentation("")
    0
    >>> indentation("foo")
    0
    >>> indentation(" foo")
    1
    
    """
    return len(s) - len(s.lstrip())


def unindent(s):
    r"""
    Reduces indentation of a docstring to the minimum.
    Empty lines don't count.
    
    Examples:
    
    >>> from atelier.utils import unindent
    >>> unindent('')
    ''
    >>> print(unindent('''
    ...   foo
    ...     foo
    ... '''))
    <BLANKLINE>
    foo
      foo
    >>> print(unindent('''
    ... foo
    ...     foo
    ... '''))
    <BLANKLINE>
    foo
        foo
    """
    s = s.rstrip()
    lines = s.splitlines()
    if len(lines) == 0:
        return s.strip()
    mini = sys.maxsize
    for ln in lines:
        ln = ln.rstrip()
        if len(ln) > 0:
            mini = min(mini, indentation(ln))
            if mini == 0:
                break
    if mini == sys.maxsize:
        return s
    return '\n'.join([i[mini:] for i in lines])


class SubProcessParent(object):

    """
    Base class for :class:`atelier.test.TestCase`.
    Also used standalone by `lino.management.commands.makescreenshots`.
    """
    default_environ = dict()
    # inheritable_envvars = ('VIRTUAL_ENV', 'PYTHONPATH', 'PATH')

    def build_environment(self):
        """Contructs and return a `dict` with the environment variables for
        the future subprocess.

        """
        env = dict()
        env.update(os.environ)
        env.update(self.default_environ)
        # env.update(COVERAGE_PROCESS_START="folder/.coveragerc")
        # for k in self.inheritable_envvars:
        #     v = os.environ.get(k, None)
        #     if v is not None:
        #         env[k] = v
        return env

    def check_output(self, args, **kw):
        env = self.build_environment()
        kw.update(env=env)
        kw.update(stderr=subprocess.STDOUT)
        return subprocess.check_output(args, **kw)

    def open_subprocess(self, args, **kw):
        """Additional keywords will be passed to the `Popen constructor
        <http://docs.python.org/2.7/library/subprocess.html#popen-constructor>`_.
        They can be e.g.  `cwd` : the working directory

        """
        env = self.build_environment()
        # raise Exception("20170912 {}".format(env.keys()))
        kw.update(env=env)
        #~ subprocess.check_output(args,**kw)
        #~ from StringIO import StringIO
        #~ buffer = StringIO()
        kw.update(stdout=subprocess.PIPE)
        kw.update(stderr=subprocess.STDOUT)
        kw.update(universal_newlines=True)
        return subprocess.Popen(args, **kw)

    def run_subprocess(self, args, **kw):
        """
        Run a subprocess, wait until it terminates,
        fail if the returncode is not 0.
        """
        # print ("20150214 run_subprocess %r" % args)
        p = self.open_subprocess(args, **kw)

        # wait() will deadlock when using stdout=PIPE and/or
        # stderr=PIPE and the child process generates enough output to
        # a pipe such that it blocks waiting for the OS pipe buffer to
        # accept more data. Use communicate() to avoid that.
        if False:
            p.wait()
        else:
            out, err = p.communicate()
        # raise Exception("20160711 run_subprocess", out)
        rv = p.returncode
        # kw.update(stderr=buffer)
        # rv = subprocess.call(args,**kw)
        if rv != 0:
            cmd = ' '.join(args)
            if six.PY2:
                # if the output contains non-asci chars, then we must
                # decode here in order to wrap it into our msg. Later
                # we must re-encode it because exceptions, in Python
                # 2, don't want unicode strings.
                out = out.decode("utf-8")
            msg = "%s (%s) returned %d:\n-----\n%s\n-----" % (
                cmd, kw, rv, out)
            # try:
            #     msg = "%s (%s) returned %d:\n-----\n%s\n-----" % (
            #         cmd, kw, rv, out)
            # except UnicodeDecodeError:
            #     out = repr(out)
            #     msg = "%s (%s) returned %d:OOPS\n-----\n%s\n-----" % (
            #         cmd, kw, rv, out)

            # print msg
            if six.PY2:
                msg = msg.encode('utf-8')
            self.fail(msg)


def date_offset(ref, days=0, **offset):
    """
    Compute a date using a "reference date" and an offset.

    >>> r = i2d(20140222)

    In 10 days:
    >>> date_offset(r, 10)
    datetime.date(2014, 3, 4)

    Four hundred days ago:
    >>> date_offset(r, -400)
    datetime.date(2013, 1, 18)


    """
    if days:
        offset.update(days=days)
    if offset:
        return ref + datetime.timedelta(**offset)
    return ref


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
    if isinstance(x, six.string_types):
        return str(x)
    return x

def sixprint(*args):
    """Like print, but simulating PY3 output under PY2."""
    for x in args:
        if six.PY2 and isinstance(x, set):
            print("{%s}" % ', '.join([str(rmu(i)) for i in x]))
        else:
            pprint(rmu(x))

# def get_visual_editor():
#     """Returns the name of the visual editor, usually stored in the
#     `VISUAL` environment variable.  If `VISUAL` is not set, return the
#     value of `EDITOR`.

#     https://help.ubuntu.com/community/EnvironmentVariables

#     """
#     return os.environ.get('VISUAL') or os.environ.get('EDITOR')


@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)


