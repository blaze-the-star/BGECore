from script import constant
from bge import logic, render, texture
from bgl import *
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
		self.hitpoly = None

		#Scale Camera X/Y
		if self.camera:
			self.scx = self.camera.ortho_scale
			self.scy = self.camera.ortho_scale * (self.height / self.width)
			self.camera.frustum_culling = False

		logic.mouse.position = (0.5,0.5)

	def update(self):
		module.post_draw_step = 0

		x, y = logic.mouse.position
		to = [(x-0.5)*self.scx, (-y+0.5)*self.scy, 0]
		cx, cy, cz = self.camera.worldPosition
		tto = [to[0]+cx, to[1]+cy, 0]
		self.generateEvents(to, tto)

		self.cursor_position = [tto[0], tto[1], self.camera_height]
		if self.cursor:
			if type(self.cursor) is ImageCursor:
				self.cursor.position = x, y
				self.cursor.scale = 0.5, 0.5
			else:
				self.cursor.worldPosition = self.cursor_position

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
			self.hitobj, self.hitpoint, self.hitnormal, self.hitpoly = gcam.rayCast(vec, gcam, gcam.far, "", 0, 0, 1)

		else:
			#Needs revision, rotation doesn't work
			scx = gcam.ortho_scale
			scy = gcam.ortho_scale * render.getWindowHeight()/render.getWindowWidth()

			to = [(x-0.5)*scx + cx, (-y+0.5)*scy + cy, 0]
			self.hitobj, self.hitpoint, self.hitnormal = gcam.rayCast(to, (to[0], to[1], gcam.position.z), gcam.far)

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
			obj = self.camera.rayCast(tto, (to[0], to[1], self.camera.position.z), self.camera.far)[0]

		event._over_event_call(obj)

	def hideCursor(self):
		""" Turns the cursor visibility Off """
		if self.cursor: self.cursor.visible = False
		logic.mouse.visible = False

	def showCursor(self):
		""" Turns the cursor visibility On """
		if self.cursor: self.cursor.visible = True
		else: logic.mouse.visible = True

	def setCursor(self, obj):
		""" Changes the cursor to a game object or image.

			:param string objName: Name of the game object to use as a cursor.
			It must be a object of the GUI scene in an inactive layer.
			Or the filepath of the image to use, relative to the data directory.
		"""
		own = self.camera
		if self.cursor and not type(self.cursor) is ImageCursor: self.cursor.endObject()

		if obj:
			if type(obj) is str:
				self.cursor = ImageCursor(obj)
			else:
				self.cursor = self.scene_gui.addObject(obj, own)
				self.cursor.position.z = 9.9
				logic.mouse.visible = False
		else:
			self.cursor = None
			logic.mouse.visible = True
			
class ImageCursor:
	def __init__(self, path):
		self.worldPosition = [0,0,0]
		self.visible = True
		self.path = path
		self.fullpath = logic.expandPath("//../data/" + path)
		self.texture = texture.ImageFFmpeg(self.fullpath)
		
		self._tex_id = glGenTextures(1)
		self.size = [0, 0]
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
		
		self.reload()
		
		self.texco = [(0, 0), (1, 0), (1, 1), (0, 1)]
		self.color = [1, 1, 1, 1]
		
		x = 0
		y = 0

		size = [50, 50]
		
		width = size[0]
		height = size[1]
		self._size = [width, height]
		# The "private" position returned by setter
		self._position = [x, y]
		self.calculate_glposition()
		module.scene_gui.post_draw.append(self.draw)

	@property
	def position(self):
		return self._position
	
	@position.setter
	def position(self, val):
		x, y = val
		winx = render.getWindowWidth()
		winy = render.getWindowHeight()
		
		self._position = x*winx, -y*winy + winy
		
	@property
	def scale(self):
		return self._size
	
	@position.setter
	def scale(self, val):
		x, y = val
		winx = render.getWindowWidth()/module.scene_gui.active_camera.ortho_scale
		
		self._size = x*winx, y*winx
	
	def calculate_glposition(self):
		# OpenGL starts at the bottom left and goes counter clockwise
		x, y = self._position
		width, height = self._size
		
		self.gl_position = [
					[x, y],
					[x + width, y],
					[x + width, y + height],
					[x, y + height]
				]
		
	def reload(self):
		img = self.texture
		
		data = img.image
		if data == None:
			raise RuntimeError("Image not loaded correctly!")

		glBindTexture(GL_TEXTURE_2D, self._tex_id)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.size[0], img.size[1], 0,
						GL_RGBA, GL_UNSIGNED_BYTE, data)

		self.image_size = img.size[:]
		
	def draw(self):
		if self.visible == False: return
		s = module.scene_gui
		end = len(s.post_draw)-1
		
		if module.post_draw_step < end:
			s.post_draw.insert(end, s.post_draw.pop(module.post_draw_step))
			module.post_draw_step += 1
			return
			#We will come back at the end of the drawing pipeline
		
		module.post_draw_step += 1
		
		height = render.getWindowHeight()
		width = render.getWindowWidth()
	
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, width, 0, height)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
	
		# Enable textures
		glEnable(GL_TEXTURE_2D)

		# Enable alpha blending
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		#glAlphaFunc(GL_SRC_ALPHA, 1)

		# Bind the texture
		glBindTexture(GL_TEXTURE_2D, self._tex_id)

		# Fix position
		w, h = self._size
		glTranslatef(0, -h, 1)

		#MipLevel
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0);
		
		# Draw the textured quad
		glColor4f(*self.color)

		glBegin(GL_QUADS)
		self.calculate_glposition()
		for i in range(4):
			glTexCoord2f(self.texco[i][0], self.texco[i][1])
			glVertex2f(self.gl_position[i][0], self.gl_position[i][1])
		glEnd()

		glBindTexture(GL_TEXTURE_2D, 0)
		
		#glDisable(GL_TEXTURE_2D)
		#glPopMatrix()
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		
#Hacks
_glGenTextures = glGenTextures
def glGenTextures(n, textures=None):
	id_buf = Buffer(GL_INT, n)
	_glGenTextures(n, id_buf)

	if textures:
		textures.extend(id_buf.to_list())

	return id_buf.to_list()[0] if n == 1 else id_buf.to_list()