# Copyright 2013-2021 Rumma & Ko Ltd.
# License: BSD, see LICENSE for more details.

"""
Defines tools for testing.

- The :func:`make_docs_suite` function to automatically run :cmd:`doctest` on each document of a doctree.
- an extended TestCase with methods to launch a subprocess.

"""

import os
from os.path import join
import unittest
import glob
from fnmatch import fnmatch
import sys
from setuptools import find_packages
# from pathlib import Path
import subprocess

from atelier.utils import SubProcessParent

DOCTEST_CMD = "doctest"


def interpreter_args():
    # if 'coverage' in sys.modules:
    #     # raise Exception('20160119')
    #     return ['coverage', 'run']
    return [sys.executable]


class DocTestCase(unittest.FunctionTestCase, SubProcessParent):
    # internally used by make_docs_suite

    def __init__(self, filename, addenv=None):
        self.addenv = addenv
        def func():
            args = [sys.executable]
            args += ["-m"]
            args += [DOCTEST_CMD]
            args += [filename]
            self.run_subprocess(args)
        func.__name__ = filename
        super(DocTestCase, self).__init__(func)

    def build_environment(self):
        env = super(DocTestCase, self).build_environment()
        env.pop('PYTHONPATH', None)  # fixes #1296
        if self.addenv is not None:
            env.update(self.addenv)
        return env


def make_docs_suite(docs_root, include="*.rst", exclude=None,
                    addenv=None):
    """
    Discover the doc files in specified directory docs_root and below
    and return a test suite which tests them all, each one in a
    separate subprocess.

    `include` is a filename pattern of the files to include. Default
    is `'*.rst'`.

    `exclude` is an optional filename pattern of the files to
    exclude. Default is None.

    `addenv` is an optional dictionary with additional environment
    variables to be set in the subprocess. Default is None.

    The tests are sorted alphabeticallly in order to avoid surprises
    when some doctest inadvertantly modifies the database.
    """
    suite = unittest.TestSuite()
    count = 0
    for root, dirs, files in os.walk(docs_root):
        dirs.sort()
        for file in sorted(files):
            fn = join(root, file)
            if fnmatch(fn, include):
                if exclude and fnmatch(fn, exclude):
                    print("Not testing file {}".format(fn))
                    continue
                suite.addTest(DocTestCase(fn, addenv))
                count += 1
    print("Loaded {} doctests from {}".format(count, docs_root))
    return suite


class TestCase(unittest.TestCase, SubProcessParent):
    "A unittest testcase with some additional utility methods."

    project_root = NotImplementedError
    # maxDiff = None

    def run_packages_test(self, declared_packages):
        """
        Checks whether the `packages` parameter to setup seems correct, i.e.
        whether all packages in the repository are being published in a source
        distribution.  This is kind of basic hygiene because you usually forget
        to update this parameter when you add or remove a package.

        """
        found_packages = find_packages()
        # if tests exists, remove it:
        if 'tests' in found_packages:
            found_packages.remove('tests')
        found_packages.sort()
        declared_packages.sort()
        self.assertEqual(found_packages, declared_packages)

    def run_simple_doctests(self, filenames, **kw):  # env.simple_doctests
        """
        run doctest of given file in a subprocess
        """
        for ln in filenames.splitlines():
            ln = ln.strip()
            if ln and not ln.startswith('#'):
                ok = False
                for fn in glob.glob(ln):
                    ok = True
                    args = interpreter_args()
                    args += ["-m"]
                    # args += ["doctest"]
                    args += [DOCTEST_CMD]
                    args += [fn]
                    self.run_subprocess(args, **kw)
                if not ok:
                    self.fail("no files matching %s" % ln)

    def run_unittest(self, filename, **kw):
        """
        run unittest of given file in a subprocess
        """
        args = interpreter_args()
        #~ args += ["-Wall"]
        args += ["-m"]
        args += ["unittest"]
        #~ args += ["--buffer"]
        args += [filename]
        self.run_subprocess(args, **kw)
