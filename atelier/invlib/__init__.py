# -*- coding: UTF-8 -*-
# Copyright 2016-2020 Rumma & Ko Ltd
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

import os

from importlib import import_module
from invoke import Collection
from pathlib import Path

import atelier


def setup_from_tasks(
    globals_dict, main_package=None,
    settings_module_name=None, **kwargs):
    """
    This is the function you must call from your :xfile:`tasks.py` file
    in order to activate the tasks defined by atelier.

    Arguments:

    - `globals_dict` must be the `globals()` of the calling script.

    - Optional `main_package` is the name of the main Python package provided by
      this project.

    - Optional `settings_module_name` will be stored in the
      :envvar:`DJANGO_SETTINGS_MODULE`, and certain project configuration
      options will get their default value from that module.

    - All remaining keyword arguments are project configuration parameters and
      stored to the :ref:`project configuration options <atelier.prjconf>`.

    """
    if '__file__' not in globals_dict:
        raise Exception(
            "No '__file__' in %r. "
            "First argument to setup_from_tasks() must be `globals()`." % globals_dict)

    tasks_file = Path(globals_dict['__file__'])
    if not tasks_file.exists():
        raise Exception("No such file: %s" % tasks_file)
    # print("20180428 setup_from_tasks() : {}".format(root_dir))

    from atelier.invlib import tasks
    from atelier.projects import get_project_from_tasks
    prj = get_project_from_tasks(tasks_file.parent)

    if atelier.current_project is None:
        atelier.current_project = prj

    if kwargs:
        prj.config.update(kwargs)

    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        from django.conf import settings
        prj.config.update(
            languages=[lng.name for lng in settings.SITE.languages])

    if isinstance(main_package, str):
        main_package = import_module(main_package)
    if main_package:
        prj.set_main_package(main_package)

    self = Collection.from_module(tasks)
    prj.set_namespace(self)

    return self
