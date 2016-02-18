from atelier.fablib import *
setup_from_fabfile(globals(), "atelier")
env.revision_control_system = 'git'

env.cleanable_files = ['docs/api/atelier.*']
# env.tolerate_sphinx_warnings = True
