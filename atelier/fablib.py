# -*- coding: UTF-8 -*-
"""
The fabric tasks I use to manage my projects.
Use at your own risk.

To be used by creating a `fabfile.py` with at least the following 
two lines::

  from atelier.fablib import *
  setup_from_project("foobar")
  
  
  env.django_admin_tests.append(...)
  env.simple_doctests.append(...)
  env.tolerate_sphinx_warnings = True
  env.demo_databases.append('foobar.demo.settings')
  
Where "foobar" is the name of your main package.
  
This fablib uses the following `env` keys:

- `tolerate_sphinx_warnings` : whether `sphinx-build html` should tolerate warnings.

- (consult the source code)

:copyright: Copyright 2013 by Luc Saffre.
:license: BSD, see LICENSE for more details.
"""
import os
import sys
import doctest
import textwrap

#~ def clean_sys_path():
    #~ # print sys.path
    #~ if sys.path[0] == '':
        #~ del sys.path[0]
        #~ print "Deleted working directory from PYTHONPATH"


import datetime
import unittest
#~ import subprocess
from setuptools import find_packages
from unipath import Path
import sphinx
#~ import six
#~ from distutils.core import run_setup

import atelier
#~ import djangosite ; print djangosite.__file__
from atelier.utils import AttrDict
from atelier import rstgen
#~ from timtools.tools.synchronizer import Synchronizer


from fabric.api import env, local, task, prompt
from fabric.utils import abort, fastprint, puts, warn
from fabric.contrib.console import confirm
from fabric.api import lcd

#~ LONG_DATE_FORMAT = 

class RstFile(object):
    def __init__(self,local_root,url_root,parts):
        self.path = local_root.child(*parts)
        self.url = url_root + "/".join(parts)
        #~ self.parts = parts
        
      
      

def setup_from_project(main_package=None):
  
    #~ env.docs_rsync_dest = 'luc@lino-framework.org'
    #~ env.sdist_dir = '../lino/docs/dl'

    #~ HOME = Path(os.path.expanduser("~"))
    #~ REMOTE = AttrDict(
      #~ lf='lino-framework.org')
      
    env.ROOTDIR = Path().absolute()

    env.project_name = env.ROOTDIR.absolute().name

    env.setdefault('long_date_format',"%Y%m%d (%A, %d %B %Y)"  )
    #~ env.setdefault('work_root','')
    env.work_root = Path(env.work_root)
    env.sdist_dir = Path(env.sdist_dir)
    #~ env.django_doctests = []
    #~ env.django_admin_tests = []
    #~ env.bash_tests = []
    #~ env.django_databases = []
    #~ env.simple_doctests = []
    #~ env.docs_doctests = []
    env.main_package = main_package
    env.tolerate_sphinx_warnings = False
    env.demo_databases = []
    

    env.languages = None
    
    #~ print env.project_name

    env.DOCSDIR = Path(env.ROOTDIR,'docs')
    #~ env.BUILDDIR = Path(env.DOCSDIR,'.build')

    if not Path(env.ROOTDIR,'setup.py').exists():
        raise Exception("You must call 'fab' from a project's root directory.")
        
    if env.main_package:
        execfile(env.ROOTDIR.child(env.main_package,'setup_info.py'),globals()) # will set SETUP_INFO 
        env.SETUP_INFO = SETUP_INFO
    else:
        env.SETUP_INFO = None
        
    


#~ def confirm(msg,default='y',others='n',**override_callbacks):
    #~ text = "%s [%s%s]" % (msg,default.upper(),others)
    #~ def y(): return True
    #~ # def n(): abort("Missing user confirmation for:\n%s" % msg)
    #~ def n(): abort("Missing user confirmation")
    #~ callbacks = dict(y=y,n=n)
    #~ callbacks.update(override_callbacks)
    #~ while True:
        #~ answer = prompt(text)
        #~ # answer = raw_input(prompt)
        #~ if not answer: 
            #~ answer = default
        #~ answer = answer.lower()
        #~ if answer: 
            #~ return callbacks.get(answer)()
            
def must_confirm(*args,**kw):
    if not confirm(*args,**kw):
        abort("Dann eben nicht...")
        
def must_exist(p):
    if not p.exists():
        abort("No such file: %s" % p.absolute())
        
def rmtree_after_confirm(p):
    if not p.exists(): return
    if confirm("OK to remove %s and everything under it?" % p.absolute()):
        p.rmtree()
    


def get_locale_dir():
    if not env.main_package:
        return None # abort("No main_package")
    p = env.ROOTDIR.child(env.main_package,"locale")
    if not p.isdir():
        return None # abort("Directory %s does not exist." % p)
    return p

   
@task(alias='mm')
def make_messages():
    "Extract messages, then initialize and update all catalogs"
    extract_messages()
    init_catalog_code()
    update_catalog_code()
    
    extract_messages_userdocs()
    setup_babel_userdocs('init_catalog')
    setup_babel_userdocs('update_catalog')
    
#~ @task(alias='em')
def extract_messages():
    """Extract messages from source files to .pot file"""
    locale_dir = get_locale_dir()
    if locale_dir is None: return 
    args = ["python", "setup.py"]
    args += [ "extract_messages"]
    args += [ "-o", locale_dir.child("django.pot")]
    cmd = ' '.join(args)
    #~ must_confirm(cmd)
    local(cmd)
    
#~ @task(alias='emu')
def extract_messages_userdocs(): 
    """
    Run the Sphinx gettext builder on userdocs.
    """
    args = ['sphinx-build','-b','gettext']
    userdocs = env.ROOTDIR.child('userdocs')
    if not userdocs.isdir():
        return # abort("Directory %s does not exist." % userdocs)
    #~ args += cmdline_args
    #~ args += ['-a'] # all files, not only outdated
    #~ args += ['-P'] # no postmortem
    #~ args += ['-Q'] # no output
    #~ if not env.tolerate_sphinx_warnings:
        #~ args += ['-W'] # consider warnings as errors
    #~ args += ['-w',env.DOCSDIR.child('warnings.txt')]
    args += [userdocs]
    args += [userdocs.child("translations")]
    cmd = ' '.join(args)
    local(cmd)
    
    

@task(alias='rename')
def rename_data_url_friendly():
    data_dir = env.ROOTDIR.child('docs','data')
    #~ print list(data_dir.listdir(names_only=True))
    print list(data_dir.walk())
    
def setup_babel_userdocs(babelcmd):
    """Create userdocs .po files if necessary."""
    userdocs = env.ROOTDIR.child('userdocs')
    if not userdocs.isdir(): return
    locale_dir = userdocs.child('translations')
    for domain in locale_dir.listdir('*.pot',names_only=True):
        domain = domain[:-4]
        for loc in env.languages:
            po_file = Path(locale_dir,loc,'LC_MESSAGES','%s.po' % domain)
            mo_file = Path(locale_dir,loc,'LC_MESSAGES','%s.mo' % domain)
            pot_file = Path(locale_dir,'%s.pot' % domain)
            if babelcmd == 'init_catalog' and po_file.exists():
                print "Skip %s because file exists." % po_file
            #~ elif babelcmd == 'compile_catalog' and not mo_file.needs_update(po_file):
                #~ print "Skip %s because newer than .po" % mo_file
            else:
                args = ["python", "setup.py"]
                args += [ babelcmd ]
                args += [ "-l" , loc ]
                args += [ "--domain", domain]
                args += [ "-d" , locale_dir ]
                #~ args += [ "-o" , po_file ]
                #~ if babelcmd == 'init_catalog':
                if babelcmd == 'compile_catalog':
                    args += [ "-i" , po_file ]
                else:
                    args += [ "-i" , pot_file ]
                cmd = ' '.join(args)
                #~ must_confirm(cmd)
                local(cmd)

#~ @task(alias='imu')
#~ def init_catalog_userdocs():
    #~ setup_babel_userdocs('init_catalog')

#~ @task(alias='umu')
#~ def update_catalog_userdocs():
    #~ setup_babel_userdocs('update_catalog')

@task(alias='cmu')
def compile_catalog_userdocs():
    setup_babel_userdocs('compile_catalog')


#~ @task(alias='im')
def init_catalog_code():
    """Create code .po files if necessary."""
    locale_dir = get_locale_dir()
    if locale_dir is None: return 
    for loc in env.languages:
        f = locale_dir.child(loc,'LC_MESSAGES','django.po')
        if f.exists():
            print "Skip %s because file exists." % f
        else:
            args = ["python", "setup.py"]
            args += [ "init_catalog"]
            args += [ "--domain django"]
            args += [ "-l" , loc ]
            args += [ "-d" , locale_dir ]
            #~ args += [ "-o" , f ]
            args += [ "-i" , locale_dir.child('django.pot') ]
            cmd = ' '.join(args)
            must_confirm(cmd)
            local(cmd)



#~ @task(alias='um')
def update_catalog_code():
    """Update .po files from .pot file."""
    locale_dir = get_locale_dir()
    if locale_dir is None: return 
    for loc in env.languages:
        args = ["python", "setup.py"]
        args += [ "update_catalog"]
        args += [ "--domain django"]
        args += [ "-d" , locale_dir ]
        args += [ "-i", locale_dir.child("django.pot")]
        args += [ "-l" , loc ]
        cmd = ' '.join(args)
        #~ must_confirm(cmd)
        local(cmd)

@task(alias='cm')
def compile_catalog():
    """Compile .po files to .mo files."""
    locale_dir = get_locale_dir()
    if locale_dir is None: return 
    for loc in env.languages:
        args = ["python", "setup.py"]
        args += [ "compile_catalog"]
        args += [ "--domain django"]
        args += [ "-d" , locale_dir ]
        args += [ "-l" , loc ]
        cmd = ' '.join(args)
        #~ must_confirm(cmd)
        local(cmd)




@task(alias='summary')
def summary(*cmdline_args):
    """Print a summary to stdout."""
    headers = (
      #~ '#','Location',
      'Project','Old version','New version')

    def cells(self):
        url = self.module.SETUP_INFO['url']
        desc = "`%s <%s>`__ -- %s" % (
            self.name,url,
            self.module.SETUP_INFO['description'])
        return (
            '\n'.join(textwrap.wrap(desc,40)),
            self.dist.version,
            self.module.__version__)
        
    print rstgen.table(headers,[cells(p) for p in atelier.load_projects()])
        
  
@task(alias='api')
def build_api(*cmdline_args):
    """
    Generate .rst files in `docs/api`.
    """
    #~ if len(env.SETUP_INFO['packages']) != 1:
        #~ abort("env.SETUP_INFO['packages'] is %s" % env.SETUP_INFO['packages'])
    
    os.environ.update(SPHINX_APIDOC_OPTIONS="members,show-inheritance")
    api_dir = env.DOCSDIR.child("api").absolute()        
    rmtree_after_confirm(api_dir)
    args = ['sphinx-apidoc']
    #~ args += ['-f'] # force the overwrite of all files that it generates.
    args += ['--no-toc'] # no modules.rst file
    args += ['-o',api_dir]
    args += [env.main_package] # packagedir 
    if False: # doesn't seem to work
        excluded = [env.ROOTDIR.child('lino','sandbox').absolute()]
        args += excluded # pathnames to be ignored
    cmd = ' '.join(args)
    #~ puts("%s> %s" % (os.getcwd(), cmd))
    #~ confirm("yes")
    local(cmd)
    

def sphinx_build(builder,docs_dir,cmdline_args=[],language=None):
    args = ['sphinx-build','-b',builder]
    args += cmdline_args
    #~ args += ['-a'] # all files, not only outdated
    #~ args += ['-P'] # no postmortem
    #~ args += ['-Q'] # no output
    build_dir = docs_dir.child('.build')
    build_root = docs_dir.child('.build')
    if language:
        args += ['-D', 'language=' + language] 
        args += ['-A', 'language=' + language] # needed in select_lang.html template
        build_dir = build_dir.child(language)
    if env.tolerate_sphinx_warnings:
        args += ['-w',docs_dir.child('warnings_%s.txt' % builder)]
    else:
        args += ['-W'] # consider warnings as errors
    #~ args += ['-w'+Path(env.ROOTDIR,'sphinx_doctest_warnings.txt')]
    args += [docs_dir,build_dir]
    cmd = ' '.join(args)
    local(cmd)
    
def sync_docs_data(docs_dir):
    build_dir = docs_dir.child('.build')
    for data in ('dl','data'):
        src = docs_dir.child(data).absolute()
        if src.isdir():
            target = build_dir.child('dl')
            target.mkdir()
            cmd = 'cp -ur %s %s' % (src,target.parent) 
            local(cmd)
    
    
@task(alias='userdocs')
def build_userdocs(*cmdline_args): 
    if env.languages is None: return
    docs_dir = env.ROOTDIR.child('userdocs')
    if not docs_dir.exists(): return
    for lng in env.languages:
        sphinx_build('html',docs_dir,cmdline_args,lng)
    dest = docs_dir.child('.build','index.html')
    docs_dir.child('index.html').copy(dest)
    sync_docs_data(docs_dir)
    
@task(alias='linkcheck')
def sphinx_build_linkcheck(*cmdline_args): 
    """sphinxbuild -b linkcheck docs."""
    docs_dir = env.ROOTDIR.child('docs')
    if docs_dir.exists(): 
        sphinx_build('linkcheck',docs_dir,cmdline_args)
    docs_dir = env.ROOTDIR.child('userdocs')
    if docs_dir.exists(): 
        lng = env.languages[0] # 
        sphinx_build('linkcheck',docs_dir,cmdline_args,lng)
    
@task(alias='docs')
def build_docs(*cmdline_args): 
    """write_readme + build sphinx html docs."""
    write_readme()
    sphinx_build('html',env.DOCSDIR,cmdline_args)
    sync_docs_data(env.DOCSDIR)
    
@task(alias='alldocs')
def build_all_docs(): 
    """write_readme + build ALL sphinx html docs."""
    write_readme()
    for n in ('docs','userdocs'):
        docs_dir = env.ROOTDIR.child(n)
        if docs_dir.exists(): 
            sphinx_build('html',docs_dir,['-a'])
            sync_docs_data(docs_dir)
    
    
    
@task(alias='clean')
def clean_html(*cmdline_args):
    """
    Delete all built Sphinx files.
    """
    build_dir = env.DOCSDIR.child('.build')
    rmtree_after_confirm(build_dir)
    if env.languages:
        build_dir = env.ROOTDIR.child('userdocs','.build')
        rmtree_after_confirm(build_dir)
    
    
#~ @task(alias='pub')
#~ def publish_all():
    #~ """
    #~ Run `publish_docs` followed by `hg_push`.
    #~ """
    #~ publish_docs()
    #~ hg_push()
    
    
@task(alias='prep')
def prepare():
    """
    Sames as `fab test html`.
    """
    run_tests()
    build_docs()
    
    
    
  
@task(alias='pub')
def publish():
    """
    Upload docs to public web server.
    """
    build_dir = env.DOCSDIR.child('.build')
    dest_url = env.docs_rsync_dest + ':~/public_html/' + env.project_name
    publish_docs(build_dir,dest_url)
    
    build_dir = env.ROOTDIR.child('userdocs','.build')
    dest_url = env.docs_rsync_dest + ':~/public_html/' + env.project_name + '-userdocs'
    if build_dir.exists():
        publish_docs(build_dir,dest_url)
    #~ if env.languages:
        #~ for lang in env.languages:
    

def publish_docs(build_dir,dest_url):
    #~ from fabric.context_managers import cd
    #~ cwd = Path(os.getcwd())
    #~ if language:
        #~ dest_url += '-userdocs/' + language
        #~ build_dir = build_dir.child(language)
        
    with lcd(build_dir):
        #~ env.BUILDDIR.chdir()
        #~ with cd(env.BUILDDIR):
        #~ addr = env.user+'@'+REMOTE.lf
        args = ['rsync','-r']
        args += ['--verbose'] 
        args += ['--progress'] # show progress
        args += ['--delete'] # delete files in dest
        args += ['--times'] # preserve timestamps
        args += ['--exclude','.doctrees'] 
        args += ['./'] # source
        args += [ dest_url ] # dest
        cmd = ' '.join(args)
        #~ must_confirm("%s> %s" % (build_dir, cmd))
        #~ confirm("yes")
        local(cmd)
        #~ cwd.chdir()
    #~ return subprocess.call(args)

#~ def run_in_demo_database(admin_cmd,*more):
	#~ if not env.demo_database: return
	#~ args = ["django-admin.py"] 
	#~ args += [admin_cmd]
	#~ args += more
	#~ args += ["--settings=" + env.demo_database]
	#~ cmd = " ".join(args)
	#~ local(cmd)
            
def run_in_demo_databases(admin_cmd,*more):
    for db in env.demo_databases:
		args = ["django-admin.py"] 
		args += [admin_cmd]
		args += more
		#~ args += ["--noinput"]
		args += ["--settings=" + db]
		#~ args += [" --pythonpath=%s" % p.absolute()]
		cmd = " ".join(args)
		local(cmd)
		
		
        #~ p = env.ROOTDIR.child(*db.split('/'))
        #~ with lcd(p):
            #~ args = ["python manage.py"] 
            #~ args += [admin_cmd]
            #~ args += more
            #~ args += [" --pythonpath=%s" % p.absolute()]
            #~ cmd = " ".join(args)
            #~ local(cmd)
  
@task()
def clean_cache():
    for db in env.demo_databases:
		m = __import__(db)
		p = Path(m.SITE.project_dir).child('media','cache')
		rmtree_after_confirm(p)
    
	
@task(alias="initdb")
def initdb_demo():
    """
    Run initdb_demo on each demo database of this project (env.demo_databases)
    """
    #~ for db in env.django_databases:
        #~ args = ["django-admin"] 
        #~ args += ["initdb_demo --settings=%s" % prj]
        #~ args += [" --pythonpath=%s" % env.DOCSDIR]
        #~ cmd = " ".join(args)
        #~ local(cmd)
        
    #~ cwd = Path(os.getcwd())
    #~ for db in env.django_databases:
        #~ env.ROOTDIR.child(db).chdir()
        #~ # cmd = 'python manage.py initdb --noinput'
        #~ args = ["django-admin"] 
        #~ args += ["initdb_demo --settings=settings"]
        #~ args += [" --pythonpath=."]
        #~ cmd = " ".join(args)
        
        #~ local(cmd)
    #~ cwd.chdir()
    
    run_in_demo_databases('initdb_demo',"--noinput")
    #~ run_in_demo_database('initdb_demo',"--noinput")
    
   

#~ @task()
#~ def runserver():
    #~ run_in_demo_databases('runserver')
    
        
@task()
def unused_run_sphinx_doctest():
    """
    Run Sphinx doctest tests. 
    Not maintained because i cannot prevent it from also trying to test 
    the documents in `django_doctests` which must be tested separately.
    """
    #~ clean_sys_path()
    #~ if sys.path[0] == '':
        #~ del sys.path[0]
    #~ print sys.path    
    #~ if len(sys.argv) > 1:
        #~ raise Exception("Unexpected command-line arguments %s" % sys.argv)
    onlythis = None
    #~ onlythis = 'docs/tutorials/human/index.rst'
    args = ['sphinx-build','-b','doctest']
    args += ['-a'] # all files, not only outdated
    args += ['-Q'] # no output
    if not onlythis:
        args += ['-W'] # consider warnings as errors
    build_dir = env.DOCSDIR.child('.build')
    args += [env.DOCSDIR,build_dir]
    if onlythis: # test only this document
        args += [ onlythis ] 
    #~ args = ['sphinx-build','-b','doctest',env.DOCSDIR,env.BUILDDIR]
    #~ raise Exception(' '.join(args))
    #~ env.DOCSDIR.chdir()
    #~ import os
    #~ print os.getcwd()
    exitcode = sphinx.main(args)
    if exitcode != 0:
        output = Path(build_dir,'output.txt')
        #~ if not output.exists():
            #~ abort("Oops: no file %s" % output)
        # six.print_("arguments to spxhinx.main() were",args)
        abort("""
=======================================
Sphinx doctest failed with exit code %s
=======================================
%s""" % (exitcode,output.read_file()))
    
@task(alias='sdist')
def setup_sdist():
    """
    Write source distribution archive file.
    """
    #~ pipy_register()
    #~ puts(env.sdist_dir)
    args = ["python", "setup.py"]
    args += [ "sdist", "--formats=gztar" ]
    args += ["--dist-dir", env.sdist_dir.child(env.SETUP_INFO['name'])]
    local(' '.join(args))
    #~ run_setup('setup.py',args)
  
@task(alias='upload')
def pypi_upload():
    """
    Upload sourcxe distribution to PyPI.
    """
    pipy_register()
    args = ["python", "setup.py"]
    args += ["sdist", "--formats=gztar" ]
    args += ["--dist-dir", env.sdist_dir.child(env.SETUP_INFO['name'])]
    args += ["upload"]
    local(' '.join(args))
    #~ run_setup('setup.py',args)
  
#~ @task()
#~ def check_packages():
    #~ """
    #~ Checks whether the `packages` list seems correct.
    #~ """
    #~ packages = find_packages()
    #~ if packages == env.SETUP_INFO['packages']: 
        #~ puts("%d packages okay" % len(packages))
        #~ return
    
    
  
@task(alias='reg')
def pipy_register():
    """
    Register to PyPI.
    """
    args = ["python", "setup.py"]
    args += ["register"]
    #~ run_setup('setup.py',args)
    local(' '.join(args))

def get_blog_entry(today):
    """
    Return an RstFile object representing the blog entry for that date.
    """
    local_root = env.work_root.child(env.blogger_project)
    parts = ('docs','blog',str(today.year),today.strftime("%m%d.rst"))
    #~ return blogdir.child(*parts)
    return RstFile(local_root,
      "http://code.google.com/p/%s/source/browse/" % env.blogger_project,
      parts)
  

@task(alias='blog')
def edit_blog_entry():
    """
    Edit today's blog entry, create an empty file if it doesn't yet exist.
    """
    today = datetime.date.today()
    entry = get_blog_entry(today)
    if not entry.path.exists():
        if confirm("Create file %s?" % entry.path):
            txt = rstgen.header(1,today.strftime(env.long_date_format))
            entry.path.write_file(txt)
            entry.path.parent.child('index.rst').set_times() # touch it for Sphinx
    args = [ os.environ['EDITOR'] ]
    args += [entry.path]
    local(' '.join(args))
  
@task(alias='ci')
def checkin():
    """
    Checkin & push to repository, using today's blog entry as commit message.
    """
    args = ["hg","st"]
    local(' '.join(args))
    if not confirm("OK to checkin %s ?" % env.SETUP_INFO['name']):
        return 
        
    entry = get_blog_entry(datetime.date.today())
    #~ entry = Path(env.ROOTDIR,'..',env.blogger_project,*parts)
    #~ print env.ROOTDIR.parent.absolute()
    if not entry.path.exists():
        abort("%s does not exist!" % entry.path.absolute())
    #~ puts("Commit message refers to %s" % entry.absolute())
        
    args = ["hg","ci"]
    args += ['-m', entry.url ]
    cmd = ' '.join(args)
    #~ confirm(cmd)
    local(cmd)
    local("hg push %s" % env.project_name)
    
#~ @task()
def unused_write_release_notes():
    """
    Generate docs/releases/x.y.z.rst file from setup_info.
    """
    v = env.SETUP_INFO['version']
    if v.endswith('+'):
        return
    notes = Path(env.ROOTDIR,'docs','releases','%s.rst' % v)
    if notes.exists():
        return
    must_confirm("Create %s" % notes.absolute())
    #~ context = dict(date=datetime.date.today().strftime(env.long_date_format))
    context = dict(date=datetime.date.today().strftime('%Y%m%d'))
    context.update(env.SETUP_INFO)
    txt = """\
==========================
Version %(version)s
==========================

Release process started :blogref:`%(date)s`


List of changes
===============

New features
------------

Optimizations
-------------

Bugfixes
--------

Manual tasks after upgrade
--------------------------


""" % context
    notes.write_file(txt)
    notes.parent.child('index.rst').set_times()
    args = [ os.environ['EDITOR'] ]
    args += [notes.absolute()]
    local(' '.join(args))
    
@task()
def write_readme():
    """
    Generate README.txt file from setup_info (if necessary).
    """
    if not env.main_package: return
    readme = env.ROOTDIR.child('README.txt')
    txt = """\
==========================
%(name)s README
==========================

%(description)s

Description
-----------

%(long_description)s

Read more on %(url)s
""" % env.SETUP_INFO
    if readme.exists() and readme.read_file() == txt:
        return 
    must_confirm("Overwrite %s" % readme.absolute())
    readme.write_file(txt)
    env.DOCSDIR.child('index.rst').set_times()
    #~ cmd = "touch " + env.DOCSDIR.child('index.rst')
    #~ local(cmd)
    #~ pipy_register()
    
  

  
@task(alias='test')
def run_tests():
    """
    Run the complete test suite of this project.
    """
    local('python setup.py -q test')
    

#~ @task(alias='listpkg')
#~ def list_subpackages():
    #~ # lst = list(env.ROOTDIR.walk("__init__.py"))
    #~ for fn in env.ROOTDIR.child('lino').walk('*.py'):
        #~ print fn

@task(alias='cov')
def run_tests_coverage():
    """
    Run all tests, creating coverage report
    """
    import coverage
    #~ clean_sys_path()
    puts("Running tests for '%s' within coverage..." % env.project_name)
    #~ env.DOCSDIR.chdir()
    source = []
    for package_name in env.SETUP_INFO['packages']:
        m = __import__(package_name)
        source.append(os.path.dirname(m.__file__))
    #~ cov = coverage.coverage(source=['djangosite'])
    if not confirm("coverage source=%s" % source):
        abort
    cov = coverage.coverage(source=source)
    #~ cov = coverage.coverage()
    cov.start()

    # .. call your code ..
    rv = run_tests()

    cov.stop()
    cov.save()

    cov.html_report()    
    return rv
    


@task(alias='esi')
def edit_setup_info():
    """
    Edit the `setup_info.py` file of this project.
    """
    sif = Path(env.ROOTDIR,env.main_package,'setup_info.py')
    print sif
    args = [ os.environ['EDITOR'] ]
    args += [sif]
    local(' '.join(args))
  
