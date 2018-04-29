# -*- coding: UTF-8 -*-
# Copyright 2011-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.
"""A minimalistic command-line project management.

See :doc:`/usage`.

"""
from __future__ import unicode_literals
from builtins import str

import os
import six

# import pkg_resources
from unipath import Path
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

from atelier.invlib.utils import SphinxTree

config_files = ['~/.atelier/config.py', '/etc/atelier/config.py',
                '~/_atelier/config.py']

_PROJECT_INFOS = []
_PROJECTS_DICT = {}


def load_inv_namespace(root_dir):
    """Load the :xfile:`tasks.py` file of this project."""
    # self._tasks_loaded = True

    if not root_dir.child('tasks.py').exists():
        raise Exception("20180428")
        # return

    # print("20180428 load tasks.py from {}".format(root_dir))
    # http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    # http://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3
    # fqname = 'atelier.prj_%s' % self.index
    cwd = Path().resolve()
    root_dir.chdir()
    fp = os.path.join(root_dir, "tasks.py")
    m = dict()
    m["__file__"] = fp
    with open(fp) as f:
        exec(f.read(), m)
    cwd.chdir()
    return m['ns']



def add_project(root_dir, nickname=None, inv_namespace=None):
    """
    To be called from your :xfile:`config.py` file.

    `root_dir` is the name of a directory which is expected to contain
    a :xfile:`fabfile.py`.

    If no `nickname` is specified, the nickname will be the leaf name
    of that directory.

    Returns a :class:`Project` instance describing the project.
    """
    i = len(_PROJECT_INFOS)
    root_dir = Path(root_dir).resolve()
    p = Project(i, root_dir, nickname=None, inv_namespace=inv_namespace)
    _PROJECT_INFOS.append(p)
    _PROJECTS_DICT[root_dir] = p
    return p


def get_project_info_from_mod(modname):
    m = import_module(modname)
    return add_project(Path(m.__file__).parent.parent)
    
def get_project_info_from_path(root_dir, inv_namespace=None):
    "Find the project info for the given directory."
    prj = _PROJECTS_DICT.get(root_dir)
    if prj is None:
        # if no config.py found, add current working directory.
        p = Path().resolve()
        while p:
            if p.child('tasks.py').exists():
                prj = add_project(p, inv_namespace=inv_namespace)
                break
            p = p.parent
        # raise Exception("No %s in %s" % (root_dir, _PROJECTS_DICT.keys()))
    return prj


def load_projects():
    for p in _PROJECT_INFOS:
        yield p


def get_setup_info(root_dir):
    """
    Return `SETUP_INFO` defined in the :xfile:`setup.py` file of the
    specified `root_dir`.
    """
    setup_file = root_dir.child('setup.py')
    if not setup_file.exists():
        # print("20180118 no setup.py file in {}".format(root_dir.absolute()))
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
    # g['__file__'] = setup_file
    cwd = Path().resolve()
    root_dir.chdir()
    with open("setup.py") as f:
        code = compile(f.read(), "setup.py", 'exec')
        try:
            exec(code, g)
        except SystemExit:
            cwd.chdir()
            raise Exception(
                "Oops, {} called sys.exit().\n"
                "Atelier requires the setup() call to be in a "
                "\"if __name__ == '__main__':\" condition.".format(
                    setup_file))
    cwd.chdir()
    info = g.get('SETUP_INFO')
    if info is None:
        raise Exception(
            "Oops, {} doesn't define a name SETUP_INFO.".format(
                setup_file))
    return info

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

    .. attribute:: main_package

        The main package (a Python module object).

    .. attribute:: index

        An integer representing the sequence number of this project in
        the global projects list.

    """
    main_package = None
    srcref_url = None
    # intersphinx_urls = {}
    SETUP_INFO = None
    # doc_trees = None
    # doc_trees = []
    # doc_trees = ['docs']
    # ns = None
    config = None
    inv_namespace = None

    def __init__(self, i, root_dir, nickname=None, inv_namespace=None):

        self.index = i
        self.root_dir = root_dir
        #~ self.local_name = local_name
        #~ self.root_dir = Path(atelier.PROJECTS_HOME,local_name)
        self.nickname = nickname or self.root_dir.name
        self.name = self.nickname  # might change in load_info()
        # self._loaded = False
        # self._tasks_loaded = False
        # print("20180428 Project {} initialized".format(self.nickname))
        self.inv_namespace = inv_namespace

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.root_dir)

    def load_info(self):
        if self.inv_namespace is None:
            self.inv_namespace = load_inv_namespace(self.root_dir)

        if self.SETUP_INFO is None:
            self.SETUP_INFO = get_setup_info(self.root_dir)
            # name = self.SETUP_INFO.get('name', None)
            name = self.inv_namespace.configuration().get(
                'main_package', None)
            # if inv_name != name:
            #     raise Exception("20180428 {} != {}".format(inv_name, name))
            if name:
                # self.doc_trees = None
                self.name = name
                self.main_package = import_module(name)

                # for k in ('srcref_url', 'doc_trees', 'intersphinx_urls'):
                #     v = getattr(self.module, k, None)
                #     if v is not None:
                #         setattr(self, k, v)
        
    def get_status(self):
        # if self.config['revision_control_system'] != 'git':
        config = self.inv_namespace.configuration()
        if config['revision_control_system'] != 'git':
            return ''
        from git import Repo
        repo = Repo(self.root_dir)
        s = str(repo.active_branch)
        if repo.is_dirty():
            s += "!"
        return s
        

    def get_doc_trees(self):
        """
        Yield one DocTree instance for every item of this project's
        :envvar:`doc_trees`.
        """
        self.load_info()
        # if not hasattr(ctx, 'doc_trees'):
        #     return
        # msg = "20180428 get_doc_tree({})"
        # print(msg.format(ctx))
        cfg = self.inv_namespace.configuration()
        if self.main_package:
            if 'doc_trees' in cfg:
                msg = "{} configures both doc_trees and main_package. "
                msg += "If you have a main_package then you must set "
                msg += "doc_trees there."
                raise Exception(msg.format(self))
            doc_trees = getattr(self.main_package, 'doc_trees', [])
        else:
            doc_trees = cfg.get('doc_trees')
        for rel_doc_tree in doc_trees:
            if isinstance(rel_doc_tree, six.string_types):
                yield SphinxTree(self, rel_doc_tree)
            elif isinstance(rel_doc_tree, tuple):
                # (BUILDER, PATH)
                clparts = rel_doc_tree[0].split('.')
                cl = import_module(clparts[0])
                for k in clparts[1:]:
                    cl = getattr(cl, k)
                yield cl(self, rel_doc_tree[1])
            else:
                raise Exception("Invalid item {} in doc_trees".format(
                    rel_doc_tree))


   
for fn in config_files:
    fn = os.path.expanduser(fn)
    if os.path.exists(fn):
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            exec(code)

