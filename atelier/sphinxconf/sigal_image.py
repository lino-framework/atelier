# -*- coding: utf-8 -*-
# Copyright 2014-2017 by Luc Saffre.
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

The file name can contain formatting instructions inspired by
`Wikipedia pictures
<https://en.wikipedia.org/wiki/Wikipedia:Picture_tutorial>`_ which
uses a variable number of pipe characters. For example:

>>> from __future__ import print_function
>>> print(line2html("foo.jpg"))
<a href="http://example.com//foo.jpg"  data-lightbox="image-1" data-title="foo.jpg"/><img src="http://example.com//thumbnails/foo.jpg" style="padding:4px; width:280px;" title="foo.jpg"/></a>

>>> print(line2html("foo.jpg|This is a nice picture"))
<a href="http://example.com//foo.jpg"  data-lightbox="image-1" data-title="This is a nice picture"/><img src="http://example.com//thumbnails/foo.jpg" style="padding:4px; width:280px;" title="This is a nice picture"/></a>

>>> print(line2html("foo.jpg|thumb|This is a nice picture"))
<a href="http://example.com//foo.jpg"  data-lightbox="image-1" data-title="This is a nice picture"/><img src="http://example.com//thumbnails/foo.jpg" style="padding:4px; float:right; width:280px;" title="This is a nice picture"/></a>

>>> print(line2html("foo.jpg|thumb|left|This is a nice picture"))
<a href="http://example.com//foo.jpg"  data-lightbox="image-1" data-title="This is a nice picture"/><img src="http://example.com//thumbnails/foo.jpg" style="padding:4px; float:left;; width:280px;" title="This is a nice picture"/></a>


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
from builtins import str
from builtins import object

import logging
logger = logging.getLogger(__name__)

import os

# from docutils.parsers.rst import directives

from atelier.sphinxconf.insert_input import InsertInputDirective

TEMPLATE1 = """

.. raw:: html

    <a href="%(target)s"><img src="%(src)s" style="padding:4px"/></a>

"""

#TEMPLATE = """<a href="%(target)s" style="%(style)s" %(class)s data-lightbox="image-1" data-title="%(caption)s"/><img src="%(src)s" style="padding:4px" title="%(caption)s"/></a>"""

TEMPLATE = """<a href="%(target)s" %(class)s data-lightbox="image-1" data-title="%(caption)s"/><img src="%(src)s" style="%(style)s" title="%(caption)s"/></a>"""


class Format(object):
    @classmethod
    def update_context(self, caption, tplkw):
        tplkw.update(caption=caption)
        tplkw.update(style="padding:4px; width:280px;")


class Thumb(Format):

    @classmethod
    def update_context(self, caption, tplkw):

        chunks = caption.split('|')
        if len(chunks) == 1:
            tplkw['style'] = "padding:4px; float:right; width:280px;"
        elif len(chunks) == 2:
            align, caption = chunks
            if not align in ("right", "left", "center"):
                raise Exception("Invalid alignment '{0}'".format(align))
            tplkw['style'] = "padding:4px; float:{0};; width:280px;".format(align)
        else:
            raise Exception("Impossible")

        tplkw.update(caption=caption)

class Wide(Format):

    @classmethod
    def update_context(self, caption, tplkw):

        chunks = caption.split('|')
        if len(chunks) == 1:
            tplkw['style'] = "padding:4px; width:100%;"
        else:
            raise Exception("Impossible")

        tplkw.update(caption=caption)

FORMATS = dict()
FORMATS[None] = Format()
FORMATS['thumb'] = Thumb()
FORMATS['wide'] = Wide()


def buildurl(*parts):
    return 'http://example.com/' + '/'.join(parts)


def line2html(name, buildurl=buildurl):
    name = name.strip()
    if not name:
        return ''
    kw = dict()  # style="padding:4px")
    kw['class'] = ''
    kw['style'] = "padding:4px; width:280px;"
    if True:  # new format using only | as separator
        caption = name
        fmt = FORMATS[None]
        chunks = name.split('|', 1)
        if len(chunks) == 2:
            name, caption = chunks
            chunks = caption.split('|', 1)
            if len(chunks) == 2:
                fmtname, caption = chunks
                fmt = FORMATS[fmtname]
        fmt.update_context(caption, kw)
        if ' ' in name:
            raise Exception("Invalid filename. Spaces not allowed.")
    else:
        chunks = name.split(None, 1)
        if len(chunks) == 1:
            kw.update(caption='')
        elif len(chunks) == 2:
            name, caption = chunks
            chunks = caption.split('|', 1)
            if len(chunks) == 1:
                fmt = FORMATS[None]
            elif len(chunks) == 2:
                fmtname, caption = chunks
                fmt = FORMATS[fmtname]
            else:
                raise Exception("Impossible")
            fmt.update_context(caption, kw)
        else:
            raise Exception("FILENAME <whitespace> DESC %s" % chunks)

    head, tail = os.path.split(name)
    kw.update(target=buildurl(head, tail))
    kw.update(src=buildurl(head, 'thumbnails', tail))

    return TEMPLATE % kw


class SigalImage(InsertInputDirective):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    # option_spec = {
    #     'style': directives.unchanged,
    #     'class': directives.unchanged,
    # }

    def get_rst(self):
        env = self.state.document.settings.env
        base_url = env.config.sigal_base_url

        def buildurl(*parts):
            return base_url + '/' + '/'.join(parts)

        s = ''
        for name in self.content:
            s += line2html(name, buildurl)

        if s:
            s = "\n\n.. raw:: html\n\n  {0}\n\n".format(s)

        return s

    def get_headers(self):
        return ['title', 'author', 'date']

    def format_entry(self, e):
        cells = []
        # text = ''.join([unicode(c) for c in e.title.children])
        # cells.append(":doc:`%s <%s>`" % (text, e.docname))
        cells.append(":doc:`%s`" % e.docname)
        cells.append(str(e.meta.get('author', '')))
        cells.append(str(e.meta.get('date', '')))
        return cells


def setup(app):
    app.add_config_value(
        'sigal_base_url', 'http://sigal.saffre-rumma.net', True)
    app.add_directive('sigal_image', SigalImage)
    # app.add_role(str('rref'), ReferingRefRole(
    #     lowercase=True,
    #     innernodeclass=nodes.emphasis,
    #     warn_dangling=True))

