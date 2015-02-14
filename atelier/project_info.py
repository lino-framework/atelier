# Copyright 2013 by Luc Saffre.
# License: BSD, see LICENSE for more details.

#~ This module has no docstring because it is to be execfile'd
#~ from `setup.py`, `atelier/__init__.py` and possibly some external
#~ tools, too.

# Explicitly install `importlib` under Python 2.6. Thanks to
# http://stackoverflow.com/questions/9418064
install_requires = ['fabric', 'Sphinx', 'Babel', 'unipath', 'python_dateutil']
try:
    import importlib
except ImportError:
    install_requires.append('importlib')

SETUP_INFO = dict(
    name='atelier',
    version='0.0.13',
    install_requires=install_requires,
    scripts=['scripts/per_project'],
    description="A collection of tools for software artists",
    license='Free BSD',
    test_suite='tests',
    author='Luc Saffre',
    author_email='luc.saffre@gmail.com',
    url="http://atelier.lino-framework.org",
    long_description="""\
`atelier` is my collection of tools for managing and
maintaining multiple Python software projects.

It contains

- some general Python utilities (:mod:`atelier.utils`)
- a library for generating reStructuredText from Python (:mod:`atelier.rstgen`)
- some Sphinx extensions (:mod:`atelier.sphinxconf`)
- a library of fabric commands (:mod:`atelier.fablib`)
- a minimalistic project management (:mod:`atelier.projects`)

""",
    classifiers="""\
Programming Language :: Python
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Framework :: Sphinx :: Extension
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent""".splitlines())

SETUP_INFO.update(packages=[str(n) for n in """
atelier
atelier.sphinxconf
""".splitlines() if n])

SETUP_INFO.update(package_data=dict())


def add_package_data(package, *patterns):
    l = SETUP_INFO['package_data'].setdefault(package, [])
    l.extend(patterns)
    return l

add_package_data('atelier.sphinxconf', '*.html')
