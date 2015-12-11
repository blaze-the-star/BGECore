from core import utils, module
from bge import logic
import time

#LibLoad
def loadIntoScene(filepath, mode, camera):
	""" Loads all objects/meshes/actions from another blend into the scene of the *camera*.

	Blends loaded with this method must have only 1 scene. They also need to have a Python controller conected with an always on module mode with the following string: ``main.libload``.
	This logic bricks are recomended to be used in an object that clearly is the main object of the scene or a camera if any. The name of the library is the filepath.

	:param string filepath: Relative path from the *data* folder where the blend file is placed.
	:param mode: The same mode that will be used on ``bge.logic.LibLoad()``, it's recomended to use "Scene".
	:type mode: "Scene","Mesh" or "Action"
	:param camera: The main camera of the scene (where logic bricks are used).
	:type camera: |KX_GameObject|

	.. note:: Trying to load multiple times the same file will throw an error. Instad use ObjectGenerator
	"""
	path = logic.expandPath("//../data/" + filepath)
	scene_to = camera.scene
	if scene_to == module.scene_gui:
		logic.LibLoad(path, mode, load_actions = True, load_scripts = False)
	elif scene_to == module.scene_game:
		module.libload_queue.append((path, mode))
		module._arecallbacks = True
	else: utils.debug("utils.loadIntoScene failed, the scene " + scene_to.name + " is not running.")

_change_scene_name = ""
_change_scene_path = ""

def loadScene(filepath, name):
	""" Loads a new scene from another blend.

	Blends loaded with this method must have only 1 scene. They also need to have a Python controller conected with an always on module mode with the following string: ``main.libload``.
	This logic bricks are recomended to be used in an object that clearly is the main object of the scene or a camera if any. The name of the library is the filepath.

	:param string filepath: Relative path from the *data* folder where the blend file is placed.
	:param string name: Name of the new scene, used with *behavior.Scene*.
	"""
	global _change_scene_name
	global _change_scene_path

	if module.change_scene_dynamic == False:
		module._started = False
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
		if name in module.scene_behavior_dict:
			module.scene_behavior = (module.scene_behavior_dict[name])()
			b = module.scene_behavior
			b.scene = scene
		loadIntoScene(_change_scene_path, "Scene", scene.active_camera)
		return

	if state == 2: return

	if state == 3: #+1 on main.libload
		module.change_scene_dynamic_state = 0

	module.change_scene_frame = False
	module.change_scene_dynamic = False

	if name in module.scene_behavior_dict:
		b = module.scene_behavior
		for ob in scene.objects: b.objects[ob.name] = ob
		for ob in scene.objectsInactive: b.objectsInactive[ob.name] = ob
		b.init()
		b.baseInit()
		for bh in b.behaviors: bh.init()

def loadLebelEditor():
	""" Loads BGECore Lebel Editor as a new game scene."""
	from core.editor.behavior import SceneEditor
	module.scene_behavior_dict["SceneEditor"] = SceneEditor
	loadScene("core/editor/editor.blend", "SceneEditor")

class ObjectGenerator:
	""" Uses dynamic loading to create new objects from other blend files.

	Now objects created with this method have thier own mesh and properties, usually
	you don't want to do this unless you are going to modify their meshes in realtime.

	If you don't want to modify their meshes in realtime, use KX_Scene.addObject() instead.

	Blends loaded with this method must have only 1 scene. Each object to be loaded needs to have a
	Python controller conected with an always on module mode with the following string: ``main.generator``.

	:param string filepath: Relative path from the *data* folder where the blend file is placed.

	.. attribute:: relative_path

		The relative path from the data folder of the blend used in this generator.

	.. attribute:: path

		The absolute path of the blend used in this generator.

	.. attribute:: objects
		A dictionary containing tupules of the objects loaded. E.j:
		*mygen.objects["ObjName"][id].worldPosition = 0,0,0*

	 """
	all = {}
	time = None

	def __init__(self, filepath):
		self.relative_path = filepath
		self.path = logic.expandPath("//../data/" + filepath)
		self.objects = {} #e.j: mygen.objects["MyObjName"][3].worldOrientation...
		self.ids = []
		with open(self.path, "rb") as input: self.data = input.read()
		if self.relative_path in ObjectGenerator.all:
			raise KeyError("A generator with path " + filepath + "already exists.")
		else: ObjectGenerator.all[self.relative_path] = self

	def new(self, id, callback=None):
		""" Loads a new copy of the object.

		:param id: An id to identify the object. Not limited to integers.
		:param callback: Function to call once the object is loaded, it's first paramater is the new KX_GameObject.
		"""
		name = self.relative_path
		arg = (self.data, name, id, callback)
		if arg not in module.libload_gqueue:
			if id not in self.ids:
				module.libload_gqueue.append(arg)
				self.ids.append(id)
			else: raise KeyError("Object with id " + str(id) + " already in this generator.")
		module._arecallbacks = True
		ObjectGenerator.time = time.time()

	def remove(self, id):
		""" Removes a loaded object.

		:param id: The id of the object.
		"""
		self.ids.remove(id)
		for obj in self.objects.values():
			if id in obj:
				#obj[id].endObject()
				del obj[id]
		logic.LibFree(self.relative_path+str(id))
