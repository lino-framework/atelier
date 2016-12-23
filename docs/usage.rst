.. _atelier.usage:

=====
Usage
=====

See also

- :doc:`invlib`

- :mod:`atelier.projects`

The :file:`config.py` file
==========================

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

    Loop over all projects, executing the given shell command in the root
    directory of each project.

    The projects are processed in the order defined in your
    :xfile:`~/.atelier/config.py` file.

    The script has the following options:

    - ``--list`` or ``-l`` : print a list of all projects to stdout. Does
      not run any command.

    - ``--start PRJNAME`` : start at project PRJNAME. This is useful
      e.g. when you have been running the test suite on all your projects
      and one project failed. After repairing that failure you want to
      continue the started loop without repeating previous test suites
      again.

    - ``--until PRJNAME`` : stop after project PRJNAME.

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
<http://www.lino-framework.org/team/projects.html>`__ page of the Lino
project for more usage examples.


