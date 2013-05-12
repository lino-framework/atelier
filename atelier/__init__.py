import os
execfile(os.path.join(os.path.dirname(__file__),'setup_info.py'))
__version__ = SETUP_INFO['version'] 

config_file = '/etc/atelier/config.py'

#~ env = dict()
#~ if os.path.exists(config_file):
    #~ execfile(config_file,ENV)

PROJECTS = []
_PROJECT_INFOS = []

if os.path.exists(config_file):
    execfile(config_file)

import pkg_resources
from unipath import Path

class Project(object):
    def __init__(self,i,name):
        self.index = i
        #~ self.local_name = local_name
        #~ self.root_dir = Path(atelier.PROJECTS_HOME,local_name)
        self.name = name
        self.dist = pkg_resources.get_distribution(name)
        self.module = __import__(name)
        self.root_dir = Path(self.module.__file__).ancestor(2)
        self.nickname = self.root_dir.name
    
def load_projects():
    if len(_PROJECT_INFOS) == 0: 
        #~ for i,prj in enumerate(env.projects.split()):
        for i,prj in enumerate(PROJECTS):
            _PROJECT_INFOS.append(Project(i,prj))
    return _PROJECT_INFOS
