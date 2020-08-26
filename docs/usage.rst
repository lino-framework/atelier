.. doctest docs/usage.rst
.. _atelier.usage:

=====
Usage
=====

How it works
=============

To install the :mod:`atelier` package you must say::

  $ pip install atelier

.. _invoke: http://www.pyinvoke.org/

Installing :mod:`atelier` also installs the invoke_ package, which installs the
command :cmd:`inv` into your PATH. When you run :cmd:`inv` (or its alias
:cmd:`invoke`) from a project directory or a subdirectory, then invoke_ reads
the :xfile:`tasks.py` in the root directory of your project.

.. command:: inv

The :cmd:`inv` command is a kind of make tool that is configured using
:xfile:`tasks.py` file.

.. xfile:: tasks.py

A configuration file for the invoke_ package. It must define a variable named
``ns``, which must be an instance of an invoke namespace.

To activate atelier for your project, you  create a :xfile:`tasks.py` file in
your project's root directory, and define the variable ``ns`` by calling
:func:`atelier.invlib.setup_from_tasks`.

Your :file:`tasks.py` should have at least the following two lines::

  from atelier.invlib import setup_from_tasks
  ns = setup_from_tasks(globals())

You can specify :ref:`project configuration settings <atelier.prjconf>` directly
in your project's :xfile:`tasks.py` file. Example content::

    from atelier.invlib import setup_from_tasks
    ns = setup_from_tasks(globals(), "mypackage",
        tolerate_sphinx_warnings=True,
        revision_control_system='git')

.. xfile:: .invoke.py

You can specify *user-wide* :ref:`project configuration settings
<atelier.prjconf>` in a file named :xfile:`.invoke.py`, which must be in your
home directory.

You can also define *system-wide* default configuration files.  See the `Invoke
documentation <http://docs.pyinvoke.org/en/latest/concepts/configuration.html>`_
for more information.


When you have no :xfile:`config.py <~/.atelier/config.py>` file,
Atelier will operate in single project mode: the :xfile:`tasks.py`
causes on the fly creation of a single project descriptor.



.. _atelier.config:

The ``config.py`` file
======================

.. xfile:: ~/.atelier/config.py
.. xfile:: ~/_atelier/config.py
.. xfile:: /etc/atelier/config.py

If you have more than one project, then you define the global projects
list in a configuration file named :xfile:`~/.atelier/config.py`,
which contains something like::

  add_project('/home/john/myprojects/p1')
  add_project('/home/john/myprojects/second_project', 'p2')

where the first argument to :func:`add_project
<atelier.projects.add_project>` is the name of a directory which is
expected to contain a :xfile:`tasks.py`.

The optional second argument is a **nickname** for that project. If no
nickname is specified, the nickname will be the leaf name of that
directory.

It is allowed but not recommended to have several projects with a same
nickname.


Your projects' ``setup.py`` files
=================================

If a project has a :file:`setup.py` file, then atelier uses it.

.. envvar:: SETUP_INFO
.. xfile:: setup.py

The :xfile:`setup.py` file of a Python project can be as simple as
this:

.. literalinclude:: p1/setup.py

But for atelier there are two additional required conventions:

- The :xfile:`setup.py` file must define a name :envvar:`SETUP_INFO`, which must
  be a dict containing the keyword arguments to be passed to the :func:`setup`
  function.

- The :xfile:`setup.py` file should actually call the :func:`setup`
  function *only if* invoked from a command line, i.e. only `if
  __name__ == '__main__'`.

So the above minimal :xfile:`setup.py` file becomes:

.. literalinclude:: p2/setup.py

Atelier tries to verify these conditions and raises an exception if
the :xfile:`setup.py` doesn't comply:

>>> from atelier.projects import get_setup_info
>>> from unipath import Path
>>> get_setup_info(Path('docs/p1'))
Traceback (most recent call last):
...
Exception: Oops, docs/p1/setup.py called sys.exit().
Atelier requires the setup() call to be in a "if __name__ == '__main__':" condition.

>>> get_setup_info(Path('docs/p3'))
Traceback (most recent call last):
...
Exception: Oops, docs/p3/setup.py doesn't define a name SETUP_INFO.

>>> d = get_setup_info(Path('docs/p2'))
>>> d == {'version': '1.0.0', 'name': 'foo'}
True
>>> d == dict(name="foo", version="1.0.0")
True

.. _atelier.prjconf:

Project configuration settings
==============================

TODO: document them all.

::
    'root_dir': root_dir,
    'build_dir_name': '.build', # e.g. ablog needs '_build'
    'project_name': str(root_dir.name),
    'locale_dir': None,
    'help_texts_source': None,
    'help_texts_module': None,
    'tolerate_sphinx_warnings': False,
    'cleanable_files': [],
    'revision_control_system': None,
    'apidoc_exclude_pathnames': [],
    'editor_command': os.environ.get('EDITOR'),
    'prep_command': "",
    'test_command': "python -m unittest discover -s tests",
    'demo_projects': [],
    'demo_prep_command': "manage.py prep --noinput --traceback",
    'coverage_command': '`which invoke` prep test clean --batch bd',
    'languages': None,
    'blog_root': root_dir.child('docs'),
    'long_date_format': "%Y%m%d (%A, %d %B %Y)",
    'sdist_dir': root_dir.child('dist'),
    'pypi_dir': root_dir.child('.pypi_cache'),
    'use_dirhtml': False,
    'doc_trees': ['docs'],
    'intersphinx_urls': {},


Defining shell aliases
======================

Under Linux you can easily define abbreviations for certain commands
which you use oftem. These are called **shell aliases**.  There are
several ways for defining them, we recommend to write them into your
:xfile:`~/.bash_aliases`.

.. xfile:: ~/.bash_aliases

    Conventional name for the file that holds your shell aliases.  See
    `Configuring your login sessions with dot files
    <http://mywiki.wooledge.org/DotFiles>`_.

After editing your :xfile:`~/.bash_aliases` you must open a new
terminal in order to see the changes.


The :cmd:`per_project` command
==============================

Installing the :mod:`atelier` package will add the :cmd:`per_project`
script:

.. command:: per_project

    Usage : per_project [options] CMD ...

    Loop over all projects, executing the given shell command CMD in
    the root directory of each project.

    Special case: When CMD starts with the word ``git``, then skip all
    projects which don't have their :envvar:`revision_control_system`
    set to ``'git'``.

    The projects are processed in the order defined in your
    :xfile:`~/.atelier/config.py` file.

    Options:

    - ``--list`` or ``-l`` : print a list of all projects to stdout. Does
      not run any command.

    - ``--start PRJNAME`` : start at project PRJNAME. This is useful
      e.g. when you have been running the test suite on all your projects
      and one project failed. After repairing that failure you want to
      continue the started loop without repeating previous test suites
      again.

    - ``--after PRJNAME`` : start after project PRJNAME (like
      `--start`, but without the named project).

    - ``--until PRJNAME`` : stop after project PRJNAME.

    - ``--voice`` : Speak the result through speakers when terminated.


.. command:: pp

    We recommend to define an alias :cmd:`pp` for :cmd:`per_project`
    in your :xfile:`~/.bash_aliases`::

        alias pp='per_project'

Note that the first argument which is not an option (i.e. not starting
with a ``-``) marks the beginning of the shell command to be executed.
Any ``-`` after that is considered a part of the command.  So the
following two lines are *not* equivalent::

  $ pp inv --help
  $ pp --help inv

Usage examples::

  $ pp -l
  $ pp inv test
  $ pp git st

See the `Project management
<http://www.lino-framework.org/dev/projects.html>`__ page of the Lino
project for more usage examples.



See also

- :doc:`invlib`
- :mod:`atelier.projects`
