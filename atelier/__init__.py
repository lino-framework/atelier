#~ Copyright 2011-2014 by Luc Saffre.
#~ License: BSD, see LICENSE for more details.
"""
This is the :mod:`atelier` package.

It deserves more documentation.
"""

import os
execfile(os.path.join(os.path.dirname(__file__), 'project_info.py'))
__version__ = SETUP_INFO['version']


intersphinx_urls = dict(docs="http://atelier.lino-framework.org")
srcref_url = 'https://github.com/lsaffre/atelier/blob/master/%s'

config_file = '/etc/atelier/config.py'

BLOG_URL = None
PROJECTS = []
_PROJECT_INFOS = []


if os.path.exists(config_file):
    execfile(config_file)

# import pkg_resources
from unipath import Path
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module


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
    cwd = root_dir.cwd()
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

    def __init__(self, i, name):
        self.index = i
        #~ self.local_name = local_name
        #~ self.root_dir = Path(atelier.PROJECTS_HOME,local_name)
        self.name = name
        # removed 20140116:
        # self.dist = pkg_resources.get_distribution(name)
        self.module = import_module(name)
        number_of_parts = len(name.split('.'))
        self.root_dir = Path(self.module.__file__).ancestor(
            number_of_parts + 1)
        self.nickname = self.root_dir.name
        self.SETUP_INFO = get_setup_info(self.root_dir)
        self.srcref_url = getattr(self.module, 'srcref_url', None)
        self.doc_trees = getattr(self.module, 'doc_trees', ['docs'])
        self.intersphinx_urls = getattr(self.module, 'intersphinx_urls', {})


def load_projects():
    if len(_PROJECT_INFOS) == 0:
        #~ for i,prj in enumerate(env.projects.split()):
        for i, prj in enumerate(PROJECTS):
            _PROJECT_INFOS.append(Project(i, prj))
    return _PROJECT_INFOS


def get_project_info(name):
    for prj in load_projects():
        if prj.name == name:
            return prj
    
