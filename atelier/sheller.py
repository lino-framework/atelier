# -*- coding: UTF-8 -*-
# Copyright 2016 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""Defines the :class:`Sheller` class.

.. to test just this module:

   python -m doctest atelier/sheller.py

I guess that others have invented similar things before, and I saw
`doctest2
<https://pythonhosted.org/doctest2/intro_for_existing.html>`__ but am
afraid switching to it because it seems not maintained. My solution is
admittedly less beautiful but much simpler.

"""

from __future__ import print_function
from builtins import str
# from builtins import input
from builtins import object
# Python 2 and 3:
from future.utils import python_2_unicode_compatible
import six
from six.moves import input

# from __future__ import unicode_literals
# causes problems on Windows where `subprocess.Popen` wants only plain strings

import os
import sys
import locale
import types
import datetime
import subprocess


class Sheller(object):
    """A sheller is a little helper object to be used in tested documents
for running shell scripts and testing their output.

Usage example:

>>> import os
>>> from atelier.sheller import Sheller
>>> shell = Sheller(os.path.dirname(__file__))
>>> shell('ls *.py')
doctest_utf8.py
__init__.py
jarbuilder.py
projects.py
rstgen.py
setup_info.py
sheller.py
test.py
utils.py

    """
    def __init__(self, cwd=None):
        self.cwd = cwd

    def __call__(self, cmd, **kwargs):
        """Run the specified shell command `cmd` in a subprocess and print its
        output to stdout. This is designed for usage from within a doctest
        snippet.

        If `cmd` is a multiline string, semicolons are automatically
        inserted as line separators.

        One challenge is that we cannot simply use `subprocess.call`
        because `sys.stdout` is handled differently when running inside
        doctest.

        """
        cmd = [ln for ln in cmd.splitlines() if ln.strip()]
        cmd = ';'.join(cmd)

        if self.cwd:
            kwargs.update(cwd=self.cwd)

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE,
            universal_newlines=True,
            stderr=subprocess.STDOUT, shell=True, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        output = output.strip()
        print(output)
        # if(output):
        #     print(output.strip())
        # else:
        #     print("(exit status {})".format(retcode))

