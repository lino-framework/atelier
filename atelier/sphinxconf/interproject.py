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
import six

from unipath import Path
from importlib import import_module

from sphinx.util import logging
logger = logging.getLogger(__name__)

from invoke import Context

# import atelier
from atelier.projects import load_projects, get_project_info_from_mod


USE_LOCAL_BUILDS = False
# Whether to use objects.inv files from other local doctrees if they
# exist.  E.g. on Travis no other projects are installed from source:


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
        count = 0
        for doc_tree in prj.get_doc_trees():
            if not doc_tree.has_intersphinx:
                continue
            count += 1
            p = None
            if USE_LOCAL_BUILDS:
                src_path = doc_tree.src_path
                if src_path and this_conf_file == src_path.child('conf.py'):
                    break
                # p = prj.root_dir.child(doc_tree, '.build', 'objects.inv')
                p = src_path.child('.build', 'objects.inv')
                if not p.exists():
                    p = None
                
            
            # The unique identifier can be used to prefix cross-reference targets
            # http://www.sphinx-doc.org/en/master/ext/intersphinx.html#confval-intersphinx_mapping
            k = prj.nickname + doc_tree.rel_path
            k = k.replace('_', '')
            k = six.text_type(k)  # make sure it's not newstr from
                                  # future because that can cause
                                  # problems when intersphinx tries to
                                  # sort them
            # if doc_tree == 'docs':
            #     k = prj.nickname
            # else:
            #     k = prj.nickname + doc_tree.replace('_', '')
            urls = getattr(prj.main_package, 'intersphinx_urls', {})
            url = urls.get(doc_tree.rel_path)
            if url:
                intersphinx_mapping[k] = (url, p)
            elif p:
                intersphinx_mapping[k] = p
            elif prjspec:
                logger.warning(
                    "No intersphinx mapping for {} of {} ({})".format(
                        doc_tree.rel_path, prj.nickname, urls))

        if count == 0 and prjspec:
            logger.warning("No doctree for {}".format(prj))
        # if prj.srcref_url:
        #     k = '%s_srcref' % prj.nickname
        #     extlinks[str(k)] = (prj.srcref_url, '')

    # atelier.current_project = this
    globals_dict.update(intersphinx_mapping=intersphinx_mapping)

    # logger.info("intersphinx_mapping set to {}".format(
    #     intersphinx_mapping))

    # if False:  # no longer used
    #     globals_dict.update(extlinks=extlinks)
