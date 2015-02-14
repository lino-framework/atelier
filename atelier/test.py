# Copyright 2013-2015 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""
Defines an extended TestCase whith methods to launch a subprocess.

- :meth:`TestCase.run_packages_test`
- :meth:`TestCase.run_subprocess`
- :meth:`TestCase.run_simple_doctests`

"""
import unittest
import glob
import sys
from setuptools import find_packages

from atelier.utils import SubProcessParent


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
        # print ("20150214b run_subprocess")
        rv = p.returncode
        #~ kw.update(stderr=buffer)
        #~ rv = subprocess.call(args,**kw)
        if rv != 0:
            cmd = ' '.join(args)
            #~ self.fail("%s returned %d:-----\n%s\n-----" % (cmd,rv,buffer.getvalue()))
            # (out, err) = p.communicate()
            msg = "%s (%s) returned %d:\n-----\n%s\n-----" % (cmd, kw, rv, out)
            # print msg
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
                    args = [sys.executable]
                    args += ["-m"]
                    args += ["atelier.doctest_utf8"]
                    args += [fn]
                    self.run_subprocess(args, **kw)
                if not ok:
                    self.fail("no files matching %s" % ln)

    def run_unittest(self, filename, **kw):
        """
        run unittest of given file in a subprocess
        """
        args = ["python"]
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
