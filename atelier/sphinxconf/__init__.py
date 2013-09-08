# -*- coding: utf-8 -*-
## Copyright 2011-2013 by Luc Saffre.
## License: BSD, see LICENSE for more details.
"""

Sphinx setup used to build the Lino documentation.

Thanks to 

- `Creating reStructuredText Directives 
  <http://docutils.sourceforge.net/docs/howto/rst-directives.html>`_


"""

import logging
logger = logging.getLogger(__name__)

  
import os
import sys
import calendar
import datetime
from StringIO import StringIO
import inspect

from unipath import Path

from docutils import nodes, utils
from docutils import statemachine
from docutils.parsers.rst import directives
from docutils.parsers.rst import roles
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util.nodes import split_explicit_title

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

import atelier
from atelier import rstgen

from atelier.utils import i2d


#~ class ScreenshotDirective(directives.images.Image):
    #~ """
    #~ Directive to insert a screenshot.
    #~ """
    #~ def run(self):
        #~ assert len(self.arguments) == 1
        #~ # name = '/../gen/screenshots/' + self.arguments[0]
        #~ name = '/gen/screenshots/' + self.arguments[0]
        #~ self.arguments = [name]
        #~ (image_node,) = directives.images.Image.run(self)
        #~ return [image_node]





def srcref(mod):
    """
    Return the `source file name` for usage by Sphinx's ``srcref`` role.
    Returns None if the source file is empty (which happens e.g. for __init__.py 
    files whose only purpose is to mark a package).
    
    >>> from atelier.sphinxconf import srcref
    >>> from lino.utils import log
    >>> print srcref(log)
    http://code.google.com/p/lino/source/browse/lino/utils/log.py

    >>> from lino import utils
    >>> print srcref(utils)
    http://code.google.com/p/lino/source/browse/lino/utils/__init__.py
    
    >>> from lino.management import commands
    >>> print srcref(commands)
    None

    >>> from lino_welfare.settings import test
    >>> print srcref(test)
    http://code.google.com/p/lino-welfare/source/browse/lino_welfare/settings/test.py

    """
    root_module_name = mod.__name__.split('.')[0]
    root_mod = __import__(root_module_name)
    srcref_url = getattr(root_mod,'srcref_url',None)
    if srcref_url is None:
        return 
    #~ if not mod.__name__.startswith('lino.'): 
        #~ return
    srcref = mod.__file__
    if srcref.endswith('.pyc'):
        srcref = srcref[:-1]
    if os.stat(srcref).st_size == 0:
        return
    #~ srcref = srcref[len(lino.__file__)-17:]
    srcref = srcref[len(Path(root_mod.__file__).ancestor(2))+1:]
    srcref = srcref.replace(os.path.sep,'/')
    return srcref_url % srcref
    
    
    
def coderef_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    has_explicit_title, title, target = split_explicit_title(text)
    try:
        modname, name = target.rsplit('.', 1)
    except ValueError:
        raise Exception("Don't know how to import name %s" % target)
    mod = import_module(modname)
    
    try:
        value = getattr(mod, name,None)
    except AttributeError:
        raise Exception("No name '%s' in module '%s'" % (name, modname))
    #~ raise Exception("20130908 %s " % lines)
    if isinstance(value,type):
        if value.__module__ != modname:
            raise Exception("20130908 %r != %r" % (value.__module__ ,modname))
            
            
    url = srcref(mod) 
    
    lines,line_no = inspect.getsourcelines(value)
    if line_no:
        url += "#" + str(line_no)
    if not has_explicit_title:
        pass
    pnode = nodes.reference(title, title, internal=False, refuri=url)
    return [pnode], []
    
    
def unused_srcref_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    has_explicit_title, title, target = split_explicit_title(text)
    url = srcref(target)
    try:
        full_url = base_url % part
    except (TypeError, ValueError):
        inliner.reporter.warning(
            'unable to expand %s extlink with base URL %r, please make '
            'sure the base contains \'%%s\' exactly once'
            % (typ, base_url), line=lineno)
        full_url = base_url + part
    if not has_explicit_title:
        if prefix is None:
            title = full_url
        else:
            title = prefix + part
    pnode = nodes.reference(title, title, internal=False, refuri=full_url)
    return [pnode], []
    
    


def autodoc_skip_member(app, what, name, obj, skip, options):
    if name != '__builtins__':
        #~ print 'autodoc_skip_member', what, repr(name), repr(obj)
    
        if what == 'class':
            if name.endswith('MultipleObjectsReturned'):
                return True
            if name.endswith('DoesNotExist'):
                return True
                
            #~ if isinstance(obj,ObjectDoesNotExist) \
              #~ or isinstance(obj,MultipleObjectsReturned): 
                #~ return True
        
    #~ if what == 'exception': 
        #~ print 'autodoc_skip_member',what, repr(name), repr(obj), skip
        #~ return True
        

#~ SIDEBAR = """
#~ (This module's source code is available at :srcref:`/%s`)

#~ """  
#~ SIDEBAR = """
#~ (source code: :srcref:`/%s`)

#~ """  

SIDEBAR = """
(:srcref:`source code </%s>`)

"""  

#~ SIDEBAR = """
#~ .. sidebar:: Use the source, Luke

  #~ We generally recommend to also consult the source code.
  #~ This module's source code is available at
  #~ :srcref:`/%s.py`

#~ """  


    
def autodoc_add_srcref(app,what,name,obj,options,lines):
    if what == 'module':
        s = srcref(obj)
        if s:
            #~ srcref = name.replace('.','/')
            s = (SIDEBAR % s).splitlines()
            s.reverse()
            for ln in s:
                lines.insert(0,ln)
            #~ lines.insert(0,'')
            #~ lines.insert(0,'(We also recommend to read the source code at :srcref:`/%s.py`)' % name.replace('.','/'))
    


    
    


class InsertInputDirective(Directive):
    """
    Base class for directives that work by generating rst markup
    to be forwarded to `state_machine.insert_input()`.
    """
    titles_allowed = False
    has_content = True
    debug = False
    raw_insert = False
    
    def get_rst(self):
        raise NotImplementedErrro()
        
    #~ def run(self):
        #~ out = self.get_rst()
        #~ env = self.state.document.settings.env
        #~ if self.debug:
            #~ print env.docname
            #~ print '-' * 50
            #~ print out
            #~ print '-' * 50
        #~ self.state_machine.insert_input(out.splitlines(),out)
        #~ return []
        
    #~ class InsertTableDirective(InsertInputDirective):
    
    def run(self):
        self.env = self.state.document.settings.env
        output = self.get_rst()
        #~ output = output.decode('utf-8')
        
        if self.debug:
            print self.state.document.settings.env.docname
            print '-' * 50
            print output
            print '-' * 50
        
        content = statemachine.StringList(output.splitlines())
        
        if self.raw_insert:
          
            self.state_machine.insert_input(content,output)
            return []
            
        
        if self.titles_allowed:
            node = nodes.section()
            # necessary so that the child nodes get the right source/line set
            node.document = self.state.document
            nested_parse_with_titles(self.state, content, node)
        else:
            node = nodes.paragraph()
            node.document = self.state.document
            self.state.nested_parse(content, self.content_offset, node)


        
        # following lines originally copied from 
        # docutils.parsers.rst.directives.tables.RSTTable 
        #~ title, messages = self.make_title()
        #~ node = nodes.Element()          # anonymous container for parsing
        #~ self.state.nested_parse(content, self.content_offset, node)
        #~ if len(node) != 1 or not isinstance(node[0], nodes.table):
            #~ error = self.state_machine.reporter.error(
                #~ 'Error parsing content block for the "%s" directive: exactly '
                #~ 'one table expected.' % self.name, nodes.literal_block(
                #~ self.block_text, self.block_text), line=self.lineno)
            #~ return [error]
        #~ return [x for x in node]
        return list(node)
        
        #~ table_node = node[0]
        #~ table_node['classes'] += self.options.get('class', [])
        #~ return [table_node] 


    

    
class Py2rstDirective(InsertInputDirective):
    """
    Run a Python code block and interpret the output as if it 
    were rst source.
    """
    titles_allowed = True
    has_content = True
    debug = False
    #~ def get_rst(self):
        #~ return self.output_from_exec('\n'.join(self.content))
        
    def get_context(self): 
        context = dict()
        context.update(self=self)
        context.update(env=self.state.document.settings.env)
        return context
    
    def get_rst(self):
        if not self.content:
            warning = self.state_machine.reporter.warning(
                'Content block expected for the "%s" directive; none found.'
                % self.name, nodes.literal_block(
                self.block_text, self.block_text), line=self.lineno)
            return [warning]
            
        #~ raise Exception("20130331 %r" % self.content)
        code = '\n'.join(self.content)
        return self.output_from_exec(code)        
        
    def output_from_exec(self,code):
        old = sys.stdout
        buffer = StringIO()
        sys.stdout = buffer
        context = self.get_context()
        exec(code,context)
        sys.stdout = old
        s = buffer.getvalue()
        #~ print 20130331, type(s)
        return s
        


class Django2rstDirective(Py2rstDirective):
    def get_context(self):
        #~ from djangosite.dbutils import set_language
        from django.conf import settings
        context = super(Django2rstDirective,self).get_context()
        #~ set_language(lng)
        context.update(settings=settings)
        context.update(settings.SITE.modules)
        return context
        
    def output_from_exec(self,code):
        lng = self.state.document.settings.env.config.language
        from django.utils import translation
        with translation.override(lng):
            return super(Django2rstDirective,self).output_from_exec(code)
        
        
        
#~ class DjangoTableDirective(InsertInputDirective):
    #~ def get_rst(self):
        #~ assert len(self.content) == 1
        #~ code = '\n'.join(self.content)
        
        #~ from django.conf import settings    
        #~ print .jobs.Candidatures.request(limit=5).to_rst()
        
        #~ code = """
        #~ """
        #~ old = sys.stdout
        #~ buffer = StringIO()
        #~ sys.stdout = buffer
        #~ context = dict()
        #~ context.update(settings.SITE.modules)
        #~ context = dict(settings=settings)
        #~ exec(code,context)
        #~ sys.stdout = old
        #~ return buffer.getvalue()
        
class TextImageDirective(InsertInputDirective):
    """
    See :blogref:`20130116` for documentation.
    """
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = dict(scale=directives.unchanged)
    #~ optional_arguments = 4
    
    def get_rst(self):
        #~ print 'MainBlogIndexDirective.get_rst()'
        #~ env = self.state.document.settings.env
        #~ print self.arguments, self.options, self.content
        left = '\n'.join(self.content)
        right = ''
        for arg in self.arguments[0].split():
            right += '.. figure:: %s\n' % arg
            for i in self.options.items():
                right += "  :%s: %s\n" % i
            right += "\n  %s\n\n" % arg
            #~ right += "\n  \n\n" % arg
            
        return rstgen.table(["",""],[[left,right]],show_headers=False)
    
class ComplexTableDirective(InsertInputDirective):
    """
    The `complextable` directive is used to create tables
    with complex cell content
    
    Usage example::
    
      .. complextable::
    
        A1
        <NEXTCELL>
        A2
        <NEXTROW>
        B1
        <NEXTCELL>
        B2
        
    
    Result:
    
    .. complextable::
    
        A1
        <NEXTCELL>
        A2
        <NEXTROW>
        B1
        <NEXTCELL>
        B2
        
        
    See Blog entry 2013/0116 for documentation.
    """
    required_arguments = 0
    final_argument_whitespace = True
    option_spec = dict(header=directives.flag)
    #~ option_spec = dict(scale=unchanged)
    #~ optional_arguments = 4
    
    def get_rst(self):
        #~ print 'MainBlogIndexDirective.get_rst()'
        #~ env = self.state.document.settings.env
        #~ print self.arguments, self.options, self.content
        cellsep = '<NEXTCELL>'
        rowsep = '<NEXTROW>'
        if len(self.arguments) > 0:
            cellsep = self.arguments[0]
        if len(self.arguments) > 1:
            rowsep = self.arguments[1]
        
        content = '\n'.join(self.content)
        rows = []
        colcount = None
        
        for row in content.split(rowsep):
            cells = [cell.strip() for cell in row.split(cellsep)]
            if colcount is None:
                colcount = len(cells)
            else:
                assert colcount == len(cells)
            rows.append(cells)
              
        if 'header' in self.options:
            return rstgen.table(rows[0],rows[1:])
            
        return rstgen.table([""] * colcount,rows,show_headers=False)




def get_blog_url(today):
    """
    Return the URL to your developer blog entry of that date.
    """
    if today.year < 2013: # TODO: make this configurable
        blogger_project = "lino"
        url_root = "http://code.google.com/p/%s/source/browse/" % blogger_project
        parts = ('docs','blog',str(today.year),today.strftime("%m%d.rst"))
        return url_root + "/".join(parts)
    
    #~ url = today.strftime("http://www.lino-framework.org/blog/%Y/%m%d.html")
    if not atelier.BLOG_URL:
        raise Exception("Please set BLOG_URL in your `/etc/atelier/config.py` to something like 'http://www.example.com/blog/%Y/%m%d.html'")
    url = today.strftime(atelier.BLOG_URL)
    return url


def blogref_role(name, rawtext, text, lineno, inliner,options={}, content=[]):
    """
    Inserts a reference to the blog entry of the specified date.
    
    Instead of writing ``:doc:`/blog/2011/0406```
    it is better to write ``:blogref:`20110406```
    because the latter works between Sphinx trees and also supports archived blog entries.
    
    """
    # thanks to http://docutils.sourceforge.net/docs/howto/rst-roles.html
    # this code originally from roles.pep_reference_role
    #~ print 20130315, rawtext, text, utils.unescape(text)
    has_explicit_title, title, target = split_explicit_title(text)
    try:
        date = i2d(int(target))
    except ValueError:
        msg = inliner.reporter.error(
            'Invalid text %r: must be an integer date of style "20130315" .'
            % text, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    #~ print repr(env)
    #~ raise Exception(20130315)
    #~ ref = inliner.document.settings.pep_base_url
           #~ + inliner.document.settings.pep_file_url_template % date)
    roles.set_classes(options)
    #~ from django.conf import settings
    #~ shown_text = settings.SITE.dtos(date)
    env = inliner.document.settings.env        
    if not has_explicit_title:
        title = date.strftime(env.settings.get('today_fmt','%Y-%m-%d'))
    title = utils.unescape(title)
    return [nodes.reference(rawtext, title, 
                            refuri=get_blog_url(date),
                            **options)], []
    



#~ def configure(filename,globals_dict,settings_module_name='settings'):
def configure(globals_dict,settings_module_name=None):
    """
    To be callsed from inside the Sphinx `conf.py` as follows::
    
      from djangosite.utils.sphinxconf import configure
      configure(globals())

    This contains the things that all my Sphinx docs configuration 
    files have in common.
    
    Automatically adds the intersphinx entries 
    for projects managed in this atelier
    by checking for an attribute `intersphinx_mapping` in 
    the global namespace of each project's main module.
    
    
    """
    filename = globals_dict.get('__file__')
    DOCSDIR = Path(filename).parent.absolute()
    sys.path.append(DOCSDIR)
    

    intersphinx_mapping = dict()
    for prj in atelier.load_projects():
        p = prj.root_dir.child('docs','.build','objects.inv')
        #~ p = Path(HGWORK,n,'docs','.build','objects.inv')
        if p.exists():
            #~ intersphinx_mapping[n] = ('http://%s.lino-framework.org' % n,p)
            try:
                intersphinx_mapping[prj.nickname] = (prj.module.intersphinx_url,p)
            except AttributeError:
                logger.warning("No intersphinx_url in %s",prj.module)
                pass
        
    # TODO: make these configurable
    #~ HGWORK = DOCSDIR.ancestor(2)
    #~ p = Path(HGWORK,'welfare','userdocs','.build','fr','objects.inv')
    #~ if p.exists():
        #~ intersphinx_mapping['welfareuserfr'] = ('http://welfare-user.lino-framework.org/fr',p)
        
    # TODO: make these configurable
    HGWORK = Path(__file__).ancestor(4).absolute()
    def f(prj):
        p = Path(HGWORK,prj,'userdocs','.build','objects.inv')
        if p.exists():
            k = '%suser' % prj
            url = 'http://%s-user.lino-framework.org' % prj
            intersphinx_mapping[k] = (url,p)
        else:
            print "No path %s" % p
    f('welfare')
    f('faggio')
    f('patrols')
    
        
        
        
    #~ intersphinx_mapping.update(django = (
        #~ 'http://docs.djangoproject.com/en/dev/', 
        #~ 'http://docs.djangoproject.com/en/dev/_objects/'))
        
    globals_dict.update(intersphinx_mapping=intersphinx_mapping)
    
    globals_dict.update(extensions = [
      'sphinx.ext.autodoc',
      #~ 'sphinx.ext.autosummary',
      'sphinx.ext.inheritance_diagram',
      'sphinx.ext.todo',
      'sphinx.ext.extlinks',
      'sphinx.ext.graphviz',
      'sphinx.ext.intersphinx',
      'sphinxcontrib.newsfeed', # no i18n, no discovery, only one entry per doc, 
      #~ 'sphinx.ext.doctest',
    ])
    
    if settings_module_name is not None:
        #~ os.environ['DJANGO_SETTINGS_MODULE'] = 'north.docs_settings'
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        """
        Trigger loading of Djangos model cache in order to avoid side effects that 
        would occur when this happens later while importing one of the models modules.
        """
        from django.conf import settings
        #~ settings.SITE # must at least access some variable in the settings
        settings.SITE.startup()
    globals_dict.update(setup=setup)

    globals_dict.update(template_bridge = 'atelier.sphinxconf.DjangoTemplateBridge')
    
    globals_dict.update(templates_path = ['.templates',Path(__file__).parent.absolute()])


def setup2(app):
    # also used by `vor/conf.py`
    app.add_directive('complextable', ComplexTableDirective)
    app.add_directive('py2rst', Py2rstDirective)
    app.add_directive('django2rst', Django2rstDirective)
    #~ app.add_directive('linotable', InsertTableDirective)
    
def setup(app):
    """
    The Sphinx setup function used for Lino-related documentation trees.
   
    """
    app.add_object_type(directivename='xfile',rolename='xfile',
      indextemplate='pair: %s; file')
    app.add_object_type(directivename='setting',rolename='setting',
      indextemplate='pair: %s; setting')
    #~ app.add_object_type(directivename='model',rolename='model',
      #~ indextemplate='pair: %s; model')
    #~ app.add_object_type(directivename='field',rolename='field',
      #~ indextemplate='pair: %s; field')
    app.add_object_type(directivename='screenshot',rolename='screen',
      indextemplate='pair: %s; screenshot')
    app.add_object_type(directivename='modattr',rolename='modattr',
      indextemplate='pair: %s; model attribute')
    app.add_object_type(directivename='model',rolename='model',indextemplate='pair: %s; model')
    #app.connect('build-finished', handle_finished)
    
    app.connect('autodoc-skip-member',autodoc_skip_member)
    app.connect('autodoc-process-docstring', autodoc_add_srcref)
    
    app.add_directive('textimage', TextImageDirective)

    app.add_role('coderef', coderef_role)
    
    roles.register_canonical_role('blogref', blogref_role)
    
    setup2(app)
    #~ app.add_directive('screenshot', ScreenshotDirective)
    #~ app.add_config_value('screenshots_root', '/screenshots/', 'html')

    #~ from djangosite.utils import doctest
    #~ doctest.setup(app)
    
#~ print "OK"    


def version2rst(self,m):
    """
    used in docs/released/index.rst
    """
    v = m.__version__
    if v.endswith('+'):
        v = v[:-1]
        print "The current stable release is :doc:`%s`." % v 
        print "We are working on a future version in the code repository."
    elif v.endswith('pre'):
        print "We're currently working on :doc:`%s`." % v[:-3]
    else:
        print "The current stable release is :doc:`%s`." % v 
        #~ print "We're currently working on :doc:`coming`."




#~ from sphinx.application import TemplateBridge

from sphinx.jinja2glue import BuiltinTemplateLoader
#~ class DjangoTemplateBridge(TemplateBridge):
class DjangoTemplateBridge(BuiltinTemplateLoader):
    """
    `template_bridge <http://sphinx-doc.org/config.html#confval-template_bridge>`_ 
    
    Adds a template variable ``settings`` 
    to the Sphinx template context
    (which cannot be done using 
    `html_context <http://sphinx-doc.org/config.html#confval-html_context>`_
    because Django settings are not pickleable.
    """
    def render(self,template, context):
        from django.conf import settings
        context.update(settings=settings)
        return super(DjangoTemplateBridge,self).render(template, context)

    def render_string(self, source, context):
        from django.conf import settings
        context.update(settings=settings)
        return super(DjangoTemplateBridge,self).render_string(source, context)
