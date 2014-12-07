#~ Copyright 2011-2014 by Luc Saffre.
#~ License: BSD, see LICENSE for more details.

import os
import imp

# import pkg_resources
from unipath import Path
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

config_files = ['~/.atelier/config.py', '/etc/atelier/config.py',
                '~/_atelier/config.py']

# PROJECTS = []
_PROJECT_INFOS = []
_PROJECTS_DICT = {}


def add_project(root_dir, nickname=None):
    i = len(_PROJECT_INFOS)
    root_dir = Path(root_dir).absolute()
    p = Project(i, root_dir, nickname=None)
    _PROJECT_INFOS.append(p)
    _PROJECTS_DICT[root_dir] = p


def get_project_info(root_dir):
    if not root_dir in _PROJECTS_DICT:
        raise Exception("No %s in %s" % (root_dir, _PROJECTS_DICT.keys()))
    p = _PROJECTS_DICT[root_dir]
    p.load_fabfile()
    return p


def load_projects():
    for p in _PROJECT_INFOS:
        yield p


def get_setup_info(root_dir):
    if not root_dir.child('setup.py').exists():
        raise RuntimeError(
            "You must call 'fab' from a project's root directory.")
    # sys.path.insert(0, root_dir)
    # setup_module = __import__('setup')
    # print 20140610, root_dir
    # del sys.path[0]
    # return getattr(setup_module, 'SETUP_INFO', None)
    g = dict()
    g['__name__'] = 'not_main'
    cwd = Path().absolute()
    root_dir.chdir()
    execfile(root_dir.child('setup.py'), g)
    cwd.chdir()
    return g.get('SETUP_INFO')

    # # Expected to define global SETUP_INFO.
    # # Note that main_package may be "sphinxcontrib.dailyblog"
    # args = env.main_package.split('.')
    # args.append('project_info.py')
    # execfile(env.ROOTDIR.child(*args), globals())
    # env.SETUP_INFO = SETUP_INFO


class Project(object):
    module = None
    srcref_url = None
    intersphinx_urls = {}
    SETUP_INFO = {}
    doc_trees = ['docs']

    def __init__(self, i, root_dir, nickname=None):
        self.index = i
        self.root_dir = root_dir
        #~ self.local_name = local_name
        #~ self.root_dir = Path(atelier.PROJECTS_HOME,local_name)
        self.nickname = nickname or self.root_dir.name
        self._loaded = False

    def __repr__(self):
        return "<%s %s>" % (self.__class__, self.root_dir)
    # def __getattr__(self, k):
    #     if self._loaded:
    #         raise AttributeError(k)
    #     self.load_fabfile()
    #     return getattr(self, k)

    def load_fabfile(self):
        
        if self._loaded:
            return

        self._loaded = True
        fqname = 'atelier.prj_%s' % self.index
    
        cwd = Path().absolute()
        self.root_dir.chdir()
        # print("20141027 %s %s " % (self, self.root_dir))
        (fp, pathname, desc) = imp.find_module('fabfile', [self.root_dir])
        m = imp.load_module(fqname, fp, pathname, desc)
        cwd.chdir()

        main_package = getattr(m.env, 'main_package', None)
        if main_package:
            self.name = main_package
            # self.name = name
            # removed 20140116:
            # self.dist = pkg_resources.get_distribution(name)
            self.module = import_module(main_package)
            self.SETUP_INFO = get_setup_info(self.root_dir)
            self.srcref_url = getattr(self.module, 'srcref_url', None)
            self.doc_trees = getattr(self.module, 'doc_trees', self.doc_trees)
            self.intersphinx_urls = getattr(
                self.module, 'intersphinx_urls', {})
        else:
            self.name = self.nickname
            # print("20141027 %s %s" % (i, root_dir))


for fn in config_files:
    fn = os.path.expanduser(fn)
    if os.path.exists(fn):
        execfile(fn)  # supposed to call add_project

if len(_PROJECT_INFOS) == 0:
    # if no config.py found, add current working directory.
    p = Path().absolute()
    while p:
        if p.child('fabfile.py').exists():
            add_project(p)
            break
        p = p.parent

