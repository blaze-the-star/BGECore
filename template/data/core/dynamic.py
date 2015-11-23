from core import utils, module
from bge import logic

#LibLoad
def loadIntoScene(filepath, mode, camera):
	""" Loads an blend dinamically.
	
	Blends loaded with this method must have only 1 scene. They also need to have a Python controller conected with an always on module mode with the following string: ``main.libload``.
	This logic bricks are recomended to be used in an object that clearly is the main object of the scene or a camera if any.
	
	:param string filepath: Relative path from the *data* folder where the blend file is placed.
	:param mode: The same mode that will be used on ``bge.logic.LibLoad()``, it's recomended to use "Scene".
	:param camera: The main camera of the scene (where logic bricks are used).
	:type camera: |KX_GameObject|
	"""
	path = logic.expandPath("//../data/" + filepath)
	scene_to = camera.scene
	if scene_to == module.scene_gui:
		logic.LibLoad(path, mode, load_actions = True, load_scripts = False)
	elif scene_to == module.scene_game:
		module.libload_queue.append((path, mode))
		camera.sensors["Always"].usePosPulseMode=1
	else: utils.debug("utils.loadIntoScene failed, the scene " + scene_to.name + " is not running.")
	
	
_change_scene_name = ""
_change_scene_path = ""
def loadScene(filepath, name):
	global _change_scene_name
	global _change_scene_path
	
	if module.change_scene_dynamic == False:
		module.change_scene_dynamic = True
		utils.setScene("Dynamic")
		_change_scene_name = name
		_change_scene_path = filepath
		module.change_scene_dynamic_state = 1
		return
		
	#Once scene is loaded
	else:
		if name or filepath: return
		
	name = _change_scene_name
	scene = utils.getSceneByName("Dynamic")
	if not scene: return
	
	state = module.change_scene_dynamic_state
	if state == 1:
		module.change_scene_dynamic_state += 1
		module.scene_game = scene
		loadIntoScene(_change_scene_path, "Scene", scene.active_camera)
		return
	
	if state == 3: #+1 on main.libload
		module.change_scene_dynamic_state = 0
	
	module.change_scene_frame = False
	module.change_scene_dynamic = False

	if name in module.scene_behavior_dict:
		module.scene_behavior = (module.scene_behavior_dict[name])()
		b = module.scene_behavior
		b.scene = scene
		for ob in scene.objects: b.objects[ob.name] = ob
		b.init()
		b.baseInit()
		for bh in b.behaviors: bh.init()