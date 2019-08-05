.. _atelier.changes:

=======================
Changes in `atelier`
=======================

2019-08-05
==========

We have now two config settings for :cmd:`inv prep`: :envvar:`prep_command` and
:envvar:`demo_prep_command`. :envvar:`demo_prep_command` is what
:envvar:`prep_command` was until now (i.e. a command to run in every demo
project). :envvar:`prep_command` (default empty) is now a command to run in the
project's root directory.  Used by :ref:`getlino`. Both settings are meant to be
customized in the projects :xfile:`tasks.py` file.

Released version 1.1.14.


2019-08-02
==========

The :cmd:`pp -l` command no longer shows the doctrees. If you want to see them,
change ``SHOW_DOCTREES`` in :mod:`atelier.projects` to `True`. Showing the
doctrees causes the command to need about 7 seconds instead of one second (in my
environment) because it also imports the :xfile:`conf.py` file of every doctree.

2019-08-01
==========

Renamed ```inv configure`` to :cmd:`inv install`

2019-07-29
==========

The default value for the :envvar:`editor_command` setting is now taken from
the :envvar:`EDITOR` environment variable.

2019-07-20
==========

Added a new command ``inv configure`` (which later became :cmd:`inv install`).

Released version 1.1.13.


2019-07-01
==========

The :cmd:`inv release` command no longer creates a version branch by default.
If you want a branch, you must now say ``--branch``.

2019-06-07
==========

Added support for multilingual Sphinx sites. When the :xfile:`conf.py` file of
a Sphinx doctree defines a variable :attr:`translated_languages` (which is
expected to be a list of language codes), then :cmd:`inv mm` and :cmd:`inv bd`
now act accordingly.  This works only if you previously did ``pip install
sphinx-intl``. You should add yourself interlanguage links.  The simplest way
is to write a template :xfile:`languages.html` and add it to your
:attr:`html_sidebars`.

2019-03-07
==========

- :cmd:`per_project -l` now shows the title of each doctree

- interproject no longer stops loading after current project when no explicit
  project list is given.

2019-03-06
==========

Fixed a bug in :mod:`atelier.sphinxcontrib.interproject` which caused it to not
correctly set `intersphinx_mapping
<https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#confval-intersphinx_mapping>`__
when local builds are being used. Intersphinx data in builds of other local
projects is now being used by default if it exists.  To simulate the situation
on Travis where they never exist, set an environment variable
:envvar:`ATELIER_IGNORE_LOCAL_BUILDS` to the string "yes".


2019-02-12
==========

The ``notag`` option of :cmd:`inv release` was renamed to ``nobranch``.

2019-01-21
==========

Added a ``--reverse`` option to :command:`pp`.

You can now run a command in all projects in the reversed order of what is
defined in your :xfile:`~/.atelier/config.py`.

This is important if you maintain several projects whose docs use intersphinx
to refer to each other. In such a context you will use the ``--reverse`` option
for commands like :command:`inv bd` and :command:`inv pd`. You can then run a
full pp tour as follows::

    $ pp -rv inv clean -b bd pd
    $ pp inv prep test

Rule of thumb : project a must come before project b if

- code in a requires code in b to be installed
- docs in a require intersphinx references to docs of b


Version 1.1.12 (released 2018-11-24)
====================================

(20181124) The :envvar:`intersphinx_urls` can now be specified in
:xfile:`tasks.py` for projects without a :attr:`main_module`.

Version 1.1.11 (released 2018-11-05)
====================================

(20181105) changed the syntax of :envvar:`demo_projects`: instead of
specifying paths (relative to the project's :attr:`root_dir`) we now
specify them as Python modules.

(20181102) added an option --only (or -o) to :cmd:`inv bd` and
:cmd:`inv pd` because in book we have now already 4 doctrees and
sometimes you might want to build only one of them.

Version 1.1.10 (released 2018-10-29)
====================================

(20181029) The :cmd:`inv release` command now creates a *branch*
instead of a *tag* (:ticket:`2599` ).



Version 1.1.9 (released 2018-09-19)
===================================

(20180901) : The :cmd:`inv release` command now also pushes the
version tag.  Tag creation can be skipped by specifying the new
argument ``--notag``.

(20180821) Added support for Sphinx version is 1.8 or later.
:func:`atelier.sphinxconf.configure` now checks the Sphinx version and
sets the new `autodoc_default_options
<http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options>`__
configuration value instead of the deprecated `autodoc_default_flags
<http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html?highlight=autodoc_default_flags#confval-autodoc_default_flags>`__
(if Sphinx is 1.8 or newer).

The :cmd:`inv clean` command now also removes :xfile:`.eggs`
directories and :xfile:`__pycache__` directories.

The :class:`DjangoTemplateBridge` from :mod:`atelier.sphinxconf` was
not used and has been removed.

(20180806) : The context variable ``{prj}`` in :envvar:`sdist_dir`
must not be the :attr:`project_name
<atelier.projects.Project.project_name>` but ``SETUP_INFO['name']``.

(20180803) : :envvar:`sdist_dir` now supports a string template with a
single context variable: ``{prj}`` will be replaced by the
:attr:`project_name <atelier.projects.Project.project_name>`

:func:`atelier.invlib.tasks.show_pypi_status` has a new optional
argument `severe`.  Default value is True (same behaviour as before),
but the :cmd:`inv sdist` command now calls with `severe=False`.

(20180521) Bugfix: When the :xfile:`~/.atelier/config.py` file
contained an invalid project name (i.e. it calls
:func:`atelier.projects.add_project` with a `root_dir` that doesn't
exist), the project was being added to the list, but :cmd:`pp -l`
failed::

  AttributeError: 'NoneType' object has no attribute 'configuration'

Now this configuration error will already raise an exception when
reading the :xfile:`~/.atelier/config.py` file, making it easier to
localize.



Version 1.1.8 (released 2018-05-21)
===================================

(20180510) :func:`get_project_info_from_mod
<atelier.projects.get_project_info_from_mod>` didn't yet work in
environments without a local :xfile:`config.py` file.  Such projects
have neither a :xfile:`tasks.py` file not a :xfile:`setup.py` file,
but at least they have a :attr:`main_package
<atelier.projects.Project.main_package>` (and that's what `intersphinx
<http://www.sphinx-doc.org/en/master/ext/intersphinx.html>`__ needs).
This fixes :ticket:`2385` (intersphinx does not find the `objects.inv`
for :ref:`atelier` on Travis).


Version 1.1.7 (released 2018-05-04)
===================================

More internal optimizations.  Fixed a bug which caused problems in
:cmd:`per_project` with reading the configuration.


Version 1.1.6 (released 2018-05-02)
===================================

The test suite generated by :func:`atelier.test.make_docs_suite` is
now sorted alphabeticallly in order to avoid surprises when some
doctest inadvertantly modifies a demo database or some other
condition.

Fixed a bug in :xfile:`per_project`: commands starting with ``git``
(e.g. :cmd:`pp git st`) would fail with a traceback.

More internal optimizations, e.g. the :attr:`config` of a project now
always has all keys.


Version 1.1.5 (released 2018-04-30)
====================================

Fixes some bugs that caused failures when building docs on Travis.
Versions 1.1.0 through 1.1.4 were beta previews for this.

Backwards-incompatible new syntax for :xfile:`tasks.py` files:

Before::

    from atelier.invlib.ns import ns
    ns.setup_from_tasks(globals(), ...)

After::

    from atelier.invlib import setup_from_tasks
    ns = setup_from_tasks(globals(), ...)





Version 1.0.14 (released 2018-03-15)
====================================

- New function :func:`atelier.utils.isidentifier`


Version 1.0.13 (released 2017-12-17)
====================================

Better support for Python 2-3 compatible doctests:

- Added a new function :func:`atelier.utils.sixprint`.
- :func:`atelier.utils.rmu` now honors Mike Orr's :class:`unipath.Path`
  objects which happen to print differently under Python 3.


Version 1.0.12 (released 2017-10-11)
====================================

New optional parameter addenv for
:func:`atelier.test.make_docs_suite`.

Version 1.0.11 (released 2017-09-26)
====================================

Better Python 3 support and increased test coverage.

Version 1.0.10 (released 2017-09-22)
====================================

Version 1.0.9 wasn't enough: the default value for
:envvar:`prep_command` also needs to use :attr:`sys.executable`.

Version 1.0.9 (released 2017-09-22)
===================================

Several tasks in :mod:`atelier.invlib` used to call hard-coded
`python`, but on certain CI environments the Python executable has
another name. Replaced by :attr:`sys.executable`.

Version 1.0.8 (released 2017-09-20)
===================================

Changed configuration API for demo_projects: I moved the definition of
:envvar:`demo_projects` from Lino to :mod:`atelier.invlib` and changed
the syntax: the itema of :envvar:`demo_projects` must now be directory
names (and no longer names of Django settings modules).

Version 1.0.7 (released 2017-09-12)
===================================

DocTestCase removes PYTHONPATH from environment. Fixes #1296.


Version 1.0.6 (released 2017-06-07)
===================================

New functions :func:`atelier.utils.isiterable` and
:func:`atelier.utils.is_string`.


Version 1.0.5 (released 2017-02-16)
===================================

- Fixes some Python 3 issues.

Version 1.0.4 (released 2016-10-26)
===================================

- A minor but backwards-incompatible optimization of the modules below
  :mod:`atelier.invlib` requires changes in the :xfile:`tasks.py` file
  of every project which uses Atelier.

Version 1.0.3 (released 2016-08-31)
===================================

- The :cmd:`inv ls` command has been replaced by a ``--list`` option
  to :cmd:`per_project`.  (:blogref:`20160814`)

- :cmd:`inv sdist` now creates the archive file directly in
  `sdist_dir` and no longer in a subdir thereof (using the project
  name).

- Worked on :cmd:`inv cov`.


Version 1.0.2 (released 2016-07-16)
===================================

- Fixes :message:`TypeError: setup_from_tasks() got an unexpected
  keyword argument 'demo_projects'`. Thanks to Grigorij for reporting
  the problem.


Version 1.0.1 (released 2016-06-19)
===================================

- Support the new `pyinvoke <http://www.pyinvoke.org>`__ version 0.13
  (`released 10 days ago <http://www.pyinvoke.org/changelog.html>`_).
  :mod:`atelier.invlib` now works with both versions. Thanks to James
  for reporting problem and solution.


Version 1.0.0 (released 2016-03-25)
===================================

- First satisfying API and docs for :doc:`/invlib`

Version 0.0.20 (released 2016-03-24)
====================================

- Most :cmd:`fab` commands now work as :cmd:`inv`.
- Fixed a bug which caused :message:`TypeError:
  object.__new__(NotImplementedType) is not safe, use
  NotImplementedType.__new__()`

Version 0.0.19 (released 2016-03-08)
====================================

- New functions :func:`atelier.utils.dict_py2`,
  :func:`atelier.utils.list_py2` and :func:`atelier.utils.tuple_py2` are
  required for Lino's test suite.

Version 0.0.18 (released 2016-03-04)
====================================

- New function :func:`atelier.utils.last_day_of_month`.


Version 0.0.17 (released 2016-02-15)
====================================

- Subtle change in :attr:`docs_rsync_dest
  <atelier.fablib.env.docs_rsync_dest>`: until now it was not possible
  to specify a template without any placeholder (as the one in the
  example on https://github.com/lsaffre/dblog)

- Started to replace fabric by invoke. This is not finished. For the
  moment you should continue to use the ``fab`` commands. But soon
  they will be replaced by ``inv`` commands.


Version 0.0.16 (released 2015-12-04)
====================================

- :mod:`atelier.fablib` no longer tries to import
  `django.utils.importlib`. (Dropped support for Python 2.6)

- Fixed :ticket:`553`. The :cmd:`fab bd` command failed to call
  :meth:`load_fabfile <atelier.projects.Project.load_fabfile>` when
  trying to write the `README.rst` file. This didn't disturb anybody
  until now because I have a :xfile:`~/.atelier/config.py` file (and
  when you have such a file, all projects are automatically loaded,
  including :meth:`load_fabfile
  <atelier.projects.Project.load_fabfile>`.

- Fixed :ticket:`533`. :cmd:`fab bd` failed when the repository was in
  a directory using a symbolic link because Python got hassled when
  importing the main module. :mod:`atelier.projects` now resolves the
  `project_dir`.


Version 0.0.15 (released 2015-06-10)
====================================

New setting :attr:`atelier.fablib.env.locale_dir`. Until now
:command:`fab mm` always wrote the locale files into a subdirectory of
the main module. Now a project can specify an arbitrary location. This
was necessary for Django 1.7 where you cannot have plugins named
`foo.modlib.bar` if you also have a plugin whose full name is `foo`
(:blogref:`20150427`)

New function `atelier.rstgen.attrtable`.

Version 0.0.14 (released 2015-03-15)
====================================

Importing :mod:`atelier` now automatically adds a codecs writer to
`sys.stdout`.  As a consequence, :mod:`atelier.doctest_utf8` is no
longer needed.


Version 0.0.13 (released 2015-02-14)
====================================

Fixed a bug in :meth:`atelier.test.TestCase.run_subprocess` which
could cause a subprocess to deadlock when it generated more output
than the OS pipe buffer would swallow.

:class:`JarBuilder <atelier.jarbuilder.JarBuilder>` is now in a
separate module, the usage API is slightly changed. Signing with a
timestamp is now optional, and the URL of the TSA can be configured.


Version 0.0.12 (released 2015-02-02)
====================================

Getting Lino to build on Travis CI.  Once again I changed the whole
system of declaring demo projects. The parameter to
:func:`atelier.fablib.add_demo_project` must be a Django settings
module, it cannot be a path.  And
:func:`atelier.fablib.run_in_demo_projects` must set the current
working directory to the :attr:`cache_dir
<lino.core.site.Site.cache_dir>`, not the :attr:`project_dir
<lino.core.site.Site.project_dir>`.


Version 0.0.11 (released :blogref:`20150129`)
==============================================

- Users of :mod:`atelier.fablib` who used "demo databases" (which we
  now call "Django demo projects", see
  :attr:`atelier.fablib.env.demo_projects`) must adapt their
  :xfile:`fabfile.py` as described in :blogref:`20150129`.

- New configuration setting :attr:`atelier.fablib.env.editor_command`.

Version 0.0.10 (released :blogref:`20141229`)
==============================================

Fixes a problem for generating the calendar view of a
:rst:dir:`blogger_year`: the cell for December 29, 2014 was not
clickable even when a blog entry existed.

Version 0.0.9  (released :blogref:`20141226`)
=============================================

- :cmd:`fab blog` failed when the user had only :envvar:`VISUAL` but
  not :envvar:`EDITOR` set (:blogref:`20141227`).

- :cmd:`fab blog` failed when the directory for the current year
  didn't yet exist.  Now it automatically wishes "Happy New Year",
  creates both the directory and the default :file:`index.rst` file
  for that year.

- Removed :srcref:`scripts/shotwell2blog.py` which has now `its own
  repository <https://github.com/lsaffre/shotwell2blog>`_.

- :srcref:`scripts/per_project` no longer stumbles over projects whose
  `revision_control_system` is None.

Version 0.0.8  (released :blogref:`20141226`)
=============================================

- `fab_commands` can now be invoked from a subdirectory of the
  project's root. And :mod:`atelier.projects` now supports to work in
  undeclared projects even if there is a :xfile:`config.py` file.
  (:blogref:`20141226`)

- New method :meth:`shell_block
  <atelier.sphinxconf.insert_input.Py2rstDirective.shell_block>`.
- `fab docs` renamed to :cmd:`fab bd`, `fab pub` renamed to :cmd:`fab pd`



Version 0.0.7 (released :blogref:`20141222`)
============================================

This is a bugfix release for 0.0.6 which fixes one bug::

  [localhost] local: git tag -a 0.0.6 -m Release atelier 0.0.6.
  fatal: too many params


Version 0.0.6 (released :blogref:`20141222`)
============================================

- The :cmd:`fab release` now also does `git tag`.
- The :cmd:`fab release` command now reminds me of the things to check
  before a release, communicates with PyPI and displays information
  about the last official release.
- Improved the documentation.


Version 0.0.5 (released 20141207)
=================================

Version 0.0.3
==============================

- Fixed `AttributeError: work_root` occuring when there was
  no `work_root` in user's :xfile:`.fabricrc` file.
  The `work_root` env setting is no longer used.

- (:blogref:`20140117`) atelier now supports namespace packages
  (and thus the :cmd:`fab summary` fablib command no longer prints "old" and
  "new" version because that would require the Distribution object
  (returned from `pkg_resources.get_distribution`) which afaics makes
  problems for namespace packages.

-   (:blogref:`20130623`)
    :meth:`atelier.test.TestCase.run_simple_doctests`
    didn't yet support non-ascii characters.

    Now it does.
    Had to add a new module :mod:`atelier.doctest_utf8`
    for this.
    Because we need to run each doctest in a separate subprocess
    and because the command-line interface
    of `python -m doctest`  has no way to specify an encoding
    of the input file.


- :func:`atelier.sphinxconf.configure` now
  automatically adds the intersphinx entries
  for projects managed in this atelier.


- The `PROJECTS` variable in `/etc/atelier/config.py` is now a list of
  importable Python module names, and their local path will be
  automatically extracted.
  No longer necessary to define a `PROJECTS_HOME`

- `per_project` no longer inserts "fab" as first command.

- Renamed `atelier.test.SubProcessTestCase` to `atelier.test.TestCase`.
  Moved Django-specific methods away to a new module
  :mod:`djangosite.utils.pythontest`.

Version 0.0.2 (released :blogref:`20130505`)
============================================

- `atelier.test.SubProcessTestCase.run_docs_doctests`
  now activates the Site's default language for each testcase
  (when :mod:`north` is available)

Version 0.0.1 (released :blogref:`20130422`)
============================================

- This project was split out of
  `djangosite <https://pypi.python.org/pypi/djangosite>`_ in
  April 2013.
  See :blogref:`20130410`.
