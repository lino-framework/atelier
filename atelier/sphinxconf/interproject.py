# -*- coding: utf-8 -*-
# Copyright 2011-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.

"""
- `intersphinx_mapping` : The intersphinx entries for projects
   managed in this atelier. Atelier gets this information by
   checking for an attribute `intersphinx_urls` in the global
   namespace of each project's main module.

TODO: rename :func:`configure` to intersphinx_mapping

"""
from builtins import str
import six

from unipath import Path
from importlib import import_module

from sphinx.util import logging
logger = logging.getLogger(__name__)

from invoke import Context

# import atelier
from atelier.projects import load_projects, get_project_info_from_mod

def configure(globals_dict, prjspec=None):
    """
    Install doctrees of all projects (or only some) into
    `intersphinx_mapping` of your :xfile:`conf.py`

    `prjspec` is a set of importable python modules or a string with a
    space-separated list thereof.  Each of these modules must adhere
    to the atelier convention of having two attributes
    :envvar:`doc_trees` and :envvar:`intersphinx_urls`.  

    If `prjspec` is not given, then all projects of the atelier (see
    :ref:`atelier.config`) that come *before* the current project are
    added.
    """
    
    intersphinx_mapping = dict()
    # extlinks = dict()

    # this = atelier.current_project
    # if this is None:
    #     raise Exception("current_project in {} is None!".format(globals_dict['__file__']))

    this_conf_file = Path(globals_dict['__file__']).resolve()
    
    if prjspec:
        if isinstance(prjspec, six.string_types):
            prjspec = prjspec.split()
        prjlist = [get_project_info_from_mod(n) for n in prjspec]
            
    else:
        prjlist = []
        for p in load_projects():
            if this_conf_file.startswith(p.root_dir):
                break
            prjlist.append(p)
        
    for prj in prjlist:
        # This will load the `tasks.py` of other
        # projects. Possible side effects.
        # print("20180428 {} {}".format(prj.name, prj.config['doc_trees']))
        # config = prj.inv_namespace.configuration()
        # print("20180428 {} {}".format(prj.name, config['doc_trees']))
        # ctx = Context(config)
        # for doc_tree in prj.config['doc_trees']:
        for doc_tree in prj.get_doc_trees():
            if not doc_tree.has_intersphinx:
                continue
            if this_conf_file == doc_tree.src_path.child('conf.py'):
                break
            # p = prj.root_dir.child(doc_tree, '.build', 'objects.inv')
            p = doc_tree.src_path.child('.build', 'objects.inv')
            if not p.exists():
                p = None
            # if True: simulate situation on travis where no other
            # projects are installed from source.
            #     p = None
            k = prj.nickname + doc_tree.rel_path.replace('_', '')
            # if doc_tree == 'docs':
            #     k = prj.nickname
            # else:
            #     k = prj.nickname + doc_tree.replace('_', '')
            url = prj.intersphinx_urls.get(doc_tree.rel_path)
            if url:
                intersphinx_mapping[k] = (url, p)
            elif p:
                intersphinx_mapping[k] = p
            if p or url:
                pass
                # logger.info(
                #     "Loading intersphinx info for {} from {}".format(
                #         k, p or url))
            else:
                logger.warning("No objects.inv for {} of {}".format(
                    doc_tree.rel_path, prj.nickname))

        # if prj.srcref_url:
        #     k = '%s_srcref' % prj.nickname
        #     extlinks[str(k)] = (prj.srcref_url, '')

    # atelier.current_project = this
    globals_dict.update(intersphinx_mapping=intersphinx_mapping)

    # print(20180203, intersphinx_mapping)

    if False:  # no longer used
        globals_dict.update(extlinks=extlinks)
