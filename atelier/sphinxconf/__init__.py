# -*- coding: utf-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.

"""
Sphinx extensions and a :func:`configure` function used to build
the documentation trees maintained by us.


.. toctree::

.. autosummary::
   :toctree:

   base
   dirtables
   refstothis
   insert_input
   sigal_image
   complex_tables
   blog
   interproject
"""

import logging ; logger = logging.getLogger(__name__)

import sys

from unipath import Path
# from distutils.version import LooseVersion
# from setuptools import version
from pkg_resources import parse_version
import sphinx

def configure(globals_dict):
    """
    Adds to your `conf.py` an arbitrary series of things that all my
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
    if parse_version(sphinx.__version__) < parse_version("1.8"):
    # if LooseVersion(sphinx.__version__) < LooseVersion("1.8"):
        globals_dict.update(autodoc_default_flags=[
            'show-inheritance', 'members'])

    else:
        globals_dict.update(autodoc_default_options={
            'members': None, 'show-inheritance': None})

    mydir = Path(__file__).parent.absolute()
    globals_dict.update(templates_path=['.templates', mydir])

    # globals_dict.update(html_static_path=['.static'])

    # some settings i use in all projects:

    globals_dict.update(master_doc='index')
    globals_dict.update(source_suffix='.rst')
    globals_dict.update(primary_domain='py')
    globals_dict.update(pygments_style='sphinx')

    globals_dict.update(autodoc_member_order='bysource')
    globals_dict.update(
        autodoc_inherit_docstrings=False)



    if True:
        # globals_dict.update(html_theme="bizstyle")
        globals_dict.update(html_theme="sphinx_rtd_theme")
        globals_dict.update(html_theme_options={
            "prev_next_buttons_location": "both",
            "style_nav_header_background": "#dddddd",
            "style_external_links": False,  # disadvantage: line spacing increases for lines with a link
            "includehidden": False,
        })
    else:
        # use default html_theme ("alabaster")
        globals_dict.update(html_theme="alabaster")
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
