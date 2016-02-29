# -*- coding: UTF-8 -*-
# Copyright 2013-2016 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.

"""A library for `invoke <http://www.pyinvoke.org/>`__ with tasks I use
to manage my Python projects.

.. contents::
  :local:

.. _inv_commands:

``inv`` commands
================

.. command:: inv

The :cmd:`inv` command has been installed with the `invoke
<http://www.pyinvoke.org/>`_ package.

Documenting
-----------

.. command:: inv blog

    Edit today's blog entry, create an empty file if it doesn't yet exist.

.. command:: inv bd

    Build docs. Build all Sphinx HTML doctrees for this project.

    This runs :cmd:`invoke readme`, followed by `sphinx-build html` in
    every directory defined in :attr:`env.doc_trees`.  The exact
    options for `sphinx-build` depend also on
    :attr:`env.tolerate_sphinx_warnings` and :attr:`env.use_dirhtml`.

.. command:: inv pd

    Publish docs. Upload docs to public web server.


.. command:: inv clean

    Remove temporary and generated files:

    - Sphinx `.build` files
    - Dangling `.pyc` files which don't have a corresponding `.py` file.
    - `cache` directories of demo projects
    - additional files specified in :attr:`env.cleanable_files`

.. command:: inv readme

    Generate or update `README.txt` or `README.rst` file from
    `SETUP_INFO`.

Internationalization
--------------------

.. command:: inv mm

    ("make messages")

    Extracts messages from both code and userdocs, then initializes and
    updates all catalogs. Needs :attr:`env.locale_dir`

Deploy
------

.. command:: inv ci

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

.. command:: inv reg

    Register this project (and its current version) to PyPI.

Testing
-------

.. command:: inv initdb

    Run :manage:`initdb_demo` on every demo :attr:`env.demo_projects`.

.. command:: inv test

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
from __future__ import unicode_literals

import importlib
import os
from contextlib import contextmanager
import glob
import datetime
import subprocess
import sys

from builtins import str
from builtins import object
from atelier.utils import i2d
from babel.dates import format_date
from atelier import rstgen
from unipath import Path
from invoke import ctask as task
from invoke import run as local
from atelier.utils import confirm


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


def sphinx_clean(ctx):
    """Delete all generated Sphinx files.

    """
    for docs_dir in get_doc_trees(ctx):
        rmtree_after_confirm(docs_dir.child(ctx.build_dir_name))


def py_clean(ctx):
    """Delete dangling `.pyc` files.

    """
    if ctx.current_project.module is not None:
        p = Path(ctx.current_project.module.__file__).parent
        cleanup_pyc(p)
    p = ctx.root_dir.child('tests')
    if p.exists():
        cleanup_pyc(p)

    files = []
    for pat in ctx.cleanable_files:
        for p in glob.glob(os.path.join(ctx.root_dir, pat)):
            files.append(p)
    if len(files):
        must_confirm("Remove {0} cleanable files".format(len(files)))
        for p in files:
            os.remove(p)


def run_in_demo_projects(ctx, admin_cmd, *more):
    """Run the given shell command in each demo project (see
    :attr:`ctx.demo_projects`).

    """
    for mod in ctx.demo_projects:
        # puts("-" * 80)
        # puts("In demo project {0}:".format(mod))
        print("-" * 80)
        print("In demo project {0}:".format(mod))

        from importlib import import_module
        m = import_module(mod)
        p = m.SITE.cache_dir or m.SITE.project_dir

        with cd(p):
            # m = import_module(mod)
            args = ["django-admin.py"]
            args += [admin_cmd]
            args += more
            args += ["--settings=" + mod]
            cmd = " ".join(args)
            local(cmd)


def add_demo_project(ctx, p):
    """Register the specified settings module as being a Django demo project.
    See also :attr:`ctx.demo_projects`.

    """
    if p in ctx.get('demo_projects', False):
        return
        # raise Exception("Duplicate entry %r in demo_projects." % db)
    ctx['demo_projects'].append(p)


def get_doc_trees(ctx):
    for rel_doc_tree in ctx.doc_trees:
        docs_dir = ctx.root_dir.child(rel_doc_tree)
        if not docs_dir.exists():
            msg = "Directory %s does not exist." % docs_dir
            msg += "\nCheck your project's `doc_trees` setting."
            raise Exception(msg)
        yield docs_dir


def sync_docs_data(ctx, docs_dir):
    build_dir = docs_dir.child(ctx.build_dir_name)
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


def sphinx_build(ctx, builder, docs_dir,
                 cmdline_args=[], language=None, build_dir_cmd=None):
    args = ['sphinx-build', '-b', builder]
    args += cmdline_args
    # ~ args += ['-a'] # all files, not only outdated
    # ~ args += ['-P'] # no postmortem
    # ~ args += ['-Q'] # no output
    # build_dir = docs_dir.child(ctx.build_dir_name)
    build_dir = Path(ctx.build_dir_name)
    if language is not None:
        args += ['-D', 'language=' + language]
        # needed in select_lang.html template
        args += ['-A', 'language=' + language]
        if language != ctx.languages[0]:
            build_dir = build_dir.child(language)
            # print 20130726, build_dir
    if ctx.tolerate_sphinx_warnings:
        args += ['-w', 'warnings_%s.txt' % builder]
    else:
        args += ['-W']  # consider warnings as errors
        # args += ['-vvv']  # increase verbosity
    # args += ['-w'+Path(ctx.root_dir,'sphinx_doctest_warnings.txt')]
    args += ['.', build_dir]
    cmd = ' '.join(args)
    with cd(docs_dir):
        local(cmd)
    if build_dir_cmd is not None:
        with cd(build_dir):
            local(build_dir_cmd)


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
        msg = "Must set `config.{0}` in `tasks.py`!"
        msg = msg.format(name)
        Exception.__init__(self, msg)


@task(name='initdb')
def initdb_demo(ctx):
    """Run `manage.py initdb_demo` on every demo project."""
    run_in_demo_projects(ctx, 'initdb_demo', "--noinput", '--traceback')


@task(name='test')
def run_tests(ctx):
    """Run the test suite of this project."""
    if not ctx.root_dir.child('setup.py').exists():
        return
    local('python setup.py -q test')


@task(name='readme')
def write_readme(ctx):
    """Generate or update `README.txt` or `README.rst` file from `SETUP_INFO`. """
    if not ctx.main_package:
        return
    if len(ctx.doc_trees) == 0:
        # when there are no docs, then the README file is manually maintained
        return
    if ctx.revision_control_system == 'git':
        readme = ctx.root_dir.child('README.rst')
    else:
        readme = ctx.root_dir.child('README.txt')

    ctx.current_project.load_tasks()
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
""" % ctx.current_project.SETUP_INFO
    txt = txt.encode('utf-8')
    if readme.exists() and readme.read_file() == txt:
        return
    must_confirm("Overwrite %s" % readme.absolute())
    readme.write_file(txt)
    docs_index = ctx.root_dir.child('docs', 'index.rst')
    if docs_index.exists():
        docs_index.set_times()
        # cmd = "touch " + ctx.DOCSDIR.child('index.rst')
        # local(cmd)
        # pypi_register()


@task(write_readme, name='bd')
def build_docs(ctx, *cmdline_args):
    """Build docs. Build all Sphinx HTML doctrees for this project. """
    for docs_dir in get_doc_trees(ctx):
        print("Invoking Sphinx in in directory %s..." % docs_dir)
        builder = 'html'
        if ctx.use_dirhtml:
            builder = 'dirhtml'
        sphinx_build(ctx, builder, docs_dir, cmdline_args)
        sync_docs_data(ctx, docs_dir)


@task(name='clean')
def clean(ctx, *cmdline_args):
    """Remove temporary and generated files."""
    sphinx_clean(ctx)
    py_clean(ctx)
    # clean_demo_caches()


@task(name='cov')
def run_tests_coverage(ctx):
    """
    Run all tests, creating coverage report.
    """
    covfile = ctx.root_dir.child('.coveragerc')
    if not covfile.exists():
        return
    import coverage
    # ~ clean_sys_path()
    print("Running tests for '%s' within coverage..." % ctx.project_name)
    # ~ ctx.DOCSDIR.chdir()
    if False:
        source = []
        ctx.current_project.load_tasks()
        for package_name in ctx.current_project.SETUP_INFO['packages']:
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

        source = []
        prj = ctx.current_project
        prj.load_tasks()
        packages = prj.SETUP_INFO.get('packages')
        if not packages:
            raise Exception("No packages in {0}".format(prj))
        for package_name in packages:
            m = importlib.import_module(package_name)
            source.append(os.path.dirname(m.__file__))
        cov = coverage.coverage(source=source, )
        # cov = coverage.coverage()
        cov.start()
        with cd(ctx.root_dir):
            # Get coverage for project.py
            args = [sys.executable]
            args += ['setup.py', 'test', '-q']
            rv = subprocess.check_output(args, env=os.environ)
        cov.stop()
        cov.save()

    # cov.html_report()
    with cd(ctx.root_dir):
        local('coverage report')
    return rv


@task(name='mm')
def make_messages(ctx):
    "Extract messages, then initialize and update all catalogs."
    extract_messages(ctx)
    init_catalog_code(ctx)
    update_catalog_code(ctx)

    # if False:
    #     pass
    # extract_messages_userdocs()
    # setup_babel_userdocs('init_catalog')
    # setup_babel_userdocs('update_catalog')


@task(name='reg')
def pypi_register(ctx):
    """Register this project (and its current version) to PyPI. """
    args = ["python", "setup.py"]
    args += ["register"]
    # ~ run_setup('setup.py',args)
    local(' '.join(args))


@task(name='ci')
def checkin(ctx, today=None):
    """Checkin and push to repository, using today's blog entry as commit message."""

    if ctx.revision_control_system is None:
        return

    if ctx.revision_control_system == 'git':
        from git import Repo
        repo = Repo(ctx.root_dir)
        if not repo.is_dirty():
            print("No changes to commit in {0}.".format(ctx.root_dir))
            return

    show_revision_status(ctx)

    today = get_current_date(today)

    entry = get_blog_entry(ctx, today)
    if not entry.path.exists():
        quit("%s does not exist!" % entry.path.absolute())

    msg = entry.url

    if not confirm("OK to checkin %s %s?" % (ctx.project_name, msg)):
        return
    # ~ puts("Commit message refers to %s" % entry.absolute())

    if ctx.revision_control_system == 'hg':
        args = ["hg", "ci"]
    else:
        args = ["git", "commit", "-a"]
    args += ['-m', msg]
    cmd = ' '.join(args)
    local(cmd)
    if ctx.revision_control_system == 'hg':
        local("hg push %s" % ctx.project_name)
    else:
        local("git push")


@task(name='blog')
def edit_blog_entry(ctx, today=None):
    """Edit today's blog entry, create an empty file if it doesn't yet exist.

    :today: Useful when a working day lasted longer than midnight, or
            when you start some work in the evening, knowing that you
            won't commit it before the next morning.  Note that you
            must specify the date using the YYYYMMDD format.

            Usage example::

                $ fab blog:20150727

    """
    if not ctx.editor_command:
        raise MissingConfig("editor_command")
    today = get_current_date(today)
    entry = get_blog_entry(ctx, today)
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

        if ctx.languages is None:
            txt = today.strftime(ctx.long_date_format)
        else:
            txt = format_date(
                today, format='full', locale=ctx.languages[0])
        entry.path.write_file(rstgen.header(1, txt).encode('utf-8'))
        # touch it for Sphinx:
        entry.path.parent.child('index.rst').set_times()
    args = [ctx.editor_command]
    args += [entry.path]
    local(' '.join(args))


@task(name='pd')
def publish(ctx):
    """Publish docs. Upload docs to public web server. """
    if not ctx.docs_rsync_dest:
        raise MissingConfig("docs_rsync_dest")

    for docs_dir in get_doc_trees(ctx):
        build_dir = docs_dir.child(ctx.build_dir_name)
        if build_dir.exists():
            # name = '%s_%s' % (ctx.project_name, docs_dir.name)
            # dest_url = ctx.docs_rsync_dest % name
            if "%" in ctx.docs_rsync_dest:
                name = '%s_%s' % (ctx.project_name, docs_dir.name)
                dest_url = ctx.docs_rsync_dest % name
            else:
                dest_url = ctx.docs_rsync_dest.format(
                    prj=ctx.project_name, docs=docs_dir.name)
            publish_docs(build_dir, dest_url)

            # build_dir = ctx.root_dir.child('userdocs', ctx.build_dir_name)
            # if build_dir.exists():
            #     dest_url = ctx.docs_rsync_dest % (ctx.project_name + '-userdocs')
            #     publish_docs(build_dir, dest_url)


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


def show_revision_status(ctx):
    if ctx.revision_control_system == 'hg':
        args = ["hg", "st"]
    elif ctx.revision_control_system == 'git':
        args = ["git", "status"]
    else:
        print("Invalid revision_control_system %r !" %
              ctx.revision_control_system)
        return
    print("-" * 80)
    local(' '.join(args))
    print("-" * 80)


def get_blog_entry(ctx, today):
    """Return an RstFile object representing the blog entry for that date
    in the current project.

    """
    parts = ('blog', str(today.year), today.strftime("%m%d"))
    return RstFile(Path(ctx.blog_root), ctx.blogref_url, parts)


def extract_messages(ctx):
    """Extract messages from source files to `django.pot` file"""
    # locale_dir = get_locale_dir()
    locale_dir = ctx.locale_dir
    if locale_dir is None:
        return
    args = ["python", "setup.py"]
    args += ["extract_messages"]
    args += ["-o", Path(locale_dir).child("django.pot")]
    cmd = ' '.join(args)
    # ~ must_confirm(cmd)
    local(cmd)


def init_catalog_code(ctx):
    """Create code .po files if necessary."""
    from lino.core.site import to_locale
    locale_dir = ctx.locale_dir
    # locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    locale_dir = Path(locale_dir)
    for loc in ctx.languages:
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


def update_catalog_code(ctx):
    """Update .po files from .pot file."""
    from lino.core.site import to_locale
    locale_dir = ctx.locale_dir
    # locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    locale_dir = Path(locale_dir)
    for loc in ctx.languages:
        if loc != ctx.languages[0]:
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
