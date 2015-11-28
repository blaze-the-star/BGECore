Media
=========
This module contains useful objects for easy us of video and audio.

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

.. autoclass:: AudioFile
	:members: