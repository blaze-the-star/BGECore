Behaviors
==========

.. currentmodule:: core.behavior
.. code-block:: python

	import core
	key = core.key
	
	from script.behavior.player import ThirdPerson
	
	class MySceneBehavior(core.behavior.Scene):
		def init(self):
			self.b_camera = self.addBehavior(ThirdPerson, "Player")
			core.utils.setFilter2D("ChromaticAberration", self.scene.active_camera, 1)
			core.module.enableInputFor(self)
			
		def update(self):
			pass
			
		def onKeyDown(self, keys):
			if key.W in keys:
				print("W pressed.")
			if key.S in keys:
				print("S pressed.")

	behavior.addScene(MySceneBehavior, "MainScene")
	
.. autofunction:: addScene

Scene Behavior
--------------

.. autoclass:: core.behavior.Scene
	:members:
	
Object Behavior
---------------
	
.. autoclass:: core.behavior.Object
	:members:
	
Preseted Behaviors
------------------

.. autoclass:: core.behavior.camera.MouseLook
	:members:
	