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

.fabricrc
---------

To get started, you need a file `.fabricrc` file with at least the
following content::

  sdist_dir
  long_date_format


fabfile.py
----------

In your :file:`fabfile.py` file you may 
optionally specify some project-specific configuration settings like::  
  
  from atelier.fablib import *
  setup_from_project("foobar")
  env.languages = "de fr et nl".split()
  env.tolerate_sphinx_warnings = True
  env.demo_databases.append('foobar.demo.settings')


You may define user-specific default values for some of these settings 
(those who are simple strings) by creating a file :file:`.fabricrc` 
in your home directory with content like this::

    work_root = /home/luc/hgwork
    user = luc
    blogger_project = lino
    docs_rsync_dest = luc@lino-framework.org:~/public_html/%s
    sdist_dir = /home/luc/hgwork/lino/docs/dl

List of existing `env` keys:

- `tolerate_sphinx_warnings` : whether `sphinx-build html` should 
  tolerate warnings.
- `languages` : a list of language codes for which userdocs are being 
  maintained.

- (consult the source code)


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
(specified in `env.demo_databases`)

.. command:: fab ci

    Checkin and push to repository, using today's blog entry as commit message.
    

.. command:: fab release

Create official source distribution and upload it to PyPI.

.. command:: fab userdocs

Run `sphinx build html` in `userdocs`.

.. command:: fab write_readme

Generate `README.txt` file from project_info (if necessary).


.. command:: fab api

Generate `.rst` files below `docs/api`.



.. command:: fab blog

Edit today's blog entry, create an empty file if it doesn't yet exist.


.. command:: fab docs

Run `sphinx build html` in `docs`.



