.. _atelier.invlib:

======================================
``inv`` tasks defined by atelier
======================================

.. _invoke: http://www.pyinvoke.org/

Installing the :mod:`atelier` package also installs the invoke_
package, which installs a command ``inv`` into your Python
environment.  This document describes the tasks and configuration
settings for invoke_ provided by atelier.

.. contents::
  :local:



How it works
=============

The ``inv`` command is a kind of make tool which works by looking for
a file named :xfile:`tasks.py`.  To activate the following subcommands
("tasks") for your project, you must create a file named
:file:`tasks.py` in your project's root directory with at least the
following two lines::

  from atelier.invlib.ns import ns
  ns.setup_from_tasks(globals())

.. xfile:: tasks.py

In your project's :xfile:`tasks.py` file you must define a variable
``ns`` which you usually import from :mod:`atelier.invlib`.

You can specify project-specific configuration settings directly in
your :xfile:`tasks.py` file. Example content::

    from atelier.tasks import ns
    ns.setup_from_tasks(globals(), "mypackage", 
        tolerate_sphinx_warnings=True,
        revision_control_system='git')

.. xfile:: .invoke.py

You can specify user-wide invoke settings in a file named
:xfile:`.invoke.py` which must be in your home directory.

You can also define system-wide default configuration files.  See the
`Invoke documentation
<http://docs.pyinvoke.org/en/latest/concepts/configuration.html>`_ for
more information.
           

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

.. command:: inv prep

    Prepare a test run. This runs :manage:`prep` on every demo project
    defined by :envvar:`demo_projects`.

    It is not launched automatically by :cmd:`inv test` or :cmd:`inv
    bd` because it can take some time and is not always necessary.

    

.. command:: inv test

    Run the test suite of this project.

    This is a shortcut for either ``python setup.py test`` or
    ``py.test`` (depending on whether your project has a
    :xfile:`pytest.ini` file or not.
    

.. command:: inv cov

    Run :envvar:`coverage_command` and create a `coverage
    <https://pypi.python.org/pypi/coverage>`_ report.

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


.. envvar:: srcref_url
            
    The URL template to use for `srcref`.
    
    If the project has a main package which has an attribute
    :envvar:`srcref_url`,
    then this value will be used.
    
.. envvar:: intersphinx_urls
            
    A dict which maps doctree names to the URL where they are published.
    This is used when this project's documentation is added to a
    doctree using :mod:`atelier.sphinxconf.interproject`.
    
    If the project has a main package which has an attribute
    :envvar:`intersphinx_urls`,
    then this value will be used.

.. envvar:: doc_trees

    A list of directory names (relative to your project directory)
    containing Sphinx document trees.
    Default value is ``['docs']``

    If the project has a main package which has an attribute
    :envvar:`doc_trees`,
    then this value will be used.

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

    The revision control system used by your project.  Allowed values
    are `'git'`, `'hg'` or `None`.  Used by :cmd:`inv ci`, :cmd:`inv
    release`, :cmd:`per_project`.

.. envvar:: use_mercurial

    **No longer used.** Use :envvar:`revision_control_system` instead.)


.. envvar:: demo_projects

    The list of *Django demo projects* included in this project.

    Django demo projects are used by the test suite and the Sphinx
    documentation.  Before running :cmd:`inv test` or :cmd:`inv bd`,
    they must have been initialized with :cmd:`inv prep`.


.. envvar:: prep_command

    The shell command to be run in every :envvar:`demo project
    <demo_projects>` when :cmd:`inv prep` is invoked.  The default
    value is ``manage.py prep --noinput --traceback``.
