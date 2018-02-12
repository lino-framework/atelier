# -*- coding: utf-8 -*-
# Copyright 2011-2018 by Luc Saffre.
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

from unipath import Path
from importlib import import_module

from atelier.projects import load_projects, get_project_info_from_mod

def configure(globals_dict, prjspec=None):
    """
    Install doctrees of all projects (or only some) into
    `intersphinx_mapping`.

    If `prjspec` is None, then all projects of the atelier are added
    (see :ref:`atelier.config`).

    Otherwise `prjspec` must be a set of importable python modules or
    a string with a space-separated list thereof.  Each of these
    modules must adher to the atelier convention of having two
    attributes :envvar:`doc_trees` and :envvar:`intersphinx_urls`.
    """
    
    intersphinx_mapping = dict()
    extlinks = dict()
    
    if prjspec is not None:
        if isinstance(prjspec, six.string_types):
            prjspec = prjspec.split()
        prjlist = [get_project_info_from_mod(n) for n in prjspec]
            
        # prjlist = 
        # for n in prjspec:
        #     prj = 
        #     m = import_module(n)
        #     doc_trees = getattr(m, 'doc_trees', [])
        #     if not hasattr(m, 'intersphinx_urls'):
        #         raise Exception(
        #             "Module {} has no attribute intersphinx_urls".format(n))

        #     root_dir = Path(m.__file__).parent.parent
        #     for doc_tree in doc_trees:
        #         p = root_dir.child(doc_tree, '.build', 'objects.inv')
        #         k = n.replace('_', "") + doc_tree
        #         intersphinx_mapping[k] = (m.intersphinx_urls['docs'], p)

    else:
        # This will load the `tasks.py` of other
        # projects. Possible side effects.
        prjlist = load_projects()
        
    for prj in prjlist:
        prj.load_tasks()
        for doc_tree in prj.doc_trees:
            p = prj.root_dir.child(doc_tree, '.build', 'objects.inv')
            if not p.exists():
                p = None
            k = prj.nickname + doc_tree.replace('_', '')
            # if doc_tree == 'docs':
            #     k = prj.nickname
            # else:
            #     k = prj.nickname + doc_tree.replace('_', '')
            url = prj.intersphinx_urls.get(doc_tree)
            if url:
                intersphinx_mapping[k] = (url, p)

        if prj.srcref_url:
            k = '%s_srcref' % prj.nickname
            extlinks[str(k)] = (prj.srcref_url, '')

    globals_dict.update(intersphinx_mapping=intersphinx_mapping)

    # print(20180203, intersphinx_mapping)

    if False:  # no longer used
        globals_dict.update(extlinks=extlinks)
