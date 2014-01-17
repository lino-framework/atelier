#~ Copyright 2011-2014 by Luc Saffre.
#~ License: BSD, see LICENSE for more details.
"""
This is the :mod:`atelier` package.

It deserves more documentation.
"""

import os
execfile(os.path.join(os.path.dirname(__file__), 'project_info.py'))
__version__ = SETUP_INFO['version']

intersphinx_url = "http://atelier.lino-framework.org"
srcref_url = 'https://github.com/lsaffre/atelier/blob/master/%s'

config_file = '/etc/atelier/config.py'

TODAY = None
"""
Used by  :func:`atelier.fablib.get_current_date`.
"""

BLOG_URL = None
PROJECTS = []
_PROJECT_INFOS = []


if os.path.exists(config_file):
    execfile(config_file)

# import pkg_resources
from unipath import Path
from importlib import import_module


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


def load_projects():
    if len(_PROJECT_INFOS) == 0:
        #~ for i,prj in enumerate(env.projects.split()):
        for i, prj in enumerate(PROJECTS):
            _PROJECT_INFOS.append(Project(i, prj))
    return _PROJECT_INFOS
