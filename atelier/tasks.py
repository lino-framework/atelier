# -*- coding: UTF-8 -*-
# Copyright 2013-2016 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.
"""A library for `invoke <http://www.pyinvoke.org/>`__ with tasks I use
to manage my Python projects.

.. contents::
  :local:

.. _invoke_commands:

``invoke`` commands
================

Documenting
-----------

.. command:: invoke blog

    Edit today's blog entry, create an empty file if it doesn't yet exist.

.. command:: invoke bd

    Build docs. Build all Sphinx HTML doctrees for this project.

    This runs :cmd:`invoke readme`, followed by `sphinx-build html` in
    every directory defined in :attr:`env.doc_trees`.  The exact
    options for `sphinx-build` depend also on
    :attr:`env.tolerate_sphinx_warnings` and :attr:`env.use_dirhtml`.

.. command:: invoke pd

    Publish docs. Upload docs to public web server.


.. command:: invoke clean

    Remove temporary and generated files:

    - Sphinx `.build` files
    - Dangling `.pyc` files which don't have a corresponding `.py` file.
    - `cache` directories of demo projects
    - additional files specified in :attr:`env.cleanable_files`

Internationalization
--------------------

.. command:: invoke mm

    ("make messages")

    Extracts messages from both code and userdocs, then initializes and
    updates all catalogs. Needs :attr:`env.locale_dir`

Deploy
------

.. command:: invoke ci

    Checkin and push to repository, using today's blog entry as commit
    message.

    Asks confirmation before doing so.

    Does nothing in a project whose
    :attr:`env.revision_control_system` is `None`.

    In a project whose :attr:`env.revision_control_system` is
    ``'git'`` it checks whether the repository is dirty (i.e. has
    uncommitted changes) and returns without asking confirmation if
    the repo is clean.  Note that unlike ``git status``, this check
    does currently not (yet) check whether my branch is up-to-date
    with 'origin/master'.

.. command:: invoke reg

    Register this project (and its current version) to PyPI.

Testing
-------

.. command:: invoke initdb

    Run :manage:`initdb_demo` on every demo :attr:`env.demo_projects`.

.. command:: invoke test

    See :func:`run_tests`.

Installation
============

To be used by creating a :file:`tasks.py` in your project's root
directory with at least the following two lines::

  from atelier.tasks import *
  env.setup_from_tasks(globals())

See :func:`setup_from_tasks` for more information.

Configuration files
===================

.. xfile:: tasks.py

In your :xfile:`tasks.py` file you can specify project-specific
configuration settings.  Example content::

  from atelier.tasks import *
  env.setup_from_tasks(globals(), "foobar")
  env.languages = "de fr et nl".split()
  env.tolerate_sphinx_warnings = True
  add_demo_project('foobar.demo')

"""

from __future__ import print_function
from builtins import str
from builtins import object
import importlib

import os
from contextlib import contextmanager
import glob
import datetime
from time import sleep
from atelier.utils import i2d
from babel.dates import format_date

from atelier import rstgen

from unipath import Path
from invoke import task
from invoke import run as local
from atelier.utils import confirm, AttrDict
import subprocess
import sys


@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)


def get_current_date(today=None):
    """
    """

    if today is None:
        return datetime.date.today()
    return i2d(today)


def must_confirm(*args, **kwargs):
    if not confirm(''.join(args)):
        raise Exception("User failed to confirm.")


def must_exist(p):
    if not p.exists():
        raise Exception("No such file: %s" % p.absolute())


def rmtree_after_confirm(p):
    if not p.exists():
        return
    if confirm("OK to remove %s and everything under it?" % p.absolute()):
        p.rmtree()


def cleanup_pyc(p):
    """Thanks to oddthinking on http://stackoverflow.com/questions/2528283
    """
    for root, dirs, files in os.walk(p):
        pyc_files = [filename for filename in files if filename.endswith(".pyc")]
        py_files = set([filename for filename in files if filename.endswith(".py")])
        excess_pyc_files = [pyc_filename for pyc_filename in pyc_files if pyc_filename[:-1] not in py_files]
        for excess_pyc_file in excess_pyc_files:
            full_path = os.path.join(root, excess_pyc_file)
            must_confirm("Remove excess file %s:" % full_path)
            os.remove(full_path)


class Atelier(AttrDict):
    def setup_from_tasks(
            env, globals_dict, main_package=None, settings_module_name=None):
        if '__file__' not in globals_dict:
            raise Exception(
                "No '__file__' in %r. "
                "First parameter to must be `globals()`" % globals_dict)

        tasks = Path(globals_dict['__file__'])
        if not tasks.exists():
            raise Exception("No such file: %s" % tasks)
        defaults = dict(
            root_dir=tasks.parent.absolute(),
            main_package=main_package,
            locale_dir=None,
            tolerate_sphinx_warnings=False,
            demo_projects=[],
            revision_control_system=None,
            apidoc_exclude_pathnames=[],
            project_name=tasks.parent.absolute().name,
            editor_command=None)

        env.update(defaults)

        if settings_module_name is not None:
            os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
            from django.conf import settings
            # why was this? settings.SITE.startup()
            env.update(
                languages=[lng.name for lng in settings.SITE.languages])

        env.setdefault('build_dir_name', '.build')  # but ablog needs '_build'
        env.setdefault('use_dirhtml', False)

        # # The following import will populate the projects
        from atelier.projects import get_project_info
        prj = get_project_info(env.root_dir)
        prj.load_tasks()
        env.update(
            current_project=prj, doc_trees=prj.doc_trees)

    def sphinx_clean(env):
        """Delete all generated Sphinx files.

        """
        for docs_dir in env.get_doc_trees():
            rmtree_after_confirm(docs_dir.child(env.build_dir_name))

    def py_clean(env):
        """Delete dangling `.pyc` files.

        """
        if env.current_project.module is not None:
            p = Path(env.current_project.module.__file__).parent
            cleanup_pyc(p)
        p = env.root_dir.child('tests')
        if p.exists():
            cleanup_pyc(p)

        files = []
        for pat in env.cleanable_files:
            for p in glob.glob(os.path.join(env.root_dir, pat)):
                files.append(p)
        if len(files):
            must_confirm("Remove {0} cleanable files".format(len(files)))
            for p in files:
                os.remove(p)

    def run_in_demo_projects(env, admin_cmd, *more):
        """Run the given shell command in each demo project (see
        :attr:`env.demo_projects`).

        """
        for mod in env.demo_projects:
            # puts("-" * 80)
            # puts("In demo project {0}:".format(mod))
            print("-" * 80)
            print("In demo project {0}:".format(mod))

            # m = import_module(mod)
            args = ["django-admin.py"]
            args += [admin_cmd]
            args += more
            args += ["--settings=" + mod]
            cmd = " ".join(args)
            local(cmd)

    def add_demo_project(env, p):
        """Register the specified settings module as being a Django demo project.
        See also :attr:`env.demo_projects`.

        """
        if p in env.demo_projects:
            return
            # raise Exception("Duplicate entry %r in demo_projects." % db)
        env.demo_projects.append(p)

    def get_doc_trees(env):
        for rel_doc_tree in env.doc_trees:
            docs_dir = env.root_dir.child(rel_doc_tree)
            if not docs_dir.exists():
                msg = "Directory %s does not exist." % docs_dir
                msg += "\nCheck your project's `doc_trees` setting."
                raise Exception(msg)
            yield docs_dir

    def sync_docs_data(env, docs_dir):
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

    def sphinx_build(env, builder, docs_dir,
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
                # print 20130726, build_dir
        if env.tolerate_sphinx_warnings:
            args += ['-w', 'warnings_%s.txt' % builder]
        else:
            args += ['-W']  # consider warnings as errors
            # args += ['-vvv']  # increase verbosity
        # args += ['-w'+Path(env.root_dir,'sphinx_doctest_warnings.txt')]
        args += ['.', build_dir]
        cmd = ' '.join(args)
        with cd(docs_dir):
            local(cmd)
        if build_dir_cmd is not None:
            with cd(build_dir):
                local(build_dir_cmd)


env = Atelier()


class RstFile(object):
    def __init__(self, local_root, url_root, parts):
        self.path = local_root.child(*parts) + '.rst'
        self.url = url_root + "/" + "/".join(parts) + '.html'
        # if parts[0] == 'docs':
        #     self.url = url_root + "/" + "/".join(parts[1:]) + '.html'
        # else:
        #     raise Exception("20131125")
        # self.url = url_root + "/" + "/".join(parts) + '.html'


class MissingConfig(Exception):
    def __init__(self, name):
        msg = "Must set `env.{0}` in `tasks.py`!"
        msg = msg.format(name)
        Exception.__init__(self, msg)


@task(name='initdb')
def initdb_demo():
    env.run_in_demo_projects('initdb_demo', "--noinput", '--traceback')


@task(name='test')
def run_tests():
    """Run the test suite of this project."""
    if not env.root_dir.child('setup.py').exists():
        return
    local('python setup.py -q test')


@task(name='readme')
def write_readme():
    """See :cmd:`inv readme`. """
    if not env.main_package:
        return
    if len(env.doc_trees) == 0:
        # when there are no docs, then the README file is manually maintained
        return
    if env.revision_control_system == 'git':
        readme = env.root_dir.child('README.rst')
    else:
        readme = env.root_dir.child('README.txt')

    env.current_project.load_tasks()
    # for k in ('name', 'description', 'long_description', 'url'):
    #     if k not in env.current_project.SETUP_INFO:
    #         msg = "SETUP_INFO for {0} has no key '{1}'"
    #         raise Exception(msg.format(env.current_project, k))

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
        # cmd = "touch " + env.DOCSDIR.child('index.rst')
        # local(cmd)
        # pypi_register()


@task(write_readme, name='bd')
def build_docs(*cmdline_args):
    """See :cmd:`inv bd`. """
    # env.write_readme()
    for docs_dir in env.get_doc_trees():
        print("Invoking Sphinx in in directory %s..." % docs_dir)
        builder = 'html'
        if env.use_dirhtml:
            builder = 'dirhtml'
        env.sphinx_build(builder, docs_dir, cmdline_args)
        env.sync_docs_data(docs_dir)


@task(name='clean')
def clean(*cmdline_args):
    """See :inv:`inv clean`. """
    env.sphinx_clean()
    env.py_clean()
    # clean_demo_caches()


@task(name='cov')
def run_tests_coverage():
    """
    Run all tests, creating coverage report
    """
    covfile = env.root_dir.child('.coveragerc')
    if not covfile.exists():
        return
    import coverage
    # ~ clean_sys_path()
    print("Running tests for '%s' within coverage..." % env.project_name)
    # ~ env.DOCSDIR.chdir()
    if False:
        source = []
        env.current_project.load_tasks()
        for package_name in env.current_project.SETUP_INFO['packages']:
            m = importlib.import_module(package_name)
            source.append(os.path.dirname(m.__file__))
        if not confirm("coverage source=%s" % source):
            exit()
        cov = coverage.coverage(source=source, )
        cov.start()
        # .. call your code ..
        rv = run_tests()
        cov.stop()
        cov.save()

    else:
        os.environ['COVERAGE_PROCESS_START'] = covfile

        args = [sys.executable]
        args += ['setup.py', 'test', '-q']
        cov = coverage.coverage()
        cov.start()
        with cd(env.root_dir):
            rv = subprocess.check_output(args, env=os.environ)
            # Get coverage for project.py
            env.current_project.load_tasks()
        cov.stop()
        cov.save()


    # cov.html_report()
    with cd(env.root_dir):
        local('coverage report')
    return rv


@task(name='mm')
def make_messages():
    "Extract messages, then initialize and update all catalogs."
    extract_messages()
    init_catalog_code()
    update_catalog_code()

    # if False:
    #     pass
    # extract_messages_userdocs()
    # setup_babel_userdocs('init_catalog')
    # setup_babel_userdocs('update_catalog')


@task(name='reg')
def pypi_register():
    """See :cmd:`inv reg`. """
    args = ["python", "setup.py"]
    args += ["register"]
    # ~ run_setup('setup.py',args)
    local(' '.join(args))


@task(name='ci')
def checkin(today=None):
    """See :cmd:`inv ci`. """

    if env.revision_control_system is None:
        return

    if env.revision_control_system == 'git':
        from git import Repo
        repo = Repo(env.root_dir)
        if not repo.is_dirty():
            print("No changes to commit in {0}.".format(env.root_dir))
            return

    show_revision_status()

    today = get_current_date(today)

    entry = get_blog_entry(today)
    if not entry.path.exists():
        quit("%s does not exist!" % entry.path.absolute())

    msg = entry.url

    if not confirm("OK to checkin %s %s?" % (env.project_name, msg)):
        return
    # ~ puts("Commit message refers to %s" % entry.absolute())

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


@task(name='blog')
def edit_blog_entry(today=None):
    """Edit today's blog entry, create an empty file if it doesn't yet exist.

    :today: Useful when a working day lasted longer than midnight, or
            when you start some work in the evening, knowing that you
            won't commit it before the next morning.  Note that you
            must specify the date using the YYYYMMDD format.

            Usage example::

                $ fab blog:20150727

    """
    if not env.editor_command:
        raise MissingConfig("editor_command")
    today = get_current_date(today)
    entry = get_blog_entry(today)
    if not entry.path.exists():
        if not confirm("Create file %s?" % entry.path):
            return
        # for every year we create a new directory.
        yd = entry.path.parent
        if not yd.exists():
            if not confirm("Happy New Year! Create directory %s?" % yd):
                return
            yd.mkdir()
            txt = ".. blogger_year::\n"
            yd.child('index.rst').write_file(txt.encode('utf-8'))

        if env.languages is None:
            txt = today.strftime(env.long_date_format)
        else:
            txt = format_date(
                today, format='full', locale=env.languages[0])
        entry.path.write_file(rstgen.header(1, txt).encode('utf-8'))
        # touch it for Sphinx:
        entry.path.parent.child('index.rst').set_times()
    args = [env.editor_command]
    args += [entry.path]
    local(' '.join(args))


@task(name='pd')
def publish():
    """See :cmd:`inv pd`. """
    if not env.docs_rsync_dest:
        raise MissingConfig("docs_rsync_dest")

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


def get_doc_trees():
    for rel_doc_tree in env.doc_trees:
        docs_dir = env.root_dir.child(rel_doc_tree)
        if not docs_dir.exists():
            msg = "Directory %s does not exist." % docs_dir
            msg += "\nCheck your project's `doc_trees` setting."
            raise Exception(msg)
        yield docs_dir


def publish_docs(build_dir, dest_url):
    with cd(build_dir):
        args = ['rsync', '-r']
        args += ['--verbose']
        args += ['--progress']  # show progress
        args += ['--delete']  # delete files in dest
        args += ['--times']  # preserve timestamps
        args += ['--exclude', '.doctrees']
        args += ['./']  # source
        args += [dest_url]  # dest
        cmd = ' '.join(args)
        # ~ must_confirm("%s> %s" % (build_dir, cmd))
        # ~ confirm("yes")
        local(cmd)


def show_revision_status():
    if env.revision_control_system == 'hg':
        args = ["hg", "st"]
    elif env.revision_control_system == 'git':
        args = ["git", "status"]
    else:
        print("Invalid revision_control_system %r !" %
              env.revision_control_system)
        return
    print("-" * 80)
    local(' '.join(args))
    print("-" * 80)


def get_blog_entry(today):
    """Return an RstFile object representing the blog entry for that date
    in the current project.

    """
    parts = ('blog', str(today.year), today.strftime("%m%d"))
    return RstFile(Path(env.blog_root), env.blogref_url, parts)


def extract_messages():
    """Extract messages from source files to `django.pot` file"""
    # locale_dir = get_locale_dir()
    locale_dir = env.locale_dir
    if locale_dir is None:
        return
    args = ["python", "setup.py"]
    args += ["extract_messages"]
    args += ["-o", Path(locale_dir).child("django.pot")]
    cmd = ' '.join(args)
    # ~ must_confirm(cmd)
    local(cmd)


def init_catalog_code():
    """Create code .po files if necessary."""
    from lino.core.site import to_locale
    locale_dir = env.locale_dir
    # locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    locale_dir = Path(locale_dir)
    for loc in env.languages:
        if loc != 'en':
            f = locale_dir.child(loc, 'LC_MESSAGES', 'django.po')
            if f.exists():
                print("Skip %s because file exists." % f)
            else:
                args = ["python", "setup.py"]
                args += ["init_catalog"]
                args += ["--domain django"]
                args += ["-l", to_locale(loc)]
                args += ["-d", locale_dir]
                # ~ args += [ "-o" , f ]
                args += ["-i", locale_dir.child('django.pot')]
                cmd = ' '.join(args)
                must_confirm(cmd)
                local(cmd)


def update_catalog_code():
    """Update .po files from .pot file."""
    from lino.core.site import to_locale
    locale_dir = env.locale_dir
    # locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    locale_dir = Path(locale_dir)
    for loc in env.languages:
        if loc != env.languages[0]:
            args = ["python", "setup.py"]
            args += ["update_catalog"]
            args += ["--domain django"]
            # ~ args += [ "-d" , locale_dir ]
            args += ["-o", locale_dir.child(loc, 'LC_MESSAGES', 'django.po')]
            args += ["-i", locale_dir.child("django.pot")]
            args += ["-l", to_locale(loc)]
            cmd = ' '.join(args)
            # ~ must_confirm(cmd)
            local(cmd)
