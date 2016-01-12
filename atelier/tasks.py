# -*- coding: UTF-8 -*-
# Copyright 2013-2016 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.


import os
from  contextlib import contextmanager

from unipath import Path
from invoke import env, task
from invoke import run as local


@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)


def run_in_demo_projects(admin_cmd, *more):
    """Run the given shell command in each demo project (see
    :attr:`env.demo_projects`).

    """
    for mod in env.demo_projects:
        # puts("-" * 80)
        # puts("In demo project {0}:".format(mod))
        print("-" * 80)
        print("In demo project {0}:".format(mod))

        from importlib import import_module
        m = import_module(mod)
        args = ["django-admin.py"]
        args += [admin_cmd]
        args += more
        args += ["--settings=" + mod]
        cmd = " ".join(args)
        local(cmd)


@task(name='initdb')
def initdb_demo():
    run_in_demo_projects('initdb_demo', "--noinput", '--traceback')


@task(name='test')
def run_tests():
    """See :cmd:`fab test`. """
    if not env.root_dir.child('setup.py').exists():
        return
    local('python setup.py -q test')


def add_demo_project(p):
    """Register the specified settings module as being a Django demo project.
    See also :attr:`env.demo_projects`.

    """
    if p in env.demo_projects:
        return
        # raise Exception("Duplicate entry %r in demo_projects." % db)
    env.demo_projects.append(p)


def setup_from_tasks(
        globals_dict, main_package=None, settings_module_name=None):
    if not '__file__' in globals_dict:
        raise Exception(
            "No '__file__' in %r. "
            "First parameter to must be `globals()`" % globals_dict)

    tasks = Path(globals_dict['__file__'])
    if not tasks.exists():
        raise Exception("No such file: %s" % tasks)
    env.root_dir = tasks.parent.absolute()

    env.main_package = main_package
    env.locale_dir = None
    env.tolerate_sphinx_warnings = False
    env.demo_projects = []
    env.revision_control_system = None
    env.apidoc_exclude_pathnames = []
    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        from django.conf import settings
        # why was this? settings.SITE.startup()
        env.languages = [lng.name for lng in settings.SITE.languages]
