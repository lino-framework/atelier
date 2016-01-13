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


Testing
-------

.. command:: invoke initdb

    Run :manage:`initdb_demo` on every demo :attr:`env.demo_projects`.

.. command:: invoke test

    See :func:`run_tests`.



"""


from __future__ import print_function

import os
from contextlib import contextmanager
import glob
# from importlib import import_module

from unipath import Path
from invoke import task
from invoke import run as local
from atelier.utils import confirm, AttrDict


@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)


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
            root_dir = tasks.parent.absolute(),
            main_package = main_package,
            locale_dir = None,
            tolerate_sphinx_warnings = False,
            demo_projects = [],
            revision_control_system = None,
            apidoc_exclude_pathnames = [])

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

    env.current_project.load_fabfile()
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
    """See :cmd:`fab bd`. """
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
    """See :cmd:`fab clean`. """
    env.sphinx_clean()
    env.py_clean()
    # clean_demo_caches()
