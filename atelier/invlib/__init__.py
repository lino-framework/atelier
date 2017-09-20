# -*- coding: UTF-8 -*-
# Copyright 2016-2017 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.
"""An extensible library of `invoke
<http://docs.pyinvoke.org/en/latest/index.html>`__ tasks.
See :doc:`/invlib`.

.. autosummary::
   :toctree:

   dummy

"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from invoke import Collection
from unipath import Path

import atelier

def setup_from_tasks(
        self, globals_dict, main_package=None,
        settings_module_name=None, **kwargs):
    """This is the function you must call from your :xfile:`tasks.py` file
    in order to activate the tasks defined by atelier. 

    """
    if '__file__' not in globals_dict:
        raise Exception(
            "No '__file__' in %r. "
            "First parameter to must be `globals()`" % globals_dict)

    tasks = Path(globals_dict['__file__'])
    if not tasks.exists():
        raise Exception("No such file: %s" % tasks)
    root_dir = tasks.parent.absolute()
    configs = {
        'root_dir': root_dir,
        'main_package': main_package,
        'locale_dir': None,
        'help_texts_source': None,
        'help_texts_module': None,
        'tolerate_sphinx_warnings': False,
        'cleanable_files': [],
        'revision_control_system': None,
        'apidoc_exclude_pathnames': [],
        'project_name': tasks.parent.absolute().name,
        'editor_command': None,
        'coverage_command': 'setup.py test',
        'languages': None,
        'blog_root': root_dir.child('docs'),
        'long_date_format': "%Y%m%d (%A, %d %B %Y)",
        'sdist_dir': root_dir.child('dist'),
        'pypi_dir': root_dir.child('.pypi_cache'),
    }

    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        from django.conf import settings
        self.configure({
            'languages': [lng.name for lng in settings.SITE.languages]})

    configs.setdefault(
        'build_dir_name', '.build')  # but ablog needs '_build'
    configs.setdefault('use_dirhtml', False)

    # # The following import will populate the projects
    from atelier.projects import get_project_info_tasks
    prj = get_project_info_tasks(root_dir)
    prj.load_tasks()

    # we cannot store current_project using configure() because it
    # cannot be pickled. And we don't need to store it there, it is
    # not a configuration value but just a global internal variable.
    atelier.current_project = prj
    
    self.main_package = main_package
    
    self.configure({'doc_trees': prj.doc_trees})
    self.configure(configs)
    if kwargs:
        self.configure(kwargs)
    # return _globals_dict


class MyCollection(Collection):
    
    def setup_from_tasks(self, *args, **kwargs):
        return setup_from_tasks(self, *args, **kwargs)

    @classmethod
    def from_module(cls, *args, **kwargs):
        """
        A hack needed to make it work as long as invoke does not yet
        support subclassing Collection
        (https://github.com/pyinvoke/invoke/pull/342)
        """
        
        ns = super(MyCollection, cls).from_module(*args, **kwargs)

        if ns.__class__ != cls:
            from functools import partial
            ns.setup_from_tasks = partial(setup_from_tasks, ns)
        return ns

