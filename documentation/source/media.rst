Media
=========
This module contains useful objects for easy use of video and audio.

.. currentmodule:: core.media

.. autodata:: screen
.. autofunction:: showScreen
.. autofunction:: hideScreen

Video
------
.. autoclass:: Screen
	:members:

Audio
------
.. data:: device

	The master device of the audio of the game.
	
	See: `aud.Device <http://www.blender.org/api/blender_python_api_2_76_2/aud.html?highlight=aud.device#aud.Device>`_ (External Link)
	
.. data:: music
	
	Default instance of AudioFile for music.
	
.. data:: sui

	Sound User Interface. A dictionary specific for AudioEffects that will be used on the GUI. Files listed here should be inside the ``data/sound/ui/`` directory.

.. autoclass:: AudioFile
	:members:
	
.. autoclass:: AudioEffect
	:members:
	
.. autoclass:: RandomMusic
	:members: