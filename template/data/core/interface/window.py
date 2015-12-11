from script import constant
from bge import logic, render
from core import utils, module
from core.interface import event

# Window Class:
#	This class handles the game window. It allows you to use of a custom cursor and generates mouse events.
#	Internally the class throws a raycast from the cursor position in the GUI scene and the GAME scene.
#	The current implementation only works with orthographic cameras facing the ground (0,0,0). The recomended height
#	from the world origin is 10.
#	The current implementation forces the same scale ratio on the window. This is nescesary to work properly.

class Window():
	""" Handles the game window and cursor.

	Internally it throws a raycast from the cursor position in the *scene_gui* and the *scene_game* (if aviable) to generate mouse events.
	The current implementation only works with orthographic cameras with orientation (0,0,0). The recomended height
	from the world origin is 10.

	.. attribute:: cursor

	The |KX_GameObject| of a custom cursor is used, otherwise *None*

	.. attribute:: cursor_position

	A |Vector| representing the position of the cursor. Same as *cursor.position* if using a custom cursor, otherwise the position it would have.

	.. attribute:: hitpoint

	When using a game scene a 3D Vector representing the position of the cursor in 3D space. If the raycast doesn't collide
	or there is no game scene loaded, None.

	.. attribute:: hitnormal

	The normal vector returned along the hitpoint on the window raycast, or None.

	"""

	cursor = None

	def __init__(self):
		self.height = render.getWindowHeight()
		self.width = render.getWindowWidth()
		self.scale = self.width / self.height

		self.scene_gui = utils.getSceneByName(constant.CORE_SCENE_GUI)
		module.scene_gui = self.scene_gui
		self.camera = self.scene_gui.active_camera
		self.camera_height = self.camera.worldPosition.z - 0.5
		self.cursor_position = None
		self.hitobj = None
		self.hitpoint = None
		self.hitnormal = None

		#Scale Camera X/Y
		if self.camera:
			self.scx = self.camera.ortho_scale
			self.scy = self.camera.ortho_scale * (self.height / self.width)
			self.camera.frustum_culling = False

		logic.mouse.position = (0.5,0.5)

	def update(self):
		x, y = logic.mouse.position
		to = [(x-0.5)*self.scx, (-y+0.5)*self.scy, 0]
		cx, cy, cz = self.camera.worldPosition
		tto = [to[0]+cx, to[1]+cy, 0]
		self.generateEvents(to, tto)

		self.cursor_position = [tto[0], tto[1], self.camera_height]
		if self.cursor: self.cursor.worldPosition = self.cursor_position

		winx = render.getWindowWidth()
		winy = render.getWindowHeight()
		if winx == self.width and winy == self.height: return
		else: self.resize(winx, winy)
		
	def secondary_update(self):
		scene_game = module.scene_game
		if not scene_game: return
		x, y = logic.mouse.position
		gcam = scene_game.active_camera
		cx, cy, cz = gcam.position
		if gcam.perspective:
			lens = gcam.lens
			vec = gcam.getScreenVect(x, y)
			vec.negate()
			vec = vec + gcam.position
			#render.drawLine(gcam.position, vec, [0, 1, 0])
			#render.drawLine([0,0,0], vec, [0.6, 0.2, 0.5])
			obj, self.hitpoint, self.hitnormal = gcam.rayCast(vec, gcam, gcam.far)

		else:
			#Needs revision, rotation doesn't work
			scx = gcam.ortho_scale
			scy = gcam.ortho_scale * render.getWindowHeight()/render.getWindowWidth()

			to = [(x-0.5)*scx + cx, (-y+0.5)*scy + cy, 0]
			obj, self.hitpoint, self.hitnormal = gcam.rayCast(to, (to[0], to[1], gcam.position.z), gcam.far)
			if not self.hitobj: self.hitobj = obj

	def cursorInsideFrustum(self):
		""" Checks if the custom is inside the frustum of the camera.

		:return bool: True if it is.
		"""
		return self.camera.pointInsideFrustum(self.cursor_position)

	def resize(self, winx, winy):
		""" Resize the window, the new size will maintain the same aspect ratio.

		:param integer winx: Window width in pixels.
		:param integer winy: Window height in pixels.
		"""


		_winx = self.width
		_winy = self.height
		_wins = self.scale
		try: wins = winx/winy
		except: wins = 0.001
		diff = _wins-wins
		if not (diff > 0.01 or diff < -0.01): return

		if winx != _winx: winy = int(winx/_wins)
		else:
			if winy != _winy: winx = int(winy*_wins)
		render.setWindowSize(winx, winy)
		self.width = winx
		self.height= winy

	def generateEvents(self, to, tto):
		scene_gui = self.scene_gui

		if scene_gui:
			self.hitobj = self.camera.rayCast(tto, (to[0], to[1], self.camera.position.z), self.camera.far)[0]

		event._over_event_call(self.hitobj)

	def hideCursor(self):
		""" Turns the cursor visibility Off """
		if self.cursor: self.cursor.visible = False
		logic.mouse.visible = False

	def showCursor(self):
		""" Turns the cursor visibility On """
		if self.cursor: self.cursor.visible = True
		else: logic.mouse.visible = True

	def setCursor(self, objName):
		""" Changes the cursor to a game object, usually the sprite of a new cursor.

			:param string objName: Name of the game object to use as a cursor. It must be a object of the GUI scene in an inactive layer.
		"""
		own = self.camera
		if self.cursor: self.cursor.endObject()

		if objName:
			obj = self.scene_gui.objectsInactive[objName]
			self.cursor = self.scene_gui.addObject(obj, own)
			self.cursor.position.z = 9.9
			logic.mouse.visible = False
		else:
			self.cursor = None
			logic.mouse.visible = True
