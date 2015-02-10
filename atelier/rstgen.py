# -*- coding: utf-8 -*-
# Copyright 2011-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

r"""A suite of utilities to programmatically generate chunks of
`reStructuredText <http://docutils.sourceforge.net/rst.html>`__.

Especially the :func:`table` function is used by the
:class:`complextable
<djangosite.utils.sphinxconf.ComplexTableDirective>` directive and by
:meth:`Table.to_rst <lino.core.actions.ActionRequest.to_rst>`.  Here
we present the raw API.

Usage examples
--------------

Here is the data we are going to render into different tables:

>>> headers = ["Country", "City", "Name"]
>>> rows = []
>>> rows.append(["Belgium","Eupen","Gerd"])
>>> rows.append(["Estonia","Vigala","Luc"])
>>> rows.append(["St. Vincent and the Grenadines","Chateaubelair","Nicole"])


The simplest case of :func:`table`:

.. complextable::
  :header: 
  
  Code <NEXTCELL> Result <NEXTROW>

  >>> from atelier.rstgen import table
  >>> print(table(headers,rows))
  ================================ =============== ========
   Country                          City            Name
  -------------------------------- --------------- --------
   Belgium                          Eupen           Gerd
   Estonia                          Vigala          Luc
   St. Vincent and the Grenadines   Chateaubelair   Nicole
  ================================ =============== ========
  <BLANKLINE>
  
  <NEXTCELL>
  
  `\ ` 
  
  ================================ =============== ========
   Country                          City            Name
  -------------------------------- --------------- --------
   Belgium                          Eupen           Gerd
   Estonia                          Vigala          Luc
   St. Vincent and the Grenadines   Chateaubelair   Nicole
  ================================ =============== ========

A table without headers:

.. complextable::
  :header: 
  
  Code <NEXTCELL> Result <NEXTROW>

  >>> print(table(headers, rows, show_headers=False))
  ================================ =============== ========
   Belgium                          Eupen           Gerd
   Estonia                          Vigala          Luc
   St. Vincent and the Grenadines   Chateaubelair   Nicole
  ================================ =============== ========
  <BLANKLINE>

  <NEXTCELL>
  
  `\ ` 
  
  ================================ =============== ========
   Belgium                          Eupen           Gerd
   Estonia                          Vigala          Luc
   St. Vincent and the Grenadines   Chateaubelair   Nicole
  ================================ =============== ========
  
You might prefer to use directly the :class:`Table` class:

.. complextable::
  :header: 
  
  Code <NEXTCELL> Result <NEXTROW>

  >>> from atelier.rstgen import Table
  >>> t = Table(headers)
  >>> print(t.to_rst(rows))
  ================================ =============== ========
   Country                          City            Name
  -------------------------------- --------------- --------
   Belgium                          Eupen           Gerd
   Estonia                          Vigala          Luc
   St. Vincent and the Grenadines   Chateaubelair   Nicole
  ================================ =============== ========
  <BLANKLINE>

  <NEXTCELL>
  
  `\ ` 
  
  ================================ =============== ========
   Country                          City            Name
  -------------------------------- --------------- --------
   Belgium                          Eupen           Gerd
   Estonia                          Vigala          Luc
   St. Vincent and the Grenadines   Chateaubelair   Nicole
  ================================ =============== ========

If there is at least one cell that contains a newline character,
the result will be a complex table:

.. complextable::
  :header: 
  
  Code <NEXTCELL> Result <NEXTROW>

  >>> rows[2] = ['''St. Vincent
  ... and the Grenadines''',"Chateaubelair","Nicole"]
  >>> print(table(headers,rows))
  +--------------------+---------------+--------+
  | Country            | City          | Name   |
  +====================+===============+========+
  | Belgium            | Eupen         | Gerd   |
  +--------------------+---------------+--------+
  | Estonia            | Vigala        | Luc    |
  +--------------------+---------------+--------+
  | St. Vincent        | Chateaubelair | Nicole |
  | and the Grenadines |               |        |
  +--------------------+---------------+--------+
  <BLANKLINE>

  <NEXTCELL>
  
  `\ ` 

  +--------------------+---------------+--------+
  | Country            | City          | Name   |
  +====================+===============+========+
  | Belgium            | Eupen         | Gerd   |
  +--------------------+---------------+--------+
  | Estonia            | Vigala        | Luc    |
  +--------------------+---------------+--------+
  | St. Vincent        | Chateaubelair | Nicole |
  | and the Grenadines |               |        |
  +--------------------+---------------+--------+
  

Empty tables
------------
  
A special case is a table with no rows.  For ``table(headers, [])``
the following output would be logical::

    ========= ====== ======
     Country   City   Name
    --------- ------ ------
    ========= ====== ======

But Sphinx would consider this a malformed table.  That's why we
return a blank line when there are no rows:

>>> print(table(headers, []))
<BLANKLINE>
<BLANKLINE>

"""

from __future__ import unicode_literals, print_function

import sys
# import cStringIO as StringIO
import StringIO


class Column(object):
    "A column in a table. "
    def __init__(self, table, index, header, width=None):
        self.table = table
        self.header = header
        self.width = width
        self.index = index

    def adjust_width(self, row):
        """Adjust required width of this column for the given row.
        """
        s = self.table.format_value(row[self.index])
        s = unicode(s)
        for ln in s.splitlines():
            if self.width is None or self.width < len(ln):
                self.width = len(ln)
        # if self.width > 500:
        #     raise Exception("width %r more than 500" % s)


def write_header(fd, level, s):
    def writeln(s=''):
        fd.write(s + '\n')
    _write_header(writeln, level, s)


def header(level, text):
    """
    Render the text as a header with the specified level.
    
    It uses and supposes the following system of header levels::

       =======
       Level 1
       =======
       
       -------
       Level 2
       -------
       
       ~~~~~~~
       Level 3
       ~~~~~~~
       
       Level 4
       =======

       Level 5
       -------
       
       Level 6
       ~~~~~~~
    
    """
    result = StringIO.StringIO()

    def writeln(s=''):
        result.write(s + '\n')
    _write_header(writeln, level, text)
    return result.getvalue()


def _write_header(writeln, level, s):
    if level == 1:
        writeln('=' * len(s))
    elif level == 2:
        writeln('-' * len(s))
    elif level == 3:
        writeln('~' * len(s))
    writeln(s)
    if level == 1:
        writeln('=' * len(s))
    elif level == 2:
        writeln('-' * len(s))
    elif level == 3:
        writeln('~' * len(s))
    elif level == 4:
        writeln('=' * len(s))
    elif level == 5:
        writeln('-' * len(s))
    elif level == 6:
        writeln('~' * len(s))
    else:
        raise Exception("Invalid level %d" % level)
    writeln()


class Table(object):

    """
    Renders as a table.
    
    """
    simple = True

    def format_value(self, v):
        return unicode(v)

    def __init__(self, headers, show_headers=True):
        self.headers = [self.format_value(h) for h in headers]
        self.show_headers = show_headers
        self.cols = [Column(self, i, h) for i, h in enumerate(headers)]
        self.adjust_widths(headers)

    def adjust_widths(self, row):
        if len(row) != len(self.headers):
            raise Exception("Invalid row %(row)s" % dict(row=row))
        for col in self.cols:
            col.adjust_width(row)
            if '\n' in row[col.index]:
                self.simple = False

    def format_row(self, row):
        #~ return ' '.join([unicode(row[c.index]).ljust(c.width) for c in self.cols])
        lines = [[] for x in self.cols]
        for c in self.cols:
            cell = row[c.index]
            for ln in cell.splitlines():
                lines[c.index].append(ln.ljust(c.width))
        height = 1
        for c in self.cols:
            height = max(height, len(lines[c.index]))
        for c in self.cols:
            while len(lines[c.index]) < height:
                lines[c.index].append(''.ljust(c.width))
        x = []
        for i in range(height):
            x.append(self.margin
                     +
                     self.colsep.join(
                         [' ' + lines[c.index][i] + ' ' for c in self.cols])
                     + self.margin)
        return '\n'.join(x)

    def write(self, fd, data=[]):
        """
        rstgen.table(['header1','header2']) no longer raises an exception "No rows in []"
        but renders a table with only headers and no rows.
        """
        #~ if len(data) == 0:
            #~ raise Exception("No rows in %r" % data)
        rows = []
        for i, row in enumerate(data):
            assert len(row) == len(self.cols)
            rows.append([self.format_value(v) for v in row])

        for row in rows:
            self.adjust_widths(row)

        # for c in self.cols:
        #     if c.width == 0:
        #         raise Exception("width %r is 0" % c)

        if self.simple:
            self.header1 = ' '.join([('=' * (c.width + 2)) for c in self.cols])
            self.header2 = ' '.join([('-' * (c.width + 2)) for c in self.cols])
            self.margin = ''
            self.colsep = ' '
        else:
            self.header1 = '+' + \
                '+'.join([('-' * (c.width + 2)) for c in self.cols]) + '+'
            self.header2 = '+' + \
                '+'.join([('=' * (c.width + 2)) for c in self.cols]) + '+'
            self.margin = '|'
            self.colsep = '|'

        def writeln(s):
            fd.write(s.rstrip() + '\n')

        writeln(self.header1)
        if self.show_headers:
            writeln(self.format_row(self.headers))
            writeln(self.header2)
        for row in rows:
            writeln(self.format_row(row))
            if not self.simple:
                writeln(self.header1)
        if self.simple:
            writeln(self.header1)

    def to_rst(self, rows):
        if len(rows) == 0:
            return "\n"
        fd = StringIO.StringIO()
        self.write(fd, rows)
        return fd.getvalue()


def table(headers, rows=tuple(), **kw):
    t = Table(headers, **kw)
    return t.to_rst(rows)


#~ def py2rst(v):
    #~ from django.db import models
    #~ if issubclass(v,models.Model):
        #~ headers = ("name","verbose name","type","help text")
        #~ rows = [
          #~ (f.name,f.verbose_name,f.__class__.__name__,f.help_text)
          #~ for f in v._meta.fields
        #~ ]
        #~ return table(headers,rows)
    #~ return unicode(v)


def ul(items, bullet="-"):
    r"""
    Render the given `items` as a `bullet list 
    <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#bullet-lists>`.
    `items` must be an iterable whose elements are strings.
    
    If at least one item contains more than one paragraph, 
    then all items are separated by an additional blank line.
    
    >>> print(ul(["Foo", "Bar", "Baz"]))
    - Foo
    - Bar
    - Baz
    <BLANKLINE>
    >>> print(ul([
    ...   "Foo", "An item\nwith several lines of text.", "Bar"]))
    - Foo
    - An item
      with several lines of text.
    - Bar
    <BLANKLINE>
    >>> print(ul([
    ...   "A first item\nwith several lines of text.",
    ...   "Another item with a nested paragraph:\n\n  Like this.\n\nWow."]))
    <BLANKLINE>
    - A first item
      with several lines of text.
    <BLANKLINE>
    - Another item with a nested paragraph:
    <BLANKLINE>
        Like this.
    <BLANKLINE>
      Wow.
    <BLANKLINE>

    """
    s = ""
    compressed = True
    for i in items:
        if '\n\n' in i:
            compressed = False
            break

    innersep = '\n' + (' ' * (len(bullet) + 1))
    if compressed:
        for i in items:
            text = innersep.join(i.splitlines())
            s += "%s %s\n" % (bullet, text)
    else:
        for i in items:
            text = innersep.join(i.splitlines())
            s += "\n%s %s\n" % (bullet, text)
    return s


def ol(items, bullet="#."):
    r"""
    >>> print(ol(["Foo", "Bar", "Baz"]))
    #. Foo
    #. Bar
    #. Baz
    <BLANKLINE>
    >>> print(ol([
    ...   "Foo", "An item\nwith several lines of text.", "Bar"]))
    #. Foo
    #. An item
       with several lines of text.
    #. Bar
    <BLANKLINE>
    >>> print(ol([
    ...   "A first item\nwith several lines of text.",
    ...   "Another item with a nested paragraph:\n\n  Like this.\n\nWow."]))
    <BLANKLINE>
    #. A first item
       with several lines of text.
    <BLANKLINE>
    #. Another item with a nested paragraph:
    <BLANKLINE>
         Like this.
    <BLANKLINE>
       Wow.
    <BLANKLINE>
    """
    return ul(items, bullet)


def boldheader(title):
    return "\n\n**%s**\n\n" % unicode(title).strip()


class stdout_prefix():
    # experimental
    def __init__(self, prefix):
        self.prefix = '\n' + prefix
        self.saved_stdout = sys.stdout

    def __enter__(self):
        sys.stdout = self

    def write(self, s):
        s = self.prefix + self.prefix.join(s.splitlines())
        self.saved_stdout.write(s)
            
    def __exit__(self, type, value, traceback):
        sys.stdout = self.saved_stdout
        self.writer = None


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
