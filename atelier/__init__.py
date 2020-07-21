# Copyright 2011-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.
"""
This is the :mod:`atelier` package.

.. autosummary::
   :toctree:

   invlib
   invlib.utils
   invlib.tasks
   jarbuilder
   projects
   test
   utils
   sphinxconf
   sheller

"""

import setuptools  # try to avoid "Distutils was imported before Setuptools"

from .setup_info import SETUP_INFO

__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="http://atelier.lino-framework.org")
srcref_url = 'https://github.com/lino-framework/atelier/blob/master/%s'
doc_trees = ['docs']

current_project = None
"""
The currently loaded project.  An instance of
:class:`atelier.Project`.  This is set by :func:`atelier.invlib.setup_from_tasks`.
"""
