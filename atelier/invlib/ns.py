# -*- coding: UTF-8 -*-
# Copyright 2016-2017 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.

from atelier.invlib import MyCollection
from . import tasks

ns = MyCollection.from_module(tasks)
configs = dict(
    demo_projects=[],
    prep_command="python manage.py prep --noinput --traceback")
ns.configure(configs)

