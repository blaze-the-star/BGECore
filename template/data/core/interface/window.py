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
		
		#Scale Camera X/Y
		if self.camera:
			self.scx = self.camera.ortho_scale
			self.scy = self.camera.ortho_scale * (self.height / self.width)
			#utils.setFilter2D("bloom", self.camera, 0)
			#utils.setFilter2D("barrel", self.camera, 1)
			
			
		logic.mouse.position = (0.5,0.5)
		
	def update(self):
		x, y = logic.mouse.position
		to = [(x-0.5)*self.scx, (-y+0.5)*self.scy, 0]
		cx, cy, cz = self.camera.worldPosition
		tto = [to[0]+cx, to[1]+cy, 0]
		self.generateEvents(to, tto)
		
		if self.cursor:
			self.cursor.worldPosition = [tto[0], tto[1], self.camera_height]
			
		winx = render.getWindowWidth()
		winy = render.getWindowHeight()
		if winx == self.width and winy == self.height: return
		else: self.resize(winx, winy)
	
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
		scene_game = module.scene_game
		scene_gui = self.scene_gui
		
		if scene_gui:
			obj = self.camera.rayCast(tto, (to[0], to[1], self.camera.position.z), self.camera.far)[0]
		
		if scene_game and not obj:
			x, y = logic.mouse.position
			gcam = scene_game.active_camera
			cx, cy, cz = gcam.position
			scx = gcam.ortho_scale
			scy = gcam.ortho_scale * render.getWindowHeight()/render.getWindowWidth()
			
			to = [(x-0.5)*scx + cx, (-y+0.5)*scy + cy, 0]
			obj = gcam.rayCast(to, (to[0], to[1], gcam.position.z), gcam.far)[0]
		
		event._over_event_call(obj)
		
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