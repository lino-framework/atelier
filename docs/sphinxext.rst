.. _atelier.sphinxext:

Sphinx extensions
=================

.. directive:: currentlanguage

This directive solves a subtle problem when documenting multilingual
Lino applications: I want to write tickets in the language of the user
who reported it. That language is not necessarily English. I don't
want to translate tickets. But I want to expand :role:`ddref` roles
into the user's language, not to English.

Blogging
--------

.. directive:: blogger_year

Inserts a calendar for the given year with the twelve months.  The
individual days are linked to their respective daily entry.

.. directive:: blogger_index

Inserts a main index page forthis blog, one entry for every year.


Inline markup
-------------

.. role:: role

Inserts a reference to a :directive:`role`.

Example::

  The :role:`role` *role* inserts a *reference to* a
  role definition which is defined somewhere else using a 
  :directive:`role` *directive*.

Result:

  The :role:`role` *role* inserts a *reference to* a
  role definition which is defined somewhere else using a 
  :directive:`role` *directive*.


.. role:: directive

Inserts a reference to a :directive:`directive`.


Paragraph markup
----------------

.. directive:: role

Inserts a description of a 
`docutils role
<http://docutils.sourceforge.net/docs/ref/rst/roles.html>`_.

.. directive:: directive

Inserts a description of a `docutils directive 
<http://docutils.sourceforge.net/docs/ref/rst/directives.html>`_.

.. directive:: py2rst

Executes the Python code, capturing the `stdout` and inserting it to
the document, parsing it as reStructuredText.

For example, if you write::

  .. py2rst::

      url = 'http://planet.python.org/'
      print("`This <%s>`_ is my *favourite* planet." % url)

then you get:

.. py2rst::

  url = 'http://planet.python.org/'
  print("`This <%s>`_ is my *favourite* planet." % url)



Note that when the Sphinx builder is running under Python 2.7, the
following future imports have been done::

  from __future__ import print_function
  from __future__ import unicode_literals




