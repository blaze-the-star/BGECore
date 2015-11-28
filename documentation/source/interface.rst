Interface
=========
This module is the one that generates events for widgets and buttons that you use in
your :file:`data/script/GUI` file or packge.

	**Shortcuts:**
	:class:`core.interface.window.Window`,
	:class:`core.interface.button.Button`,
	:class:`core.interface.button.TextButton`,
	:class:`core.interface.button.Menu`,
	:class:`core.interface.button.TextMenu`
	
.. automodule:: core.interface
	:members:
    
Window
--------
.. autoclass:: core.interface.window.Window
	:members:

Widget
--------
.. autoclass:: core.interface.widget.Widget
	:members:
	
Buttons
--------
.. inheritance-diagram:: Button TextButton
	:parts: 1
.. autoclass:: core.interface.button.Button
	:members:
	:inherited-members:

.. autoclass:: core.interface.button.TextButton
	:members:
	:inherited-members:
	
Menus
--------
.. inheritance-diagram:: Menu TextMenu
	:parts: 1

.. autofunction:: core.interface.button.menuMove
.. autofunction:: core.interface.button.menuMoveWithCursor
.. autofunction:: core.interface.button.menuScale

.. autoclass:: core.interface.button.Menu
	:members:
	
.. autoclass:: core.interface.button.TextMenu
	:members:
	
Labels
--------
.. inheritance-diagram:: label
	:parts: 1
.. automodule:: core.interface.label
	:members:
	
.. _align-constant:

Alignation Constants
~~~~~~~~~~~~~~~~~~~~~

``core.interface.label.ALIGN_LEFT``
``core.interface.label.ALIGN_CENTER``
``core.interface.label.ALIGN_RIGHT``
