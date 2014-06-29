# -*- coding: utf-8 -*-
# Copyright 2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""Adds some css styling to your logo so that it's widths is set to
100px.

"""

from unipath import Path


def builder_inited(app):
    mydir = Path(__file__).parent.child('static').absolute()
    app.config.html_static_path.append(mydir)


def setup(app):
    app.add_stylesheet('centeredlogo.css')
    app.connect('builder-inited', builder_inited)

