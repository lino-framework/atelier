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
expected to contain a :xfile:`tasks.py`.  The optional second argument
is a `nickname` for that project. If no nickname is specified, the
nickname will be the leaf name of that directory.

See the docstring of :func:`add_project
<atelier.projects.add_project>`.  See also `Project management using
Atelier <http://noi.lino-framework.org/team/projects.html>`__ for an
introduction.


The :cmd:`per_project` command
==============================

Installing the :mod:`atelier` package will add a script
:cmd:`per_project`. We recommend to define an alias :cmd:`pp` for this
script in your :xfile:`~/.bash_aliases`::

    alias pp='per_project'


.. command:: pp
.. command:: per_project

Execute a shell command in the root directory of every project,
stopping upon the first error.

The projects are processed in the order defined in your
:xfile:`~/.atelier/config.py` file.

The script has two options ``--start`` and ``--until``.

The ``--start`` option is useful e.g. when you have been running the
test suite on all your projects and one project failed. After
repairing that failure you want to continue the started loop without
repeating previous test suites again.

Examples::

  $ pp inv test 
  $ pp -s noi inv test
  $ pp git st
  $ pp inv ci --today


The first argument starting with a ``-`` (i.e. which is not an option)
marks the beginning of the shell command to be executed. Any ``-``
after this command is considered a part of that command. So the
following to lines are not equivalent::

  $ pp inv --help
  $ pp --help inv 
