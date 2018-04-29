# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.
"""
A library of `invoke
<http://docs.pyinvoke.org/en/latest/index.html>`__ tasks.  See
:doc:`/invlib`.

.. autosummary::
   :toctree:

   tasks
   utils
"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os

# from importlib import import_module
from invoke import Collection
from unipath import Path

import atelier


def setup_from_tasks(
    globals_dict, main_package=None,
    settings_module_name=None, **kwargs):
    """
    This is the function you must call from your :xfile:`tasks.py` file
    in order to activate the tasks defined by atelier.
    """
    from atelier.invlib import tasks
    self = Collection.from_module(tasks)
    if '__file__' not in globals_dict:
        raise Exception(
            "No '__file__' in %r. "
            "First parameter to must be `globals()`" % globals_dict)

    tasks_file = Path(globals_dict['__file__'])
    if not tasks_file.exists():
        raise Exception("No such file: %s" % tasks_file)
    root_dir = tasks_file.parent.absolute()
    # print("20180428 setup_from_tasks() : {}".format(root_dir))
    
    # self.main_package = main_package
    # pp = os.environ.get('VIRTUAL_ENV') + '/bin/per_project'
    configs = {
        'root_dir': root_dir,
        'locale_dir': None,
        'help_texts_source': None,
        'help_texts_module': None,
        'tolerate_sphinx_warnings': False,
        'cleanable_files': [],
        'revision_control_system': None,
        'apidoc_exclude_pathnames': [],
        'project_name': tasks_file.parent.absolute().name,
        'editor_command': None,
        'demo_projects': [],
        'prep_command': "manage.py prep --noinput --traceback",
        # 'coverage_command': '{} inv prep test clean --batch bd'.format(pp),
        'coverage_command': '`which invoke` prep test clean --batch bd',
        'languages': None,
        'blog_root': root_dir.child('docs'),
        'long_date_format': "%Y%m%d (%A, %d %B %Y)",
        'sdist_dir': root_dir.child('dist'),
        'pypi_dir': root_dir.child('.pypi_cache'),
        'use_dirhtml': False,
    }
    
    if main_package:
        configs.update(main_package=main_package)
    else:
        configs.update(doc_trees=['docs'])
    # else:
    #     m = import_module(main_package)
    #     for k in ('srcref_url', 'doc_trees', 'intersphinx_urls'):
    #         v = getattr(m, k, None)
    #         if v is not None:
    #             configs[k] = v

    if kwargs:
        configs.update(kwargs)
        
    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        from django.conf import settings
        configs.update(
            languages=[lng.name for lng in settings.SITE.languages])

    configs.setdefault(
        'build_dir_name', '.build')  # but ablog needs '_build'

    self.configure(configs)
    
    # The following import will populate the projects
    from atelier.projects import get_project_info_from_path
    prj = get_project_info_from_path(root_dir, self)
    # 20180428 prj.load_tasks()
    # prj.inv_namespace = self

    # we cannot store current_project using configure() because it
    # cannot be pickled. And we don't need to store it there, it is
    # not a configuration value but just a global internal variable.
    atelier.current_project = prj
    # configs.update(project=prj)
    
    # if prj.doc_trees is not None:
    #     configs.setdefault('doc_trees', prj.doc_trees)
    # return _globals_dict

    # doc_trees = configs.get('doc_trees', prj.doc_trees)
    # if not doc_trees:
    #     if root_dir.child('docs').exists():
    #         msg = "20180428 {} exists but doc_trees is empty"
    #         raise Exception(msg.format(root_dir.child('docs')))

    return self

# class MyCollection(Collection):
    
#     def setup_from_tasks(self, *args, **kwargs):
#         return setup_from_tasks(self, *args, **kwargs)

#     @classmethod
#     def from_module(cls, *args, **kwargs):
#         """
#         A hack needed to make it work as long as invoke does not yet
#         support subclassing Collection
#         (https://github.com/pyinvoke/invoke/pull/342)
#         """
        
#         ns = super(MyCollection, cls).from_module(*args, **kwargs)

#         if ns.__class__ != cls:
#             from functools import partial
#             ns.setup_from_tasks = partial(setup_from_tasks, ns)
#         return ns

