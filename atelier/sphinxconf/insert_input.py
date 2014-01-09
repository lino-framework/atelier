# -*- coding: utf-8 -*-
# Copyright 2011-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.
"""

Sphinx setup used to build the Lino documentation.

Thanks to 

- `Creating reStructuredText Directives 
  <http://docutils.sourceforge.net/docs/howto/rst-directives.html>`_





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


from docutils import nodes
from docutils import statemachine
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module


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

    #~ def run(self):
        #~ out = self.get_rst()
        #~ env = self.state.document.settings.env
        #~ if self.debug:
            #~ print env.docname
            #~ print '-' * 50
            #~ print out
            #~ print '-' * 50
        #~ self.state_machine.insert_input(out.splitlines(),out)
        #~ return []

    #~ class InsertTableDirective(InsertInputDirective):

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


