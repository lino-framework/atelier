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
    interproject.configure(globals(), 'package1 package2', foo=("http://foo.com", filename))  # some projects

The :func:`configure` function accepts up to two positional arguments:

The **first argument** is the global namespace of your :xfile:`conf.py` file
into which the :envvar:`intersphinx_mapping` should be defined.  If you defined that
name before calling :func:`configure`, that value will be overwritten.  You may
manually add more mappings to it after calling :func:`configure`.

The **second argument** is optional and specifies a list of importable python
module names or a string with a space-separated list thereof. If no second
argument is given, all projects that come *after* the current project
(according to the sort order defined in :ref:`atelier.config`) are added.

You can also add pure documentation projects (i.e. which don't define a Python
module) by specifying additional keyword arguments.  Each keyword maps a project
nickname to a tuple of `(URI, filename)`.  That tuple is just the default value
to use when there is no project with that nickname in the projects list defined
in :xfile:`~/.atelier/config.py` file.

Each of these projects must adhere to the convention of having two attributes
:envvar:`doc_trees` and :envvar:`intersphinx_urls` either in their main module
or in their :xfile:`tasks.py`.  Each doctree having a corresponding url in
:envvar:`intersphinx_urls` will be added to the :envvar:`intersphinx mapping`.






.. envvar:: ATELIER_IGNORE_LOCAL_BUILDS

    If this environment variable is set to "yes", the intersphinx mapping will
    ignore local data in the doctree builds of intersphinx projects.
    This can be useful to simulate behavior in an isolated testing environment.



.. envvar:: intersphinx_mapping

  A Sphinx setting in the :xfile:`conf.py` of a doctree. See `Sphinx docs
  <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#confval-intersphinx_mapping>`__
