# -*- coding: UTF-8 -*-
# Copyright 2013-2016 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""A wrapper for Python's doctest.

Because the command-line interface of `python -m doctest` has no way
to specify an encoding of a (non-.py) input file.

Code originally copied from Python 2.7 doctest.py

About the :message:`ValueError: Attempted relative import in
non-package` problem: see `Doctest and relative imports
<http://stackoverflow.com/questions/4047227/doctest-and-relative-imports>`_
where Jason Scheirer advises:

    I would get rid of the relative imports, many Python style guides
    strongly discourage them, most forbid them.

"""
from __future__ import print_function

import os
import sys
import doctest


def _test():

    testfiles = [arg for arg in sys.argv[1:] if arg and arg[0] != '-']
    if len(testfiles) == 0:
        name = os.path.basename(sys.argv[0])
        if '__loader__' in globals():          # python -m
            name, _ = os.path.splitext(name)
        print("usage: {0} [-v] file ...".format(name))
        return 2

    for filename in testfiles:
        if filename.endswith(".py"):
            # It is a module -- insert its dir into sys.path and try to
            # import it. If it is part of a package, that possibly
            # won't work because of package imports.
            dirname, filename = os.path.split(filename)
            sys.path.insert(0, dirname)
            m = __import__(filename[:-3])
            del sys.path[0]
            failures, _ = doctest.testmod(m)
            #~ raise Exception("20131022 tested %s" % m)
        else:
            failures, _ = doctest.testfile(
                os.path.abspath(filename),
                optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                encoding='utf-8',
                module_relative=False)

        if failures:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(_test())
