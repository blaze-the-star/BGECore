from core.interface import widget, flabel
from core import module, utils
from bge import logic, render
from mathutils import Vector, Euler
import blf, bgl, math

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2

def replaceBlenderText(obj):
	""" Called at the start of the game, replaces all text objects with Labels. To be replaced the objects must have the following game properties:
	
	* Font (*String*): Name of the font to use.
	* Align (*String*): Either Left, Center or Right
	* FLable (*Bool*, Optional): If true the text object will be replaced by a FLabel instead.
	* Wrap (*Float*, Optional): The width where to wrap the text, *None* if not used.
	* Shadow (*Bool*, Optional): If true the text will have shadow.
	* ShadowBlur (*Int*, Optional): The amount of blur to apply to the shadow *0, 3 or 5*
	"""
	if obj.get("FLabel") == True:
		flabel.replaceBlenderText(obj)
		return
		
	font = obj.get("Font")
	if not font:
		#utils.debug("Impossible to replace text object " + obj.name + ". Doesn't have a Font property.")
		return
	
	sx, sy, sz = [int(n*100) for n in obj.localScale]
	
	align = obj.get("Align", "Left")
	align = ["Left", "Center", "Right"].index(align)
	
	wp = obj.worldPosition
	xyz = obj.worldOrientation.to_euler()
	label = Label(font, "", sx, align, wp, xyz)
	
	label.visible = obj.visible
	label.color = obj.color
	label.shadow = obj.get("Shadow", False)
	label.shadow_blur = obj.get("ShadowBlur", 0)
	label.wrap = obj.get("Wrap", None)
	
	label.text = obj["Text"]
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
		* In order to look really good a text object with Object Properties -> Color -> Alpha > 0 and < 1 must be present (but not nescesarily inside the camera frustum).
		
		Alternatively you can use **core.interface.flabel.FLabel** (Almost same API), wich uses a bitmap texture, however it has it's own problems:
		
		* No Kerning
		* Most special characters don't work (inapropiate for anything other than english).
		* Unacurate center alignation (It can cause some wierd efects, can be fixed inside BGECore thought).
	
	.. note:: Materials using Game settings -> Alpha Sort / Alpha Blend will be rendered always behind the Label.
	
	.. attribute:: visible
	
		Visibility, *True* or *False*. Use ``color.w`` for the alpha channel. 
	
	.. attribute:: align
	
		Alignation of the text, on the following contants: ``ALIGN_LEFT``, ``ALIGN_CENTER`` or ``ALIGN_RIGHT``
	
	.. attribute:: middle_height
	
		Boolean, if *True* the text will be Y-Axis centered to the origin. Useful for widgets.
		
	.. attribute:: leading
	
		The space between two lines of text in a multiline label. **Default: 1**
		
	.. attribute:: wrap
	
		The width size where to wrap text, in blender units.
		
	.. attribute:: blur
	
		The blur of the label {0, 3, 5}
	
	.. attribute:: shadow
		
		*True* if the label should have shadow.
		
	.. attribute:: shadow_blur
	
		The blur level of the shadow, {0, 3, 5}
		
	.. attribute:: shadow_color
	
		The color of the shadow (rgba)
		
	.. attribute:: shadow_offset
	
		The (x, y) displacment of the shadow in pixels.
	
	"""
	_fontname_id = {}

	def __init__(self, font, text, size = 16, align = ALIGN_LEFT, position = [0,0,0], rotation = [0,0,0]):
		position = Vector(position)
		self.blur = 0
		self.shadow = False
		self.shadow_blur = 3
		self.shadow_color = (0, 0, 0, 1)
		self.shadow_offset = (1, -1)
		self.wrap = None
		
		self.scene = module.scene_gui
		self._font = font
		self._position = self.ProxyPosition(position)
		self._rotation = self.ProxyRotation(rotation)
		
		self._glposition = [0,0,0]
		self._glscale = None
		self._glunit = render.getWindowWidth()/self.scene.active_camera.ortho_scale
		self._scale = self.ProxyScale([size/100, size/100, size/100])
		self._color = self.ProxyColor([0,0,0,1])
		self._lines = [] #The labels containing child lines on a multiline label.
		
		self.align = align
		self.leading = 1
		self.font = self._font
		self.text = text
		self.visible = True
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
		""" Removes the label from the ``post_draw`` pipeline. """
		try: module.scene_gui.post_draw.remove(self.draw)
		except ValueError:
			raise ValueError("Trying to delete a Label that should be already deleted. Possible memory leak.")
		
		self.visible = False
		del self
		
	def draw(self):
		if self.visible == False: return
		module.post_draw_step += 1
		
		cam = self.scene.active_camera
		orth = cam.ortho_scale
		
		height = render.getWindowHeight()
		width = render.getWindowWidth()
		near = cam.near
		far = cam.far
		h = cam.worldPosition.z
		font_id = Label._fontname_id[self._font]
		unit = width/orth
		self._glunit = unit
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
		dh = oh

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
		
		x, y = blf.dimensions(font_id, self._text) #NOTE: Always after blf.size()
		
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
		
		if self.shadow == True:
			blf.position(font_id, pos[0]+self.shadow_offset[0], pos[1]+self.shadow_offset[1], pos[2])
			bgl.glColor4f(*self.shadow_color)
			blf.blur(font_id, self.shadow_blur)
			blf.draw(font_id, self._text)
			blf.position(font_id, pos[0], pos[1], pos[2])
			
		bgl.glColor4f(*self._color)
		blf.blur(font_id, self.blur)
		blf.draw(font_id, self._text)
		
		blf.disable(font_id, blf.ROTATION)
		
		self._lastscale = self.scale
	
	@property
	def position(self):
		""" A |Vector| indicating the position of the label. """
		return self._position
		
	@position.setter
	def position(self, xyz):
		self._position = self.ProxyPosition(xyz)
		x, y, z = xyz
		for i, line in enumerate(self._lines):
			line.position = x, y-self.leading*self.scale.x*(i+1), z
		
	@property
	def scale(self):
		""" A |Vector| indicating the scale of the label. Only the x axis will be considered. """
		return self._scale
		
	@scale.setter
	def scale(self, xyz):
		self._scale = self.ProxyScale(xyz)
		for line in self._lines:
			line.scale = xyz
		
	@property
	def rotation(self):
		""" A |Vector| indicating the orientation of the label. Only the z axis will be considered. """
		return self._rotation
		
	@rotation.setter
	def rotation(self, xyz):
		xyz = Euler(xyz, 'XYZ')
		self._rotation = self.ProxyRotation(xyz)
		for line in self._lines:
			line.rotation = xyz
			length = (line.position - self.position).length
			pos = Vector([0,-length,0])
			pos.rotate(xyz)
			line.position = pos + self.position
		
	@property
	def color(self):
		""" A |Vector| indicating the color of the label. """
		return self._color
		
	@color.setter
	def color(self, color):
		self._color = self.ProxyColor(color)
		for line in self._lines:
			line.color = color
			
	@property
	def visible(self):
		""" A |Vector| indicating the color of the label. """
		return self._visible
		
	@visible.setter
	def visible(self, val):
		self._visible = val
		for line in self._lines:
			line.visible = val
	
	@property
	def font(self):
		""" Font name to use from the `data/gui/font` directory. Expected a ``.ttf`` file extension.
		
		:type: String
		"""
		return self._font
		
	@font.setter
	def font(self, font):
		font_path = logic.expandPath('//gui/font/' + font + '.ttf')
		if font not in Label._fontname_id: Label._fontname_id[font] = blf.load(font_path)
		
	@property
	def text(self):
		""" The text of the label. You can use ``\\n`` to make a new line. """
		text = self._text
		for line in self._lines:
			text += "\n" + line.text
		return text
		
	@text.setter
	def text(self, text):
		for l in self._lines: l.delete()
		self._lines = []
		
		real_lines = text.splitlines()
		if self.wrap != None:
			font_id = Label._fontname_id[self._font]
			wrap = self.wrap * self._glunit
			if wrap <= 0: raise ValueError("Label wrap must be greater than 0")
			
			blf.size(font_id, int(self.scale.x*self._glunit), 72)
			lines = []
			for real_line in real_lines:
				line = ""
				for word in real_line.split():
					line += word
					x = blf.dimensions(font_id, line)[0]
					if x > wrap:
						lines.append(line[:-len(word)])
						line = word + " "
					else: line += " "
				lines.append(line) 
				
		else: lines = real_lines			
		
		if len(lines) < 2:
			self._text = text
			return
			
		self._text = lines[0]
		lines = lines[1:]
		for i, line in enumerate(lines):
			new = self.copy(line, [0,-self.leading*self.scale.x*(i+1),0])
			self._lines.append(new)
				
	def copy(self, text = None, offset = [0,0,0]):
		""" Retuns a copy of the label
		
		:param string text: The text of the new Label or None to copy the current text.
		:param offset: A vector representing the desplacment to be applied on the new Label from this Label position in local coordinates.
		"""
		
		if text == None: text = self._text
		size = self.scale.x * 100
		offset = Vector(offset)
		offset.rotate(self.rotation)
		
		label = Label(self.font, text, size, self.align, self.position + offset, self.rotation)
		label.color = self.color
		label.blur = self.blur
		label.shadow = self.shadow
		label.shadow_blur = self.shadow_blur
		label.shadow_color = self.shadow_color
		label.shadow_offset = self.shadow_offset
		return label