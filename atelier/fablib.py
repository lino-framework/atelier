# -*- coding: UTF-8 -*-
# Copyright 2013-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""This module is a library for fabric_ with tasks I use to manage my
Python projects.

.. _fabric: http://docs.fabfile.org

.. contents::
  :local:

.. _fab_commands:

``fab`` commands
================

Internationalization
--------------------

.. command:: fab mm

    ("make messages")

    Extracts messages from both code and userdocs, then initializes and
    updates all catalogs.

Deploy
------

.. command:: fab ci

    Checkin and push to repository, using today's blog entry as commit
    message.


.. command:: fab release

    Write a source distribution archive to your :attr:`env.sdist_dir`,
    then upload it to PyPI.  Create a version tag if
    :attr:`env.revision_control_system` is ``'git'``.

    This command will fail if this project has previously been
    released with the same version.



.. command:: fab reg

    Register this project (and its current version) to PyPI.

.. command:: fab sdist

    Write a source distribution archive to your :attr:`env.sdist_dir`.





Testing
-------

.. command:: fab initdb

    Run :manage:`initdb_demo` on every demo database of this project
    (specified in :attr:`env.demo_databases`).

    Demo databases are used by the test suite and the Sphinx
    documentation.  They are not included in the code repository since
    they are generated data.  Since initializing these databases can take
    some time, this is not automatically launched for each test run.


.. command:: fab test

    Run the test suite of this project.

.. command:: fab test_sdist

    Creates a temporay virtualenv, installs your project and runs your
    test suite.
        
    - creates and activates a temporay virtualenv,
    - calls ``pip install --extra-index <env.sdist_dir> <prjname>``
    - runs ``python setup.py test``
    - removes temporary files.
    
    Assumes that you previously did :cmd:`fab sdist` of all your
    projects related to this project.
    
    When using this, you should configure a local download cache for
    pip, e.g. with something like this in your
    :file:`~/.pip/pip.conf`::
    
      [global]
      download-cache=/home/luc/.pip/cache


Documenting
-----------

.. command:: fab blog

    Edit today's blog entry, create an empty file if it doesn't yet exist.


.. command:: fab md

    Make docs. Build html docs for this project.

    This run :cmd:`fab readme`, followed by `sphinx build html` in
    every directory defined in :attr:`env.doc_trees`.


.. command:: fab pd

    Publish docs. Upload docs to public web server.


.. command:: fab clean

    Remove temporary and generated files:

    - Sphinx `.build` files
    - Dangling `.pyc` files which don't have a corresponding `.py` file.
    - `cache` directories of demo databases


.. command:: fab readme

    Generate or update `README.txt` or `README.rst` file from
    `SETUP_INFO`.


.. command:: fab api

    Generate `.rst` files below `docs/api` by running `sphinx-apidoc
    <http://sphinx-doc.org/invocation.html#invocation-of-sphinx-apidoc>`_.

    This is no longer used by most of my projects, at least those
    which I converted to autosummary.


.. command:: fab docs

    Has been replaced by :cmd:`fab md`.

.. command:: fab pub

    Has been replaced by :cmd:`fab pd`.


Installation
============

To be used by creating a :file:`fabfile.py` in your project's root
directory with at least the following two lines::

  from atelier.fablib import *
  setup_from_project("foobar")
  
Where "foobar" is the Python name of your project's main package.



Configuration files
===================

.. xfile:: fabfile.py

In your :xfile:`fabfile.py` file you can specify project-specific
configuration settings.  Example content::

  from atelier.fablib import *
  setup_from_project("foobar")
  env.languages = "de fr et nl".split()
  env.tolerate_sphinx_warnings = True
  add_demo_database('foobar.demo.settings')

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
================

fabric_ works with a global "environment" object named ``env``.  The
following section documents the possible attributes of this object as
used by :mod:`atelier.fablib`.

.. class:: env

  .. attribute:: sdist_dir

  .. attribute:: docs_rsync_dest

    A Python template string which defines the rsync destination for
    publishing your projects documentation.
    Used by :cmd:`fab pub`.

    Example::

      env.docs_rsync_dest = 'luc@example.org:~/public_html/%s'


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
    run :cmd:`fab api`.

  .. attribute:: revision_control_system

    The revision control system used by your project.
    Allowed values are `'git'`, `'hg'` or `None`.
    Used by :cmd:`fab ci`.

  .. attribute:: use_mercurial

    **No longer used.** Use :attr:`env.revision_control_system` instead.)

  .. attribute:: demo_databases

You may define user-specific default values for some of these settings
(those who are simple strings) in a :file:`.fabricrc` file.




History
=======

- 20141020 moved `doc_trees` project to :class:`atelier.Project`.
- 20141001 added support for multiple doc trees per project
  (:attr:`env.doc_trees`).
- 20140116 : added support for managing namespace packages

TODO
====

- replace `env.blogger_project` by an attribute of the main module
  (like `intersphinx_urls`)

(The rest of this page is automatically generated stuff.)

"""
import os
import textwrap
import datetime

import sphinx
from babel.dates import format_date
from unipath import Path

from atelier.utils import i2d
from atelier import rstgen

from fabric.api import env, local, task
from fabric.utils import abort, puts
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
        self.url = url_root + "/" + "/".join(parts) + '.html'
        # if parts[0] == 'docs':
        #     self.url = url_root + "/" + "/".join(parts[1:]) + '.html'
        # else:
        #     raise Exception("20131125")
            # self.url = url_root + "/" + "/".join(parts) + '.html'


def add_demo_database(db):
    if db in env.demo_databases:
        return
        # raise Exception("Duplicate entry %r in demo_databases." % db)
    env.demo_databases.append(db)


def setup_from_project(
        main_package=None,
        settings_module_name=None):

    # env.ROOTDIR = Path().absolute()
    env.root_dir = Path().absolute()
    # print("20141027 %s %s " % (main_package, env.root_dir))

    env.project_name = env.root_dir.name
    env.setdefault('build_dir_name', '.build')  # but ablog needs '_build'
    
    env.setdefault('long_date_format', "%Y%m%d (%A, %d %B %Y)")
    # env.work_root = Path(env.work_root)
    env.setdefault('use_dirhtml', False)
    env.setdefault('blog_root', env.root_dir.child('docs'))

    env.setdefault('sdist_dir', None)
    if env.sdist_dir is not None:
        env.sdist_dir = Path(env.sdist_dir)
    env.main_package = main_package
    env.tolerate_sphinx_warnings = False
    env.demo_databases = []
    # env.use_mercurial = True
    env.revision_control_system = None
    env.apidoc_exclude_pathnames = []
    # env.blogger_url = "http://blog.example.com/"

    env.setdefault('languages', None)
    env.setdefault('blogger_project', None)
    env.setdefault('blogger_url', None)

    if isinstance(env.languages, basestring):
        env.languages = env.languages.split()

    # if env.main_package:
    #     env.SETUP_INFO = get_setup_info(Path(env.root_dir))
    # else:
    #     env.SETUP_INFO = None

    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        from django.conf import settings
        # why was this? settings.SITE.startup()
        env.languages = [lng.name for lng in settings.SITE.languages]
        env.demo_databases.append(settings_module_name)
        #~ env.userdocs_base_language = settings.SITE.languages[0].name

    # The following import will populate the projects
    from atelier.projects import get_project_info
    env.current_project = get_project_info(env.root_dir)

    env.doc_trees = env.current_project.doc_trees

    # env.SETUP_INFO = env.current_project.SETUP_INFO


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
    p = env.root_dir.child(*args)
    if not p.isdir():
        return None  # abort("Directory %s does not exist." % p)
    return p


def cleanup_pyc(p):
    """Thanks to oddthinking on http://stackoverflow.com/questions/2528283
    """
    for root, dirs, files in os.walk(p):
        pyc_files = filter(
            lambda filename: filename.endswith(".pyc"), files)
        py_files = set(filter(
            lambda filename: filename.endswith(".py"), files))
        excess_pyc_files = filter(
            lambda pyc_filename: pyc_filename[:-1] not in py_files, pyc_files)
        for excess_pyc_file in excess_pyc_files:
            full_path = os.path.join(root, excess_pyc_file)
            must_confirm("Remove excess file %s:" % full_path)
            os.remove(full_path)


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
    userdocs = env.root_dir.child('userdocs')
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
    data_dir = env.root_dir.child('docs', 'data')
    #~ print list(data_dir.listdir(names_only=True))
    print list(data_dir.walk())


def setup_babel_userdocs(babelcmd):
    """Create userdocs .po files if necessary."""
    userdocs = env.root_dir.child('userdocs')
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
    from lino.core.site_def import to_locale
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
    from lino.core.site_def import to_locale
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
    from lino.core.site_def import to_locale
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
    from atelier.projects import load_projects
    headers = (
        # ~ '#','Location',
        'Project',
        # 'Old version',
        'Version')

    def cells(self):
        self.load_fabfile()
        # print 20140116, self.module
        desc = "%s -- " % self.nickname
        desc += "(doc_trees : %s)\n" % ', '.join(self.doc_trees)
        url = self.SETUP_INFO.get('url', None)
        version = self.SETUP_INFO.get('version', '')
        if url:
            desc += "`%s <%s>`__ -- %s" % (
                self.name, url,
                self.SETUP_INFO['description'])
        return (
            '\n'.join(textwrap.wrap(desc, 60)),
            # self.dist.version,
            version)

    print rstgen.table(headers, [cells(p) for p in load_projects()])


@task(alias='api')
def build_api(*cmdline_args):
    """
    Generate `.rst` files in `docs/api`. See :cmd:`fab api`.
    """
    docs_dir = env.root_dir.child('docs')
    if not docs_dir.exists():
        return
    api_dir = docs_dir.child("api").absolute()
    if not api_dir.exists():
        return
    os.environ.update(SPHINX_APIDOC_OPTIONS="members,show-inheritance")
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
    #~ args += ['-w'+Path(env.root_dir,'sphinx_doctest_warnings.txt')]
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
    Deprecated. sphinx-build the userdocs tree in all languages
    """
    if env.languages is None:
        return
    docs_dir = env.root_dir.child('userdocs')
    if not docs_dir.exists():
        return
    for lng in env.languages:
        sphinx_build('html', docs_dir, cmdline_args, lng)
    sync_docs_data(docs_dir)


@task(alias='pdf')
def build_userdocs_pdf(*cmdline_args):
    if env.languages is None:
        return
    docs_dir = env.root_dir.child('userdocs')
    if not docs_dir.exists():
        return
    for lng in env.languages:
        sphinx_build('latex', docs_dir, cmdline_args,
                     lng, build_dir_cmd='make all-pdf')
    sync_docs_data(docs_dir)


@task(alias='linkcheck')
def sphinx_build_linkcheck(*cmdline_args):
    """sphinxbuild -b linkcheck docs."""
    docs_dir = env.root_dir.child('docs')
    if docs_dir.exists():
        sphinx_build('linkcheck', docs_dir, cmdline_args)
    docs_dir = env.root_dir.child('userdocs')
    if docs_dir.exists():
        lng = env.languages[0]
        #~ lng = env.userdocs_base_language
        sphinx_build('linkcheck', docs_dir, cmdline_args, lng)


def get_doc_trees():
    for rel_doc_tree in env.doc_trees:
        docs_dir = env.root_dir.child(rel_doc_tree)
        if not docs_dir.exists():
            msg = "Directory %s does not exist." % docs_dir
            msg += "\nCheck `doc_trees` in your project's main module."
            raise Exception(msg)
        yield docs_dir


@task(alias='md')
def build_docs(*cmdline_args):
    """See :cmd:`fab md`. """
    write_readme()
    for docs_dir in get_doc_trees():
        puts("Invoking Sphinx in in directory %s..." % docs_dir)
        builder = 'html'
        if env.use_dirhtml:
            builder = 'dirhtml'
        sphinx_build(builder, docs_dir, cmdline_args)
        sync_docs_data(docs_dir)


@task(alias='clean')
def clean(*cmdline_args):
    """See :cmd:`fab clean`. """
    sphinx_clean()
    py_clean()
    clean_demo_caches()


def sphinx_clean():
    """Delete all generated Sphinx files.

    """
    for docs_dir in get_doc_trees():
        rmtree_after_confirm(docs_dir.child(env.build_dir_name))


def py_clean():
    """Delete dangling `.pyc` files.

    """
    if env.current_project.module is not None:
        p = Path(env.current_project.module.__file__).parent
        cleanup_pyc(p)
    p = env.root_dir.child('tests')
    if p.exists():
        cleanup_pyc(p)


@task(alias='pd')
def publish():
    """See :cmd:`fab pd`. """
    if not env.docs_rsync_dest:
        raise Exception(
            "Must set env.docs_rsync_dest in `fabfile.py` or `~/.fabricrc`")

    for docs_dir in get_doc_trees():
        build_dir = docs_dir.child(env.build_dir_name)
        if build_dir.exists():
            name = '%s_%s' % (env.project_name, docs_dir.name)
            dest_url = env.docs_rsync_dest % name
            publish_docs(build_dir, dest_url)

    # build_dir = env.root_dir.child('userdocs', env.build_dir_name)
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


def clean_demo_caches():
    from django.utils.importlib import import_module
    for db in env.demo_databases:
        m = import_module(db)
        p = Path(m.SITE.project_dir).child('media', 'cache')
        rmtree_after_confirm(p)


@task(alias="initdb")
def initdb_demo():
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
    build_dir = env.root_dir.child('docs', env.build_dir_name)
    args += [env.root_dir.child('docs'), build_dir]
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
    """See :cmd:`fab sdist`. """
    args = ["python", "setup.py"]
    args += ["sdist", "--formats=gztar"]
    args += ["--dist-dir", env.sdist_dir.child(
        env.current_project.SETUP_INFO['name'])]
    local(' '.join(args))



LASTREL_INFO = "Last release %(filename)s was %(upload_time)s (%(downloads)d downloads)."
def show_pypi_status():

    info = env.current_project.SETUP_INFO
    version = info['version']
    name = info['name']
    
    try:
        import xmlrpclib
    except ImportError:
        import xmlrpc.client as xmlrpclib
    client = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
    released_versions = client.package_releases(name)
    if len(released_versions) == 0:
        must_confirm(
            "This is your first release of %(name)s %(version)s "
            "to PyPI" % info)
    else:
        lastrel = client.release_urls(name, released_versions[-1])[-1]
        puts(LASTREL_INFO % lastrel)
        if version in released_versions:
            abort("%(name)s %(version)s has already been released." % info)


RELEASE_CONFIRM = """
-------------------------------------------------------------------------------
This is going to officially release %(name)s %(version)s to PyPI.
It will fail if version %(version)s of %(name)s has previously been released.
Your `docs/changes.rst` should have a section about this version.
Your working directory should be clean (otherwise answer 'n' and run `fab ci`).
Are you sure?"""


@task(alias='release')
def pypi_release():
    """See :cmd:`fab release`. """

    info = env.current_project.SETUP_INFO
    version = info['version']

    show_revision_status()
    show_pypi_status()

    must_confirm(RELEASE_CONFIRM % info)

    if env.revision_control_system == 'git':
        args = ["git", "tag"]
        args += ["-a", version]
        args += ["-m", "'Release %(name)s %(version)s.'" % info]
        local(' '.join(args))

    pypi_register()
    args = ["python", "setup.py"]
    args += ["sdist", "--formats=gztar"]
    args += ["--dist-dir", env.sdist_dir.child(
        env.current_project.SETUP_INFO['name'])]
    args += ["upload"]
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

    context = dict(
        name=env.current_project.SETUP_INFO['name'],
        sdist_dir=env.sdist_dir,
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
    TODO: convert this to a Lino management command.
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


@task(alias='reg')
def pypi_register():
    """See :cmd:`fab reg`. """
    args = ["python", "setup.py"]
    args += ["register"]
    #~ run_setup('setup.py',args)
    local(' '.join(args))


def get_blog_entry(today):
    """Return an RstFile object representing the blog entry for that date
    in the current project.

    """
    parts = ('blog', str(today.year), today.strftime("%m%d"))
    return RstFile(Path(env.blog_root), env.blogref_url, parts)


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


def show_revision_status():

    if env.revision_control_system == 'hg':
        args = ["hg", "st"]
    elif env.revision_control_system == 'git':
        args = ["git", "status"]
    else:
        abort("Invalid revision_control_system %r !" %
              env.revision_control_system)
    local(' '.join(args))


@task(alias='ci')
def checkin(today=None):
    """See :cmd:`fab ci`. """

    show_revision_status()

    if today is None:
        today = get_current_date()
    else:
        today = i2d(today)

    entry = get_blog_entry(today)
    #~ entry = Path(env.root_dir,'..',env.blogger_project,*parts)
    #~ print env.root_dir.parent.absolute()
    if not entry.path.exists():
        abort("%s does not exist!" % entry.path.absolute())

    msg = entry.url

    if not confirm("OK to checkin %s %s?" % (env.project_name, msg)):
        return
    #~ puts("Commit message refers to %s" % entry.absolute())

    if env.revision_control_system == 'hg':
        args = ["hg", "ci"]
    else:
        args = ["git", "commit", "-a"]
    args += ['-m', msg]
    cmd = ' '.join(args)
    local(cmd)
    if env.revision_control_system == 'hg':
        local("hg push %s" % env.project_name)
    else:
        local("git push")


def unused_write_release_notes():
    """
    Generate docs/releases/x.y.z.rst file from setup_info.
    """
    v = env.current_project.SETUP_INFO['version']
    if v.endswith('+'):
        return
    notes = Path(env.root_dir, 'docs', 'releases', '%s.rst' % v)
    if notes.exists():
        return
    must_confirm("Create %s" % notes.absolute())
    #~ context = dict(date=get_current_date().strftime(env.long_date_format))
    context = dict(date=get_current_date().strftime('%Y%m%d'))
    context.update(env.current_project.SETUP_INFO)
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


@task(alias='readme')
def write_readme():
    """See :cmd:`fab readme`. """
    if not env.main_package:
        return
    if len(env.doc_trees) == 0:
        # when there are no docs, then the README file is manually maintained
        return
    if env.revision_control_system == 'git':
        readme = env.root_dir.child('README.rst')
    else:
        readme = env.root_dir.child('README.txt')
    txt = """\
==========================
%(name)s README
==========================

%(description)s

Description
-----------

%(long_description)s

Read more on %(url)s
""" % env.current_project.SETUP_INFO
    txt = txt.encode('utf-8')
    if readme.exists() and readme.read_file() == txt:
        return
    must_confirm("Overwrite %s" % readme.absolute())
    readme.write_file(txt)
    docs_index = env.root_dir.child('docs', 'index.rst')
    if docs_index.exists():
        docs_index.set_times()
    #~ cmd = "touch " + env.DOCSDIR.child('index.rst')
    #~ local(cmd)
    #~ pypi_register()


@task(alias='test')
def run_tests():
    """See :cmd:`fab test`. """
    local('python setup.py -q test')


#~ @task(alias='listpkg')
#~ def list_subpackages():
    # ~ # lst = list(env.root_dir.walk("__init__.py"))
    #~ for fn in env.root_dir.child('lino').walk('*.py'):
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
    for package_name in env.current_project.SETUP_INFO['packages']:
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
    sif = Path(env.root_dir, env.main_package, 'project_info.py')
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


