.. _atelier.changes: 

=======================
Changes in `atelier`
=======================

Version 0.0.3 (in development)
==============================

- Fixed `AttributeError: work_root` occuring when there was 
  no `work_root` in user's :xfile:`.fabricrc` file.  
  The `work_root` env setting is no longer used.

- (:blogref:`20140117`) atelier now supports namespace packages
  (and thus the :fab:`summary` fablib command no longer prints "old" and
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
  `djangosite <https://pypi.python.org/pypi/djangosite>` in 
  April 2013.
  See :blogref:`20130410`.
  

