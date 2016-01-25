Interface
=========
This module is the one that generates events for widgets and buttons that you use in
your :file:`data/script/GUI` file or packge.

	**Shortcuts:**
	:class:`core.interface.Window`,
	:class:`core.interface.Button`,
	:class:`core.interface.TextButton`,
	:class:`core.interface.Menu`,
	:class:`core.interface.TextMenu`
	
.. automodule:: core.interface
	:members:

Window
--------
.. currentmodule:: core.interface.window

.. autoclass:: core.interface.window.Window
	:members:

Cursor
~~~~~~~~
.. autoclass:: core.interface.window.ImageCursor
	:members:

Widget
--------
.. currentmodule:: core.interface.widget

.. autoclass:: core.interface.widget.Widget
	:members:
	
.. currentmodule:: core.interface
	
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

When extending menus you can overwritte new class attributes to apply the same arguments to all instances of that menu, e.j:

.. code-block:: python

	from core import module, interface
	gui = module.scene_gui_behavior
	
	[...]
		MyTextMenu(0, "MButton1", "Button One")
		MyTextMenu(1, "MButton2", "Button Two")
	
	class MyTextMenu(interface.TextMenu):
		over = gui.objects["MButtonOver"]
		font = "Amble"
		size = 32
		align = interface.label.ALIGN_LEFT
		
		def select(self):
			if self.index == 0: print("Clicked the first button.")
			else: print("Clciked the " + str(self.index) + "button.")


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
