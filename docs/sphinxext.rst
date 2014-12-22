.. _atelier.sphinxext:


Sphinx extensions
=================


.. default-domain:: rst

.. directive:: currentlanguage

This directive solves a subtle problem when documenting multilingual
Lino applications: I want to write tickets in the language of the user
who reported it. That language is not necessarily English. I don't
want to translate tickets. But I want to expand :role:`ddref` roles
into the user's language, not to English.


Commands
--------

.. directive:: command

Define a "command", i.e. a suite of words to be typed at a command
line.

.. role:: cmd

Refer to a :dir:`command` defined elsewhere.

Don't mix this with the built-in `command
<http://sphinx-doc.org/markup/inline.html?highlight=command#role-command>`_
role.




Blogging
--------

.. directive:: blogger_year

Inserts a calendar for the given year with the twelve months.  The
individual days are linked to their respective daily entry.

.. directive:: blogger_index

Inserts a main index page forthis blog, one entry for every year.


Miscellaneous
-------------

An example to demonstrate the :dir:`refstothis` directive.

.. toctree::
   :maxdepth: 2

   refstothis/index



