# -*- coding: utf-8 -*-
# Copyright 2011-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""Defines the :class:`InsertInputDirective` class and some
subclasses, installing the following directives:

- :directive:`py2rst`
- :directive:`django2rst`
- :directive:`textimage`
- :directive:`complextable`


.. directive:: py2rst

Run a Python code block and interpret the output as if it were rst
source.

.. directive:: django2rst

Like :directive:`py2rst` but with the Django environment
initialized.

.. directive:: textimage

Insert a text and an image side by side.
See :blogref:`20130116` for documentation.

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
        



"""

from __future__ import print_function
from __future__ import unicode_literals

"""Note: the `import unicode_literals` caused the following::

    Traceback (most recent call last):
      File "/home/luc/pythonenvs/py27/local/lib/python2.7/site-packages/sphinx/cmdline.py", line 245, in main
        warningiserror, tags, verbosity, parallel)
      File "/home/luc/pythonenvs/py27/local/lib/python2.7/site-packages/sphinx/application.py", line 122, in __init__
        self.config.setup(self)
      File "/home/luc/hgwork/atelier/atelier/sphinxconf/__init__.py", line 654, in setup
        indextemplate='pair: %s; management command')
      File "/home/luc/pythonenvs/py27/local/lib/python2.7/site-packages/sphinx/application.py", line 503, in add_object_type
        'doc_field_types': doc_field_types})
    TypeError: type() argument 1 must be string, not unicode
    
I solved this by a manual patch in line 308 of 
:file:`sphinx/application.py`::
    
    def import_object(self, objname, source=None):
        objname = str(objname)  # LS 20140108 accept unicode strings
        # needed when calling from Python 2.7 with
        # `from __future__ import unicode_literals`
        try:
            module, name = objname.rsplit('.', 1)
        except ValueError, err:
    

"""


import logging
logger = logging.getLogger(__name__)

import sys
from StringIO import StringIO

from docutils import nodes
from docutils import statemachine
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles

from atelier import rstgen

#~ class ScreenshotDirective(directives.images.Image):
    #~ """
    #~ Directive to insert a screenshot.
    #~ """
    #~ def run(self):
        #~ assert len(self.arguments) == 1
        # ~ # name = '/../gen/screenshots/' + self.arguments[0]
        #~ name = '/gen/screenshots/' + self.arguments[0]
        #~ self.arguments = [name]
        #~ (image_node,) = directives.images.Image.run(self)
        #~ return [image_node]


class InsertInputDirective(Directive):
    """
    Base class for directives that work by generating rst markup
    to be forwarded to `state_machine.insert_input()`.
    """
    titles_allowed = False
    has_content = True
    debug = False
    raw_insert = False
    option_spec = {
        'language': directives.unchanged_required,
    }

    def get_rst(self):
        "Override this to return a string in rst syntax"
        raise NotImplementedError()

    def run(self):

        self.env = self.state.document.settings.env
        self.language = self.options.get('language', self.env.config.language)
        self.env.temp_data['language'] = self.language

        output = self.get_rst()
        #~ output = output.decode('utf-8')

        if self.debug:
            print(self.env.docname)
            print('-' * 50)
            print(output)
            print('-' * 50)

        content = statemachine.StringList(output.splitlines())

        if self.raw_insert:

            self.state_machine.insert_input(content, output)
            return []

        if self.titles_allowed:
            node = nodes.section()
            # necessary so that the child nodes get the right source/line set
            node.document = self.state.document
            nested_parse_with_titles(self.state, content, node)
        else:
            node = nodes.paragraph()
            node.document = self.state.document
            self.state.nested_parse(content, self.content_offset, node)

        # following lines originally copied from
        # docutils.parsers.rst.directives.tables.RSTTable
        #~ title, messages = self.make_title()
        # ~ node = nodes.Element()          # anonymous container for parsing
        #~ self.state.nested_parse(content, self.content_offset, node)
        #~ if len(node) != 1 or not isinstance(node[0], nodes.table):
            #~ error = self.state_machine.reporter.error(
                #~ 'Error parsing content block for the "%s" directive: exactly '
                #~ 'one table expected.' % self.name, nodes.literal_block(
                #~ self.block_text, self.block_text), line=self.lineno)
            #~ return [error]
        #~ return [x for x in node]
        return list(node)

        #~ table_node = node[0]
        #~ table_node['classes'] += self.options.get('class', [])
        #~ return [table_node]


class Py2rstDirective(InsertInputDirective):

    """Defines the :directive:`py2rst` directive."""

    titles_allowed = True
    has_content = True
    debug = False
    #~ def get_rst(self):
        #~ return self.output_from_exec('\n'.join(self.content))

    def get_context(self):
        context = dict()
        context.update(self=self)
        context.update(env=self.state.document.settings.env)
        return context

    def get_rst(self):
        if not self.content:
            warning = self.state_machine.reporter.warning(
                'Content block expected for the "%s" directive; none found.'
                % self.name, nodes.literal_block(
                    self.block_text, self.block_text), line=self.lineno)
            return [warning]

        #~ raise Exception("20130331 %r" % self.content)
        code = '\n'.join(self.content)
        return self.output_from_exec(code)

    def output_from_exec(self, code):
        old = sys.stdout
        buffer = StringIO()
        sys.stdout = buffer
        context = self.get_context()

        # TODO: catch exceptions and report them together with the
        # name of the guilty file

        exec(code, context)
        sys.stdout = old
        s = buffer.getvalue()
        #~ print 20130331, type(s)
        return s


#~ class DjangoTableDirective(InsertInputDirective):
    #~ def get_rst(self):
        #~ assert len(self.content) == 1
        #~ code = '\n'.join(self.content)
        #~ from django.conf import settings
        #~ print .jobs.Candidatures.request(limit=5).to_rst()
        #~ code = """
        #~ """
        #~ old = sys.stdout
        #~ buffer = StringIO()
        #~ sys.stdout = buffer
        #~ context = dict()
        #~ context.update(settings.SITE.modules)
        #~ context = dict(settings=settings)
        #~ exec(code,context)
        #~ sys.stdout = old
        #~ return buffer.getvalue()


class TextImageDirective(InsertInputDirective):
    """Defines the :directive:`textimage` directive."""

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

    """Defines the :directive:`complextable` directive."""

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


# class BlogNoteDirective(Py2rstDirective):

#     def get_rst(self):
#         return '\n'.join(self.content)


def setup(app):
    # also used by `vor/conf.py`
    app.add_directive(str('complextable'), ComplexTableDirective)
    app.add_directive(str('py2rst'), Py2rstDirective)
    # app.add_directive(str('blognote'), BlogNoteDirective)
    app.add_directive(str('textimage'), TextImageDirective)

