# Copyright 2013 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""
Defines an extended TestCase whith shortcut methods to launch
a subprocess.

- :meth:`TestCase.run_packages_test`
- :meth:`TestCase.run_subprocess`
- :meth:`TestCase.run_simple_doctests`

"""
import os
import sys
import doctest
import unittest
import subprocess
from setuptools import find_packages

from atelier.utils import SubProcessParent

class TestCase(unittest.TestCase,SubProcessParent):
    "Deserves a docstring"
    project_root = NotImplementedError
    #~ maxDiff = None
    
    def run_packages_test(self,declared_packages):
        """
        Checks whether the `packages` parameter to setup seems correct.
        """
        found_packages = find_packages()
        found_packages.remove('tests') # if it exists, remove it
        found_packages.sort()
        declared_packages.sort()
        self.assertEqual(found_packages,declared_packages)
        
    def run_subprocess(self,args,**kw): 
        """
        Run a subprocess, wait until it terminates, 
        fail if the returncode is not 0.
        """
        p = self.open_subprocess(args,**kw)
        p.wait()
        rv = p.returncode
        #~ kw.update(stderr=buffer)
        #~ rv = subprocess.call(args,**kw)
        if rv != 0:
            cmd = ' '.join(args)
            #~ self.fail("%s returned %d:-----\n%s\n-----" % (cmd,rv,buffer.getvalue()))
            (out, err) = p.communicate()
            msg = "%s (%s) returned %d:\n-----\n%s\n-----" % (cmd,kw,rv,out)
            print msg
            self.fail(msg)
        
    def run_simple_doctests(self,filename,**kw): # env.simple_doctests
        """
        run doctest of given file in a subprocess
        """
        #~ cmd = "python -m doctest %s" % filename    
        args = ["python"] 
        args += ["-m"]
        args += ["atelier.doctest_utf8"]
        #~ args += ["doctest"]
        args += [filename]
        self.run_subprocess(args,**kw)

    #~ def run_simple_doctests(self,filename,**kw): # env.simple_doctests
        #~ doctest.testfile(os.path.abspath(filename),
            #~ encoding='utf-8',
            #~ module_relative=False)
