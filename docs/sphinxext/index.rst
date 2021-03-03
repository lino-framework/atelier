.. _atelier.sphinxext:

=================
Sphinx extensions
=================


.. contents::
   :depth: 1
   :local:


.. default-domain:: rst


Commands
========

.. directive:: command

Define a "command", i.e. a suite of words to be typed at a command
line.

.. role:: cmd

Refer to a :dir:`command` defined elsewhere.

Don't mix this with Sphinx's built-in :role:`command` role.


Blogging
========

.. directive:: blogger_year

Inserts a calendar for the given year with the twelve months.  The
individual days are linked to their respective daily entry.

.. directive:: blogger_index

Inserts a main index page for this blog, one entry for every year.


The `complextable` directive
============================

.. directive:: complextable

Create tables with complex cell content.

Usage example (imagine that A1...B2 are complex blocks of text
that can contain other tables, images, code snippets, ...)::

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


The `cards` directive
=====================

.. directive:: cards

Render the content in individual "cards" that are positioned side by side on
large screens and after each other on small screens.

Deprecated. We recommend using `sphinx-panels
<https://sphinx-panels.readthedocs.io/en/latest/>`__ instead of this.

Individual cards may not contain titles.

Usage example (imagine that A1...B2 are complex blocks of text
that can contain other tables, images, code snippets, ...)::

  .. cards::

    A1
    <NEXTCARD>
    A2
    <NEXTROW>
    B1
    <NEXTCARD>
    B2


Result (requires a theme that uses bootstrap):

.. cards::

    A1
    <NEXTCARD>
    A2
    <NEXTROW>
    B1
    <NEXTCARD>
    B2



Miscellaneous
=============

.. toctree::
   :maxdepth: 2

   interproject
   /textimage/index
   /refstothis/index
