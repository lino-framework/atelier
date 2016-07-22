# Copyright 2013-2016 by Luc Saffre.
# License: BSD, see LICENSE for more details.

# ~ This module has no docstring because it is to be execfile'd
# ~ from `setup.py`, `atelier/__init__.py` and possibly some external
# ~ tools, too.

# Explicitly install `importlib` under Python 2.6. Thanks to
# http://stackoverflow.com/questions/9418064
install_requires = ['Sphinx', 'invoke', 'argh', 
                    'future', 'Babel', 'unipath',
                    'python_dateutil', 'gitpython']
try:
    import importlib
except ImportError:
    install_requires.append('importlib')

SETUP_INFO = dict(
    name='atelier',
    version='1.0.2',
    install_requires=install_requires,
    scripts=['scripts/per_project'],
    description="A collection of tools for software artists",
    license='Free BSD',
    test_suite='tests',
    author='Luc Saffre',
    author_email='luc.saffre@gmail.com',
    url="http://atelier.lino-framework.org",
    long_description="""\
`atelier` is a collection of tools for managing and maintaining
Python software projects.

It contains:

- some general Python utilities
  (`atelier.utils <http://atelier.lino-framework.org/api/atelier.utils.html>`_)
- a library for generating reStructuredText from Python
  (`atelier.rstgen <http://atelier.lino-framework.org/api/atelier.rstgen.html>`_)
- some Sphinx extensions
  (`atelier.sphinxconf <http://atelier.lino-framework.org/api/atelier.sphinxconf.html>`_)
- a library of invoke commands
  (`atelier.invlib <http://atelier.lino-framework.org/api/atelier.invlib.html>`_)
- a minimalistic project management
  (`atelier.projects <http://atelier.lino-framework.org/api/atelier.projects.html>`_)

.. raw:: html

  <a href="https://travis-ci.org/lsaffre/atelier">
  <img src="https://api.travis-ci.org/lsaffre/atelier.png?branch=master"/>
  </a>

The central project homepage is http://atelier.lino-framework.org



""",
    classifiers="""\
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Framework :: Sphinx :: Extension
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent""".splitlines())

SETUP_INFO.update(packages=[n for n in """
atelier
atelier.sphinxconf
""".splitlines() if n])

SETUP_INFO.update(package_data=dict())


def add_package_data(package, *patterns):
    l = SETUP_INFO['package_data'].setdefault(package, [])
    l.extend(patterns)
    return l


add_package_data('atelier.sphinxconf', '*.html')
