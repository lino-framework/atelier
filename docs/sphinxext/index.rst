.. _atelier.sphinxext:

=================
Sphinx extensions
=================


.. toctree::
   :maxdepth: 2

   interproject


.. default-domain:: rst

Multilingual doctrees
=====================

.. directive:: currentlanguage

(no longer used) This directive solves a subtle problem when
documenting multilingual Lino applications: I want to write tickets in
the language of the user who reported it. That language is not
necessarily English. I don't want to translate tickets. But I want to
expand :role:`ddref` roles into the user's language, not to English.


Commands
========

.. directive:: command

Define a "command", i.e. a suite of words to be typed at a command
line.

.. role:: cmd

Refer to a :dir:`command` defined elsewhere.

Don't mix this with the built-in `command
<http://sphinx-doc.org/markup/inline.html?highlight=command#role-command>`_
role.




Blogging
========

.. directive:: blogger_year

Inserts a calendar for the given year with the twelve months.  The
individual days are linked to their respective daily entry.

.. directive:: blogger_index

Inserts a main index page forthis blog, one entry for every year.

The `refstothis` directive
============================

.. rst:directive:: refstothis

Inserts a bulleted list of documents referring to "this", where "this"
can be either the current document or a specified reference name.

It recognizes all references made using `XRefRole` roles, including
for example
`:ref: <http://sphinx-doc.org/markup/inline.html#role-ref>`__
and
`:doc: <http://sphinx-doc.org/markup/inline.html#role-doc>`__.

The list has currently a hard-coded, non configurable, format: one
entry for each page, consisting of the title of the document where the
reference was made, followed by the time of last modification of that
document.

The list is ordered by these file timestamps.

If a label gets referenced more than once in a same document, it is
mentioned only once.

A fictive usage example is in :doc:`/refstothis/index`.


The `complextable` directive
============================

.. directive:: complextable

Create tables with complex cell content

Usage example (imagine that A1...B2 is more complex.
It can contain other tables, headers, images, code snippets, ...)::

  .. complextable::

    A1
    <NEXTCELL>
    A2
    <NEXTROW>
    B1
    <NEXTCELL>
    B2


Result:

.. complextable::

    A1
    <NEXTCELL>
    A2
    <NEXTROW>
    B1
    <NEXTCELL>
    B2
        




Miscellaneous
=============

- :doc:`/textimage/index` : The :dir:`textimage` directive.


.. toctree::
   :hidden:

   /textimage/index
   /refstothis/index



