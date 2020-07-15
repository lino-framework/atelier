# -*- coding: utf-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.

"""
Defines the :func:`atelier.sphinxconf.interproject.configure` function.

"""
import os

from unipath import Path
# from importlib import import_module
from sphinx.util import logging ; logger = logging.getLogger(__name__)

# from invoke import Context

# import atelier
from atelier.projects import load_projects, get_project_info_from_mod
from atelier.projects import get_project_from_nickname


USE_LOCAL_BUILDS = os.environ.get("ATELIER_IGNORE_LOCAL_BUILDS", "") != "yes"

# Whether to use objects.inv files from other local doctrees if they exist.
# E.g. on Travis no other projects are installed from source, so there we
# cannot use it.


def configure(globals_dict, prjspec=None, **nicknames):
    """

    Install doctrees of all (or some) atelier projects into the
    :envvar:`intersphinx_mapping` of your :xfile:`conf.py`.

    See :doc:`/sphinxext/interproject`.

    """

    intersphinx_mapping = dict()
    # extlinks = dict()

    # this = atelier.current_project
    # if this is None:
    #     raise Exception("current_project in {} is None!".format(globals_dict['__file__']))

    this_conf_file = Path(globals_dict['__file__']).resolve()

    if prjspec:
        if isinstance(prjspec, str):
            prjspec = prjspec.split()
        prjlist = [get_project_info_from_mod(n) for n in prjspec]

    else:
        prjlist = []
        # for p in load_projects():
        for p in reversed(list(load_projects())):
            if this_conf_file.startswith(p.root_dir):
                # print("20190122 {} startswith  {}".format(this_conf_file, p.root_dir))
                continue
            prjlist.append(p)

    for k, v in nicknames.items():
        p = get_project_from_nickname(k)
        if p:
            prjlist.append(p)
        else:
            intersphinx_mapping[k] = v

    # logger.info("20180907 prjlist {}".format(prjlist))
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
                logger.info("%s has no intersphinx", p)
                continue
            count += 1
            urls = prj.get_xconfig('intersphinx_urls') or {}
            url = urls.get(doc_tree.rel_path)
            if not url:
                if prjspec:
                    logger.warning(
                        "No intersphinx mapping for {} of {} ({})".format(
                            doc_tree.rel_path, prj.nickname, urls))
                continue

            # if prj.nickname == "getlino":
            #     raise Exception("20191003 {}".format(doc_tree.src_path))

            p = None
            src_path = doc_tree.src_path
            if src_path is not None:
                if this_conf_file == src_path.child('conf.py'):
                    # don't add myself to intersphinx.
                    continue

                if USE_LOCAL_BUILDS:
                        # print("20190306a", doc_tree, src_path)
                    # p = prj.root_dir.child(doc_tree, '.build', 'objects.inv')
                    p = src_path.child('.build', 'objects.inv')
                    if p.exists():
                        logger.info("Found local {}".format(p))
                    else:
                        logger.info("File %s does not exist", p)
                        p = None


            # The unique identifier can be used to prefix cross-reference targets
            # http://www.sphinx-doc.org/en/master/ext/intersphinx.html#confval-intersphinx_mapping
            k = prj.nickname + doc_tree.rel_path
            k = k.replace('_', '')
            k = str(k)

            if k in intersphinx_mapping:
                raise Exception("Duplicate intersphinx key {} used for {} "
                                "(you ask to redefine it to {})".format(
                    k, intersphinx_mapping[k], p))
            intersphinx_mapping[k] = (url, p)

        if count == 0 and prjspec:
            logger.warning("No doctree for {}".format(prj))
        # if prj.srcref_url:
        #     k = '%s_srcref' % prj.nickname
        #     extlinks[str(k)] = (prj.srcref_url, '')

    # atelier.current_project = this
    globals_dict.update(intersphinx_mapping=intersphinx_mapping)

    # logger.info("20190306 prjlist is {}, intersphinx_mapping is {}".format(
    #     prjlist, intersphinx_mapping))

    # if False:  # no longer used
    #     globals_dict.update(extlinks=extlinks)
