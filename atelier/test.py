"""

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
        
class SubProcessTestCase(unittest.TestCase):
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
        
    def run_subprocess(self,args,**kw): 
        """
        Additional keywords can be 
        `cwd` : the working directory
        """
        env = dict(self.default_environ)
        for k in self.inheritable_envvars:
            v = os.environ.get(k,None)
            if v is not None:
                env[k] = v
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
        
    def run_simple_doctests(self,n,**kw): # env.simple_doctests
        #~ cmd = "python -m doctest %s" % filename    
        args = ["python"] 
        args += ["-m"]
        args += ["doctest"]
        args += [n]
        self.run_subprocess(args,**kw)
        
    def run_docs_django_tests(self,n,**kw): # django_doctests
        args = ["django-admin.py"] 
        args += ["test"]
        args += ["--settings=%s" % n]
        args += ["--failfast"]
        args += ["--verbosity=0"]
        args += ["--pythonpath=%s" % self.project_root.child('docs')]
        self.run_subprocess(args,**kw)

    def run_django_manage_test(self,db,**kw): # run_django_databases_tests
        p = self.project_root.child(*db.split('/'))
        args = ["python","manage.py"] 
        args += ["test"]
        #~ args += more
        args += ["--noinput"]
        args += ["--failfast"]
        #~ args += ["--settings=settings"]
        args += ["--pythonpath=%s" % p.absolute()]
        kw.update(cwd=p)
        self.run_subprocess(args,**kw)
        
    #~ def run_django_admin_tests(self,settings_module,**kw): # django_admin_tests
    def run_django_admin_test(self,settings_module,**kw): # django_admin_tests
        args = ["django-admin.py"] 
        args += ["test"]
        args += ["--settings=%s" % settings_module]
        args += ["--noinput"]
        args += ["--failfast"]
        args += ["--traceback"]
        args += ["--verbosity=0"]
        self.run_subprocess(args,**kw)
    
        #~ cmd = "django-admin.py test --settings=%s --verbosity=0 --failfast --traceback" % prj

    def run_docs_doctests(self,filename):
        """
        Run a simple doctest for specified file
        """
        filename = 'docs/' + filename
        #~ p = self.project_root.child(*filename.split('/')).parent
        #~ os.environ['DJANGO_SETTINGS_MODULE']='settings'
        #~ oldcwd = os.getcwd()
        #~ self.project_root.child('docs').chdir()
        #~ p.chdir()
        #~ sys.path.insert(0,'.')
        #~ print p
        sys.path.insert(0,'docs')
        import conf
        doctest.testfile(filename, module_relative=False,encoding='utf-8')
        del sys.path[0]
        #~ os.chdir(oldcwd)
