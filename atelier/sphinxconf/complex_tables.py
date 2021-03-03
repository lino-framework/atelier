# -*- coding: utf-8 -*-
# Copyright 2011-2021 by Rumma & Ko Ltd.
# License: BSD, see LICENSE for more details.

"""Defines the :rst:dir:`textimage` and :rst:dir:`complextable`
directives.

"""
from pathlib import Path
from docutils.parsers.rst import directives

import rstgen

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
            for i in list(self.options.items()):
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


container_tpl = """

.. raw:: html

    <div class="container-fluid">
        {% for col_class, row in rows %}
        <div class="row">
           {% for cell_content in row %}
            <div class="{{col_class}}">
                <div class="card text-center intro-card shadow">
                <div class="card-body flex-fill">

{{cell_content}}

.. raw:: html

                </div>
                </div>
            </div>

           {% endfor %}

.. raw:: html

        </div>

        {% endfor %}

.. raw:: html

    </div>

    """

card_class_map = {
    2 : "col-md-6 col-sm-6 col-xs-12 d-flex align-items-start",
    3 : "col-md-4 col-sm-6 col-xs-12 d-flex align-items-start",
    4 : "col-md-3 col-sm-6 col-xs-12 d-flex align-items-start",
}

from jinja2 import Environment
JINJA_ENV = Environment()


class CardsDirective(InsertInputDirective):
    """Defines the :rst:dir:`cards` directive."""

    # titles_allowed = True
    required_arguments = 0
    final_argument_whitespace = True

    def get_rst(self):
        cellsep = '<NEXTCARD>'
        rowsep = '<NEXTROW>'

        rows = []
        content = '\n'.join(self.content)
        for row in content.split(rowsep):
            cells = [cell.strip() for cell in row.split(cellsep)]
            col_class = card_class_map[len(cells)]
            rows.append([col_class, cells])

        # print(rows)
        tpl = JINJA_ENV.from_string(container_tpl)
        s = tpl.render(rows=rows)
        # pth = Path("~/tmp/tmp.rst").expanduser()
        # with open(pth, 'w') as fh:
        #     fh.write(s)
        return s


def setup(app):
    app.add_directive(str('textimage'), TextImageDirective)
    app.add_directive(str('complextable'), ComplexTableDirective)
    app.add_directive(str('cards'), CardsDirective)
