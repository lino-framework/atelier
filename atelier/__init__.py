#~ Copyright 2011-2015 by Luc Saffre.
#~ License: BSD, see LICENSE for more details.
"""
This is the :mod:`atelier` package.

.. autosummary::
   :toctree:

   fablib
   jarbuilder
   projects
   rstgen
   test
   utils
   sphinxconf



"""

import os
execfile(os.path.join(os.path.dirname(__file__), 'project_info.py'))
__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="http://atelier.lino-framework.org")
srcref_url = 'https://github.com/lsaffre/atelier/blob/master/%s'


# thanks to http://stackoverflow.com/questions/11741574/how-to-print-utf-8-encoded-text-to-the-console-in-python-3
import sys, codecs, locale
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
