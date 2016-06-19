# -*- coding: UTF-8 -*-
# Copyright 2013-2016 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.

"""A library for `invoke <http://www.pyinvoke.org/>`__ with tasks I use
to manage my Python projects.

See :doc:`/invlib`

"""

from __future__ import print_function
from __future__ import unicode_literals

from importlib import import_module
import os
from contextlib import contextmanager
import glob
import datetime

from builtins import str
from builtins import object
from atelier.utils import i2d
from babel.dates import format_date
from atelier import rstgen
from unipath import Path
try:
    from invoke import ctask as task
    # before version 0.13 (see http://www.pyinvoke.org/changelog.html)
except ImportError:
    from invoke import task

from invoke import run

import atelier
from atelier.utils import confirm
from .projects import get_setup_info


def local(*args, **kwargs):
    """Call :func:`invoke.run` with `pty=True
    <http://www.pyinvoke.org/faq.html#why-is-my-command-behaving-differently-under-invoke-versus-being-run-by-hand>`_.

    This is usefule e.g. to get colors in a terminal.

    """
    kwargs.update(pty=True)
    run(*args, **kwargs)


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
    if atelier.current_project.module is not None:
        p = Path(atelier.current_project.module.__file__).parent
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

    atelier.current_project.load_tasks()
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
""" % atelier.current_project.SETUP_INFO
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
def run_tests_coverage(ctx, html=False, html_cov_dir='htmlcov'):
    """Run all tests and create a coverage report.

    If there a directory named :xfile:`htmlcov` in your project's
    `root_dir`, then it will write a html report into this directory
    (overwriting any files without confirmation).

    """
    if True:
        SETUP_INFO = get_setup_info(ctx.root_dir)
        if 'test_suite' not in SETUP_INFO:
            raise Exception("No `test_suite` in your `setup.py`.")
        test_suite = ctx.root_dir.child(SETUP_INFO['test_suite'])
    else:
        test_suite = ctx.root_dir

    covfile = ctx.root_dir.child('.coveragerc')
    if not covfile.exists():
        raise Exception('There is no file {0}'.format(covfile))
    import coverage
    # ~ clean_sys_path()
    # print("Running tests for '%s' within coverage..." % ctx.project_name)
    print("Running tests in '%s' within coverage..." % test_suite)
    # ~ ctx.DOCSDIR.chdir()
    os.environ['COVERAGE_PROCESS_START'] = covfile
    # cov = coverage.coverage()
    # cov.start()
    # import unittest
    # tests = unittest.TestLoader().discover(test_suite)
    # unittest.TextTestRunner(verbosity=1).run(tests)
    # cov.stop()
    # cov.save()
    # cov.combine()
    # cov.report()
    # htmlcov = ctx.root_dir.child('htmlcov')
    # if htmlcov.exists():
    #     print("Writing html report to %s" % htmlcov)
    #     cov.html_report(include=cov.get_data().measured_files())
    # cov.erase()
    local('coverage erase')
    local('coverage run setup.py test')
    local('coverage combine')
    local('coverage report')
    if html:
        print("Writing html report to %s" % html_cov_dir)
        local('coverage html -d {html_cov_dir} && open {html_cov_dir}/index.html'.format(html_cov_dir=html_cov_dir))
        print('html report is ready.')
    local('coverage erase')


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
        if ctx.languages is None:
            txt = today.strftime(ctx.long_date_format)
        else:
            txt = format_date(
                today, format='full', locale=ctx.languages[0])
        content = rstgen.header(1, txt)
        content = ":date: {0}\n\n".format(today) + content
        msg = "{0}\nCreate file {1}?".format(content, entry.path)
        if not confirm(msg):
            return
        # for every year we create a new directory.
        yd = entry.path.parent
        if not yd.exists():
            if not confirm("Happy New Year! Create directory %s?" % yd):
                return
            yd.mkdir()
            txt = ".. blogger_year::\n"
            yd.child('index.rst').write_file(txt.encode('utf-8'))

        entry.path.write_file(content.encode('utf-8'))
        # touch it for Sphinx:
        entry.path.parent.child('index.rst').set_times()
    args = [ctx.editor_command.format(entry.path)]
    args += [entry.path]
    # raise Exception("20160324 %s", args)
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
        # must_confirm("%s> %s" % (build_dir, cmd))
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

