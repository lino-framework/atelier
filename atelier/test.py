# Copyright 2013-2016 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""
Defines an extended TestCase whith methods to launch a subprocess.

- :meth:`TestCase.run_packages_test`
- :meth:`TestCase.run_subprocess`
- :meth:`TestCase.run_simple_doctests`

"""
from __future__ import unicode_literals

import six
import unittest
import glob
import sys
from setuptools import find_packages
# from unipath import Path

# from atelier import SETUP_INFO
from atelier.utils import SubProcessParent

# ROOTDIR = Path(__file__).parent.parent


def interpreter_args():
    # if 'coverage' in sys.modules:
    #     # raise Exception('20160119')
    #     return ['coverage', 'run']
    return [sys.executable]


class TestCase(unittest.TestCase, SubProcessParent):
    "Deserves a docstring"
    project_root = NotImplementedError
    #~ maxDiff = None

    def run_packages_test(self, declared_packages):
        """
        Checks whether the `packages` parameter to setup seems correct.
        """
        found_packages = find_packages()
        # if tests exists, remove it:
        if 'tests' in found_packages:
            found_packages.remove('tests')
        found_packages.sort()
        declared_packages.sort()
        self.assertEqual(found_packages, declared_packages)

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
                    args += ["atelier.doctest_utf8"]
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

    # ~ def run_simple_doctests(self,filename,**kw): # env.simple_doctests
        #~ doctest.testfile(os.path.abspath(filename),
            #~ encoding='utf-8',
            #~ module_relative=False)


# class BaseTestCase(TestCase):
#     project_root = ROOTDIR
    

# class BasicTests(BaseTestCase):

#     def test_01(self):
#         self.assertEqual(1+1, 2)

#     def test_utils(self):
#         self.run_simple_doctests('atelier/utils.py')

#     def test_rstgen(self):
#         self.run_simple_doctests('atelier/rstgen.py')


# class PackagesTests(BaseTestCase):
#     def test_packages(self):
#         self.run_packages_test(SETUP_INFO['packages'])


# class SphinxTests(BaseTestCase):
#     def test_sphinxconf(self):
#         self.run_simple_doctests('atelier/sphinxconf/__init__.py')

#     def test_base(self):
#         self.run_simple_doctests('atelier/sphinxconf/base.py')

#     def test_sigal(self):
#         self.run_simple_doctests('atelier/sphinxconf/sigal_image.py')


