===========
The Sheller
===========

>>> from atelier.sheller import Sheller
>>> shell = Sheller('.')
>>> shell('inv prep --foo')
No idea what '--foo' is!

>>> shell('inv prep')
<BLANKLINE>
