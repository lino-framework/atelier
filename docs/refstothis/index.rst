==========================
The `refstothis` directive
==========================

.. default-domain:: rst

.. rst:directive:: refstothis

Inserts a bulleted list of documents referring to "this", where "this"
can be either the current document or a specified reference name.

It recognizes all references made using `XRefRole` roles, including
for example :rst:role:`ref` and :rst:role:`doc`.

.. `:ref: <http://sphinx-doc.org/markup/inline.html#role-ref>`__
  and
  `:doc: <http://sphinx-doc.org/markup/inline.html#role-doc>`__.

The list has currently a hard-coded, non configurable, format: one
entry for each page, consisting of the title of the document where the
reference was made, followed by the time of last modification of that
document.

The list is ordered by these timestamps.

If a label gets referenced more than once in a same document, it is
mentioned only once.

The following is a fictive usage example.

This example consists of four files:

.. toctree::
   :maxdepth: 1

   foobar
   baz
   0115
   0116
