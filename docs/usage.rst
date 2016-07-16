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



.. command:: per_project
.. command:: pp

Installing the :mod:`atelier` package will add a shell command
:cmd:`per_project`.

We also suggest to define a short alias for this script in your
:xfile:`~/.bash_aliases`::

    alias pp='per_project'

