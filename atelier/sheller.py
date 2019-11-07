# -*- coding: UTF-8 -*-
# $ doctest atelier/sheller.py
# Copyright 2016-2019 by Rumma & Ko Ltd.
# License: BSD, see LICENSE for more details.

"""Defines the :class:`Sheller` class for testing bash commands in a doctest.

Others have invented similar things before.
For example `doctest2 <https://pythonhosted.org/doctest2/intro_for_existing.html>`__
by Devin Jeanpierre.
Another alternative is `Clatter
<https://clatter.readthedocs.io/en/latest/readme.html>`__
by Michael Delgado.

"""

import os
import sys
import locale
import types
import datetime
import subprocess
from tempfile import TemporaryDirectory


class Sheller:
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

When you don't specify a directory, Sheller creates a temporary directory and
has all processes run there.


    """
    def __init__(self, cwd=None):
        if cwd is None:
            self.temp_dir = TemporaryDirectory()
            cwd = self.temp_dir.name
        self.cwd = cwd

    def __call__(self, cmd, **kwargs):
        """Run the specified shell command `cmd` in a subprocess and print its
        output to stdout. This is designed for usage from within a doctest
        snippet.

        If `cmd` is a multiline string, semicolons are automatically inserted as
        line separators.

        One challenge is that we cannot simply use `subprocess.call` because
        `sys.stdout` is handled differently when running inside doctest.

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
