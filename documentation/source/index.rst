Welcome to BGECore's documentation!
===================================
BGECore is a framework for BGE games. It's meant to be a tool for coders, not for artists. If you are an artist and you still whant to use BGECore you will
have to become also a coder. BGECore not only is the framework but also the design pattern you should use when making your game. This design will help you
to improve the readibility and maintanibility of your code. Please read the BGECore Guide.

Contents:

.. toctree::
   :maxdepth: 2
   
   behavior
   interface
   utils
   media

Module
==================
The ``core.module`` module provides acces to some very important references. This module can be imported from any file without risk of circular dependences.

.. data:: core.module.scene_gui
	
	The ``KX_Scene`` of the GUI.

.. data:: core.module.scene_game
	
	The ``KX_Scene`` of the game, or ``None``.
	
.. data:: core.module.scene_gui_behavior
	
	The ``bahavior.Scene`` of the GUI.
	
.. data:: core.module.scene_game_behavior
	
	The ``behavior.Scene`` of the game scene or ``None``.

.. data:: core.module.labels
	
	A dictionary providing acces to the Label instances of replaced Text Objects using their original name.
	
.. data:: core.module.window

	Reference to :data:`core.interface.window`. 
   
Indices and tables
==================
* :ref:`genindex`
* :ref:`search`