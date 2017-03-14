# -*- coding: UTF-8 -*-
# Copyright 2011-2017 by Luc Saffre.
# License: BSD, see LICENSE for more details.
"""A minimalistic command-line project management.

See :doc:`/usage`.

"""
from __future__ import unicode_literals
from builtins import object, str

import os

# import pkg_resources
from unipath import Path
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

config_files = ['~/.atelier/config.py', '/etc/atelier/config.py',
                '~/_atelier/config.py']

_PROJECT_INFOS = []
_PROJECTS_DICT = {}


def add_project(root_dir, nickname=None):
    """To be called from your :xfile:`config.py` file.

    `root_dir` is the name of a directory which is expected to contain
    a :xfile:`fabfile.py`.

    If no `nickname` is specified, the nickname will be the leaf name
    of that directory.

    Returns a :class:`Project` instance describing the project.

    """
    i = len(_PROJECT_INFOS)
    root_dir = Path(root_dir).resolve()
    p = Project(i, root_dir, nickname=None)
    _PROJECT_INFOS.append(p)
    _PROJECTS_DICT[root_dir] = p
    return p


def get_project_info_tasks(root_dir):
    "Find the project info for the given directory."
    prj = _PROJECTS_DICT.get(root_dir)
    if prj is None:
        # if no config.py found, add current working directory.
        p = Path().resolve()
        while p:
            if p.child('tasks.py').exists():
                prj = add_project(p)
                break
            p = p.parent
        # raise Exception("No %s in %s" % (root_dir, _PROJECTS_DICT.keys()))
    prj.load_tasks()
    return prj


def load_projects():
    for p in _PROJECT_INFOS:
        yield p


def get_setup_info(root_dir):
    if not root_dir.child('setup.py').exists():
        return {}
        # raise RuntimeError(
        #     "You must call 'inv' from a project's root directory.")
    # sys.path.insert(0, root_dir)
    # setup_module = __import__('setup')
    # print 20140610, root_dir
    # del sys.path[0]
    # return getattr(setup_module, 'SETUP_INFO', None)
    g = dict()
    g['__name__'] = 'not_main'
    cwd = Path().resolve()
    root_dir.chdir()
    with open("setup.py") as f:
        code = compile(f.read(), "setup.py", 'exec')
        exec(code, g)
    cwd.chdir()
    return g.get('SETUP_INFO')

    # # Expected to define global SETUP_INFO.
    # # Note that main_package may be "sphinxcontrib.dailyblog"
    # args = env.main_package.split('.')
    # args.append('project_info.py')
    # file =env.ROOTDIR.child(*args)
    # with open(file) as f:
    #    code = compile(f.read(), file, 'exec')
    #    exec(code, globals())
    # #execfile(env.ROOTDIR.child(*args), globals())
    # env.SETUP_INFO = SETUP_INFO


class Project(object):
    """Represents a project.

    .. attribute:: module

        The main module (a Python module object).

    .. attribute:: index

        An integer representing the sequence number of this project in
        the global projects list.

    .. attribute:: doc_trees

        A list of directories containing Sphinx documentation trees.

    """
    module = None
    srcref_url = None
    intersphinx_urls = {}
    SETUP_INFO = {}
    doc_trees = ['docs']
    # ns = None
    config = None

    def __init__(self, i, root_dir, nickname=None):
        self.index = i
        self.root_dir = root_dir
        #~ self.local_name = local_name
        #~ self.root_dir = Path(atelier.PROJECTS_HOME,local_name)
        self.nickname = nickname or self.root_dir.name
        self.name = self.nickname  # might change in load_tasks()
        self._loaded = False
        self._tasks_loaded = False

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.root_dir)

    def load_tasks(self):
        """Load the :xfile:`tasks.py` of this project."""
        if self._tasks_loaded:
            return

        self._tasks_loaded = True

        if not self.root_dir.child('tasks.py').exists():
            return

        # fqname = 'atelier.prj_%s' % self.index
        cwd = Path().resolve()
        self.root_dir.chdir()
        # print("20160121 pseudo-importing file %s %s/tasks.py " % (
        #     self, self.root_dir))

        # http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
        # http://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3
        fp = os.path.join(self.root_dir, "tasks.py")
        m = dict()
        m["__file__"] = fp
        with open(fp) as f:
            exec(f.read(), m)

        cwd.chdir()

        ns = m['ns']
        main_package = ns.main_package
        self.config = ns.configuration()
        self.SETUP_INFO = get_setup_info(self.root_dir)
        
        if main_package is None:
            # print("20161229 no main_package in {}".format(self))
            return
        self.name = main_package
        # self.name = name
        # removed 20140116:
        # self.dist = pkg_resources.get_distribution(name)
        self.module = import_module(main_package)
        self.srcref_url = getattr(self.module, 'srcref_url', None)
        self.doc_trees = getattr(self.module, 'doc_trees', self.doc_trees)
        self.intersphinx_urls = getattr(
            self.module, 'intersphinx_urls', {})

    def get_status(self):
        if self.config['revision_control_system'] != 'git':
            return ''
        from git import Repo
        repo = Repo(self.root_dir)
        s = str(repo.active_branch)
        if repo.is_dirty():
            s += "!"
        return s
        


for fn in config_files:
    fn = os.path.expanduser(fn)
    if os.path.exists(fn):
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            exec(code)

