===================================
A collection of ``invoke`` commands
===================================

Atelier defines a collection of commands for `invoke
<http://www.pyinvoke.org/>`__ .  These commands are documented below.
To activate them for your project, you must create a file named
:file:`tasks.py` in your project's root directory with at least the
following two lines::

  from atelier.tasks import ns
  ns.setup_from_tasks(globals())

See Configuration_ for more information.


.. contents::
  :local:

.. _inv_commands:

``invoke`` commands
===================

Commands for documenting
------------------------

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

.. command:: inv bh

    No longer exists.

    Build :xfile:`help_texts.py` file for this project.
    
    Needs :attr:`env.help_texts_source` and :attr:`env.help_texts_module`.


.. command:: inv clean

    Remove temporary and generated files:

    - Sphinx `.build` files
    - Dangling `.pyc` files which don't have a corresponding `.py` file.
    - `cache` directories of demo projects
    - additional files specified in :attr:`env.cleanable_files`

.. command:: inv readme

    Generate or update `README.txt` or `README.rst` file from
    `SETUP_INFO`.

Commands for internationalization
---------------------------------

.. command:: inv mm

    ("make messages")

    Extracts messages from both code and userdocs, then initializes and
    updates all catalogs. Needs :attr:`env.locale_dir`

Commands for deployment
-----------------------

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

.. command:: inv release

    Write a source distribution archive to your :attr:`env.sdist_dir`,
    then upload it to PyPI.  Create a version tag if
    :attr:`env.revision_control_system` is ``'git'``.

    This command will fail if this project has previously been
    released with the same version.


.. command:: inv sdist

    Write a source distribution archive to your :attr:`env.sdist_dir`.




Commands for testing
--------------------

.. command:: inv initdb

    Run :manage:`initdb_demo` on every demo project
    :attr:`env.demo_projects`.

.. command:: inv test

    See :func:`run_tests`.

.. command:: inv cov

    Run all tests and create a `coverage
    <https://pypi.python.org/pypi/coverage>`_ report


Commands for project management
-------------------------------

.. command:: inv ls

    List all your projects.




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
    ns.setup_from_tasks(globals(), "lino")
    ns.configure(dict(languages="en de fr et nl".split()))


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


Project settings
================

The following section documents the possible settings used by
:mod:`atelier.invlib` to be defined in your :xfile:`invoke.yaml`.

.. class:: inv

  .. attribute:: locale_dir

    The name of the directory where `inv mm` et al should write their
    catalog files.

  .. attribute:: sdist_dir


  .. attribute:: editor_command

    A string with the command name of your text editor. Example::

      editor_command = "emacsclient -n {0}"

    The ``{0}`` will be replaced by the filename.

    Note that this must be a *non waiting* command, i.e. which
    launches the editor on the specified file in a new window and then
    returns control to the command line without waiting for that new
    window to terminate.



  .. attribute:: docs_rsync_dest

    A Python template string which defines the rsync destination for
    publishing your projects documentation.
    Used by :cmd:`fab pub`.

    Example::

      env.docs_rsync_dest = 'luc@example.org:~/public_html/{prj}_{docs}'

    The ``{prj}`` in this template will be replaced by the internal
    name of this project, and ``{{docs}}`` by the name of the doctree
    (taken from :attr:`doc_trees`).

    For backward compatibility the following (deprecated) template is
    also still allowed::

      env.docs_rsync_dest = 'luc@example.org:~/public_html/%s'

    The ``%s`` in this template will be replaced by a name `xxx_yyy`,
    where `xxx` is the internal name of this project and `yyy` the
    name of the doctree (taken from :attr:`doc_trees`).


  .. attribute:: doc_trees

    A list of directory names (relative to your project directory)
    containing Sphinx document trees.
    Default value is ``['docs']``

    If this project has a main package, then `env.doc_trees` will be
    replaced by `doc_trees` attribute of that module.

  .. attribute:: cleanable_files

    A list of wildcards to be cleaned by :cmd:`inv clean`.

  .. attribute:: use_dirhtml

    Whether `sphinx-build
    <http://sphinx-doc.org/invocation.html#invocation-of-sphinx-build>`__
    should use ``dirhtml`` instead of the default ``html`` builder.

  .. attribute:: tolerate_sphinx_warnings

    Whether `sphinx-build` should tolerate warnings.

  .. attribute:: languages

    A list of language codes for which userdocs are being maintained.

  .. attribute:: apidoc_exclude_pathnames

    No longer used because we now use autosummary instead of
    sphinx-apidoc.

    a list of filenames (or directory names) to be excluded when you
    run :cmd:`fab api`.

  .. attribute:: revision_control_system

    The revision control system used by your project.
    Allowed values are `'git'`, `'hg'` or `None`.
    Used by :cmd:`inv ci`.

  .. attribute:: use_mercurial

    **No longer used.** Use :attr:`env.revision_control_system` instead.)

  .. attribute:: demo_projects

    The list of *Django demo projects* included in this project.

    Django demo projects are used by the test suite and the Sphinx
    documentation.  Before running :command:`inv test` or
    :command:`inv bd`, they must have been initialized.  To initialize
    them, run :command:`inv initdb`.

    It is not launched automatically by :command:`inv test` or
    :command:`inv bd` because it can take some time and is not always
    necessary.


