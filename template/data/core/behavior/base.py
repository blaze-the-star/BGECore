_argn = 0
_lastb = None
class Object():
	"""
		Use :meth:`Scene.addBehavior` to construct this behavior.
	
		:param object: Object to apply this behavior on.
		:type object: |KX_GameObject| or String
		
		.. attribute:: obj
			
			The object that this behavior is being applied to.
			
			:type: |KX_GameObject|
			
		.. attribute:: scene
		
			The scene that's using this behavior. Typically :obj:`core.module.scene_game`
			
			:type: |KX_Scene|
			
		
	"""

	def __init__(self, object):
		self.obj = object
		self.scene = object.scene
		self.paused = False
		self.use_keyboard = False
		self._immuse_keyboard = True
		
	def init(self):
		""" Override this with your behavior initialization. """
		pass
		
	def update(self):
		""" Override this with your behavior update (each frame). """
		pass
		
	def argument(self, arg):
		""" Prints a fancy text if *arg* is ``None``. """
		global _argn, _lastb
		_argn += 1
		if arg == None: raise Exception("(Init failed on " + self.__class__.__name__ + " behavior) Argument " + str(_argn) + " is missing.")
		if _lastb and _lastb != self: _argn = 0
		_lastb = self
		
	def onKeyDown(self, keys):
		""" Called when a key is pressed, includes mouse and joystick keys.
		
		:param list keys: A list of the keys that have been pressed during this logic tic.
		
		.. note:: You need to call ``module.enableInputFor(self)`` in order to use this event.
		
		"""
		pass
		
	def onKeyPressed(self, keys):
		""" Called when a key is being pressed, includes mouse and joystick keys.
		
		:param list keys: A list of the keys that are beeing pressed during this logic tic.
		
		.. note:: You need to call ``module.enableInputFor(self)`` in order to use this event.
		
		"""
		pass
	
	def onKeyUp(self, keys):
		""" Called when a key is released, includes mouse and joystick keys.
		
		:param list keys: A list of the keys that have been released during this logic tic.
		
		.. note:: You need to call ``module.enableInputFor(self)`` in order to use this event.
		
		"""
		pass
		
class Scene():
	""" Scene behavior. Each scene can have one, the GUI scene must. This behavior is automatically instancied when the scene is loaded. """
	
	def __init__(self):
		self.behaviors = []
		self.paused = False
		self.use_keyboard = True
		self._immuse_keyboard = True
		self.sun_position = None
		self.scene = None
		self.objects = {}
		self.objectsInactive = {}
		
	def init(self):
		""" Override this with your behavior initialization. """
		pass
	
	def baseInit(self):
		self.sun_position = None
		if "Sun" in self.scene.objects: self.sun_position = self.scene.objects["Sun"].worldPosition.copy()
	
	def update(self):
		""" Override this with your behavior update (each frame). """
		pass
		
	#Like "update" but for preseted behaviors.
	def baseUpdate(self):
		if "Sun" in self.scene.objects:
			self.scene.objects["Sun"].worldPosition = self.scene.active_camera.worldPosition + self.sun_position
		if "Sky" in self.scene.objects:
			self.scene.objects["Sky"].worldPosition = self.scene.active_camera.worldPosition
		
	def onKeyDown(self, keys):
		""" Called when a key is pressed, includes mouse and joystick keys.
		
		:param list keys: A list of the keys that have been pressed during this logic tic.
		
		.. note:: You need to call ``module.enableInputFor(self)`` in order to use this event.
		
		"""
		pass
		
	def onKeyPressed(self, keys):
		""" Called when a key is being pressed, includes mouse and joystick keys.
		
		:param list keys: A list of the keys that are beeing pressed during this logic tic.
		
		.. note:: You need to call ``module.enableInputFor(self)`` in order to use this event.
		
		"""
		pass
	
	def onKeyUp(self, keys):
		""" Called when a key is released, includes mouse and joystick keys.
		
		:param list keys: A list of the keys that have been released during this logic tic.
		
		.. note:: You need to call ``module.enableInputFor(self)`` in order to use this event.
		
		"""
		pass
		
	def onExit(self):
		""" Called when exiting the behavior. Usually when the scene is being replaced or deleted. """
		pass
		
	def addBehavior(self, Behavior, obj):
		""" Adds an object behavior to a given object.
			
			:param behavior.Object Behavior: The behavior to use.
			:param obj: The obj that will have this behavior.
			:type obj: |KX_GameObject| or string
		"""
		
		if type(obj) is str:
			try:
				obj = self.scene.objects[obj]
				if obj == None: raise Exception()
			except: obj = self.scene.objectsInactive[obj]
		b = Behavior(obj)
		self.behaviors.append(b)
		return b
		
	def removeBehavior(self, behavior):
		""" """
		self.behaviors.remove(behavior)