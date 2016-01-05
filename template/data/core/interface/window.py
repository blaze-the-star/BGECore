from script import constant
from bge import logic, render, texture, types
import bgl
from core import utils, module
from core.interface import event

class Window():
	""" Handles the game window and cursor.

	Internally it throws a raycast from the cursor position in the *scene_gui* and the *scene_game* (if aviable) to generate mouse events. The current implementation only allows to use orthographic cameras with orientation (0,0,0) on the GUI scene. The recomended height from the world origin is 10.

	.. attribute:: cursor

		The |KX_GameObject| or :class:`.ImageCursor` of a custom cursor if used, otherwise *None*

	.. attribute:: cursor_position

		A |Vector| representing the position of the cursor. Same as *cursor.position* if using a custom cursor, otherwise the position it would have.

	.. attribute:: hitobj

		The object returned along the hitpoint on the window raycast, or ``None``.
	
	.. attribute:: hitpoint

		When using a game scene, a 3D Vector representing the position of the cursor in 3D space. If the raycast doesn't collide or there is no game scene loaded, ``None``.

	.. attribute:: hitnormal

		The normal vector returned along the hitpoint on the window raycast, or ``None``.
	
	.. attribute:: hitpoly

		The |KX_PolyProxy| returned along the hitpoint on the window raycast, or ``None``.
		
	.. attribute:: hitproperty
	
		The object property that objects need to have in order to be returned as hitobj on the window raycast, or an empty string to detect any object. See hitxray.
		
	.. attribute:: hitxray
	
		Use with hitproperty. If 0 *None* will be returned if the first object detected doesn't match the property, if 1 the raycast will continue until it finds a object that matchs the property or *camera.far* is reached.

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
		self.cursor = None
		self.cursor_position = None
		self.hitobj = None
		self.hitpoint = None
		self.hitnormal = None
		self.hitpoly = None
		self.hitproperty =  ""
		self.hitxray = 0

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
			self.hitobj, self.hitpoint, self.hitnormal, self.hitpoly = gcam.rayCast(vec, gcam, gcam.far, self.hitproperty, 0, self.hitxray, 1)

		else:
			#Needs revision, rotation doesn't work
			scx = gcam.ortho_scale
			scy = gcam.ortho_scale * render.getWindowHeight()/render.getWindowWidth()

			to = [(x-0.5)*scx + cx, (-y+0.5)*scy + cy, 0]
			self.hitobj, self.hitpoint, self.hitnormal = gcam.rayCast(to, (to[0], to[1], gcam.position.z), gcam.far, self.hitproperty, 0, self.hitxray)

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
			
		if not obj and self.hitobj: obj = self.hitobj

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
		""" Changes the cursor by a game object or a :class:`.ImageCursor`.

			:param obj: Cursor to use. Path if :class:`.ImageCursor`.
			:type obj: String or |KX_GameObject|
			
			It must be a object of the GUI scene in an inactive layer.
			Or the filepath of the image to use, relative to the data directory.
		"""
		own = self.camera
		if self.cursor:
			if type(self.cursor) is ImageCursor: self.cursor.delete()
			if type(self.cursor) is types.KX_GameObject: self.cursor.endObject()

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
	""" A cursor made from an external texture. 
	
	This cursor is rendered using BGL after all other post_draw calls. Therefore we can render it with alpha blend over BLF texts (Labels).
	
	:param string path: The path to the texture, relative to the *data* directory.
	
	.. attribute:: visible
	
		Boolean indicating the visibility of the cursor. 
	
	.. attribute:: color
	
		A 4-val list RGBA indicating the scale of each color channel to use with the cursor. *Default: [1,1,1,1]*
	
	.. attribute:: position
	
		A pair containing the positon in screen coordinates. Equal to ``bge.logic.mouse.position``. Altering this value will not modify the mouse position and the cursor will be returned to the mouse position at the next frame.
	
	.. attribute:: scale
	
		A pair containing the scale of the cursor. *Default: (0.5, 0.5)*

	.. attribute:: texture
	
		A bitmap containing the texture data to use for the cursor. The date has been loaded using ``bge.texture.ImageFFmpeg``.
	"""

	def __init__(self, path):
		self.worldPosition = [0,0,0]
		self.visible = True
		self.path = path
		self.fullpath = logic.expandPath("//../data/" + path)
		self.texture = texture.ImageFFmpeg(self.fullpath)
		
		self._tex_id = glGenTextures(1)
		self.size = [0, 0]
		bgl.glTexEnvf(bgl.GL_TEXTURE_ENV, bgl.GL_TEXTURE_ENV_MODE, bgl.GL_MODULATE)
		
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
		self.scale = 0.5, 0.5

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
		""" Reloads the texture contained in the ``texture`` attribute. Can be used to create animated cursors. """
		
		img = self.texture
		
		data = img.image
		if data == None:
			raise RuntimeError("Image not loaded correctly!")

		bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._tex_id)
		bgl.glTexImage2D(bgl.GL_TEXTURE_2D, 0, bgl.GL_RGBA, img.size[0], img.size[1], 0,
						bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, data)

		self.image_size = img.size[:]
		
	def draw(self):
		if self.visible == False: return
		
		module.post_draw_step += 1
		
		height = render.getWindowHeight()
		width = render.getWindowWidth()
	
		bgl.glMatrixMode(bgl.GL_PROJECTION)
		bgl.glLoadIdentity()
		bgl.gluOrtho2D(0, width, 0, height)
		bgl.glMatrixMode(bgl.GL_MODELVIEW)
		bgl.glLoadIdentity()
	
		# Enable textures
		bgl.glEnable(bgl.GL_TEXTURE_2D)

		# Enable alpha blending
		bgl.glEnable(bgl.GL_BLEND)
		bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
		bgl.glAlphaFunc(bgl.GL_SRC_ALPHA, 1)

		# Bind the texture
		bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._tex_id)

		# Fix position
		w, h = self._size
		bgl.glTranslatef(0, -h, 1)

		#MipLevel
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_BASE_LEVEL, 0);
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAX_LEVEL, 0);
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR);
		bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR);
		
		# Draw the textured quad
		bgl.glColor4f(*self.color)

		bgl.glBegin(bgl.GL_QUADS)
		self.calculate_glposition()
		for i in range(4):
			bgl.glTexCoord2f(self.texco[i][0], self.texco[i][1])
			bgl.glVertex2f(self.gl_position[i][0], self.gl_position[i][1])
		bgl.glEnd()

		bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
		
		bgl.glDisable(bgl.GL_BLEND)
		bgl.glDisable(bgl.GL_TEXTURE_2D)

		bgl.glMatrixMode(bgl.GL_PROJECTION)
		bgl.glPopMatrix()
		bgl.glMatrixMode(bgl.GL_MODELVIEW)
		
	def delete(self):
		""" Deletes the cursor. Usually you should use interface.window.setCursor(None) but this is for crazy bastards that have deleted the refernce on the window object. """
		
		self.visible = False
		try:
			module.scene_gui.post_draw.remove(self.draw)
		except KeyError:
			pass
		
#Hacks
_glGenTextures = bgl.glGenTextures
def glGenTextures(n, textures=None):
	id_buf = bgl.Buffer(bgl.GL_INT, n)
	_glGenTextures(n, id_buf)

	if textures:
		textures.extend(id_buf.to_list())

	return id_buf.to_list()[0] if n == 1 else id_buf.to_list()