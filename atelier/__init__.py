# Copyright 2011-2016 by Luc Saffre.
# License: BSD, see LICENSE for more details.
"""
This is the :mod:`atelier` package.

.. autosummary::
   :toctree:

   fablib
   tasks
   invlib
   jarbuilder
   projects
   rstgen
   test
   utils
   sphinxconf
   sheller

"""
# from __future__ import unicode_literals

import os
from .setup_info import SETUP_INFO

fn = os.path.join(os.path.dirname(__file__), 'setup_info.py')
exec(compile(open(fn, "rb").read(), fn, 'exec'))
# above line is equivalent to the line below, except that it works
# also in Python 3:
# execfile(fn)

__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="http://atelier.lino-framework.org")
srcref_url = 'https://github.com/lsaffre/atelier/blob/master/%s'


# thanks to http://stackoverflow.com/questions/11741574/how-to-print-utf-8-encoded-text-to-the-console-in-python-3
# import sys, codecs, locale
# sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
