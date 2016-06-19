# -*- coding: UTF-8 -*-
# Copyright 2013-2016 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""A library for `fabric <http://docs.fabfile.org>`__ with tasks I use
to manage my Python projects.

NOTE: This module is deprecated. Use :mod:`atelier.invlib` instead.

.. contents::
  :local:

.. _fab_commands:

``fab`` commands
================

Documenting
-----------

.. command:: fab blog

    Edit today's blog entry, create an empty file if it doesn't yet exist.

.. command:: fab cd

    Output a reStructuredText formatted list of all commits in all
    projects today.

.. command:: fab bd

    Converted to :cmd:`inv bd`.

.. command:: fab pd

    Converted to :cmd:`inv pd`.

.. command:: fab clean

    Converted to :cmd:`inv clean`.

.. command:: fab readme

    Converted to :cmd:`inv readme`.

.. command:: fab api

    No longer exists because we now use autosummary instead of
    sphinx-apidoc.

    Generate `.rst` files below `docs/api` by running `sphinx-apidoc
    <http://sphinx-doc.org/invocation.html#invocation-of-sphinx-apidoc>`_.

    This is no longer used by most of my projects, at least those
    which I converted to `sphinx.ext.autosummary`.


.. command:: fab docs

    Has been replaced by :cmd:`inv bd`.

.. command:: fab pub

    Has been replaced by :cmd:`inv pd`.


Internationalization
--------------------

.. command:: fab mm

    Converted to :cmd:`inv mm`.

Deploy
------

.. command:: fab release

    Converted to :cmd:`inv release`.

.. command:: fab sdist

    Converted to :cmd:`inv sdist`.

.. command:: fab ci

    Converted to :cmd:`inv ci`.

.. command:: fab reg

    Converted to :cmd:`inv reg`.




Testing
-------

.. command:: fab initdb

    Converted to :cmd:`inv initdb`.

.. command:: fab test

    Converted to :cmd:`inv test`.

.. command:: fab test_sdist

    (Not used)

    Creates a temporay virtualenv, installs your project and runs your
    test suite.
        
    - creates and activates a temporay virtualenv,
    - calls ``pip install --extra-index <env.sdist_dir> <prjname>``
    - runs ``python setup.py test``
    - removes temporary files.
    
    Assumes that you previously did :cmd:`fab sdist` of all your
    projects related to this project.
    
    When using this, you should configure a local download cache for
    pip, e.g. with something like this in your
    :file:`~/.pip/pip.conf`::
    
      [global]
      download-cache=/home/luc/.pip/cache


Miscellaneous
-------------

.. command:: fab summary

    Converted to :cmd:`inv ls`.


Installation
============

To be used by creating a :file:`fabfile.py` in your project's root
directory with at least the following two lines::

  from atelier.fablib import *
  setup_from_fabfile(globals())

See :func:`setup_from_fabfile` for more information.



Configuration files
===================

.. xfile:: fabfile.py

In your :xfile:`fabfile.py` file you can specify project-specific
configuration settings.  Example content::

  from atelier.fablib import *
  setup_from_fabfile(globals(), "foobar")
  env.languages = "de fr et nl".split()
  env.tolerate_sphinx_warnings = True
  add_demo_project('foobar.demo')

.. xfile:: .fabricrc

To specify certain default preferences for all your projects, you can
create a file named :xfile:`.fabricrc` in your home directory with
content like this::

    user = luc
    blogger_project = lino
    docs_rsync_dest = luc@example.org:~/public_html/%s
    docs_rsync_dest = luc@example.org:~/public_html/{prj}_{docs}
    sdist_dir = /home/luc/projects/lino/docs/dl
    temp_dir = /home/luc/tmp


Project settings
================

`fabric <http://docs.fabfile.org>`__ works with a global "environment"
object named ``env``.

The following section documents the possible attributes of this object
as used by :mod:`atelier.fablib`.

You usually define these in your :xfile:`fabfile.py`.  For some of
them (those who are simple strings) you can define user-specific
default values in a :xfile:`.fabricrc` file.


.. class:: env

  .. attribute:: locale_dir

    The name of the directory where `fab mm` et al should write their
    catalog files.

  .. attribute:: sdist_dir


  .. attribute:: editor_command

    A string with the command name of your text editor. Example::

      editor_command = "emacsclient -n {0}"

    The ``{0}`` will be replaced by the filename.

    Note that this must be a *non waiting* command, i.e. which
    launches the editor on the specified file in a new window and then
    returns control to the command line without waiting for that new
    window to terminate.



  .. attribute:: docs_rsync_dest

    A Python template string which defines the rsync destination for
    publishing your projects documentation.
    Used by :cmd:`fab pub`.

    Example::

      env.docs_rsync_dest = 'luc@example.org:~/public_html/{prj}_{docs}'

    The ``{prj}`` in this template will be replaced by the internal
    name of this project, and ``{{docs}}`` by the name of the doctree
    (taken from :attr:`doc_trees`).

    For backward compatibility the following (deprecated) template is
    also still allowed::

      env.docs_rsync_dest = 'luc@example.org:~/public_html/%s'

    The ``%s`` in this template will be replaced by a name `xxx_yyy`,
    where `xxx` is the internal name of this project and `yyy` the
    name of the doctree (taken from :attr:`doc_trees`).


  .. attribute:: doc_trees

    A list of directory names (relative to your project directory)
    containing Sphinx document trees.
    Default value is ``['docs']``

    If this project has a main package, then `env.doc_trees` will be
    replaced by `doc_trees` attribute of that module.

  .. attribute:: cleanable_files

    A list of wildcards to be cleaned by :cmd:`fab clean`.

  .. attribute:: use_dirhtml

    Whether `sphinx-build
    <http://sphinx-doc.org/invocation.html#invocation-of-sphinx-build>`__
    should use ``dirhtml`` instead of the default ``html`` builder.

  .. attribute:: tolerate_sphinx_warnings

    Whether `sphinx-build` should tolerate warnings.

  .. attribute:: languages

    A list of language codes for which userdocs are being maintained.

  .. attribute:: apidoc_exclude_pathnames

    No longer used because we now use autosummary instead of
    sphinx-apidoc.

    a list of filenames (or directory names) to be excluded when you
    run :cmd:`fab api`.

  .. attribute:: revision_control_system

    The revision control system used by your project.
    Allowed values are `'git'`, `'hg'` or `None`.
    Used by :cmd:`fab ci`.

  .. attribute:: use_mercurial

    **No longer used.** Use :attr:`env.revision_control_system` instead.)

  .. attribute:: demo_projects

    The list of *Django demo projects* included in this project.

    Django demo projects are used by the test suite and the Sphinx
    documentation.  Before running :command:`fab test` or
    :command:`fab bd`, they must have been initialized.  To initialize
    them, run :command:`fab initdb`.

    It is not launched automatically by :command:`fab test` or
    :command:`fab bd` because it can take some time and is not always
    necessary.


History
=======

- 20141020 moved `doc_trees` project to :class:`atelier.Project`.
- 20141001 added support for multiple doc trees per project
  (:attr:`env.doc_trees`).
- 20140116 : added support for managing namespace packages

TODO
====

- replace `env.blogger_project` by an attribute of the main module
  (like `intersphinx_urls`)

(The rest of this page is automatically generated stuff.)

"""
import importlib
import os
import datetime
import glob

import sphinx
from babel.dates import format_date
from unipath import Path

from atelier.utils import i2d
from atelier import rstgen

from fabric.api import env, local, task
from fabric.utils import abort, puts
from fabric.contrib.console import confirm
from fabric.api import lcd


def get_current_date(today=None):
    """
    """

    if today is None:
        return datetime.date.today()
    return i2d(today)


class RstFile(object):

    def __init__(self, local_root, url_root, parts):
        self.path = local_root.child(*parts) + '.rst'
        self.url = url_root + "/" + "/".join(parts) + '.html'
        # if parts[0] == 'docs':
        #     self.url = url_root + "/" + "/".join(parts[1:]) + '.html'
        # else:
        #     raise Exception("20131125")
            # self.url = url_root + "/" + "/".join(parts) + '.html'


def add_demo_project(p):
    """Register the specified settings module as being a Django demo project.
    See also :attr:`env.demo_projects`.

    """
    if p in env.demo_projects:
        return
        # raise Exception("Duplicate entry %r in demo_projects." % db)
    env.demo_projects.append(p)


def setup_from_fabfile(
        globals_dict, main_package=None, settings_module_name=None):
    """To be called from within your project's :xfile:`fabfile.py`.

    Minimal example::

      from atelier.fablib import *
      setup_from_fabfile(globals())

    If this doctree is the main doctree of a Python project, then the
    minimal example should be::

      from atelier.fablib import *
      setup_from_fabfile(globals(), "foobar")

    Where "foobar" is the Python name of your project's main package.

    """
    if not '__file__' in globals_dict:
        raise Exception(
            "No '__file__' in %r. "
            "First parameter to must be `globals()`" % globals_dict)
        
    fabfile = Path(globals_dict['__file__'])
    if not fabfile.exists():
        raise Exception("No such file: %s" % fabfile)
    env.root_dir = fabfile.parent.absolute()
    # print("20141027 %s %s " % (main_package, env.root_dir))

    env.project_name = env.root_dir.name
    env.setdefault('build_dir_name', '.build')  # but ablog needs '_build'
    
    env.setdefault('long_date_format', "%Y%m%d (%A, %d %B %Y)")
    # env.work_root = Path(env.work_root)
    env.setdefault('use_dirhtml', False)
    env.setdefault('blog_root', env.root_dir.child('docs'))

    env.setdefault('sdist_dir', None)
    env.setdefault('editor_command', None)
    if env.sdist_dir is not None:
        env.sdist_dir = Path(env.sdist_dir)
    env.main_package = main_package
    env.locale_dir = None
    env.tolerate_sphinx_warnings = False
    env.demo_projects = []
    env.revision_control_system = None
    env.apidoc_exclude_pathnames = []
    # env.blogger_url = "http://blog.example.com/"

    env.setdefault('languages', None)
    env.setdefault('blogger_project', None)
    env.setdefault('blogger_url', None)
    env.setdefault('cleanable_files', [])

    if isinstance(env.languages, basestring):
        env.languages = env.languages.split()

    # if env.main_package:
    #     env.SETUP_INFO = get_setup_info(Path(env.root_dir))
    # else:
    #     env.SETUP_INFO = None

    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        from django.conf import settings
        # why was this? settings.SITE.startup()
        env.languages = [lng.name for lng in settings.SITE.languages]
        # env.demo_databases.append(settings_module_name)
        #~ env.userdocs_base_language = settings.SITE.languages[0].name

    # The following import will populate the projects
    from atelier.projects import get_project_info
    env.current_project = get_project_info(env.root_dir)

    env.doc_trees = env.current_project.doc_trees

    # env.SETUP_INFO = env.current_project.SETUP_INFO


setup_from_project = setup_from_fabfile  # backwards compat


#~ def confirm(msg,default='y',others='n',**override_callbacks):
    #~ text = "%s [%s%s]" % (msg,default.upper(),others)
    #~ def y(): return True
    # ~ # def n(): abort("Missing user confirmation for:\n%s" % msg)
    #~ def n(): abort("Missing user confirmation")
    #~ callbacks = dict(y=y,n=n)
    #~ callbacks.update(override_callbacks)
    #~ while True:
        #~ answer = prompt(text)
        # ~ # answer = raw_input(prompt)
        #~ if not answer:
            #~ answer = default
        #~ answer = answer.lower()
        #~ if answer:
            #~ return callbacks.get(answer)()
def must_confirm(*args, **kw):
    if not confirm(*args, **kw):
        abort("Dann eben nicht...")


def must_exist(p):
    if not p.exists():
        abort("No such file: %s" % p.absolute())


def rmtree_after_confirm(p):
    if not p.exists():
        return
    if confirm("OK to remove %s and everything under it?" % p.absolute()):
        p.rmtree()


def unused_get_locale_dir():
    # replaced by env.locale_dir
    if not env.main_package:
        return None  # abort("No main_package")
    args = env.main_package.split('.')
    args.append('locale')
    p = env.root_dir.child(*args)
    if not p.isdir():
        return None  # abort("Directory %s does not exist." % p)
    return p


def cleanup_pyc(p):
    """Thanks to oddthinking on http://stackoverflow.com/questions/2528283
    """
    for root, dirs, files in os.walk(p):
        pyc_files = [filename for filename in files if filename.endswith(".pyc")]
        py_files = set([filename for filename in files if filename.endswith(".py")])
        excess_pyc_files = [pyc_filename for pyc_filename in pyc_files if pyc_filename[:-1] not in py_files]
        for excess_pyc_file in excess_pyc_files:
            full_path = os.path.join(root, excess_pyc_file)
            must_confirm("Remove excess file %s:" % full_path)
            os.remove(full_path)


@task(alias='unused_mm')
def make_messages():
    "Extract messages, then initialize and update all catalogs."
    extract_messages()
    init_catalog_code()
    update_catalog_code()

    if False:
        extract_messages_userdocs()
        setup_babel_userdocs('init_catalog')
        setup_babel_userdocs('update_catalog')


def extract_messages():
    """Extract messages from source files to `django.pot` file"""
    # locale_dir = get_locale_dir()
    locale_dir = env.locale_dir
    if locale_dir is None:
        return
    args = ["python", "setup.py"]
    args += ["extract_messages"]
    args += ["-o", Path(locale_dir).child("django.pot")]
    cmd = ' '.join(args)
    #~ must_confirm(cmd)
    local(cmd)


def extract_messages_userdocs():
    """
    Run the Sphinx gettext builder on userdocs.
    """
    userdocs = env.root_dir.child('userdocs')
    if not userdocs.isdir():
        return  # abort("Directory %s does not exist." % userdocs)
    args = ['sphinx-build', '-b', 'gettext']
    #~ args += cmdline_args
    # ~ args += ['-a'] # all files, not only outdated
    # ~ args += ['-P'] # no postmortem
    # ~ args += ['-Q'] # no output
    #~ if not env.tolerate_sphinx_warnings:
        # ~ args += ['-W'] # consider warnings as errors
    #~ args += ['-w',env.DOCSDIR.child('warnings.txt')]
    args += [userdocs]
    args += [userdocs.child("translations")]
    cmd = ' '.join(args)
    local(cmd)


@task(alias='rename')
def rename_data_url_friendly():
    data_dir = env.root_dir.child('docs', 'data')
    #~ print list(data_dir.listdir(names_only=True))
    print(list(data_dir.walk()))


def setup_babel_userdocs(babelcmd):
    """Create userdocs .po files if necessary."""
    userdocs = env.root_dir.child('userdocs')
    if not userdocs.isdir():
        return
    locale_dir = userdocs.child('translations')
    for domain in locale_dir.listdir('*.pot', names_only=True):
        domain = domain[:-4]
        for loc in env.languages:
            if loc != env.languages[0]:
                po_file = Path(locale_dir, loc, 'LC_MESSAGES', '%s.po' %
                               domain)
                mo_file = Path(locale_dir, loc, 'LC_MESSAGES', '%s.mo' %
                               domain)
                pot_file = Path(locale_dir, '%s.pot' % domain)
                if babelcmd == 'init_catalog' and po_file.exists():
                    print("Skip %s because file exists." % po_file)
                #~ elif babelcmd == 'compile_catalog' and not mo_file.needs_update(po_file):
                    #~ print "Skip %s because newer than .po" % mo_file
                else:
                    args = ["python", "setup.py"]
                    args += [babelcmd]
                    args += ["-l", loc]
                    args += ["--domain", domain]
                    args += ["-d", locale_dir]
                    #~ args += [ "-o" , po_file ]
                    #~ if babelcmd == 'init_catalog':
                    if babelcmd == 'compile_catalog':
                        args += ["-i", po_file]
                    else:
                        args += ["-i", pot_file]
                    cmd = ' '.join(args)
                    #~ must_confirm(cmd)
                    local(cmd)


@task(alias='cmu')
def compile_catalog_userdocs():
    setup_babel_userdocs('compile_catalog')


def init_catalog_code():
    """Create code .po files if necessary."""
    from lino.core.site import to_locale
    locale_dir = env.locale_dir
    # locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    locale_dir = Path(locale_dir)
    for loc in env.languages:
        if loc != 'en':
            f = locale_dir.child(loc, 'LC_MESSAGES', 'django.po')
            if f.exists():
                print("Skip %s because file exists." % f)
            else:
                args = ["python", "setup.py"]
                args += ["init_catalog"]
                args += ["--domain django"]
                args += ["-l", to_locale(loc)]
                args += ["-d", locale_dir]
                #~ args += [ "-o" , f ]
                args += ["-i", locale_dir.child('django.pot')]
                cmd = ' '.join(args)
                must_confirm(cmd)
                local(cmd)


def update_catalog_code():
    """Update .po files from .pot file."""
    from lino.core.site import to_locale
    locale_dir = env.locale_dir
    # locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    locale_dir = Path(locale_dir)
    for loc in env.languages:
        if loc != env.languages[0]:
            args = ["python", "setup.py"]
            args += ["update_catalog"]
            args += ["--domain django"]
            #~ args += [ "-d" , locale_dir ]
            args += ["-o", locale_dir.child(loc, 'LC_MESSAGES', 'django.po')]
            args += ["-i", locale_dir.child("django.pot")]
            args += ["-l", to_locale(loc)]
            cmd = ' '.join(args)
            #~ must_confirm(cmd)
            local(cmd)


@task(alias='cm')
def compile_catalog():
    """Compile .po files to .mo files."""
    from lino.core.site import to_locale 
    locale_dir = env.locale_dir
    # locale_dir = get_locale_dir()
    if locale_dir is None:
        return
    for loc in env.languages:
        if loc != env.languages[0]:
            args = ["python", "setup.py"]
            args += ["compile_catalog"]
            args += ["-i", locale_dir.child(loc, 'LC_MESSAGES', 'django.po')]
            args += ["-o", locale_dir.child(loc, 'LC_MESSAGES', 'django.mo')]
            args += ["--domain django"]
            #~ args += [ "-d" , locale_dir ]
            args += ["-l", to_locale(loc)]
            cmd = ' '.join(args)
            #~ must_confirm(cmd)
            local(cmd)


@task(alias='mss')
def makescreenshots():
    """generate screenshot .jpg files to gen/screenshots."""
    run_in_demo_projects('makescreenshots', '--traceback')


@task(alias='sss')
def syncscreenshots():
    """synchronize gen/screenshots to userdocs/gen/screenshots."""
    run_in_demo_projects('syncscreenshots', '--traceback',
                          'gen/screenshots', 'userdocs/gen/screenshots')


def unused_build_api(*cmdline_args):
    """
    Generate `.rst` files in `docs/api`. See :cmd:`fab api`.
    """
    docs_dir = env.root_dir.child('docs')
    if not docs_dir.exists():
        return
    api_dir = docs_dir.child("api").absolute()
    if not api_dir.exists():
        return
    os.environ.update(SPHINX_APIDOC_OPTIONS="members,show-inheritance")
    rmtree_after_confirm(api_dir)
    args = ['sphinx-apidoc']
    # args += ['-f'] # force the overwrite of all files that it generates.
    args += ['--no-toc']  # no modules.rst file
    args += ['--separate']  # separate page for each module
    args += ['--module-first']  # Put module documentation before
                                # submodule documentation
    args += ['-o', api_dir]
    args += [env.main_package.replace('.', '/')]  # packagedir
    args += env.apidoc_exclude_pathnames
    if False:
        excluded = ['lino.api.dd.py']
        args += excluded  # pathnames to be ignored
    cmd = ' '.join(args)
    #~ puts("%s> %s" % (os.getcwd(), cmd))
    #~ confirm("yes")
    local(cmd)


def sphinx_build(builder, docs_dir,
                 cmdline_args=[], language=None, build_dir_cmd=None):
    args = ['sphinx-build', '-b', builder]
    args += cmdline_args
    # ~ args += ['-a'] # all files, not only outdated
    # ~ args += ['-P'] # no postmortem
    # ~ args += ['-Q'] # no output
    # build_dir = docs_dir.child(env.build_dir_name)
    build_dir = Path(env.build_dir_name)
    if language is not None:
        args += ['-D', 'language=' + language]
        # needed in select_lang.html template
        args += ['-A', 'language=' + language]
        if language != env.languages[0]:
            build_dir = build_dir.child(language)
            #~ print 20130726, build_dir
    if env.tolerate_sphinx_warnings:
        args += ['-w', 'warnings_%s.txt' % builder]
    else:
        args += ['-W']  # consider warnings as errors
        # args += ['-vvv']  # increase verbosity
    #~ args += ['-w'+Path(env.root_dir,'sphinx_doctest_warnings.txt')]
    args += ['.', build_dir]
    cmd = ' '.join(args)
    with lcd(docs_dir):
        local(cmd)
    if build_dir_cmd is not None:
        with lcd(build_dir):
            local(build_dir_cmd)


def sync_docs_data(docs_dir):
    build_dir = docs_dir.child(env.build_dir_name)
    for data in ('dl', 'data'):
        src = docs_dir.child(data).absolute()
        if src.isdir():
            target = build_dir.child('dl')
            target.mkdir()
            cmd = 'cp -ur %s %s' % (src, target.parent)
            local(cmd)
    if False:
        # according to http://mathiasbynens.be/notes/rel-shortcut-icon
        for n in ['favicon.ico']:
            src = docs_dir.child(n).absolute()
            if src.exists():
                target = build_dir.child(n)
                cmd = 'cp %s %s' % (src, target.parent)
                local(cmd)


@task(alias='userdocs')
def build_userdocs(*cmdline_args):
    """
    Deprecated. sphinx-build the userdocs tree in all languages
    """
    if env.languages is None:
        return
    docs_dir = env.root_dir.child('userdocs')
    if not docs_dir.exists():
        return
    for lng in env.languages:
        sphinx_build('html', docs_dir, cmdline_args, lng)
    sync_docs_data(docs_dir)


@task(alias='pdf')
def build_userdocs_pdf(*cmdline_args):
    if env.languages is None:
        return
    docs_dir = env.root_dir.child('userdocs')
    if not docs_dir.exists():
        return
    for lng in env.languages:
        sphinx_build('latex', docs_dir, cmdline_args,
                     lng, build_dir_cmd='make all-pdf')
    sync_docs_data(docs_dir)


@task(alias='linkcheck')
def sphinx_build_linkcheck(*cmdline_args):
    """sphinxbuild -b linkcheck docs."""
    docs_dir = env.root_dir.child('docs')
    if docs_dir.exists():
        sphinx_build('linkcheck', docs_dir, cmdline_args)
    docs_dir = env.root_dir.child('userdocs')
    if docs_dir.exists():
        lng = env.languages[0]
        #~ lng = env.userdocs_base_language
        sphinx_build('linkcheck', docs_dir, cmdline_args, lng)


def get_doc_trees():
    for rel_doc_tree in env.doc_trees:
        docs_dir = env.root_dir.child(rel_doc_tree)
        if not docs_dir.exists():
            msg = "Directory %s does not exist." % docs_dir
            msg += "\nCheck your project's `doc_trees` setting."
            raise Exception(msg)
        yield docs_dir


@task(alias='unused_bd')
def build_docs(*cmdline_args):
    """See :cmd:`fab bd`. """
    write_readme()
    for docs_dir in get_doc_trees():
        puts("Invoking Sphinx in in directory %s..." % docs_dir)
        builder = 'html'
        if env.use_dirhtml:
            builder = 'dirhtml'
        sphinx_build(builder, docs_dir, cmdline_args)
        sync_docs_data(docs_dir)


@task(alias='unused_clean')
def clean(*cmdline_args):
    """See :cmd:`fab clean`. """
    sphinx_clean()
    py_clean()
    # clean_demo_caches()


def sphinx_clean():
    """Delete all generated Sphinx files.

    """
    for docs_dir in get_doc_trees():
        rmtree_after_confirm(docs_dir.child(env.build_dir_name))


def py_clean():
    """Delete dangling `.pyc` files.

    """
    if env.current_project.module is not None:
        p = Path(env.current_project.module.__file__).parent
        cleanup_pyc(p)
    p = env.root_dir.child('tests')
    if p.exists():
        cleanup_pyc(p)

    files = []
    for pat in env.cleanable_files:
        for p in glob.glob(os.path.join(env.root_dir, pat)):
            files.append(p)
    if len(files):
        must_confirm("Remove {0} cleanable files".format(len(files)))
        for p in files:
            os.remove(p)


class MissingConfig(Exception):
    def __init__(self, name):
        msg = "Must set `env.{0}` in `fabfile.py` or `~/.fabricrc`!"
        msg = msg.format(name)
        Exception.__init__(self, msg)


@task(alias='unused_pd')
def publish():
    """See :cmd:`fab pd`. """
    if not env.docs_rsync_dest:
        raise MissingConfig("docs_rsync_dest")

    for docs_dir in get_doc_trees():
        build_dir = docs_dir.child(env.build_dir_name)
        if build_dir.exists():
            if "%" in env.docs_rsync_dest:
                name = '%s_%s' % (env.project_name, docs_dir.name)
                dest_url = env.docs_rsync_dest % name
            else:
                dest_url = env.docs_rsync_dest.format(
                    prj=env.project_name, docs=docs_dir.name)

            publish_docs(build_dir, dest_url)

    # build_dir = env.root_dir.child('userdocs', env.build_dir_name)
    # if build_dir.exists():
    #     dest_url = env.docs_rsync_dest % (env.project_name + '-userdocs')
    #     publish_docs(build_dir, dest_url)


def publish_docs(build_dir, dest_url):
    with lcd(build_dir):
        args = ['rsync', '-r']
        args += ['--verbose']
        args += ['--progress']  # show progress
        args += ['--delete']  # delete files in dest
        args += ['--times']  # preserve timestamps
        args += ['--exclude', '.doctrees']
        args += ['./']  # source
        args += [dest_url]  # dest
        cmd = ' '.join(args)
        #~ must_confirm("%s> %s" % (build_dir, cmd))
        #~ confirm("yes")
        local(cmd)


def run_in_demo_projects(admin_cmd, *more):
    """Run the given shell command in each demo project (see
    :attr:`env.demo_projects`).

    """
    for mod in env.demo_projects:
        puts("-" * 80)
        puts("In demo project {0}:".format(mod))

        from importlib import import_module
        m = import_module(mod)
        # p = Path(m.__file__).parent.absolute()
        p = m.SITE.cache_dir or m.SITE.project_dir

        with lcd(p):
            args = ["django-admin.py"]
            args += [admin_cmd]
            args += more
            #~ args += ["--noinput"]
            args += ["--settings=" + mod]
            #~ args += [" --pythonpath=%s" % p.absolute()]
            cmd = " ".join(args)
            local(cmd)


def clean_demo_caches():
    """Remove the cache directory of every demo project (see
    :attr:`env.demo_projects`).

    """
    raise Exception("Needs adaption after 20150129. Currently it would removethe source directories...")
    for dp in env.demo_projects:
        # p = dp.child('media', 'cache')
        rmtree_after_confirm(dp.child('media', 'cache'))


@task(alias="initdb")
def initdb_demo():
    run_in_demo_projects('initdb_demo', "--noinput", '--traceback')


@task()
def unused_run_sphinx_doctest():
    """
    Run Sphinx doctest tests.
    Not maintained because i cannot prevent it from also trying to test
    the documents in `django_doctests` which must be tested separately.
    """
    #~ clean_sys_path()
    #~ if sys.path[0] == '':
        #~ del sys.path[0]
    #~ print sys.path
    #~ if len(sys.argv) > 1:
        #~ raise Exception("Unexpected command-line arguments %s" % sys.argv)
    onlythis = None
    #~ onlythis = 'docs/tutorials/human/index.rst'
    args = ['sphinx-build', '-b', 'doctest']
    args += ['-a']  # all files, not only outdated
    args += ['-Q']  # no output
    if not onlythis:
        args += ['-W']  # consider warnings as errors
    build_dir = env.root_dir.child('docs', env.build_dir_name)
    args += [env.root_dir.child('docs'), build_dir]
    if onlythis:  # test only this document
        args += [onlythis]
    #~ args = ['sphinx-build','-b','doctest',env.DOCSDIR,env.BUILDDIR]
    #~ raise Exception(' '.join(args))
    #~ env.DOCSDIR.chdir()
    #~ import os
    #~ print os.getcwd()
    exitcode = sphinx.main(args)
    if exitcode != 0:
        output = Path(build_dir, 'output.txt')
        #~ if not output.exists():
            #~ abort("Oops: no file %s" % output)
        # six.print_("arguments to spxhinx.main() were",args)
        abort("""
=======================================
Sphinx doctest failed with exit code %s
=======================================
%s""" % (exitcode, output.read_file()))


TEST_SDIST_TEMPLATE = """#!/bin/bash
# generated by ``fab test_sdist``
VE_DIR=%(ve_path)s
virtualenv $VE_DIR
. $VE_DIR/bin/activate
pip install --extra-index file:%(sdist_dir)s %(name)s
"""


@task(alias='ddt')
def double_dump_test():
    """
    Perform a "double dump test" on every demo database.
    TODO: convert this to a Lino management command.
    """
    raise Exception("Not yet converted after 20150129")
    if len(env.demo_databases) == 0:
        return
    a = Path(env.temp_dir, 'a')
    b = Path(env.temp_dir, 'b')
    rmtree_after_confirm(a)
    rmtree_after_confirm(b)
    #~ if not confirm("This will possibly break the demo databases. Are you sure?"):
        #~ return
    #~ a.mkdir()
    with lcd(env.temp_dir):
        for db in env.demo_databases:
            if a.exists():
                a.rmtree()
            if b.exists():
                b.rmtree()
            local("django-admin.py dump2py --settings=%s --traceback a" % db)
            local(
                "django-admin.py run --settings=%s --traceback a/restore.py" %
                db)
            local("django-admin.py dump2py --settings=%s --traceback b" % db)
            local("diff a b")


@task(alias='reg')
def pypi_register():
    """See :cmd:`fab reg`. """
    args = ["python", "setup.py"]
    args += ["register"]
    #~ run_setup('setup.py',args)
    local(' '.join(args))


def get_blog_entry(today):
    """Return an RstFile object representing the blog entry for that date
    in the current project.

    """
    parts = ('blog', str(today.year), today.strftime("%m%d"))
    return RstFile(Path(env.blog_root), env.blogref_url, parts)


@task(alias='unused_blog')
def edit_blog_entry(today=None):
    """Edit today's blog entry, create an empty file if it doesn't yet exist.

    :today: Useful when a working day lasted longer than midnight, or
            when you start some work in the evening, knowing that you
            won't commit it before the next morning.  Note that you
            must specify the date using the YYYYMMDD format.
        
            Usage example::
        
                $ fab blog:20150727

    """
    if not env.editor_command:
        raise MissingConfig("editor_command")
    today = get_current_date(today)
    entry = get_blog_entry(today)
    if not entry.path.exists():
        if not confirm("Create file %s?" % entry.path):
            return
        # for every year we create a new directory.
        yd = entry.path.parent
        if not yd.exists():
            if not confirm("Happy New Year! Create directory %s?" % yd):
                return
            yd.mkdir()
            txt = ".. blogger_year::\n"
            yd.child('index.rst').write_file(txt.encode('utf-8'))
            
        if env.languages is None:
            txt = today.strftime(env.long_date_format)
        else:
            txt = format_date(
                today, format='full', locale=env.languages[0])
        entry.path.write_file(rstgen.header(1, txt).encode('utf-8'))
        # touch it for Sphinx:
        entry.path.parent.child('index.rst').set_times()
    args = [env.editor_command]
    args += [entry.path]
    local(' '.join(args))


def show_revision_status():

    if env.revision_control_system == 'hg':
        args = ["hg", "st"]
    elif env.revision_control_system == 'git':
        args = ["git", "status"]
    else:
        puts("Invalid revision_control_system %r !" %
             env.revision_control_system)
        return
    puts("-" * 80)
    local(' '.join(args))
    puts("-" * 80)


@task(alias='unused_ci')
def checkin(today=None):
    """See :cmd:`fab ci`. """

    if env.revision_control_system is None:
        return

    if env.revision_control_system == 'git':
        from git import Repo
        repo = Repo(env.root_dir)
        if not repo.is_dirty():
            puts("No changes to commit in {0}.".format(env.root_dir))
            return

    show_revision_status()

    today = get_current_date(today)

    entry = get_blog_entry(today)
    if not entry.path.exists():
        abort("%s does not exist!" % entry.path.absolute())

    msg = entry.url

    if not confirm("OK to checkin %s %s?" % (env.project_name, msg)):
        return
    #~ puts("Commit message refers to %s" % entry.absolute())

    if env.revision_control_system == 'hg':
        args = ["hg", "ci"]
    else:
        args = ["git", "commit", "-a"]
    args += ['-m', msg]
    cmd = ' '.join(args)
    local(cmd)
    if env.revision_control_system == 'hg':
        local("hg push %s" % env.project_name)
    else:
        local("git push")


@task(alias='readme')
def write_readme():
    """See :cmd:`fab readme`. """
    if not env.main_package:
        return
    if len(env.doc_trees) == 0:
        # when there are no docs, then the README file is manually maintained
        return
    if env.revision_control_system == 'git':
        readme = env.root_dir.child('README.rst')
    else:
        readme = env.root_dir.child('README.txt')

    env.current_project.load_fabfile()
    # for k in ('name', 'description', 'long_description', 'url'):
    #     if k not in env.current_project.SETUP_INFO:
    #         msg = "SETUP_INFO for {0} has no key '{1}'"
    #         raise Exception(msg.format(env.current_project, k))

    txt = """\
==========================
%(name)s README
==========================

%(description)s

Description
-----------

%(long_description)s

Read more on %(url)s
""" % env.current_project.SETUP_INFO
    txt = txt.encode('utf-8')
    if readme.exists() and readme.read_file() == txt:
        return
    must_confirm("Overwrite %s" % readme.absolute())
    readme.write_file(txt)
    docs_index = env.root_dir.child('docs', 'index.rst')
    if docs_index.exists():
        docs_index.set_times()
    #~ cmd = "touch " + env.DOCSDIR.child('index.rst')
    #~ local(cmd)
    #~ pypi_register()


@task(alias='unused_test')
def run_tests():
    """See :cmd:`fab test`. """
    if not env.root_dir.child('setup.py').exists():
        return
    local('python setup.py -q test')


#~ @task(alias='listpkg')
#~ def list_subpackages():
    # ~ # lst = list(env.root_dir.walk("__init__.py"))
    #~ for fn in env.root_dir.child('lino').walk('*.py'):
        #~ print fn

@task(alias='unused_cov')
def run_tests_coverage():
    """
    Run all tests, creating coverage report
    """
    import coverage
    #~ clean_sys_path()
    puts("Running tests for '%s' within coverage..." % env.project_name)
    #~ env.DOCSDIR.chdir()
    source = []
    env.current_project.load_fabfile()
    for package_name in env.current_project.SETUP_INFO['packages']:
        m = importlib.import_module(package_name)
        source.append(os.path.dirname(m.__file__))
    #~ cov = coverage.coverage(source=['djangosite'])
    must_confirm("coverage source=%s" % source)
    cov = coverage.coverage(source=source,)
    #~ cov = coverage.coverage()
    cov.start()

    # .. call your code ..
    rv = run_tests()

    cov.stop()
    cov.save()

    print(cov.html_report())
    return rv

