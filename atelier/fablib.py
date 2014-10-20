# -*- coding: UTF-8 -*-
# Copyright 2013-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""This module is a library for fabric_ with tasks I use to manage my
Python projects.

.. _fabric: http://docs.fabfile.org

To be used by creating a :file:`fabfile.py` in your project's root
directory with at least the following two lines::

  from atelier.fablib import *
  setup_from_project("foobar")
  
Where "foobar" is the Python name of your project's main package.

Configuration files
-------------------

.. xfile:: fabfile.py

In your :xfile:`fabfile.py` file you can specify project-specific
configuration settings.  Example content::

  from atelier.fablib import *
  setup_from_project("foobar")
  env.languages = "de fr et nl".split()
  env.tolerate_sphinx_warnings = True
  env.demo_databases.append('foobar.demo.settings')

.. xfile:: .fabricrc

To specify certain default preferences for all your projects, you can
create a file named :file:`.fabricrc` in your home directory with
content like this::

    user = luc
    blogger_project = lino
    docs_rsync_dest = luc@example.org:~/public_html/%s
    sdist_dir = /home/luc/projects/lino/docs/dl
    temp_dir = /home/luc/tmp


Project settings
----------------

fabric_ works with a global "environment" object named ``env``.  The
following section documents the possible attributes of this object as
used by :mod:`atelier.fablib`.

.. class:: env

  .. attribute:: doc_trees

    Replaced by `doc_trees` attribute of the project's main module.

    A list of directory names (relative to your project directory)
    containing Sphinx document trees.
    Default value is ``['docs']``

  .. attribute:: tolerate_sphinx_warnings

    Whether `sphinx-build html` should tolerate warnings.

  .. attribute:: languages

    A list of language codes for which userdocs are being maintained.

  .. attribute:: apidoc_exclude_pathnames

    a list of filenames (or directory names) to be excluded when you
    run :command:`fab api`.

  .. attribute:: use_mercurial

    set this to False if you use Git. Used by :command:`fab ci`

  .. attribute:: demo_databases

You may define user-specific default values for some of these settings
(those who are simple strings) in a :file:`.fabricrc` file.


``fab`` commands
----------------

.. command:: fab mm

("make messages")

Extracts messages from both code and userdocs, then initializes and
updates all catalogs.


.. command:: fab test

Run the test suite of this project.

.. command:: fab test_sdist

    Creates a temporay virtualenv, installs your project and runs your
    test suite.
        
    - creates and activates a temporay virtualenv,
    - calls ``pip install --extra-index <env.sdist_dir> <prjname>``
    - runs ``python setup.py test``
    - removes temporary files.
    
    assumes that you previously did ``pp fab sdist``
    i.e. your `env.sdist_dir` contains the pre-release sdist of all your 
    projects.
    
    When using this, you should configure a local download cache for 
    pip, e.g. with something like this in your :file:`~/.pip/pip.conf`::
    
      [global]
      download-cache=/home/luc/.pip/cache


.. command:: fab initdb

Run :manage:`initdb_demo` on every demo database of this project 
(specified in :attr:`env.demo_databases`).

Demo databases are used by the test suite and the Sphinx
documentation.  They are not included in the code repository since
they are generated data.  Since initializing these databases can take
some time, this is not automatically launched for each test run.

.. command:: fab ci

    Checkin and push to repository, using today's blog entry as commit
    message.
    

.. command:: fab release

Create official source distribution and upload it to PyPI.

.. command:: fab userdocs

Run `sphinx build html` in `userdocs`.

.. command:: fab write_readme

Generate `README.txt` file from project_info (if necessary).


.. command:: fab api

Generate `.rst` files below `docs/api` by running `sphinx-apidoc
<http://sphinx-doc.org/invocation.html#invocation-of-sphinx-apidoc>`_.



.. command:: fab blog

Edit today's blog entry, create an empty file if it doesn't yet exist.


.. command:: fab docs

Run `sphinx build html` in `docs`.



History
-------

- 20141020 moved `doc_trees` project to :class:`atelier.Project`.
- 20141001 added support for multiple doc trees per project
  (:attr:`env.doc_trees`).
- 20140116 : added support for managing namespace packages

TODO
----

- replace `env.blogger_project` by an attribute of the main module
  (like `intersphinx_urls`)

"""
import os
import textwrap

from babel.dates import format_date

import datetime
from unipath import Path
import sphinx

import atelier
from atelier.utils import i2d
from atelier import rstgen
from atelier import get_setup_info
from atelier import get_project_info

from fabric.api import env, local, task
from fabric.utils import abort, fastprint, puts, warn
from fabric.contrib.console import confirm
from fabric.api import lcd


class JarBuilder(object):
    """
    Used by my Java projects :ref:`davlink` and :ref:`eidreader`.
    """
    def __init__(self, jarfile, sourcedir):
        self.jarfile = Path(jarfile)
        self.sourcedir = Path(sourcedir)
        self.sources = list(self.sourcedir.listdir('*.java'))

        self.jarcontent = [Path('Manifest.txt')]
        self.jarcontent += list(self.sourcedir.listdir('*.class'))
        self.jarcontent = [
            Path(x.replace("$", "\\$")) for x in self.jarcontent]
        self.libjars = []

    def add_lib(self, pth):
        self.libjars.append(Path(pth))

    def build_jar(self, outdir, alias):
        flags = '-storepass "`cat ~/.secret/.keystore_password`"'
        flags += ' -tsa http://timestamp.globalsign.com/scripts/timestamp.dll'
        outdir = Path(outdir)
        jarfile = outdir.child(self.jarfile)
        if jarfile.needs_update(self.jarcontent):
            local("jar cvfm %s %s" % (jarfile, ' '.join(self.jarcontent)))
        local("jarsigner %s %s %s" % (flags, jarfile, alias))
        for libfile in self.libjars:
            jarfile = outdir.child(libfile.name)
            if libfile.needs_update([jarfile]):
                libfile.copy(jarfile)
            local("jarsigner %s %s %s" % (flags, jarfile, alias))

    def build_classes(self):
        flags = "-Xlint:unchecked"
        if len(self.libjars):
            cp = ':'.join(self.libjars)
            flags += " -classpath %s" % cp
        for src in self.sources:
            local("javac %s %s" % (flags, src))


def get_current_date():
    """
    Useful when a working day lasted longer than midnight,
    or when you start some work in the evening, knowing that you won't
    commit it before the next morning.

    Note that you must specify the date using the YYYYMMDD format.
    """
    # if atelier.TODAY is not None:
    #     return i2d(atelier.TODAY)
    return datetime.date.today()


class RstFile(object):

    def __init__(self, local_root, url_root, parts):
        self.path = local_root.child(*parts) + '.rst'
        if parts[0] == 'docs':
            self.url = url_root + "/" + "/".join(parts[1:]) + '.html'
        else:
            raise Exception("20131125")
            # self.url = url_root + "/" + "/".join(parts) + '.html'


def setup_from_project(
        main_package=None,
        settings_module_name=None):

    env.ROOTDIR = Path().absolute()

    env.project_name = env.ROOTDIR.name
    env.setdefault('build_dir_name', '.build')  # but ablog needs '_build'
    
    env.current_project = get_project_info(env.project_name)

    env.setdefault('long_date_format', "%Y%m%d (%A, %d %B %Y)")
    # env.work_root = Path(env.work_root)
    env.setdefault('sdist_dir', None)
    env.setdefault('use_dirhtml', False)

    if env.sdist_dir is not None:
        env.sdist_dir = Path(env.sdist_dir)
    env.main_package = main_package
    env.tolerate_sphinx_warnings = False
    env.demo_databases = []
    env.use_mercurial = True
    env.apidoc_exclude_pathnames = []
    # env.blogger_url = "http://blog.example.com/"

    env.setdefault('languages', None)
    env.setdefault('blogger_project', None)
    env.setdefault('blogger_url', None)
    # env.setdefault('doc_trees', ['docs'])

    if isinstance(env.languages, basestring):
        env.languages = env.languages.split()

    if env.main_package:
        env.SETUP_INFO = get_setup_info(Path(env.ROOTDIR))
    else:
        env.SETUP_INFO = None

    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        from django.conf import settings
        # why was this? settings.SITE.startup()
        env.languages = [lng.name for lng in settings.SITE.languages]
        env.demo_databases.append(settings_module_name)
        #~ env.userdocs_base_language = settings.SITE.languages[0].name


#~ def confirm(msg,default='y',others='n',**override_callbacks):
    #~ text = "%s [%s%s]" % (msg,default.upper(),others)
    #~ def y(): return True
    # ~ # def n(): abort("Missing user confirmation for:\n%s" % msg)
    #~ def n(): abort("Missing user confirmation")
    #~ callbacks = dict(y=y,n=n)
    #~ callbacks.update(override_callbacks)
    #~ while True:
        #~ answer = prompt(text)
        # ~ # answer = raw_input(prompt)
        #~ if not answer:
            #~ answer = default
        #~ answer = answer.lower()
        #~ if answer:
            #~ return callbacks.get(answer)()
def must_confirm(*args, **kw):
    if not confirm(*args, **kw):
        abort("Dann eben nicht...")


def must_exist(p):
    if not p.exists():
        abort("No such file: %s" % p.absolute())


def rmtree_after_confirm(p):
    if not p.exists():
        return
    if confirm("OK to remove %s and everything under it?" % p.absolute()):
        p.rmtree()


def get_locale_dir():
    if not env.main_package:
        return None  # abort("No main_package")
    args = env.main_package.split('.')
    args.append('locale')
    p = env.ROOTDIR.child(*args)
    if not p.isdir():
        return None  # abort("Directory %s does not exist." % p)
    return p


@task(alias='mm')
def make_messages():
    "Extract messages, then initialize and update all catalogs."
    extract_messages()
    init_catalog_code()
    update_catalog_code()

    if False:
        extract_messages_userdocs()
        setup_babel_userdocs('init_catalog')
        setup_babel_userdocs('update_catalog')


def extract_messages():
    """Extract messages from source files to `django.pot` file"""
    locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    args = ["python", "setup.py"]
    args += ["extract_messages"]
    args += ["-o", locale_dir.child("django.pot")]
    cmd = ' '.join(args)
    #~ must_confirm(cmd)
    local(cmd)


def extract_messages_userdocs():
    """
    Run the Sphinx gettext builder on userdocs.
    """
    userdocs = env.ROOTDIR.child('userdocs')
    if not userdocs.isdir():
        return  # abort("Directory %s does not exist." % userdocs)
    args = ['sphinx-build', '-b', 'gettext']
    #~ args += cmdline_args
    # ~ args += ['-a'] # all files, not only outdated
    # ~ args += ['-P'] # no postmortem
    # ~ args += ['-Q'] # no output
    #~ if not env.tolerate_sphinx_warnings:
        # ~ args += ['-W'] # consider warnings as errors
    #~ args += ['-w',env.DOCSDIR.child('warnings.txt')]
    args += [userdocs]
    args += [userdocs.child("translations")]
    cmd = ' '.join(args)
    local(cmd)


@task(alias='rename')
def rename_data_url_friendly():
    data_dir = env.ROOTDIR.child('docs', 'data')
    #~ print list(data_dir.listdir(names_only=True))
    print list(data_dir.walk())


def setup_babel_userdocs(babelcmd):
    """Create userdocs .po files if necessary."""
    userdocs = env.ROOTDIR.child('userdocs')
    if not userdocs.isdir():
        return
    locale_dir = userdocs.child('translations')
    for domain in locale_dir.listdir('*.pot', names_only=True):
        domain = domain[:-4]
        for loc in env.languages:
            if loc != env.languages[0]:
                po_file = Path(locale_dir, loc, 'LC_MESSAGES', '%s.po' %
                               domain)
                mo_file = Path(locale_dir, loc, 'LC_MESSAGES', '%s.mo' %
                               domain)
                pot_file = Path(locale_dir, '%s.pot' % domain)
                if babelcmd == 'init_catalog' and po_file.exists():
                    print "Skip %s because file exists." % po_file
                #~ elif babelcmd == 'compile_catalog' and not mo_file.needs_update(po_file):
                    #~ print "Skip %s because newer than .po" % mo_file
                else:
                    args = ["python", "setup.py"]
                    args += [babelcmd]
                    args += ["-l", loc]
                    args += ["--domain", domain]
                    args += ["-d", locale_dir]
                    #~ args += [ "-o" , po_file ]
                    #~ if babelcmd == 'init_catalog':
                    if babelcmd == 'compile_catalog':
                        args += ["-i", po_file]
                    else:
                        args += ["-i", pot_file]
                    cmd = ' '.join(args)
                    #~ must_confirm(cmd)
                    local(cmd)


@task(alias='cmu')
def compile_catalog_userdocs():
    setup_babel_userdocs('compile_catalog')


def init_catalog_code():
    """Create code .po files if necessary."""
    from north.utils import to_locale
    locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    for loc in env.languages:
        if loc != 'en':
            f = locale_dir.child(loc, 'LC_MESSAGES', 'django.po')
            if f.exists():
                print "Skip %s because file exists." % f
            else:
                args = ["python", "setup.py"]
                args += ["init_catalog"]
                args += ["--domain django"]
                args += ["-l", to_locale(loc)]
                args += ["-d", locale_dir]
                #~ args += [ "-o" , f ]
                args += ["-i", locale_dir.child('django.pot')]
                cmd = ' '.join(args)
                must_confirm(cmd)
                local(cmd)


def update_catalog_code():
    """Update .po files from .pot file."""
    from north.utils import to_locale
    locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    for loc in env.languages:
        if loc != env.languages[0]:
            args = ["python", "setup.py"]
            args += ["update_catalog"]
            args += ["--domain django"]
            #~ args += [ "-d" , locale_dir ]
            args += ["-o", locale_dir.child(loc, 'LC_MESSAGES', 'django.po')]
            args += ["-i", locale_dir.child("django.pot")]
            args += ["-l", to_locale(loc)]
            cmd = ' '.join(args)
            #~ must_confirm(cmd)
            local(cmd)


@task(alias='cm')
def compile_catalog():
    """Compile .po files to .mo files."""
    from north.utils import to_locale
    locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    for loc in env.languages:
        if loc != env.languages[0]:
            args = ["python", "setup.py"]
            args += ["compile_catalog"]
            args += ["-i", locale_dir.child(loc, 'LC_MESSAGES', 'django.po')]
            args += ["-o", locale_dir.child(loc, 'LC_MESSAGES', 'django.mo')]
            args += ["--domain django"]
            #~ args += [ "-d" , locale_dir ]
            args += ["-l", to_locale(loc)]
            cmd = ' '.join(args)
            #~ must_confirm(cmd)
            local(cmd)


@task(alias='mss')
def makescreenshots():
    """generate screenshot .jpg files to gen/screenshots."""
    run_in_demo_databases('makescreenshots', '--traceback')


@task(alias='sss')
def syncscreenshots():
    """synchronize gen/screenshots to userdocs/gen/screenshots."""
    run_in_demo_databases('syncscreenshots', '--traceback',
                          'gen/screenshots', 'userdocs/gen/screenshots')


@task(alias='summary')
def summary(*cmdline_args):
    """Print a summary to stdout."""
    headers = (
        # ~ '#','Location',
        'Project',
        # 'Old version',
        'Version')

    def cells(self):
        # print 20140116, self.module
        url = self.SETUP_INFO['url']
        desc = "`%s <%s>`__ -- %s" % (
            self.name, url,
            self.SETUP_INFO['description'])
        #~ import pkg_resources
        #~ for d in pkg_resources.find_distributions(self.name):
        #~ d = pkg_resources.get_distribution(self.name)
        #~ d = pkg_resources.Distribution.from_location("http://pypi.python.org/simple/",self.name)
        #~ print 20130911, self.name, d.version

        return (
            '\n'.join(textwrap.wrap(desc, 60)),
            # self.dist.version,
            self.SETUP_INFO['version'])

    print rstgen.table(headers, [cells(p) for p in atelier.load_projects()])


@task(alias='api')
def build_api(*cmdline_args):
    """
    Generate `.rst` files in `docs/api`. See :cmd:`fab api`.
    """
    docs_dir = env.ROOTDIR.child('docs')
    if not docs_dir.exists():
        return
    os.environ.update(SPHINX_APIDOC_OPTIONS="members,show-inheritance")
    api_dir = docs_dir.child("api").absolute()
    rmtree_after_confirm(api_dir)
    args = ['sphinx-apidoc']
    # args += ['-f'] # force the overwrite of all files that it generates.
    args += ['--no-toc']  # no modules.rst file
    args += ['--separate']  # separate page for each module
    args += ['--module-first']  # Put module documentation before
                                # submodule documentation
    args += ['-o', api_dir]
    args += [env.main_package.replace('.', '/')]  # packagedir
    args += env.apidoc_exclude_pathnames
    if False:
        excluded = ['lino/dd.py']
        args += excluded  # pathnames to be ignored
    cmd = ' '.join(args)
    #~ puts("%s> %s" % (os.getcwd(), cmd))
    #~ confirm("yes")
    local(cmd)


def sphinx_build(builder, docs_dir,
                 cmdline_args=[], language=None, build_dir_cmd=None):
    args = ['sphinx-build', '-b', builder]
    args += cmdline_args
    # ~ args += ['-a'] # all files, not only outdated
    # ~ args += ['-P'] # no postmortem
    # ~ args += ['-Q'] # no output
    # build_dir = docs_dir.child(env.build_dir_name)
    build_dir = Path(env.build_dir_name)
    if language is not None:
        args += ['-D', 'language=' + language]
        # needed in select_lang.html template
        args += ['-A', 'language=' + language]
        if language != env.languages[0]:
            build_dir = build_dir.child(language)
            #~ print 20130726, build_dir
    if env.tolerate_sphinx_warnings:
        args += ['-w', 'warnings_%s.txt' % builder]
    else:
        args += ['-W']  # consider warnings as errors
    #~ args += ['-w'+Path(env.ROOTDIR,'sphinx_doctest_warnings.txt')]
    args += ['.', build_dir]
    cmd = ' '.join(args)
    with lcd(docs_dir):
        local(cmd)
    if build_dir_cmd is not None:
        with lcd(build_dir):
            local(build_dir_cmd)


def sync_docs_data(docs_dir):
    build_dir = docs_dir.child(env.build_dir_name)
    for data in ('dl', 'data'):
        src = docs_dir.child(data).absolute()
        if src.isdir():
            target = build_dir.child('dl')
            target.mkdir()
            cmd = 'cp -ur %s %s' % (src, target.parent)
            local(cmd)
    if False:
        # according to http://mathiasbynens.be/notes/rel-shortcut-icon
        for n in ['favicon.ico']:
            src = docs_dir.child(n).absolute()
            if src.exists():
                target = build_dir.child(n)
                cmd = 'cp %s %s' % (src, target.parent)
                local(cmd)


@task(alias='userdocs')
def build_userdocs(*cmdline_args):
    """
    sphinx-build the userdocs tree in all languages
    """
    if env.languages is None:
        return
    docs_dir = env.ROOTDIR.child('userdocs')
    if not docs_dir.exists():
        return
    for lng in env.languages:
        sphinx_build('html', docs_dir, cmdline_args, lng)
    sync_docs_data(docs_dir)


@task(alias='pdf')
def build_userdocs_pdf(*cmdline_args):
    if env.languages is None:
        return
    docs_dir = env.ROOTDIR.child('userdocs')
    if not docs_dir.exists():
        return
    for lng in env.languages:
        sphinx_build('latex', docs_dir, cmdline_args,
                     lng, build_dir_cmd='make all-pdf')
    sync_docs_data(docs_dir)


@task(alias='linkcheck')
def sphinx_build_linkcheck(*cmdline_args):
    """sphinxbuild -b linkcheck docs."""
    docs_dir = env.ROOTDIR.child('docs')
    if docs_dir.exists():
        sphinx_build('linkcheck', docs_dir, cmdline_args)
    docs_dir = env.ROOTDIR.child('userdocs')
    if docs_dir.exists():
        lng = env.languages[0]
        #~ lng = env.userdocs_base_language
        sphinx_build('linkcheck', docs_dir, cmdline_args, lng)


def get_doc_trees():
    for rel_doc_tree in env.current_project.doc_trees:
    # for rel_doc_tree in env.doc_trees:
        docs_dir = env.ROOTDIR.child(rel_doc_tree)
        if not docs_dir.exists():
            msg = "Directory %s does not exist." % docs_dir
            msg += "\nCheck `doc_trees` in your project's main module."
            raise Exception(msg)
        yield docs_dir


@task(alias='docs')
def build_docs(*cmdline_args):
    """write_readme + build sphinx html docs."""
    for docs_dir in get_doc_trees():
        puts("Invoking Sphinx in in directory %s..." % docs_dir)
        write_readme()
        builder = 'html'
        if env.use_dirhtml:
            builder = 'dirhtml'
        sphinx_build(builder, docs_dir, cmdline_args)
        sync_docs_data(docs_dir)


@task(alias='clean')
def sphinx_clean(*cmdline_args):
    """
    Delete all generated Sphinx files.
    """
    for docs_dir in get_doc_trees():
        rmtree_after_confirm(docs_dir.child(env.build_dir_name))
        # if env.languages:
        #     rmtree_after_confirm(env.ROOTDIR.child('userdocs', env.build_dir_name))


@task(alias='pub')
def publish():
    """
    Upload docs to public web server.
    """
    if not env.docs_rsync_dest:
        raise Exception(
            "Must set env.docs_rsync_dest in `fabfile.py` or `~/.fabricrc`")

    for docs_dir in get_doc_trees():
        build_dir = docs_dir.child(env.build_dir_name)
        if build_dir.exists():
            name = '%s_%s' % (env.project_name, docs_dir.name)
            dest_url = env.docs_rsync_dest % name
            publish_docs(build_dir, dest_url)

    # build_dir = env.ROOTDIR.child('userdocs', env.build_dir_name)
    # if build_dir.exists():
    #     dest_url = env.docs_rsync_dest % (env.project_name + '-userdocs')
    #     publish_docs(build_dir, dest_url)


def publish_docs(build_dir, dest_url):
    with lcd(build_dir):
        args = ['rsync', '-r']
        args += ['--verbose']
        args += ['--progress']  # show progress
        args += ['--delete']  # delete files in dest
        args += ['--times']  # preserve timestamps
        args += ['--exclude', '.doctrees']
        args += ['./']  # source
        args += [dest_url]  # dest
        cmd = ' '.join(args)
        #~ must_confirm("%s> %s" % (build_dir, cmd))
        #~ confirm("yes")
        local(cmd)


def run_in_demo_databases(admin_cmd, *more):
    """Run the given django admin command for each demo database.
    """
    for db in env.demo_databases:
        args = ["django-admin.py"]
        args += [admin_cmd]
        args += more
        #~ args += ["--noinput"]
        args += ["--settings=" + db]
        #~ args += [" --pythonpath=%s" % p.absolute()]
        cmd = " ".join(args)
        local(cmd)


@task()
def clean_cache():
    for db in env.demo_databases:
        m = __import__(db)
        p = Path(m.SITE.project_dir).child('media', 'cache')
        rmtree_after_confirm(p)


@task(alias="initdb")
def initdb_demo():
    """
    Run initdb_demo on every demo database of this project
    (env.demo_databases)
    """
    run_in_demo_databases('initdb_demo', "--noinput", '--traceback')


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
    args = ['sphinx-build', '-b', 'doctest']
    args += ['-a']  # all files, not only outdated
    args += ['-Q']  # no output
    if not onlythis:
        args += ['-W']  # consider warnings as errors
    build_dir = env.ROOTDIR.child('docs', env.build_dir_name)
    args += [env.ROOTDIR.child('docs'), build_dir]
    if onlythis:  # test only this document
        args += [onlythis]
    #~ args = ['sphinx-build','-b','doctest',env.DOCSDIR,env.BUILDDIR]
    #~ raise Exception(' '.join(args))
    #~ env.DOCSDIR.chdir()
    #~ import os
    #~ print os.getcwd()
    exitcode = sphinx.main(args)
    if exitcode != 0:
        output = Path(build_dir, 'output.txt')
        #~ if not output.exists():
            #~ abort("Oops: no file %s" % output)
        # six.print_("arguments to spxhinx.main() were",args)
        abort("""
=======================================
Sphinx doctest failed with exit code %s
=======================================
%s""" % (exitcode, output.read_file()))


@task(alias='sdist')
def setup_sdist():
    """
    Write source distribution archive file.
    """
    args = ["python", "setup.py"]
    args += ["sdist", "--formats=gztar"]
    args += ["--dist-dir", env.sdist_dir.child(env.SETUP_INFO['name'])]
    local(' '.join(args))


TEST_SDIST_TEMPLATE = """#!/bin/bash
# generated by ``fab test_sdist``
VE_DIR=%(ve_path)s
virtualenv $VE_DIR
. $VE_DIR/bin/activate
pip install --extra-index file:%(sdist_dir)s %(name)s
"""


@task(alias='test_sdist')
def setup_test_sdist():
    if len(env.demo_databases) == 0:
        return
    ve_path = Path(env.temp_dir, 'test_sdist')
    #~ if ve_path.exists():
    ve_path.rmtree()
    #~ rmtree_after_confirm(ve_path)
    ve_path.mkdir()
    script = ve_path.child('tmp.sh')

    context = dict(name=env.SETUP_INFO['name'], sdist_dir=env.sdist_dir,
                   ve_path=ve_path)
    #~ file(script,'w').write(TEST_SDIST_TEMPLATE % context)
    txt = TEST_SDIST_TEMPLATE % context
    for db in env.demo_databases:
        txt += "django-admin.py test --settings=%s --traceback\n" % db
    script.write_file(txt)
    script.chmod(0o777)
    with lcd(ve_path):
        local(script)


@task(alias='ddt')
def double_dump_test():
    """
    Perform a "double dump test" on every demo database.
    """
    if len(env.demo_databases) == 0:
        return
    a = Path(env.temp_dir, 'a')
    b = Path(env.temp_dir, 'b')
    rmtree_after_confirm(a)
    rmtree_after_confirm(b)
    #~ if not confirm("This will possibly break the demo databases. Are you sure?"):
        #~ return
    #~ a.mkdir()
    with lcd(env.temp_dir):
        for db in env.demo_databases:
            if a.exists():
                a.rmtree()
            if b.exists():
                b.rmtree()
            local("django-admin.py dump2py --settings=%s --traceback a" % db)
            local(
                "django-admin.py run --settings=%s --traceback a/restore.py" %
                db)
            local("django-admin.py dump2py --settings=%s --traceback b" % db)
            local("diff a b")


@task(alias='release')
def pypi_release():
    """
    Create official source distribution and upload it to PyPI.
    """
    must_confirm(
        "This is going to officially release %(name)s %(version)s to PyPI" %
        env.SETUP_INFO)
    pypi_register()
    args = ["python", "setup.py"]
    args += ["sdist", "--formats=gztar"]
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
def pypi_register():
    """
    Register to PyPI.
    """
    args = ["python", "setup.py"]
    args += ["register"]
    #~ run_setup('setup.py',args)
    local(' '.join(args))


def get_blog_entry(today):
    """Return an RstFile object representing the blog entry for that date
    in the current project.

    """
    parts = ('docs', 'blog', str(today.year), today.strftime("%m%d"))
    if env.blogger_project:
        # local_root = env.work_root.child(env.blogger_project)
        m = __import__(env.blogger_project)
        local_root = Path(m.__file__).parent.parent
        return RstFile(local_root, m.intersphinx_urls['docs'], parts)
    else:
        return RstFile(env.ROOTDIR, env.blogger_url, parts)


@task(alias='blog')
def edit_blog_entry(today=None):
    """
    Edit today's blog entry, create an empty file if it doesn't yet exist.
    """
    if today is None:
        today = get_current_date()
    else:
        today = i2d(today)
    entry = get_blog_entry(today)
    if not entry.path.exists():
        if not confirm("Create file %s?" % entry.path):
            return
        if env.languages is None:
            txt = today.strftime(env.long_date_format)
        else:
            txt = format_date(
                today, format='full', locale=env.languages[0])
        entry.path.write_file(rstgen.header(1, txt).encode('utf-8'))
        # touch it for Sphinx:
        entry.path.parent.child('index.rst').set_times()
    args = [os.environ['EDITOR']]
    args += [entry.path]
    local(' '.join(args))


@task(alias='ci')
def checkin(today=None):
    """
    Checkin and push to repository, using today's blog entry as commit
    message.
    """
    if env.use_mercurial:
        args = ["hg", "st"]
    else:
        args = ["git", "status"]
    local(' '.join(args))

    if today is None:
        today = get_current_date()
    else:
        today = i2d(today)

    # if atelier.TODAY is not None:
    #     if not confirm("Hard-coded TODAY in your %s! Are you sure?" %
    #                    atelier.config_file):
    #         return

    entry = get_blog_entry(today)
    #~ entry = Path(env.ROOTDIR,'..',env.blogger_project,*parts)
    #~ print env.ROOTDIR.parent.absolute()
    if not entry.path.exists():
        abort("%s does not exist!" % entry.path.absolute())

    msg = entry.url

    if not confirm("OK to checkin %s %s?" % (env.project_name, msg)):
        return
    #~ puts("Commit message refers to %s" % entry.absolute())

    if env.use_mercurial:
        args = ["hg", "ci"]
    else:
        args = ["git", "commit", "-a"]
    args += ['-m', msg]
    cmd = ' '.join(args)
    local(cmd)
    if env.use_mercurial:
        local("hg push %s" % env.project_name)
    else:
        local("git push")

#~ @task()


def unused_write_release_notes():
    """
    Generate docs/releases/x.y.z.rst file from setup_info.
    """
    v = env.SETUP_INFO['version']
    if v.endswith('+'):
        return
    notes = Path(env.ROOTDIR, 'docs', 'releases', '%s.rst' % v)
    if notes.exists():
        return
    must_confirm("Create %s" % notes.absolute())
    #~ context = dict(date=get_current_date().strftime(env.long_date_format))
    context = dict(date=get_current_date().strftime('%Y%m%d'))
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
    args = [os.environ['EDITOR']]
    args += [notes.absolute()]
    local(' '.join(args))


@task()
def write_readme():
    """
    Generate README.txt file from setup_info (if necessary).
    """
    if not env.main_package:
        return
    if env.use_mercurial:
        readme = env.ROOTDIR.child('README.txt')
    else:
        readme = env.ROOTDIR.child('README.rst')
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
    txt = txt.encode('utf-8')
    if readme.exists() and readme.read_file() == txt:
        return
    must_confirm("Overwrite %s" % readme.absolute())
    readme.write_file(txt)
    env.ROOTDIR.child('docs', 'index.rst').set_times()
    #~ cmd = "touch " + env.DOCSDIR.child('index.rst')
    #~ local(cmd)
    #~ pypi_register()


@task(alias='test')
def run_tests():
    """
    Run the complete test suite of this project.
    """
    local('python setup.py -q test')


#~ @task(alias='listpkg')
#~ def list_subpackages():
    # ~ # lst = list(env.ROOTDIR.walk("__init__.py"))
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
    Edit the `project_info.py` file of this project.
    """
    sif = Path(env.ROOTDIR, env.main_package, 'project_info.py')
    print sif
    args = [os.environ['EDITOR']]
    args += [sif]
    local(' '.join(args))


#~ @task(alias='sdist_test')
#~ def extract_messages():
    #~ """Create a temporary virtual environment"""
    #~ locale_dir = get_locale_dir()
    #~ if locale_dir is None: return
    #~ args = ["python", "setup.py"]
    #~ args += [ "extract_messages"]
    #~ args += [ "-o", locale_dir.child("django.pot")]
    #~ cmd = ' '.join(args)
    #~ must_confirm(cmd)
    #~ local(cmd)


