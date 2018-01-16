# -*- coding: utf-8 -*-
# Copyright 2011-2016 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""Sphinx setup used to build most of the documentation trees
mainained by myself.


.. toctree::

.. autosummary::
   :toctree:

   insert_input
   refstothis
   sigal_image
   complex_tables
   blog
   base
   dirtables
   interproject



"""

from __future__ import print_function
from __future__ import unicode_literals
#from builtins import str

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

import os
import sys

from unipath import Path

def configure(globals_dict):
    """Adds to your `conf.py` an arbitrary series of things that all my
    Sphinx docs configuration files have in common.

    To be called from inside the Sphinx `conf.py` as follows::

      from atelier.sphinxconf import configure
      configure(globals())

    Incomplete list of `conf.py` settings that will be set:

    - `extensions`
    - `templates_path`
    - `html_static_path`
    - master_doc='index'
    - source_suffix='.rst'
    - primary_domain='py'
    - pygments_style='sphinx'


    """
    filename = globals_dict['__file__']
    sys.path.append(Path(filename).parent.absolute())

    globals_dict.update(extensions=[
        'sphinx.ext.autodoc',
        'sphinx.ext.autosummary',
        'sphinx.ext.inheritance_diagram',
        'sphinx.ext.todo',
        'sphinx.ext.extlinks',
        'sphinx.ext.graphviz',
        'sphinx.ext.intersphinx',
        # no i18n, no discovery, only one entry per doc,
        # 'sphinxcontrib.newsfeed',
        #~ 'sphinx.ext.doctest',
        'atelier.sphinxconf.base',
        'atelier.sphinxconf.dirtables',
        'atelier.sphinxconf.refstothis',
        'atelier.sphinxconf.insert_input',
    ])

    # default config for autosummary:
    globals_dict.update(autosummary_generate=True)
    globals_dict.update(autodoc_default_flags=['members'])

    mydir = Path(__file__).parent.absolute()
    globals_dict.update(templates_path=['.templates', mydir])

    # globals_dict.update(html_static_path=['.static'])

    # some settings i use in all projects:

    globals_dict.update(master_doc='index')
    globals_dict.update(source_suffix='.rst')
    globals_dict.update(primary_domain='py')
    globals_dict.update(pygments_style='sphinx')

    globals_dict.update(autodoc_member_order='bysource')
    globals_dict.update(autodoc_default_flags=[
        'show-inheritance', 'members'])

    globals_dict.update(
        autodoc_inherit_docstrings=False)
    


    if False:
        globals_dict.update(html_theme="bizstyle")
    else:
        # use default html_theme ("alabaster")
        my_font_family = "Swiss, Helvetica, 'Liberation Sans'"
        globals_dict.update(html_theme_options={
            "font_family": my_font_family,
            "head_font_family": my_font_family,
        })


    # globals_dict.update(
    #     blogref_format="http://www.lino-framework.org/blog/%Y/%m%d.html")


def version2rst(self, m):
    """
    used in docs/released/index.rst
    """
    v = m.__version__
    if v.endswith('+'):
        v = v[:-1]
        print("The current stable release is :doc:`%s`." % v)
        print("We are working on a future version in the code repository.")
    elif v.endswith('pre'):
        print("We're currently working on :doc:`%s`." % v[:-3])
    else:
        print("The current stable release is :doc:`%s`." % v)
        #~ print("We're currently working on :doc:`coming`.")


from sphinx.jinja2glue import BuiltinTemplateLoader


class DjangoTemplateBridge(BuiltinTemplateLoader):

    """The :meth:`configure` method installs this as `template_bridge
    <http://sphinx-doc.org/config.html#confval-template_bridge>`_ for
    Sphinx.  It causes a template variable ``settings`` to be added
    the Sphinx template context. This cannot be done using
    `html_context
    <http://sphinx-doc.org/config.html#confval-html_context>`_ because
    Django settings are not pickleable.

    """

    def render(self, template, context):
        from django.conf import settings
        context.update(settings=settings)
        return super(DjangoTemplateBridge, self).render(template, context)

    def render_string(self, source, context):
        from django.conf import settings
        context.update(settings=settings)
        return super(DjangoTemplateBridge, self).render_string(source, context)


