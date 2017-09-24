# -*- coding: UTF-8 -*-
# Copyright 2016-2017 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.
"""A little hack for Lino developers who also have non-Lino projects.

Because otherwise commands like :cmd:`pp inv prep` would fail on
non-Lino projects because they wouldn't know what :cmd:`inv prep`
means.

"""

from .ns import ns

# from invoke import task

# @task(name='prep')
# def prep(ctx, *args, **kwargs):
#     """Does nothing. """

# ns.add_task(prep)
