=========================
The `textimage` directive
=========================

.. rst:directive:: textimage

Insert a text and an image side by side.

Usage::

  .. textimage:: 0114a.jpg
    :scale: 40 %
    
    **This is a test**. 
    We start by including a .py file:
    
    .. literalinclude:: 0116a.py
    
    Here are some explanations.

This directive will generate the following intermediate rst markup::
  
  +-----------------------------------+----------------------+
  | **This is a test**.               | .. image:: 0114a.jpg |
  | We start by including a .py file: |   :scale: 40 %       |
  |                                   |                      |
  | .. literalinclude:: 0116a.py      |                      |
  |                                   |                      |
  | Here are some explanations.       |                      |
  +-----------------------------------+----------------------+


... leading to the final result:

.. textimage:: 0114a.jpg
  :scale: 40 %
  
  **This is a test**.
  We start by including a .py file:
  
  .. literalinclude:: 0116a.py
  
  Here are some explanations.
  

Implemented by :class:`atelier.sphinxconf.complex_tables.InsertInputDirective`)
