# -*- coding: utf-8 -*-
# Copyright 2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""Defines the :directive:`sigal_image` directive.

.. directive:: sigal_image

Example::

  .. sigal_image:: 2014/04/10/img_6617.jpg

will insert the following rst code::

    .. raw:: html

      <a href="http://sigal.saffre-rumma.net/2014/04/10/img_6617.jpg">
      <img 
      src="http://sigal.saffre-rumma.net/2014/04/10/thumbnails/img_6617.jpg"/>
    </a>


For the first time I now have a bridge between my photo collection and
my blog. I manage my personal photo collection with Shotwell. All
photos are in a single tree, organized into years, months and days as
Shotwell does automatically. Within Shotwell I use a special tag
"blog" to mark all photos that are to be published.

Then I use the :mod:`atelier.scripts.shotwell2blog.py` script to
extract those images to a separate tree. This tree serves as input for
sigal which will generate a static html gallery.

The :directive:`sigal_image` directive was the last missing part of
this publishing chain.

**Why?**

Because I want to remain master of my data. This system allows me to
host my pictures on my own server, to integrate them into blog
entries, to extend the system in case I want to generate pdf files
some day.

"""

from __future__ import print_function
from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

import os

from docutils.parsers.rst import directives

from .insert_input import InsertInputDirective

BASE_URL = "http://sigal.saffre-rumma.net"
TEMPLATE = """

.. raw:: html

    <a href="%(target)s"><img src="%(src)s"/></a>

"""


class SigalImage(InsertInputDirective):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    # option_spec = {
    #     'filter': directives.unchanged,
    #     'orderby': directives.unchanged,
    # }

    def get_rst(self):
        env = self.state.document.settings.env
        base_url = env.config.sigal_base_url

        def buildurl(*parts):
            return base_url + '/' + '/'.join(parts)

        s = ''
        for name in self.content:
            if not name:
                continue
            head, tail = os.path.split(name)
            kw = dict()
            kw.update(target=buildurl(head, tail))
            kw.update(src=buildurl(head, 'thumbnails', tail))
            s += TEMPLATE % kw

        return s

    def get_headers(self):
        return ['title', 'author', 'date']

    def format_entry(self, e):
        cells = []
        # text = ''.join([unicode(c) for c in e.title.children])
        # cells.append(":doc:`%s <%s>`" % (text, e.docname))
        cells.append(":doc:`%s`" % e.docname)
        cells.append(unicode(e.meta.get('author', '')))
        cells.append(unicode(e.meta.get('date', '')))
        return cells


def setup(app):
    app.add_config_value(
        'sigal_base_url', 'http://sigal.saffre-rumma.net', True)
    app.add_directive('sigal_image', SigalImage)
    # app.add_role(str('rref'), ReferingRefRole(
    #     lowercase=True,
    #     innernodeclass=nodes.emphasis,
    #     warn_dangling=True))

