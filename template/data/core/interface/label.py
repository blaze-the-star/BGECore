from core.interface import widget, flabel
from core import module, utils
from bge import logic, render
from mathutils import Vector
import blf, bgl, math

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2

def replaceBlenderText(obj):
	""" Called at the start of the game, replaces all text objects with Labels. To be replaced the objects must have the following game properties:
	
	* Font (*String*): Name of the font to use.
	* Align (*String*): Either Left, Center or Right
	* FLable (*Bool*, Optional): If true the text object will be replaced by a FLabel instead.
	
	"""
	if obj.get("FLabel") == True:
		flabel.replaceBlenderText(obj)
		return
		
	font = obj.get("Font")
	if not font:
		#utils.debug("Impossible to replace text object " + obj.name + ". Doesn't have a Font property.")
		return
	
	sx, sy, sz = [int(n*100) for n in obj.localScale]
	
	align = obj.get("Align", 0)
	align = ["Left", "Center", "Right"].index(align)
	
	wp = obj.worldPosition
	label = Label(font, obj["Text"], sx, align, wp)
	xyz = obj.worldOrientation.to_euler()
	label.rotation = xyz
	
	label.visible = obj.visible
	label.color = obj.color
	
	module.labels[obj.name] = label
	obj.endObject()
		
def reverse_text(text):
	""" Returns the reversed version of *text*
	
	:arg string text: Original text.
	:return: Reversed text. 
	"""
	
	newText = ""
	l = text.find("\n")
	u = True
	if l < 0:
		l = len(text)
		u = False
	while(text != ""):
		for x in range(l):
			newText += text[(l-1)-x]
		if u == True: newText += '\n'
		text = text[l+1:]
		l = text.find("\n")
		if l < 0:
			l = len(text)
			u = False
	return newText
	
def _swap_UV_2(v0, v1):
	uv0 = v0.getUV()
	uv1 = v1.getUV()
	uv0[0],uv1[0] = uv1[0],uv0[0]
	uv0[1],uv1[1] = uv1[1],uv0[1]
	v0.setUV(uv0)
	v1.setUV(uv1)
	
class Label():
	"""
	The basic Text object of BGECore.
	
	:param string font: The font of the label.
	:param string text: The text of the label.
	:param integer size: The size of the label. (100 times the scale)
	:param align: The alignation of the text in the label.
	:type align: :ref:`align-constant`
	:param position: The label position.
	:type position: |Vector| or size-3 list
		
	.. warning:: This version uses the blender font module (blf). Currently text rendered with blf have the following bugs:
		
		* Pixelation when rotating them.
		* Incompativility with object materials using Alpha Sort / Alpha Blend.
		* In order to look really good a text object with Object Properties -> Colro -> Alpha > 0 and < 1 must be present (but not nescesarily inside the camera frustum).
		
		Alternatively you can use **core.interface.flabel.FLabel** (Same API), wich uses a bitmap texture, however it has it's own problems:
		
		* No Kerning
		* Most special characters don't work (inapropiate for anything other than english).
		* Unacurate center alignation (It can cause some wierd efects, can be fixed inside BGECore thought).
	
	.. note:: Materials using Game settings -> Alpha Sort / Alpha Blend will be rendered always behind the Label.
	
	.. attribute:: visible
	
		Visibility, true or false. Use *color.w* for alpha channel. 
	
	.. attribute:: align
	
		Alignation of the text, on the following contants: ``ALIGN_LEFT``, ``ALIGN_CENTER`` or ``ALIGN_RIGHT``

	.. attribute:: text
	
	.. attribute:: middle_height
	
		**Bool**, if True the text will be Y-Axis centered to the origin. Useful for widgets.
	
	"""
	_fontname_id = {}

	def __init__(self, font, text, size = 16, align = ALIGN_LEFT, position = [0,0,0]):
		position = Vector(position)
		
		self.scene = module.scene_gui
		self._font = font
		self._position = self.ProxyPosition(position)
		self._rotation = self.ProxyRotation([0,0,0])
		
		self._glposition = [0,0,0]
		self._glscale = None
		self._glunit = None
		self._glzunit = None
		self._scale = self.ProxyScale([size/100, size/100, size/100])
		self._color = self.ProxyColor([1,1,1,1])
		
		self.text = text
		self.font = self._font
		self.visible = True
		self.align = align
		self.scene.post_draw.append(self.draw)
		self.middle_height = False
		
		self._lastscale = None
		self._lastorth = self.scene.active_camera.ortho_scale
		
	def ProxyPosition(self, position):
		P = widget.ProxyPosition(position)
		P.obj = self; return P
		
	def ProxyScale(self, scale):
		P = widget.ProxyScale(scale)
		P.obj = self; return P
		
	def ProxyRotation(self, orientation):
		P = widget.ProxyRotation(orientation)
		P.obj = self; return P
		
	def ProxyColor(self, color):
		P = widget.ProxyColor(color)
		P.obj = self; return P
		
	def delete(self):
		""" """
		scene.post_draw.remove(self.draw)
		del self
		
	def draw(self):
		if self.visible == False: return
		module.post_draw_step += 1
		
		cam = self.scene.active_camera
		orth = cam.ortho_scale
		
		#TO IMPROVE
		height = render.getWindowHeight()
		width = render.getWindowWidth()
		near = cam.near
		far = cam.far
		h = cam.worldPosition.z
		font_id = Label._fontname_id[self._font]
		unit = width/orth
		rpos = self._position - cam.worldPosition
		
		bgl.glMatrixMode(bgl.GL_PROJECTION)
		bgl.glLoadIdentity()
		bgl.gluOrtho2D(0, width, 0, height)
		bgl.glMatrixMode(bgl.GL_MODELVIEW)
		bgl.glLoadIdentity()
		
		bgl.glEnable(bgl.GL_BLEND)
		bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
		bgl.glAlphaFunc(bgl.GL_SRC_ALPHA, 1)
		
		#Z AXIS
		oh = (far-near)/2
		ortho_unit = 1/oh
		dh = oh - h

		pos = list([width/2+rpos[0]*unit, height/2+rpos[1]*unit, dh*ortho_unit + rpos[2]*ortho_unit])
		if self._lastscale != self.scale or True:
			blf.size(font_id, int(self.scale.x*unit), 72)
		else:
			if self._lastorth != orth:
				sc = (float(self._lastorth) / float(orth)) * self.scale.x
				bgl.glScalef(sc,sc,1)
				print(str(self._lastorth) + " " + str(orth))
				pos[0] /= sc
				pos[1] /= sc
				
			else:
				self._lastorth = orth
		
		x, y = blf.dimensions(font_id, self.text) #NOTE: Always after blf.size()
		
		if self.align == ALIGN_CENTER:
			pos[0] -= (x)/2 * math.cos(self._rotation.z)
			pos[1] -= x/2 * math.sin(self._rotation.z)
		if self.align == ALIGN_RIGHT:
			pos[0] -= x * math.cos(self._rotation.z)
			pos[1] -= x * math.sin(self._rotation.z)
			
		if self.middle_height == True:
			pos[0] -= y/4 * math.sin(self._rotation.z)
			pos[1] -= y/4 * math.cos(self._rotation.z)
		
		blf.position(font_id, pos[0], pos[1], pos[2])
		blf.enable(font_id, blf.ROTATION)
		if self.rotation.z > 0.01 or self.rotation.z < -0.01:
			blf.rotation(font_id, self._rotation.z)
		else:
			blf.rotation(font_id, 0)
		
		bgl.glColor4f(self._color.x, self._color.y, self._color.z, self._color.w)
		blf.draw(font_id, self.text)
		blf.disable(font_id, blf.ROTATION)
		
		self._lastscale = self.scale
	
	@property
	def position(self):
		""" """
		return self._position
		
	@position.setter
	def position(self, xyz):
		self._position = self.ProxyPosition(xyz)
		
	@property
	def scale(self):
		"""  """
		return self._scale
		
	@scale.setter
	def scale(self, xyz):
		self._scale = self.ProxyScale(xyz)
		
	@property
	def rotation(self):
		"""  """
		return self._rotation
		
	@rotation.setter
	def rotation(self, xyz):
		self._rotation = self.ProxyRotation(xyz)
		
	@property
	def color(self):
		"""  """
		return self._color
		
	@color.setter
	def color(self, color):
		self._color = self.ProxyColor(color)
	
	@property
	def font(self):
		""" Font name to use from the `data/gui/font` directory. Ecpected ``.ttf`` file extension.
		
		:type: String
		"""
		return self._font
		
	@font.setter
	def font(self, font):
		font_path = logic.expandPath('//gui/font/' + font + '.ttf')
		if font not in Label._fontname_id: Label._fontname_id[font] = blf.load(font_path)