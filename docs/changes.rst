.. _atelier.changes: 

=======================
Changes in `atelier`
=======================

Version 0.0.3 (in development)
==============================

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
  

