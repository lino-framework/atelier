# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.
raise Exception("""
Backwards-incompatible new syntax for :xfile:`tasks.py` files.

Before::

    from atelier.invlib.ns import ns
    ns.setup_from_tasks(globals(), ...)

After::

    from atelier.invlib import setup_from_tasks
    ns = setup_from_tasks(globals(), ...)


""")
# from atelier.invlib import MyCollection
# from . import tasks
#
# ns = MyCollection.from_module(tasks)
