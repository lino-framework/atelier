.. _atelier.interproject:

=======================================
Referring to doctrees in other projects
=======================================

The :mod:`atelier.sphinxconf.interproject` module is a utility to install the
doctrees of all (or some) other atelier projects into your
:envvar:`intersphinx_mapping` configuration setting.

Usage
=====

Add the following lines to your :xfile:`conf.py` file::

    from atelier.sphinxconf import interproject
    interproject.configure(globals())  # all projects

Or::

    from atelier.sphinxconf import interproject
    interproject.configure(globals(), 'package1 package2')  # some projects

The :func:`configure` function accepts two positional argments:

The **first argument** is the global namespace of your :xfile:`conf.py` file
into which the :envvar:`intersphinx_mapping` should be defined.  If you defined that
name before calling :func:`configure`, that value will be overwritten.  You may
manually add more mappings to it after calling :func:`configure`.

The **second argument** is optional and specifies a list of importable python
module names or a string with a space-separated list thereof. If no second
argument is given, all projects defined in in :ref:`atelier.config` which come
after the current project are added.

Each of these modules must adhere to the atelier convention of having two
attributes :envvar:`doc_trees` and :envvar:`intersphinx_urls`.  Each doctree of
each project will be added to the intersphinx mapping (if it has a
corresponding url in :envvar:`intersphinx_urls`).



.. envvar:: ATELIER_IGNORE_LOCAL_BUILDS

    If this environment variable is set to "yes", the intersphinx mapping will
    ignore local data in the doctree builds of intersphinx projects.
    This can be useful to simulate behavior in an isolated testing environment.



.. envvar:: intersphinx_mapping

  A Sphinx setting in the :xfile:`conf.py` of a doctree. See `Sphinx docs
  <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#confval-intersphinx_mapping>`__
