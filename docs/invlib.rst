.. _atelier.invlib:

======================================
``inv`` tasks defined by atelier
======================================

This document describes the tasks and configuration settings for :cmd:`inv`
provided by atelier.

.. contents::
  :local:


Note: code examples in this document use the atelier project

>>> from atelier.projects import get_project_info_from_mod
>>> prj = get_project_info_from_mod('atelier')

Tasks
=====

Following are the tasks you get when you import :mod:`atelier.invlib`
into your :xfile:`tasks.py` file.


Commands for documenting
------------------------

.. command:: inv bd

    Build docs. Build all Sphinx HTML doctrees for this project.

    This runs :cmd:`inv readme`, followed by `sphinx-build html` in
    every directory defined in :envvar:`doc_trees`.  The exact options
    for `sphinx-build` depend also on
    :envvar:`tolerate_sphinx_warnings` and :envvar:`use_dirhtml`.

.. command:: inv pd

    Publish docs. Upload docs to public web server.

.. command:: inv blog

    Edit today's blog entry, create an empty file if it doesn't yet exist.

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

.. command:: inv sdist

    Write a source distribution archive to your :envvar:`sdist_dir`.

.. command:: inv release

    Upload the source distribution archive previously created by
    :cmd:`inv sdist` to PyPI, i.e. publish an official version of your
    package.

    Before doing anything, it shows the status of your local
    repository (which should be clean) and a summary of the project
    status on PyPI.  It then asks a confirmation.  The release will
    fail if the project has previously been published on PyPI with the
    same version.

    If :envvar:`revision_control_system` is ``'git'``, create and push a
    version branch "vX.Y.Z".  This step can be skipped by specifying
    ``--nobranch``.

    This command requires that `twine
    <https://pypi.python.org/pypi/twine>`_ is installed.


Commands for testing
--------------------

.. command:: inv install

    Install Python requirements.  Runs :manage:`install` on every demo
    project defined by :envvar:`demo_projects`.

.. command:: inv prep

    Prepare a test run. This runs :manage:`prep` on every demo project
    defined by :envvar:`demo_projects`.

    It is not launched automatically by :cmd:`inv test` or :cmd:`inv
    bd` because it can take some time and is not always necessary.



.. command:: inv test

    Run the test suite of this project.

    This is a shortcut for either ``python setup.py test`` or
    ``py.test`` or `` tox`` (depending on whether your project has a
    :xfile:`pytest.ini` or :xfile:`tox.ini` files or not and  ).


.. command:: inv cov

    Create a `coverage <https://pypi.python.org/pypi/coverage>`_ report.

    You can configure the command to use by setting :envvar:`coverage_command`.

.. command:: inv test_sdist

    Creates and activates a temporay virtualenv, installs your project
    and runs your test suite.

    - creates and activates a temporay virtualenv,
    - calls ``pip install --no-index -f <env.sdist_dir> <prjname>``
    - runs ``python setup.py test``
    - removes temporary files.

    Assumes that you previously did :cmd:`inv sdist` of all your
    projects related to this project.


Miscellaneous commands
----------------------

.. command:: inv clean

    Remove temporary and generated files:

    - Sphinx `.build` files
    - Dangling `.pyc` files which don't have a corresponding `.py` file.
    - `cache` directories of demo projects
    - additional files specified in :envvar:`cleanable_files`

    Unless option ``--batch`` is specified, ask for an interactive
    user confirmation before removing these files.

.. command:: inv ct

    Display a list of commits in all projects during the last 24
    hours.



Configuration settings
======================

This lists the settings available in your :xfile:`tasks.py` when it
uses :mod:`atelier.invlib`.

.. envvar:: locale_dir

    The name of the directory where `inv mm` et al should write their
    catalog files.

.. envvar:: sdist_dir

    The template for the local directory where :cmd:`inv sdist` should
    store the packages.  Any string ``{prj}`` in this template will be
    replaced by the projects Python name.  The resulting string is
    passed as the `--dist-dir` option to the :cmd:`setup.py sdist`
    command.

.. envvar:: pypi_dir

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


.. envvar:: srcref_url

    The URL template to use for `srcref`.

    If the project has a main package which has an attribute
    :envvar:`srcref_url`,
    then this value will be used.

.. envvar:: intersphinx_urls

    A dict which maps doctree names to the URL where they are published.
    This is used when this project's documentation is added to a
    doctree using :mod:`atelier.sphinxconf.interproject`.

    If the project has a main package which defines an attribute
    :envvar:`intersphinx_urls`,
    then this will override any value define in :xfile:`tasks.py`.

.. envvar:: doc_trees

    A list of directory names (relative to your project directory)
    containing Sphinx document trees.

    Default value is ``['docs']``

    >>> prj.get_xconfig('doc_trees')
    ['docs']

    If the project has a main package which defines an attribute
    :envvar:`doc_trees`,
    then this will override any value define in :xfile:`tasks.py`.

.. envvar:: cleanable_files

    A list of wildcards to be cleaned by :cmd:`inv clean`.

.. envvar:: use_dirhtml

    Whether `sphinx-build
    <http://sphinx-doc.org/invocation.html#invocation-of-sphinx-build>`__
    should use ``dirhtml`` instead of the default ``html`` builder.

.. envvar:: tolerate_sphinx_warnings

    Whether `sphinx-build` should tolerate warnings.

.. envvar:: languages

    A list of language codes for which userdocs are being maintained.

.. envvar:: revision_control_system

    The revision control system used by your project.  Allowed values
    are `'git'`, `'hg'` or `None`.  Used by :cmd:`inv ci`, :cmd:`inv
    release`, :cmd:`per_project`.

.. envvar:: use_mercurial

    **No longer used.** Use :envvar:`revision_control_system` instead.)


.. envvar:: demo_projects

    The list of *Django demo projects* included in this project.

    Every item of this list is the full Python path of a package which
    must have a :xfile:`manage.py` file.

    Django demo projects are used by the test suite and the Sphinx
    documentation.  Before running :cmd:`inv test` or :cmd:`inv bd`,
    they must have been initialized with :cmd:`inv prep`.

.. envvar:: prep_command

    A shell command to be run in in the project's root directory when :cmd:`inv
    prep` is invoked.  The default value is empty.

    Default value is empty.

    >>> prj.get_xconfig('prep_command')
    ''

.. envvar:: demo_prep_command

    A shell command to be run in every :envvar:`demo project <demo_projects>`
    when :cmd:`inv prep` is invoked.  The default value is ``manage.py prep
    --noinput --traceback``.

    Default value is empty.

    >>> prj.get_xconfig('demo_prep_command')
    'manage.py prep --noinput --traceback'

.. envvar:: test_command

    The command to be run by :cmd:`inv test`.

    Default value is ``unit2 discover -s tests``.

    >>> prj.get_xconfig('test_command')
    'unit2 discover -s tests'

.. envvar:: coverage_command

    The command to be run under coverage by :cmd:`inv cov`.

    Default value runs :cmd:`inv prep`, then :cmd:`inv test` then :cmd:`inv clean -b`
    and finally :cmd:`inv bd`.

    >>> prj.get_xconfig('coverage_command')
    '`which invoke` prep test clean --batch bd'
