# -*- coding: utf-8 -*-
# Copyright 2011-2017 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""This Sphinx extension defines the :rst:dir:`blogger_year` and
:rst:dir:`blogger_index` directives.

Usage: add the following to your `conf.py`::

  extensions += ['atelier.sphinxconf.blog']

And usually this file structure:

- docs/blog/index.rst --> contains a main_blogindex directive (hidden toctree)
    
Individual blog entries, including yearly directories and
`index.rst` files, are automatically created by :cmd:`inv blog`,
leading to a file structure like this:
    
- docs/blog/2013/index.rst --> contains a :rst:dir:`blogger_year` directive
- docs/blog/2013/0107.rst --> a blog entry
- docs/blog/2010/0107.rst
   
Thanks to

- `Creating reStructuredText Directives
  <http://docutils.sourceforge.net/docs/howto/rst-directives.html>`_

"""
# from past.builtins import cmp
from builtins import str
# from builtins import map
# from builtins import range
# from builtins import object

import os
import calendar
import datetime

import jinja2

from babel.dates import format_date

from .insert_input import InsertInputDirective
from atelier.rstgen import toctree


def monthname(n, language):
    """
    Return the monthname for month # n in specified language.
    """
    d = datetime.date(2013, n, 1)
    return format_date(d, "MMMM", locale=language)


templates = dict()
templates['calendar.rst'] = """
====
{{year}}
====

{{intro}}

.. |br| raw:: html

   <br />   

.. |sp| raw:: html

   <span style="color:white;">00</span>

{{calendar}}


"""

JINJA_ENV = jinja2.Environment(
    #~ extensions=['jinja2.ext.i18n'],
    loader=jinja2.DictLoader(templates))


class BloggerYear(object):

    """A :class:`BloggerYear` instance is created for each `blogger_year`
    directive.

    """

    def __init__(self, env):
        """
        :docname: the name of the document containing the `main_blogindex` directive
        :starting_year: all years before this year will be pruned
        """

        blogname, year, index = env.docname.rsplit('/', 3)
        if index != 'index':
            raise Exception(
                "Allowed only in /<blogname>/<year>/index.rst files")
        self.blogname = blogname
        self.year = int(year)

        #~ print "20130113 Year.__init__", blogname, self.year
        #~ self.blogname = blogname
        self.days = []
        self.dates = set()
        #~ self.years = set()
        #~ self.starting_year = int(starting_year)
        top = os.path.dirname(env.doc2path(env.docname))
        #~ print top
        for (dirpath, dirnames, filenames) in os.walk(top):
            del dirnames[:]  # don't descend another level
            #~ unused, year = dirpath.rsplit(os.path.sep,2)
            #~ year = int(year)
            #~ assert year in self.years
            d = None
            for fn in sorted(filenames):
                if fn.endswith('.rst'):
                    docname = fn[:-4]
                    if docname == "index":
                        continue
                    if len(fn) == 8:
                        d = docname_to_day(self.year, docname)
                        self.days.append(d)
                        self.dates.add(d.date)
                        #~ self.years.add(s)
                    elif d is not None:
                        d.docnames.append(docname)

        #~ self.years = sorted(self.years)
        if not hasattr(env, 'blog_instances'):
            env.blog_instances = dict()
        years = env.blog_instances.setdefault(blogname, dict())
        years[self.year] = self


def docname(y):
    assert isinstance(y, BloggerYear)
    return "/" + y.blogname + "/" + str(y.year) + "/index"


def navigator(years, current):
    chunks = []
    for y in years:
        if y == current:
            chunks.append(str(y.year))
        else:
            chunks.append(
                ":doc:`{0} <{1}>`".format(y.year, docname(y)))
    old = ' '.join(chunks)
    return "\n\n{0}\n\n".format(old)


def get_blogger_years(env, blogname):
    blog_instances = getattr(env, 'blog_instances', dict())
    blog = blog_instances.get(blogname)
    if blog is None:
        return []
    years = list(blog.values())

    years.sort(key=lambda f: f.year)
    return years


class MainBlogIndexDirective(InsertInputDirective):
    """
    Directive to insert a blog master archive page toctree
    """
    #~ required_arguments = 1
    #~ allow_titles = True
    raw_insert = True

    def get_rst(self):
        #~ print 'MainBlogIndexDirective.get_rst()'
        env = self.state.document.settings.env
        blogname, index = env.docname.rsplit('/', 2)
        if index != 'index':
            raise Exception("Allowed only inside index.rst file")
        text = ''
        years = get_blogger_years(env, blogname)
    
        hidden = []
        visible = []

        # for y in years:
            # text += "\n    {0}/index".format(blogger_year.year)
            # visible.append(str(blogger_year.year) + "/index")
        if len(years) > 1:
            hidden = years[:-1]
            visible = years[-1:]
        else:
            visible = years

        text += navigator(years, None)

        text += '\n'.join(self.content)
        if len(years) == 0:
            text += "\n\nNo blogger years found.\n"
        else:
            children = list(map(docname, years))
            text += toctree(*children, hidden=True)

        # if len(hidden):
        #     children = map(docname, hidden)
        #     text += toctree(*children, hidden=True)
        # if len(visible):
        #     children = map(docname, visible)
        #     text += toctree(*children, maxdepth=2)
        # text += "\n"
        #~ print text
        return text


class YearBlogIndexDirective(InsertInputDirective):

    """
    Directive to insert a year's calendar
    """
    #~ required_arguments = 1
    #~ allow_titles = True
    raw_insert = True

    def get_rst(self):

        env = self.state.document.settings.env
        today = datetime.date.today()

        blogger_year = BloggerYear(env)
        years = get_blogger_years(env, blogger_year.blogname)
        tpl = JINJA_ENV.get_template('calendar.rst')

        intro = navigator(years, blogger_year)
        intro += '\n'.join(self.content)

        text = ''
        cal = calendar.Calendar()
        for month in range(1, 13):

            text += """
            
.. |M%02d| replace::  **%s**""" % (month, monthname(month, self.language))

            weeknum = None
            #~ text += "\n  |br| Mo Tu We Th Fr Sa Su "
            for day in cal.itermonthdates(blogger_year.year, month):
                iso_year, iso_week, iso_day = day.isocalendar()
                if iso_week != weeknum:
                    text += "\n  |br|"
                    weeknum = iso_week
                if day.month == month:
                    label = "%02d" % day.day
                    docname = "%02d%02d" % (day.month, day.day)
                    # if blogger_year.year == iso_year and day in blogger_year.days:
                    if day in blogger_year.dates:
                        text += " :doc:`%s <%s>` " % (label, docname)
                    elif day > today:
                        text += ' |sp| '
                    else:
                        text += ' ' + label + ' '
                else:
                    text += ' |sp| '

        text += """
        
===== ===== =====
|M01| |M02| |M03|
|M04| |M05| |M06|
|M07| |M08| |M09|
|M10| |M11| |M12|
===== ===== =====
        
        """

        text += """

.. rubric:: {0}

.. toctree::
    :maxdepth: 2
    
""".format("All entries:")

        for day in blogger_year.days:
            for docname in day.docnames:
                text += ("\n    " + docname)
    #         text += """
    # %02d%02d""" % (day.month, day.day)

        return tpl.render(
            calendar=text,
            intro=intro,
            year=blogger_year.year)
            # days=blogger_year.days)

class BloggerDay(object):
    def __init__(self, docname, *args, **kwargs):
        self.docnames = [docname]
        self.date = datetime.date(*args, **kwargs)

def docname_to_day(year, s):
    #~ print fn
    month = int(s[:2])
    day = int(s[2:])
    return BloggerDay(s, year, month, day)


#~ class ChangedDirective(InsertInputDirective):

    #~ def get_rst(self):
        #~ env = self.state.document.settings.env
        #~ blogname, year, monthday = env.docname.rsplit('/',3)
        # ~ # raise Exception("Allowed only in blog entries")

        #~ year = int(year)
        #~ day = docname_to_day(year,monthname)

        #~ if not hasattr(env,'changed_items'):
            #~ env.changed_items = dict()
        #~ env.changed_items
        #~ for item in self.content:
            #~ entries = env.changed_items.setdefault(item,dict())
            #~ entries.setdefault(env.docname)


def setup(app):
    #~ app.add_node(blogindex)
    #~ app.add_node(blogindex,html=(visit_blogindex,depart_blogindex))
    #~ app.add_directive('changed', ChangedDirective)
    # app.add_config_value('blog_instances', dict(), '')
    app.add_directive('blogger_year', YearBlogIndexDirective)
    app.add_directive('blogger_index', MainBlogIndexDirective)
