=============================
The ``atelier.fablib`` module
=============================

Here is a reference to :ref:`atelier.changes`.

sdist_dir

Overview
========

A library for fabric_ with tasks I use to manage my projects.

.. _fabric: http://docs.fabfile.org

To be used by creating a :file:`fabfile.py` in your project's root directory 
with at least the following two lines::

  from atelier.fablib import *
  setup_from_project("foobar")
  
Where "foobar" is the Python name of your main package.

Configuration
-------------

.. xfile:: fabfile.py

In your :xfile:`fabfile.py` file you can specify project-specific
configuration settings.  Example content::
  
  from atelier.fablib import *
  setup_from_project("foobar")
  env.languages = "de fr et nl".split()
  env.tolerate_sphinx_warnings = True
  env.demo_databases.append('foobar.demo.settings')

List of existing `env` keys:

- `tolerate_sphinx_warnings` : whether `sphinx-build html` should 
  tolerate warnings.

- `languages` : a list of language codes for which userdocs are being 
  maintained.

- `apidoc_exclude_pathnames` : a list of filenames (or directory
  names) to be excluded when you run :command:`fab api`.

- `use_mercurial` : set this to False if you use Git.
  Used by :command:`fab ci`

- (consult the source code)

You may define user-specific default values for some of these settings
(those who are simple strings) in a :file:`.fabricrc` file.


.. xfile:: .fabricrc

To specify certain default preferences for all your projects, you can
create a file named :file:`.fabricrc` in your home directory with
content like this::

    user = luc
    blogger_project = lino
    docs_rsync_dest = luc@example.org:~/public_html/%s
    sdist_dir = /home/luc/projects/lino/docs/dl
    temp_dir = /home/luc/tmp




``fab`` commands
================

.. command:: fab mm

("make messages")

Extracts messages from both code and userdocs, then initializes and
updates all catalogs.


.. command:: fab test

Run the test suite of this project.

.. command:: fab test_sdist

    Creates a temporay virtualenv, installs your project and runs your test suite.
        
    - creates and activates a temporay virtualenv,
    - calls ``pip install --extra-index <env.sdist_dir> <prjname>``
    - runs ``python setup.py test``
    - removes temporary files.
    
    assumes that you previously did ``pp fab sdist``
    i.e. your `env.sdist_dir` contains the pre-release sdist of all your 
    projects.
    
    When using this, you should configure a local download cache for 
    pip, e.g. with something like this in your :file:`~/.pip/pip.conf`::
    
      [global]
      download-cache=/home/luc/.pip/cache



.. command:: fab initdb

Run :manage:`initdb_demo` on every demo database of this project 
(specified in `env.demo_databases`).

Demo databases are used by the test suite and the Sphinx
documentation.  They are not included in the code repository since
they are generated data.  Since initializing these databases can take
some time, this is not automatically launched for each test run.

.. command:: fab ci

    Checkin and push to repository, using today's blog entry as commit
    message.
    

.. command:: fab release

Create official source distribution and upload it to PyPI.

.. command:: fab userdocs

Run `sphinx build html` in `userdocs`.

.. command:: fab write_readme

Generate `README.txt` file from project_info (if necessary).


.. command:: fab api

Generate `.rst` files below `docs/api` by running `sphinx-apidoc
<http://sphinx-doc.org/invocation.html#invocation-of-sphinx-apidoc>`_.



.. command:: fab blog

Edit today's blog entry, create an empty file if it doesn't yet exist.


.. command:: fab docs

Run `sphinx build html` in `docs`.



