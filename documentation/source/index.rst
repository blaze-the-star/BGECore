Welcome to BGECore's documentation!
===================================
BGECore is a framework for BGE games. It makes Python the main system for adding logic to your games and changes completly the way Blender games are made. BGECore also provides common features to any kind of game so that you don't have to reinvent the wheel. 

BGECore Framework can be downloaded or cloned from GitHub at `https://github.com/elmeunick9/BGECore/
<https://github.com/elmeunick9/BGECore/>`_.

Contents:

.. toctree::
   :maxdepth: 2
   
   behavior
   interface
   utils
   media
   sequencer
   dynamic   
   
Module
==================
The ``core.module`` module provides acces to important references that can be used anywere.

.. data:: core.module.scene_gui
	
	The ``KX_Scene`` of the GUI.

.. data:: core.module.scene_game
	
	The ``KX_Scene`` of the game, or ``None``.
	
.. data:: core.module.scene_gui_behavior
	
	The ``bahavior.Scene`` of the GUI.
	
.. data:: core.module.scene_behavior
	
	The ``behavior.Scene`` of the game scene or ``None``.
	
.. data:: core.module.window

	Reference to :data:`core.interface.window`.

.. data:: core.module.labels
	
	A dictionary providing acces to the Label instances of replaced Text Objects using their original name. Labels created manually won't be added to this dictionary. It works for both ``core.interface.label.Label`` and ``core.interface.flabel.FLabel``.
	
.. data:: core.module.low_frequency_callbacks

	A list of functions that will be called after each ``LOW_FREQUECY_TICK``. Functions are called with the argument ``time``, a float representing the amount of time since the last call.
	
.. data:: core.module.height_frequency_callbacks

	A list of functions that will be called after each ``HEIGHT_FREQUECY_TICK``. Functions are called with the argument ``time``, a float representing the amount of time since the last call.
	
.. data:: core.module.is_standalone

	True if BGE is running in standalone mode, False if it's running in embedded mode.
	
.. function:: enableInputFor (behavior)

	Enables input events on a specific behavior.

.. function:: enableInputForGUI ()

	Enables input events on the GUI behavior.
	
.. function:: disableInputFor (behavior)

	Disables input events on a specific behavior.

.. function:: disableInputForGUI ()

	Disables input events on the GUI behavior.	
	
   
Indices and tables
==================
* :ref:`genindex`
* :ref:`search`