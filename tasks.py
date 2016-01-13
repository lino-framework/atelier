from atelier.tasks import *
# env = Atelier(globals(), "atelier")
env.setup_from_tasks(globals(), "atelier")
env.revision_control_system = 'git'
