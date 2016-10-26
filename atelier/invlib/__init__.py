# -*- coding: UTF-8 -*-
# Copyright 2016 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.
"""An extensible library of `invoke
<http://docs.pyinvoke.org/en/latest/index.html>`__ tasks.


Tasks
=====
    

Commands for documenting
------------------------

.. command:: inv blog

    Edit today's blog entry, create an empty file if it doesn't yet exist.

.. command:: inv bd

    Build docs. Build all Sphinx HTML doctrees for this project.

    This runs :cmd:`invoke readme`, followed by `sphinx-build html` in
    every directory defined in :envvar:`doc_trees`.  The exact
    options for `sphinx-build` depend also on
    :envvar:`tolerate_sphinx_warnings` and :envvar:`use_dirhtml`.

.. command:: inv pd

    Publish docs. Upload docs to public web server.

.. command:: inv bh

    No longer exists.

    Build :xfile:`help_texts.py` file for this project.
    
    Needs :envvar:`help_texts_source` and :envvar:`help_texts_module`.


.. command:: inv clean

    Remove temporary and generated files:

    - Sphinx `.build` files
    - Dangling `.pyc` files which don't have a corresponding `.py` file.
    - `cache` directories of demo projects
    - additional files specified in :envvar:`cleanable_files`

    Unless option ``--batch`` is specified, ask for an interactive
    user confirmation before removing these files.

.. command:: inv readme

    Generate or update `README.txt` or `README.rst` file from
    `SETUP_INFO`.

Commands for internationalization
---------------------------------

.. command:: inv mm

    ("make messages")

    Extracts messages from both code and userdocs, then initializes and
    updates all catalogs. Needs :envvar:`locale_dir`

Commands for deployment
-----------------------

.. command:: inv ci

    Checkin and push to repository, using today's blog entry as commit
    message.

    Asks confirmation before doing so.

    Does nothing in a project whose
    :envvar:`revision_control_system` is `None`.

    In a project whose :envvar:`revision_control_system` is
    ``'git'`` it checks whether the repository is dirty (i.e. has
    uncommitted changes) and returns without asking confirmation if
    the repo is clean.  Note that unlike ``git status``, this check
    does currently not (yet) check whether my branch is up-to-date
    with 'origin/master'.

.. command:: inv reg

    Register this project (and its current version) to PyPI.

.. command:: inv release

    Write a source distribution archive to your :envvar:`sdist_dir`,
    then upload it to PyPI.  Create a version tag if
    :envvar:`revision_control_system` is ``'git'``.

    This command will fail if this project has previously been
    released with the same version.


.. command:: inv sdist

    Write a source distribution archive to your :envvar:`sdist_dir`.



Commands for testing
--------------------

.. command:: inv test

    Run the test suite of this project.

    This is a shortcut for either ``python setup.py test`` or
    ``py.test`` (depending on whether your project has a
    :xfile:`pytest.ini` file or not.
    

.. command:: inv cov

    Run :envvar:`coverage_command` and create a `coverage
    <https://pypi.python.org/pypi/coverage>`_ report

.. command:: inv test_sdist

    Creates and activates a temporay virtualenv, installs your project
    and runs your test suite.
        
    - creates and activates a temporay virtualenv,
    - calls ``pip install --no-index -f <env.sdist_dir> <prjname>``
    - runs ``python setup.py test``
    - removes temporary files.
    
    Assumes that you previously did :cmd:`inv sdist` of all your
    projects related to this project.


Usage
=====

To activate them for your project, you must create a file named
:file:`tasks.py` in your project's root directory with at least the
following two lines::

  from atelier.invlib.ns import ns
  ns.setup_from_tasks(globals())


Configuration
=============

The details are matter of taste, but you must at least define a
:xfile:`tasks.py` file and optionally an :xfile:`invoke.yaml` file.
You can define also user-specific or system-wide default configuration
files.  See the `Invoke documentation
<http://docs.pyinvoke.org/en/latest/concepts/configuration.html>`_ for
more information.

.. xfile:: tasks.py

In your :xfile:`tasks.py` file you must define a variable ``ns`` which
you usually import from :mod:`atelier.tasks`.

You can specify project-specific configuration settings directly in
your :xfile:`tasks.py` file. Example content::

    from atelier.tasks import ns
    ns.setup_from_tasks(globals(), "lino", 
        languages="en de fr et nl".split())


.. xfile:: invoke.yaml

Optionally you can specify project-specific configuration settings in
a separate file named :xfile:`invoke.yaml`.  Example content::

    tolerate_sphinx_warnings: true
    blogref_url: http://luc.lino-framework.org
    revision_control_system: git
    locale_dir: lino/modlib/lino_startup/locale

    cleanable_files:
     - docs/api/lino.*

    demo_projects:
        - lino.projects.docs.settings.demo
        - lino.projects.belref.settings.demo
        - lino.projects.polly.settings.demo
        - lino.projects.events.settings



Configuration settings
======================

This lists the settings available in your :xfile:`tasks.py` when it
uses :mod:`atelier.invlib`.

.. envvar:: locale_dir

    The name of the directory where `inv mm` et al should write their
    catalog files.

.. envvar:: sdist_dir

.. envvar:: pypi_dir

.. envvar:: coverage_command

    The command to run for measuring coverage by :cmd:`inv cov`.
    
.. envvar:: editor_command

    A string with the command name of your text editor. Example::

      editor_command = "emacsclient -n {0}"

    The ``{0}`` will be replaced by the filename.

    Used by :cmd:`inv blog`.

    Note that this must be a *non waiting* command, i.e. which
    launches the editor on the specified file in a new window and then
    returns control to the command line without waiting for that new
    window to terminate.



.. envvar:: docs_rsync_dest

    A Python template string which defines the rsync destination for
    publishing your projects documentation.
    Used by :cmd:`fab pub`.

    Example::

      env.docs_rsync_dest = 'luc@example.org:~/public_html/{prj}_{docs}'

    The ``{prj}`` in this template will be replaced by the internal
    name of this project, and ``{{docs}}`` by the name of the doctree
    (taken from :envvar:`doc_trees`).

    For backward compatibility the following (deprecated) template is
    also still allowed::

      env.docs_rsync_dest = 'luc@example.org:~/public_html/%s'

    The ``%s`` in this template will be replaced by a name `xxx_yyy`,
    where `xxx` is the internal name of this project and `yyy` the
    name of the doctree (taken from :envvar:`doc_trees`).


.. envvar:: doc_trees

    A list of directory names (relative to your project directory)
    containing Sphinx document trees.
    Default value is ``['docs']``

    If this project has a main package, then `env.doc_trees` will be
    replaced by `doc_trees` attribute of that module.

.. envvar:: cleanable_files

    A list of wildcards to be cleaned by :cmd:`inv clean`.

  .. attribute:: use_dirhtml

    Whether `sphinx-build
    <http://sphinx-doc.org/invocation.html#invocation-of-sphinx-build>`__
    should use ``dirhtml`` instead of the default ``html`` builder.

.. envvar:: tolerate_sphinx_warnings

    Whether `sphinx-build` should tolerate warnings.

.. envvar:: languages

    A list of language codes for which userdocs are being maintained.

.. envvar:: apidoc_exclude_pathnames

    No longer used because we now use autosummary instead of
    sphinx-apidoc.

    a list of filenames (or directory names) to be excluded when you
    run :cmd:`fab api`.

.. envvar:: revision_control_system

    The revision control system used by your project.
    Allowed values are `'git'`, `'hg'` or `None`.
    Used by :cmd:`inv ci`.

.. envvar:: use_mercurial

    **No longer used.** Use :envvar:`revision_control_system` instead.)


Modules
=======


.. autosummary::
   :toctree:

   ns
   tasks
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
    
    self.configure({'doc_trees': prj.doc_trees})
    self.configure({
        # 'main_package': main_package,
        'doc_trees': prj.doc_trees})
    self.configure(configs)
    self.main_package = main_package
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

