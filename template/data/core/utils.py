from bge import logic, types
from mathutils import Vector, geometry
from random import randint, choice
from time import sleep
from script import constant
from core import module
import bisect
import os

def loadGameProperty(name):
	""" Loads a property from your :file:`config.txt` file.

		The property is loaded as string, then you use the type name to get the apropiate type.
		*e.j:* ``media.device.volume = float(utils.loadGameProperty("volume"))``

		Raises ``KeyError`` if the property is not found.

		:param string name: Name of the property to load.
		:return: A string containing the value of the property.
	"""
	path = getLocalDirectory() + "config.txt"
	with open(path, "r") as input:
		for l in input.read().splitlines():
			if len(l) == 0: continue
			if l[0] == '#': continue

			x = l.find(name)
			y = l.find(": ")
			if x == 0 and y > 0:
				prop = l[y+2:]
				return prop

	raise KeyError("Property " + name + " not found in the configuration file. ")

def saveGameProperty(name, value):
	""" Saves a property to your :file:`config.txt` file.

	:param string name: Name of the property to load.
	:param value: Value to save, will be converted into a string.
	"""
	path = getLocalDirectory() + "config.txt"
	with open(path, "r+") as input:
		match = False
		new = ""
		for l in input.read().splitlines():
			if len(l) == 0 or l[0] == '#':
				new += l + '\n'
				continue

			x = l.find(name)
			y = l.find(": ")
			if x == 0 and y > 0 and not match:
				l = l[:y+2]
				l += str(value)
				match = True
			new += l + '\n'

		if not match:
			new += "\n" + name + ": " + str(value)
		input.seek(0)
		input.write(new)
		
def getBlendFilepath():
	""" Returns the blend file absolute filepath, including the name. """
	try:
		from bpy import data
		return data.filepath
	except ImportError:
		import sys
		path = [x for x in sys.argv if x.endswith(".blend") or x.endswith(".blend~")][0]
		if path[-1] == '~': path = path[:-1]
		return logic.expandPath("//" + os.path.basename(path))

def checkVersion():
	""" Returns wather BGE version is greater or equal to ``core.module.MIN_VERSION`` """
	try: from bge import app
	except ImportError: return False
	x, y, z = app.version
	i, j, k = module.MIN_VERSION
	if x > i: return True
	elif x == i:
		if y > j: return True
		elif y == j: return z >= k
		else: return False
	else: return False

def getLocalDirectory():
	""" Returns the directory where local data can be stored. By default the same directory than the game. If there is no write acces then a directory inside the user folder. 
	
	If a local directory is created it will use the main .blend name for it.
	"""
	if module._local_data_directory == None:
		blendname = os.path.basename(getBlendFilepath())[:-6]
		try:
			path = logic.expandPath("//../")
			f = open(path + "config.txt", 'a')
			module._local_data_directory = path
		except PermissionError:
			from sys import platform as _platform
			if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
				path = os.getenv("HOME") + "/.local/share/" + blendname + '/'
			elif _platform == "win32" or _platform == "cygwin":
				import ctypes.wintypes
				CSIDL_PERSONAL = 5       # My Documents
				SHGFP_TYPE_CURRENT = 0   # Get current, not default value

				buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
				ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
				path = buf.value + os.sep + "My Games" + os.sep

			module._local_data_directory = path + blendname + os.sep

		else: f.close()

	if os.path.isdir(module._local_data_directory):
		return module._local_data_directory
	else:
		path = module._local_data_directory
		os.makedirs(path)
		import shutil
		shutil.copyfile(logic.expandPath("//../config.txt"), path + "config.txt")
		return path

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

def randRGB(r = None, g = None, b = None, a = 1):
	""" Generates a random vector representing a color, paramaters not *None* will use that value instead of generating a new one. """
	if not r: r = randint(0,100)/100
	if not g: g = randint(0,100)/100
	if not b: b = randint(0,100)/100
	if not a: a = randint(0,100)/100
	return Vector((r,g,b,a))
	
def getTimeFromString(text):
	""" Returns a float reperesenting time in seconds from a string formatted like: hh:mm:ss,sss"""
	text = text.replace(',', '.')
	hours, minutes, seconds = (0, 0, 0)
	l = text.split(':')
	if len(l) == 1: seconds = float(l)
	if len(l) == 2: minutes, seconds = int(l[0]), float(l[1])
	if len(l) == 3: hours, minutes, seconds = int(l[0]), int(l[1]), float(l[2])
	return hours*3600 + minutes*60 + seconds
	
#Math

#THE SHAME BLOCK
#Returns a list of multiples of d form num. Ex 32, 2: 32, 16, 8, 4, 2
def getMultiples(num, d = [2]):
	l = []
	if len(d) > 1:
		for i in d: l.extend(getMultiples(num, [i]))
		return l

	d = d[0]
	while(num >= d):
		if num % d == 0: l.append(num)
		num /= d
	return l

def getPrimes(limit):
	l = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
	if limit <= 101:
		i = bisect.bisect_left(l, limit)
		return l[:i]
	else:
		i = 102
		while(i <= limit):
			isp = True
			for x in l:
				if i % x == 0: isp = False; break
			if isp: l.append(i)
			i += 1

		return l
#END OF THE SHAME BLOCK

def getNearestVertexToPoly(object, poly, point):
	""" Returns the nearest vertext to a poligon.

	:param poly: The poligon if wich vertex you want to check.
	:type poly: |KX_PolyProxy|
	:param point: The point to check, in world coordinates.
	:type point: |Vector|
	"""

	if not type(point) is Vector: point = Vector(point)
	mesh = poly.getMesh()

	min = None
	f = None
	for i in range(poly.getNumVertex()):
		v = mesh.getVertex(0, poly.getVertexIndex(i))
		r = vectorFrom2Points(v.XYZ, point - object.worldPosition).length
		if not min or r < min:
			min = r
			f = v

	return f

def getPolyNormal(poly):
	""" Returns the normal of poligon based on the position of their vertex. It calculates the normal, it doesn't return manually modified normals.

	:param poly: The poligon.
	:type poly: |KX_PolyProxy|
	"""

	mesh = poly.getMesh()
	s = poly.getNumVertex()
	v1 = mesh.getVertex(0, poly.v1)
	v2 = mesh.getVertex(0, poly.v2)
	v3 = mesh.getVertex(0, poly.v3)
	if s == 4: v4v = mesh.getVertex(0, poly.v4).XYZ
	else: v4v = None

	if v4v: normal = geometry.normal(v1.XYZ, v2.XYZ, v3.XYZ, v4v)
	else: normal = geometry.normal(v1.XYZ, v2.XYZ, v3.XYZ)
	return normal

def recalculateNormals(obj):
	""" Recalculates the normals of a |KX_GameObject|, |KX_MeshProxy| or |KX_PolyProxy|.

	It iterates through all the given vertex, it may be a slow operation, use with caution. """

	if type(obj) is types.KX_GameObject:
		mesh = obj.meshes[0]
	elif type(obj) is types.KX_MeshProxy: mesh = obj
	elif type(obj) is types.KX_PolyProxy: mesh = obj.getMesh()
	else: raise ValueError("Argument must be KX_GameObject, KX_MeshPoxy or KX_PolyProxy, not " + str(type(obj)))
	verdict = {} #Vertex Dictionary LOL

	#Iterate throught Faces and make a list with all the vertex and the normals of the faces the are part of.
	if type(obj) is not types.KX_PolyProxy:
		for i in range(mesh.numPolygons):
			poly = mesh.getPolygon(i)
			normal = getPolyNormal(poly)

			for j in range(poly.getNumVertex()):
				try:
					verdict[poly.getVertexIndex(j)].append(normal)
				except KeyError:
					verdict[poly.getVertexIndex(j)] = [normal]
	else:
		poly = obj
		normal = getPolyNormal(poly)

		for j in range(poly.getNumVertex()):
			try:
				verdict[poly.getVertexIndex(j)].append(normal)
			except KeyError:
				verdict[poly.getVertexIndex(j)] = [normal]

	#Iterate throught the list recalculating the normal of each vertex.
	for i, normals in verdict.items():
		normal = Vector([0,0,0])
		for n in normals:
			normal += n
		s = len(normals)
		if s == 0: continue
		normal.x /= s
		normal.y /= s
		normal.z /= s
		normal.normalize()
		mesh.getVertex(0, i).setNormal(normals[0].to_tuple())

def rand10():
	""" Generates a rondom integer from 0 to 9 """
	return randint(0,9)

def vectorFrom2Points(origin, dest, module = None):
	""" Returns a |Vector|  form 2 points in the space.

	:param origin: Point A
	:type origin: |Vector|
	:param dest: Point B
	:type dest: |Vector|
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

	:param origin: Object to move.
	:type origin: |KX_GameObject|
	:param dest: Destination object.
	:type dest: |KX_GameObject|
	:param float speed: The amount of movment to do in one frame.
	:return: True if the object has been moved, false otherwise.
	"""
	return moveObjectToPosition(origin, dest.position, speed)

def moveObjectToPosition(origin, dest, speed = 1):
	""" Moves *origin* to *dest* at a speed of *speed*. Must by called every frame for a complete movement.

	:param origin: Object to move.
	:type origin: |KX_GameObject|
	:param dest: Destination object.
	:type dest: |Vector|
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

def removeAll(original_list, sublist):
	""" Removes all ocurrences of any of the values of sublist from original_list"""
	l = []
	for x in original_list:
		inl = False
		for y in sublist:
			if x == y: inl = True
		if not inl and x not in l: l.append(x)

	return l

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
		module._started = False
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

	:param scene: Scene behavior where to change the active camera or KX_Scene
	:type scene: |KX_Scene|
	:param string camera_name: Name of the new active camera.
	"""
	camera = scene.objects[camera_name]

	#Spawn camera if in hidden layer?
	#...

	if not type(scene) is types.KX_Scene: scene = scene.scene #I know
	scene.active_camera = camera
	if scene == module.scene_gui and module.window.width != 0:
		win = module.window
		win.camera = camera
		win.camera_height = camera.worldPosition.z - 0.5
		win.scx = camera.ortho_scale
		win.scy = camera.ortho_scale * (win.height / win.width)

#GLSL 2DFilters
import core.glsl as filter2D

#DEPRECATED!

#This can be clarely optimized and improved into a class.
#This can also be optimized A LOT if we find another way to find the program id.
def getShaderSource(program):
	import bgl
	
	maxCount = 1
	count = bgl.Buffer(bgl.GL_INT, 1)
	shaders = bgl.Buffer(bgl.GL_BYTE, [maxCount])
	bgl.glGetAttachedShaders(program, maxCount, count, shaders)
	 
	maxLength = 64000
	length = bgl.Buffer(bgl.GL_INT, 1)
	source = bgl.Buffer(bgl.GL_BYTE, [maxLength])
	bgl.glGetShaderSource(shaders[0], maxLength, length, source)
	return "".join(chr(source[i]) for i in range(length[0]))

def bindUniformf(name, slot, camera):
	import bgl
	
	filter = camera.actuators["F"+str(slot)]
	text = filter.shaderText
	
	program = -1
	for prog in range(32767):
		if bgl.glIsProgram(prog) == True:
			if text == getShaderSource(prog):
				program = prog
			
	
	
			
	bgl.glUseProgram(program)
	bgl.glUniform1f(bgl.glGetUniformLocation(program, name), camera[name])

def setFilter2D(name, camera, slot):
	""" Sets or enables a 2DFilter.

	**Default aviable GLSL filters:** Bloom, Vignetting, ChromaticAberration, FXAA, SBlur.

	Some filters may need special game properties, see: *TODO*

	:param string name: Name of the filter.
	:param camera: The main camera of the scene (where logic bricks are used).
	:type camera: |KX_GameObject|
	:param integer slot: The slot (Logic Brick Actuator ID) where to apply the filter. Slots are 2DFiletre actuators connected with the Python
		controller on the main camera. Slots name are prefixed with F, e.j. F0, F1, F2.
	"""
	try:
		try: cont = camera.controllers["Python"]
		except: verbose("Filter2D failed, the camera doesn't have a controller named Python")
		if cont != logic.getCurrentController():
			module.filter_queue.append((name, camera, slot))
			module._arecallbacks = True
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

	:param camera: The main camera of the scene (where logic bricks are used).
	:type camera: |KX_GameObject|
	:param integer slot: The slot.
	"""
	try:
		filter = camera.actuators["F"+str(slot)]
		camera.controllers["Python"].deactivate(filter)
	except:
		import traceback
		traceback.print_exc()
