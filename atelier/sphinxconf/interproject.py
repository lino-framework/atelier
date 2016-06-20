# -*- coding: utf-8 -*-
# Copyright 2011-2016 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""
- `intersphinx_mapping` : The intersphinx entries for projects
   managed in this atelier. Atelier gets this information by
   checking for an attribute `intersphinx_urls` in the global
   namespace of each project's main module.
- `extlinks`

"""
from builtins import str

from atelier.projects import load_projects


def configure(globals_dict):
    # The following will load the `fabfile.py` of other
    # projects. Possible side effects.

    extlinks = dict()
        # linoticket=(
        #     'http://lino-framework.org/tickets/%s.html',
        #     'Lino Ticket #'))
    intersphinx_mapping = dict()
    for prj in load_projects():
        prj.load_fabfile()
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
