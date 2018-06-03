# -*- coding: UTF-8 -*-
# Copyright 2017-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.

"""Utilities for atelier.invlib

"""

from __future__ import print_function
from __future__ import unicode_literals

from invoke.exceptions import Exit

from atelier.utils import confirm, cd


def must_confirm(*args, **kwargs):
    if not confirm(''.join(args)):
        raise Exit("User failed to confirm.")


def must_exist(p):
    if not p.exists():
        raise Exception("No such file: %s" % p.absolute())




class DocTree(object):
    """
    Base class for a doctree descriptor.  Atelier currently supports
    `Sphinx <http://www.sphinx-doc.org/en/stable/>`__ and `Nikola
    <https://getnikola.com/>`__ docs.
    """
    src_path = None
    out_path = None
    has_intersphinx = False
    
    def __init__(self, prj, rel_doc_tree):
        self.rel_path = rel_doc_tree
        self.prj = prj
        
        if rel_doc_tree in ('', '.'):
            src_path = prj.root_dir
        else:
            src_path = prj.root_dir.child(rel_doc_tree)
        # The src_path may not exist if this is on a Project which
        # has been created from a normally installed main_package
        # (because there is has no source code).
        if src_path.exists():
            self.src_path = src_path
        
    def build_docs(self, ctx, *cmdline_args):
        raise NotImplementedError()

    def publish_docs(self, ctx):
        # build_dir = docs_dir.child(ctx.build_dir_name)
        if self.src_path is None:
            return
        build_dir = self.out_path
        if build_dir.exists():
            docs_dir = self.src_path
            # name = '%s_%s' % (ctx.project_name, docs_dir.name)
            # dest_url = ctx.docs_rsync_dest % name
            if "%" in ctx.docs_rsync_dest:
                name = '%s_%s' % (ctx.project_name, docs_dir.name)
                dest_url = ctx.docs_rsync_dest % name
            else:
                dest_url = ctx.docs_rsync_dest.format(
                    prj=ctx.project_name, docs=docs_dir.name)
            self.publish_doc_tree(ctx, build_dir, dest_url)

    def publish_doc_tree(self, ctx, build_dir, dest_url):
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
            # must_confirm("%s> %s" % (build_dir, cmd))
            ctx.run(cmd, pty=True)


class SphinxTree(DocTree):
    """
    The default docs builder using Sphinx.

    :cmd:`sphinx-build`

    .. command:: sphinx-build

        http://www.sphinx-doc.org/en/stable/invocation.html#invocation-of-sphinx-build

    
    
    """
    has_intersphinx = True
    
    def __init__(self, prj, src_path):
        super(SphinxTree, self).__init__(prj, src_path)
        if self.src_path is None:
            return
        cfg = prj.config
        self.out_path = self.src_path.child(cfg['build_dir_name'])
        
    def build_docs(self, ctx, *cmdline_args):
        if self.src_path is None:
            return
        docs_dir = self.src_path
        print("Invoking Sphinx in directory %s..." % docs_dir)
        builder = 'html'
        if ctx.use_dirhtml:
            builder = 'dirhtml'
        self.sphinx_build(ctx, builder, docs_dir, cmdline_args)
        self.sync_docs_data(ctx, docs_dir)
        
    def sphinx_build(self, ctx, builder, docs_dir,
                     cmdline_args=[], language=None, build_dir_cmd=None):
        if self.out_path is None:
            return
        # args = ['sphinx-build', builder]
        args = ['sphinx-build', '-b', builder]
        args += ['-T'] # show full traceback on exception
        args += cmdline_args
        # ~ args += ['-a'] # all files, not only outdated
        # ~ args += ['-P'] # no postmortem
        # ~ args += ['-Q'] # no output
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
        print("Invoke {}".format(cmd))
        with cd(docs_dir):
            ctx.run(cmd, pty=True)
        if build_dir_cmd is not None:
            with cd(build_dir):
                ctx.run(build_dir_cmd, pty=True)

    def sync_docs_data(self, ctx, docs_dir):
        # build_dir = docs_dir.child(ctx.build_dir_name)
        if self.src_path is None:
            return
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
        if self.src_path is None:
            return
        self.out_path = self.src_path.child('output')
        
    def build_docs(self, ctx, *cmdline_args):
        if self.src_path is None:
            return
        docs_dir = self.src_path
        print("Invoking nikola build in in %s..." % docs_dir)
        args = ['nikola', 'build']
        args += cmdline_args
        cmd = ' '.join(args)
        with cd(docs_dir):
            ctx.run(cmd, pty=True)
        
        
