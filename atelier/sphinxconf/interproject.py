# -*- coding: utf-8 -*-
# Copyright 2011-2017 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""
- `intersphinx_mapping` : The intersphinx entries for projects
   managed in this atelier. Atelier gets this information by
   checking for an attribute `intersphinx_urls` in the global
   namespace of each project's main module.
- `extlinks`

"""
from builtins import str
import six

from atelier.projects import load_projects


def configure(globals_dict, prjspec=None):
    """Install doctrees of all projects (or only some) into
    `intersphinx_mapping`.

    If `prjspec` is None, then all projects are added. Otherwise
    `prjspec` must be a set of project names to add (or a string with
    a space-separated list thereof).

    """
    
    # The following will load the `tasks.py` of other
    # projects. Possible side effects.

    if prjspec is not None:
        if isinstance(prjspec, six.string_types):
            prjspec = set(prjspec.split())

    extlinks = dict()
        # linoticket=(
        #     'http://lino-framework.org/tickets/%s.html',
        #     'Lino Ticket #'))
    intersphinx_mapping = dict()
    for prj in load_projects():
        if prjspec is not None and not prj.name in prjspec:
            continue
        # prj.load_fabfile()
        prj.load_tasks()
        for doc_tree in prj.doc_trees:
            p = prj.root_dir.child(doc_tree, '.build', 'objects.inv')
            if p.exists():
                if doc_tree == 'docs':
                    k = prj.nickname
                else:
                    k = prj.nickname + doc_tree.replace('_', '')
                url = prj.intersphinx_urls.get(doc_tree)
                if url:
                    intersphinx_mapping[k] = (url, p)

        if prj.srcref_url:
            k = '%s_srcref' % prj.nickname
            extlinks[str(k)] = (prj.srcref_url, '')

    globals_dict.update(intersphinx_mapping=intersphinx_mapping)

    if False:  # no longer used
        globals_dict.update(extlinks=extlinks)
