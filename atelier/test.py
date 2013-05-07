"""
Defines an extended TestCase whith shortcut methods that launch
a subprocess.

- :meth:`TestCase.run_packages_test`
- :meth:`TestCase.run_subprocess`
- :meth:`TestCase.run_simple_doctests`

:copyright: Copyright 2013 by Luc Saffre.
:license: BSD, see LICENSE for more details.

"""
import os
import sys
import doctest
import unittest
import subprocess
from setuptools import find_packages

import six
        
class TestCase(unittest.TestCase):
    "Deserves a docstring"
    project_root = NotImplementedError
    default_environ = dict()
    inheritable_envvars = ('VIRTUAL_ENV','PYTHONPATH','PATH')
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
        
    def build_environment(self):
        env = dict(self.default_environ)
        for k in self.inheritable_envvars:
            v = os.environ.get(k,None)
            if v is not None:
                env[k] = v
        return env
        
    def run_subprocess(self,args,**kw): 
        """
        Additional keywords can be 
        `cwd` : the working directory
        """
        env = self.build_environment()
        kw.update(env=env)
        #~ subprocess.check_output(args,**kw)
        #~ from StringIO import StringIO
        #~ buffer = StringIO()
        kw.update(stdout=subprocess.PIPE)
        kw.update(stderr=subprocess.STDOUT)
        p = subprocess.Popen(args,**kw)
        p.wait()
        rv = p.returncode
        #~ kw.update(stderr=buffer)
        #~ rv = subprocess.call(args,**kw)
        if rv != 0:
            cmd = ' '.join(args)
            #~ self.fail("%s returned %d:-----\n%s\n-----" % (cmd,rv,buffer.getvalue()))
            (out, err) = p.communicate()
            msg = "%s (%s) returned %d:\n-----\n%s\n-----" % (cmd,env,rv,out)
            print msg
            self.fail(msg)
        
    def run_simple_doctests(self,filename,**kw): # env.simple_doctests
        """
        """
        #~ cmd = "python -m doctest %s" % filename    
        args = ["python"] 
        args += ["-m"]
        args += ["doctest"]
        args += [filename]
        self.run_subprocess(args,**kw)
        

