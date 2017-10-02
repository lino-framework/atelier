# -*- coding: utf-8 -*-
# Copyright 2011-2016 by Luc Saffre.
# License: BSD, see LICENSE for more details.

r"""A library of utilities to programmatically generate chunks of
`reStructuredText <http://docutils.sourceforge.net/rst.html>`__.  It
is being used e.g. by the :rst:dir:`complextable` directive and by the
:meth:`show <lino.core.requests.BaseRequest.show>` method or a Lino
request.

Kevin Horn wrote and maintains a comparable library, also called
`rstgen <https://bitbucket.org/khorn/rstgen/src>`_. (TODO: Check
whether we should join our effords.)

"""

from __future__ import unicode_literals, print_function
import six

# from builtins import bytes
# from future.utils import python_2_unicode_compatible
# from future import standard_library
# standard_library.install_aliases()

from builtins import str
# from builtins import range
# from builtins import object

import sys
import io


class Column(object):
    "A column in a table. "

    def __init__(self, table, index, header, width=None):
        self.table = table
        self.header = header
        self.width = width
        self.index = index

    def __str__(self):
        return "{}[{}]:{}".format(self.table, self.index, self.header)

    def adjust_width(self, row):
        """Adjust required width of this column for the given row.
        """
        s = self.table.format_value(row[self.index])
        s = str(s)
        for ln in s.splitlines():
            if self.width is None or self.width < len(ln):
                self.width = len(ln)
                # if self.width > 500:
                #     raise Exception("width %r more than 500" % s)


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
    result = io.StringIO()

    def writeln(s=''):
        result.write(s + '\n')

    _write_header(writeln, level, text)
    return result.getvalue()


def write_header(fd, level, text):
    """Write the string `text` to file `fd` as a header of the given
    `level`. See :func:`header`.

    """

    def writeln(text=''):
        fd.write(text + '\n')

    _write_header(writeln, level, text)


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
    """Used to render a table.
    
    """
    simple = True

    def format_value(self, v):
        return str(v)

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
        # ~ return ' '.join([unicode(row[c.index]).ljust(c.width) for c in self.cols])
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
        # ~ if len(data) == 0:
        # ~ raise Exception("No rows in %r" % data)
        rows = []
        for i, row in enumerate(data):
            assert len(row) == len(self.cols)
            rows.append([self.format_value(v) for v in row])

        for row in rows:
            self.adjust_widths(row)

        for c in self.cols:
            if c.width is None:
                c.width = 1
                # raise Exception("width {} is None".format(c))

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
        fd = io.StringIO()
        self.write(fd, rows)
        return fd.getvalue()


def table(headers, rows=tuple(), **kw):
    """Convert the given headers and rows into an reStructuredText
formatted table.

- `headers` is an iterable of strings, one for each column
- `rows` is an iterable of rows, each row being an iterable of strings.

.. rubric:: Usage examples

Here is the data we are going to render into different tables:

>>> headers = ["Country", "City", "Name"]
>>> rows = []
>>> rows.append(["Belgium", "Eupen", "Gerd"])
>>> rows.append(["Estonia", "Vigala", "Luc"])
>>> rows.append(["St. Vincent and the Grenadines", "Chateaubelair", "Nicole"])


The simplest case of :func:`table`:

.. complextable::
  :header: 
  
  Code <NEXTCELL> Result <NEXTROW>

  >>> from atelier.rstgen import table
  >>> print(table(headers, rows))
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
  

.. rubric:: Empty tables
  
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
    t = Table(headers, **kw)
    return t.to_rst(rows)


# ~ def py2rst(v):
# ~ from django.db import models
# ~ if issubclass(v,models.Model):
# ~ headers = ("name","verbose name","type","help text")
# ~ rows = [
# ~ (f.name,f.verbose_name,f.__class__.__name__,f.help_text)
# ~ for f in v._meta.fields
# ~ ]
# ~ return table(headers,rows)
# ~ return unicode(v)


def ul(items, bullet="-"):
    r""" Render the given `items` as a `bullet list
    <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#bullet-lists>`_.
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
    r"""Convert the given `items` into an ordered list.

`items` must be an iterable whose elements are strings.
    
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
    """Convert the given string into bold string, prefixed and followed by
    newlines."""
    return "\n\n**%s**\n\n" % str(title).strip()


# @python_2_unicode_compatible
def toctree(*children, **options):
    r"""Return a `toctree` directive with specified `options` and
`children`.

.. rubric:: Usage examples

>>> toctree('a', 'b', 'c', maxdepth=2)
'\n\n.. toctree::\n    :maxdepth: 2\n\n    a\n    b\n    c\n'

>>> toctree('a', 'b', 'c', hidden=True)
'\n\n.. toctree::\n    :hidden:\n\n    a\n    b\n    c\n'


    """
    text = "\n\n.. toctree::"
    for k, v in list(options.items()):
        text += "\n    "
        text += ":{0}:".format(k)
        if isinstance(v, six.string_types):
            text += " " + v
        elif v is True:
            pass
        else:
            text += " " + str(v)

    text += "\n"
    for child in children:
        text += "\n    " + child
    text += "\n"
    return str(text)


class stdout_prefix(object):
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


def attrtable(rows, cols):
    """A shortcut for rendering a table showing the given attributes for
    each object.

    Arguments:
        rows: an iterator of objects
        cols: a string with a space-separated list of attribute names

    """
    if isinstance(cols, six.string_types):
        cols = cols.split()
    cells = [[str(getattr(obj, k)) for k in cols] for obj in rows]
    return table(cols, cells)


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
