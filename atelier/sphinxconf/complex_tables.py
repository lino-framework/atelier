# -*- coding: utf-8 -*-
# Copyright 2011-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""Defines the following directives:

- :rst:dir:`textimage`
- :rst:dir:`complextable`


.. rst:directive:: django2rst

Like :rst:dir:`py2rst` but with the Django environment
initialized.

.. rst:directive:: textimage

Insert a text and an image side by side.
See :blogref:`20130116` for documentation.

.. rst:directive:: complextable

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
        


"""

from __future__ import print_function
from __future__ import unicode_literals

from docutils.parsers.rst import directives

from atelier import rstgen

from .insert_input import InsertInputDirective


class TextImageDirective(InsertInputDirective):
    """Defines the :rst:dir:`textimage` directive."""

    required_arguments = 1
    final_argument_whitespace = True
    option_spec = dict(scale=directives.unchanged)
    #~ optional_arguments = 4

    def get_rst(self):
        #~ print 'MainBlogIndexDirective.get_rst()'
        #~ env = self.state.document.settings.env
        #~ print self.arguments, self.options, self.content
        left = '\n'.join(self.content)
        right = ''
        for arg in self.arguments[0].split():
            right += '.. figure:: %s\n' % arg
            for i in self.options.items():
                right += "  :%s: %s\n" % i
            right += "\n  %s\n\n" % arg
            #~ right += "\n  \n\n" % arg

        return rstgen.table(["", ""], [[left, right]], show_headers=False)


class ComplexTableDirective(InsertInputDirective):

    """Defines the :rst:dir:`complextable` directive."""

    required_arguments = 0
    final_argument_whitespace = True
    option_spec = dict(header=directives.flag)
    #~ option_spec = dict(scale=unchanged)
    #~ optional_arguments = 4

    def get_rst(self):
        #~ print 'MainBlogIndexDirective.get_rst()'
        #~ env = self.state.document.settings.env
        #~ print self.arguments, self.options, self.content
        cellsep = '<NEXTCELL>'
        rowsep = '<NEXTROW>'
        if len(self.arguments) > 0:
            cellsep = self.arguments[0]
        if len(self.arguments) > 1:
            rowsep = self.arguments[1]

        content = '\n'.join(self.content)
        rows = []
        colcount = None

        for row in content.split(rowsep):
            cells = [cell.strip() for cell in row.split(cellsep)]
            if colcount is None:
                colcount = len(cells)
            else:
                assert colcount == len(cells)
            rows.append(cells)

        if 'header' in self.options:
            return rstgen.table(rows[0], rows[1:])

        return rstgen.table([""] * colcount, rows, show_headers=False)


def setup(app):
    app.add_directive(str('complextable'), ComplexTableDirective)
    # app.add_directive(str('blognote'), BlogNoteDirective)
    app.add_directive(str('textimage'), TextImageDirective)

