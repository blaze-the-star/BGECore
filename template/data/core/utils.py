from bge import logic
from mathutils import Vector
from random import randint
from time import sleep
from script import constant
from core import module

def loadGameProperty(name):
	""" Loads a property from your :file:`config.txt` file.
	
		The property is loaded as string, then you use the type name to get the apropiate type.
		*e.j:* ``media.device.volume = float(utils.loadGameProperty("volume"))``
		
		:param string name: Name of the property to load.
		:return: A string containing the value of the property. 
	"""
	path = logic.expandPath("//../config.txt")
	with open(path, "r") as input:
		for l in input.read().splitlines():
			if len(l) == 0: continue
			if l[0] == '#': continue
			
			x = l.find(name)
			y = l.find(": ")
			if x == 0 and y > 0:
				prop = l[y+2:]
				return prop
				
def saveGameProperty(name, value):
	""" TODO """
	pass

#Internal
_sleeptime = 0.0000
_nosleep = False #Susped sleep
_3sleep = 0      #Only do 1 of 3 sleep calls.			
def frameSleep():
	""" Forces a sleep time on BGE to make low-consiming games not melt the CPU. """
	global _nosleep, _3sleep
	avg = logic.getAverageFrameRate()
	if avg < 45: _3sleep = 3
	else: _3sleep = 0
	if avg < 30: _nosleep = True
	else: _nosleep = False
	
	if _sleeptime <= 0 or _nosleep == True: return
	if _3sleep > 1:
		_3sleep -= 1
		return
	if _3sleep == 1: _3sleep = 3
		
	sleep(_sleeptime)
	
#Utils
def debug(text):
	""" Prints *text* if ``CORE_DEBUG_PRINT`` is enabled. """
	if constant.CORE_DEBUG_PRINT == True: print(text)

def verbose(text):
	""" Prints *text* if ``CORE_DEBUG_VERBOSE`` is enabled. """
	if constant.CORE_DEBUG_VERBOSE == True: print(text)
	
def rand10():
	""" Generates a rondom integer from 0 to 9 """
	return randint(0,9)

#3D Math
def vectorFrom2Points(origin, dest, module = None):
	""" Returns a mathutils.Vector  form 2 points in the space.
	
	:param mathutils.Vector origin: Point A
	:param mathutils.Vector dest: Point B
	:param float module: If setted, the returned vector will have this maxium lenght. The new lenght will never be greater than the original.
	"""
	vec = Vector((dest.x - origin.x, dest.y - origin.y, dest.z - origin.z))
	if not module: return vec
	
	l = vec.length
	 
	if l < 0.0125: return vec.zero()
	if l < module: return vec
	
	vec = vec / l
	if module == 1: return vec
	else: return vec * module

def moveObjectToObject(origin, dest, speed = 1):
	""" Moves *origin* to *dest* at a speed of *speed*. Must by called every frame for a complete movement. 
	
	:param KX_GameObject origin: Object to move.
	:param KX_GameObject dest: Destination object.
	:param float speed: The amount of movment to do in one frame.
	:return: True if the object has been moved, false otherwise.
	"""
	return moveObjectToPosition(origin, dest.position, speed)

def moveObjectToPosition(origin, dest, speed = 1):
	""" Moves *origin* to *dest* at a speed of *speed*. Must by called every frame for a complete movement. 
	
	:param KX_GameObject origin: Object to move.
	:param mathutils.Vector dest: Destination object.
	:param float speed: The amount of movment to do in one frame.
	:return: True if the object has been moved, false otherwise.
	"""
	fr = logic.getAverageFrameRate()
	if fr < 20: fr = 20
	vel = speed / fr
	vec = vectorFrom2Points(origin.position, dest, vel) 
	if vec:
		origin.position += vec
		return True
	else: return False
	

#Scene Managment
def getSceneByName(name):
	""" Get a scene by its name. Only works with loaded scenes.
	
	.. deprecated:: 0.3
		Use ``module.scene_game`` or ``module.scene_gui`` instead.
	
	"""
	for scn in logic.getSceneList():
		if scn.name == name: return scn

_change_scene_name = ""
#Changing scene and updating behavior is not easy. First we replace the scene and only when that's done (on the next frame) we update the behavior.
#that's why this function takes actually two or more frames to execute. Setting module._change_scene_frame to true will make the main loop abort any other call
#than this.
def setScene(name):
	"""
	Deletes the game scene (if any) and loads a new one.
	
	.. note::
		The new scene will be initialized on the next logic frame.
	
	:param string name: Name of the scene to load. If none no scene will be loaded, but the current scene will be removed.
	"""
	global _change_scene_name
	
	if module.change_scene_frame == False:
		if module.scene_game == None:
			logic.addScene(name, 0)
		else:
			if module.scene_behavior:
				module.scene_behavior.onExit()
				del module.scene_behavior
				module.scene_behavior = None
			module.scene_game.replace(name)
		if name:
			module.change_scene_frame = True
			_change_scene_name = name
		return

	#From here the scene is already replaced, now is time to initializate.
	if name:
		debug("Multiple calls to utils.setScene(), this call will be ignored.")
		return
	
	name = _change_scene_name
	scene = getSceneByName(name)
	if not scene: return

	module.change_scene_frame = False
	module.scene_game = scene

	if name in module.scene_behavior_dict:
		module.scene_behavior = (module.scene_behavior_dict[name])()
		b = module.scene_behavior
		b.scene = scene
		for ob in scene.objects: b.objects[ob.name] = ob
		b.init()
		b.baseInit()
		for bh in b.behaviors: bh.init()
		
def removeScene():
	""" Removes the game scene. Same functionality that ``setScene(None)``. """
	if not module.scene_behavior: return
	module.scene_behavior.onExit()
	del module.scene_behavior
	module.scene_behavior = None
	module.scene_game.end()
	module.scene_game = None
		
def setCamera(scene, camera_name):
	""" Sets the active_camera of the a scene by another.
	
	.. note::
		Use instead of ``KX_Scene.active_camera = KX_GameObject``.
	
	:param KX_Scene scene: Scene where to change the active camera.
	:param string camera_name: Name of the new active camera.
	"""
	camera = scene.objects[camera_name]
	
	#Spawn camera if in hidden layer?
	#...
	
	scene.active_camera = camera
	if scene == module.scene_gui:
		win = module.window
		win.camera = camera
		win.camera_height = camera.worldPosition.z - 0.5
		win.scx = camera.ortho_scale
		win.scy = camera.ortho_scale * (win.height / win.width)
		
#GLSL 2DFilters
def setFilter2D(name, camera, slot):
	""" Sets or enables a 2DFilter.

	**Default aviable GLSL filters:** Bloom, Vignetting, ChromaticAberration, FXAA.
	
	Some filters may need special game properties, see: *TODO*
	
	:param string name: Name of the filter.
	:param KX_GameObject camera: The main camera of the scene (where logic bricks are used).
	:param integer slot: The slot (Logic Brick Actuator ID) where to apply the filter. Slots are 2DFiletre actuators connected with the Python 
		controller on the main camera. Slots name are prefixed with F, e.j. F0, F1, F2.
	"""
	try:
		try: cont = camera.controllers["Python"]
		except: return
		if cont != logic.getCurrentController():
			module.filter_queue.append((name, camera, slot))
			camera.sensors["Always"].usePosPulseMode=1 
			return
		
		path = logic.expandPath("//core/glsl/" + name + ".filter2D")
		with open(path, "r") as input:
			text = input.read()
		
		filter = camera.actuators["F"+str(slot)]
		filter.mode = logic.RAS_2DFILTER_CUSTOMFILTER
		filter.passNumber = slot
		filter.shaderText = text
		cont.activate(filter)
		verbose("Setted 2D Filter " + name + " to slot " + str(slot))
	except:
		import traceback
		traceback.print_exc()

def removeFilter2D(camera, slot):
	""" Removes a 2DFilter.
	
	:param KX_GameObject camera: The main camera of the scene (where logic bricks are used).
	:param integer slot: The slot.
	"""
	try:
		filter = camera.actuators["F"+str(slot)]
		camera.controllers["Python"].deactivate(filter)
	except:
		import traceback
		traceback.print_exc()
		
#LibLoad
def libLoad(filepath, mode, camera):
	""" Loads an blend dinamically.
	
	Blends loaded with this method must have only 1 scene. They also need to have a Python controller conected with an always on module mode with the following string: ``main.libLoad``.
	This logic bricks are recomended to be used in an object that clearly is the main object of the scene or a camera if any.
	
	:param string filepath: Relative path from the *data* folder where the blend file is placed.
	:param mode: The same mode that will be used on ``bge.logic.LibLoad()``, it's recomended to use "Scene".
	:param KX_GameObject camera: The main camera of the scene (where logic bricks are used).
	"""
	path = logic.expandPath("//../data/" + filepath)
	scene_to = camera.scene
	if scene_to == module.scene_gui:
		logic.LibLoad(path, mode, load_actions = True, load_scripts = False)
	elif scene_to == module.scene_game:
		module.libload_queue.append((path, mode))
		camera.sensors["Always"].usePosPulseMode=1
	else: debug("utils.libLoad failed, the scene provided is not running.")