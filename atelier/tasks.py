# -*- coding: UTF-8 -*-
# Copyright 2016 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.

""""""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from invoke import Collection
from unipath import Path

import atelier
from . import invlib


def setup_from_tasks(
        self, globals_dict, main_package=None,
        settings_module_name=None, **kwargs):
    """This is the function you must call from your :xfile:`tasks.py` file
    in order to use atelier. See :doc:`/usage`.

    """
    if '__file__' not in globals_dict:
        raise Exception(
            "No '__file__' in %r. "
            "First parameter to must be `globals()`" % globals_dict)

    tasks = Path(globals_dict['__file__'])
    if not tasks.exists():
        raise Exception("No such file: %s" % tasks)
    root_dir = tasks.parent.absolute()
    _globals_dict = {
        'root_dir': root_dir,
        'main_package': main_package,
        'locale_dir': None,
        'help_texts_source': None,
        'help_texts_module': None,
        'tolerate_sphinx_warnings': False,
        'demo_projects': [],
        'cleanable_files': [],
        'revision_control_system': None,
        'apidoc_exclude_pathnames': [],
        'project_name': tasks.parent.absolute().name,
        'editor_command': None,
        'languages': None,
        'blog_root': root_dir.child('docs'),
        'long_date_format': "%Y%m%d (%A, %d %B %Y)",
    }

    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        from django.conf import settings
        # why was this? settings.SITE.startup()
        self.configure({
            'languages': [lng.name for lng in settings.SITE.languages]})

    _globals_dict.setdefault(
        'build_dir_name', '.build')  # but ablog needs '_build'
    _globals_dict.setdefault('use_dirhtml', False)

    # # The following import will populate the projects
    from atelier.projects import get_project_info_tasks
    prj = get_project_info_tasks(root_dir)
    prj.load_tasks()

    # we cannot store current_project using configure() because it
    # cannot be pickled. And we don't need to store it there, it is
    # not a configuration value but just a global internal variable.
    # self.configure({ 'current_project': prj})
    atelier.current_project = prj
    self.configure({'doc_trees': prj.doc_trees})
    self.configure({
        # 'main_package': main_package,
        'doc_trees': prj.doc_trees})
    self.configure(_globals_dict)
    self.main_package = main_package
    if kwargs:
        self.configure(kwargs)
    return _globals_dict


class MyCollection(Collection):
    
    def setup_from_tasks(self, *args, **kwargs):
        return setup_from_tasks(self, *args, **kwargs)


ns = MyCollection.from_module(invlib)

# The following hack is to make it work as long as invoke does not yet
# support subclassing Collection
# (https://github.com/pyinvoke/invoke/pull/342)
# 

if ns.__class__ != MyCollection:
    from functools import partial
    ns.setup_from_tasks = partial(setup_from_tasks, ns)
