# -*- coding: UTF-8 -*-
# Copyright 2017 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.

"""Utilities for atelier.invlib

"""

from __future__ import print_function
from __future__ import unicode_literals

import six
from importlib import import_module
from unipath import Path
from invoke.exceptions import Exit

from atelier.utils import confirm, cd


def must_confirm(*args, **kwargs):
    if not confirm(''.join(args)):
        raise Exit("User failed to confirm.")


def must_exist(p):
    if not p.exists():
        raise Exception("No such file: %s" % p.absolute())




class DocTree(object):
    src_path = None
    out_path = None
    
    def __init__(self, ctx, rel_doc_tree):
        if rel_doc_tree in ('', '.'):
            src_path = ctx.root_dir
        else:
            src_path = ctx.root_dir.child(rel_doc_tree)
        if not src_path.exists():
            msg = "Directory %s does not exist." % src_path
            raise Exception(msg)
        self.src_path = src_path
        self.ctx = ctx
        
    def build_docs(self, *cmdline_args):
        raise NotImplementedError()

    def publish_docs(self):
        # build_dir = docs_dir.child(ctx.build_dir_name)
        build_dir = self.out_path
        if build_dir.exists():
            docs_dir = self.src_path
            # name = '%s_%s' % (ctx.project_name, docs_dir.name)
            # dest_url = ctx.docs_rsync_dest % name
            if "%" in self.ctx.docs_rsync_dest:
                name = '%s_%s' % (self.ctx.project_name, docs_dir.name)
                dest_url = self.ctx.docs_rsync_dest % name
            else:
                dest_url = self.ctx.docs_rsync_dest.format(
                    prj=self.ctx.project_name, docs=docs_dir.name)
            self.publish_doc_tree(build_dir, dest_url)

    def publish_doc_tree(self, build_dir, dest_url):
        with cd(build_dir):
            args = ['rsync', '-e', 'ssh', '-r']
            args += ['--verbose']
            args += ['--progress']  # show progress
            args += ['--delete']  # delete files in dest
            args += ['--times']  # preserve timestamps
            args += ['--exclude', '.doctrees']
            args += ['./']  # source
            args += [dest_url]  # dest
            cmd = ' '.join(args)
            must_confirm("%s> %s" % (build_dir, cmd))
            self.ctx.run(cmd, pty=True)


            

class SphinxTree(DocTree):
    """
    Requires Sphinx.
    """
    def __init__(self, ctx, src_path):
        super(SphinxTree, self).__init__(ctx, src_path)
        self.out_path = self.src_path.child(ctx.build_dir_name)
        
    def build_docs(self, *cmdline_args):
        docs_dir = self.src_path
        print("Invoking Sphinx in in directory %s..." % docs_dir)
        builder = 'html'
        if self.ctx.use_dirhtml:
            builder = 'dirhtml'
        self.sphinx_build(builder, docs_dir, cmdline_args)
        self.sync_docs_data(docs_dir)
        
    def sphinx_build(self, builder, docs_dir,
                     cmdline_args=[], language=None, build_dir_cmd=None):
        ctx = self.ctx
        args = ['sphinx-build', '-b', builder]
        args += cmdline_args
        # ~ args += ['-a'] # all files, not only outdated
        # ~ args += ['-P'] # no postmortem
        # ~ args += ['-Q'] # no output
        # build_dir = docs_dir.child(ctx.build_dir_name)
        # build_dir = Path(ctx.build_dir_name)
        build_dir = self.out_path
        if language is not None:
            args += ['-D', 'language=' + language]
            # needed in select_lang.html template
            args += ['-A', 'language=' + language]
            if language != ctx.languages[0]:
                build_dir = build_dir.child(language)
                # print 20130726, build_dir
        if ctx.tolerate_sphinx_warnings:
            args += ['-w', 'warnings_%s.txt' % builder]
        else:
            args += ['-W']  # consider warnings as errors
            # args += ['-vvv']  # increase verbosity
        # args += ['-w'+Path(ctx.root_dir,'sphinx_doctest_warnings.txt')]
        args += ['.', build_dir]
        cmd = ' '.join(args)
        with cd(docs_dir):
            ctx.run(cmd, pty=True)
        if build_dir_cmd is not None:
            with cd(build_dir):
                ctx.run(build_dir_cmd, pty=True)

    def sync_docs_data(self, docs_dir):
        ctx = self.ctx
        # build_dir = docs_dir.child(ctx.build_dir_name)
        build_dir = self.out_path
        for data in ('dl', 'data'):
            src = docs_dir.child(data).absolute()
            if src.isdir():
                target = build_dir.child('dl')
                target.mkdir()
                cmd = 'cp -ur %s %s' % (src, target.parent)
                ctx.run(cmd, pty=True)
        if False:
            # according to http://mathiasbynens.be/notes/rel-shortcut-icon
            for n in ['favicon.ico']:
                src = docs_dir.child(n).absolute()
                if src.exists():
                    target = build_dir.child(n)
                    cmd = 'cp %s %s' % (src, target.parent)
                    ctx.run(cmd, pty=True)



class NikolaTree(DocTree):
    """Requires Nikola. 

    Note that Nikola requires::

        $ sudo apt install python-gdbm

    """
    def __init__(self, ctx, src_path):
        super(NikolaTree, self).__init__(ctx, src_path)
        self.out_path = self.src_path.child('output')
        
    def build_docs(self, *cmdline_args):
        docs_dir = self.src_path
        print("Invoking nikola build in in %s..." % docs_dir)
        args = ['nikola', 'build']
        args += cmdline_args
        cmd = ' '.join(args)
        with cd(docs_dir):
            self.ctx.run(cmd, pty=True)
        
        
def get_doc_trees(ctx):
    """Yield one DocTree instance for every item of this project's
    :envvar:`doc_trees`.

    """
    for rel_doc_tree in ctx.doc_trees:
        if isinstance(rel_doc_tree, six.string_types):
            yield SphinxTree(ctx, rel_doc_tree)
        elif isinstance(rel_doc_tree, tuple):
            # (BUILDER, PATH)
            clparts = rel_doc_tree[0].split('.')
            cl = import_module(clparts[0])
            for k in clparts[1:]:
                cl = getattr(cl, k)
            yield cl(ctx, rel_doc_tree[1])


