# -*- coding: utf-8 -*-
# Copyright 2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""Defines the :rst:dir:`sigal_image` directive.

.. rst:directive:: sigal_image

Example::

  .. sigal_image:: 2014/04/10/img_6617.jpg

will insert the following rst code::

    .. raw:: html

      <a href="http://sigal.saffre-rumma.net/2014/04/10/img_6617.jpg">
      <img 
      src="http://sigal.saffre-rumma.net/2014/04/10/thumbnails/img_6617.jpg"/>
    </a>


Supposing that `sigal_base_url` in your :xfile:`conf.py` is set to
``"http://sigal.saffre-rumma.net"``.



.. _shotwell2blog: https://github.com/lsaffre/shotwell2blog
.. _Shotwell: https://en.wikipedia.org/wiki/Shotwell_%28software%29
.. _Sigal: http://sigal.saimon.org/en/latest/

This creates a bridge between my photo collection and my blog. I
manage my personal photo collection with Shotwell_. All photos are in
a single central file tree, organized into years, months and days as
Shotwell does automatically.

From within Shotwell I use a tag "blog" to mark all photos that are to
be published.  Then I use the shotwell2blog_ script to extract those
images to a separate tree. This tree serves as input for Sigal_ which
will generate a static html gallery. My pricate Sigal gallery is `here
<http://sigal.saffre-rumma.net/>`__.

The :rst:dir:`sigal_image` directive was the last missing part of this
publishing bridge: it allows me to integrate these pictures into blog
entries.

New since 20140729: Requires `lightbox
<http://lokeshdhakar.com/projects/lightbox2/>`_.  And then write a
`layout.html` template as follows::

    {%- block extrahead %}
      {{ super() }}
    <script src="{{ pathto('')}}data/lightbox/js/jquery-1.11.0.min.js"></script>
    <script src="{{ pathto('')}}data/lightbox/js/lightbox.min.js"></script>
    <link href="{{ pathto('')}}data/lightbox/css/lightbox.css" rel="stylesheet" />
    {% endblock %}

"""

from __future__ import print_function
from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

import os

from docutils.parsers.rst import directives

from .insert_input import InsertInputDirective

TEMPLATE1 = """

.. raw:: html

    <a href="%(target)s"><img src="%(src)s" style="padding:4px"/></a>

"""

TEMPLATE = """

.. raw:: html

    <a href="%(target)s" style="padding:4px" data-lightbox="image-1" data-title="%(caption)s"/><img src="%(src)s" style="padding:4px" title="%(caption)s"/></a>

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
            kw = dict()
            chunks = name.split(None, 1)
            if len(chunks) == 1:
                kw.update(caption='')
            elif len(chunks) == 2:
                name = chunks[0]
                kw.update(caption=chunks[1])
            else:
                raise Exception("FILENAME <whitespace> CAPTION %s" % chunks)
            head, tail = os.path.split(name)
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

