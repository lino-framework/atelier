from atelier.tasks import ns
ns.setup_from_tasks(
    globals(), "atelier",
    blogref_url="http://luc.lino-framework.org",
    revision_control_system='git',
    cleanable_files=['docs/api/atelier.*'])

