from core.interface.widget import Widget
from core import module, utils
from bge import logic

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2

def replaceBlenderText(obj):
	font = obj.get("Font")
	if not font:
		#utils.debug("Impossible to replace text object " + obj.name + ". Doesn't have a Font property.")
		return
	
	sx, sy, sz = [int(n*100) for n in obj.localScale]
	if sx != sy or sy != sz:
		utils.debug("Impossible to replace text object " + obj.name + ". Size is not uniform.")
		return
	
	align = obj.get("Align", 0)
	align = ["Left", "Center", "Right"].index(align)
	
	wp = obj.worldPosition
	#position = [wp.x+float(0.006*sx), wp.y+(0.002*sx), wp.z]
	label = Label(font, obj["Text"], sx/2.5, align, wp)
	xyz = obj.worldOrientation.to_euler()
	label.rotation = xyz
	if align == ALIGN_RIGHT: label.rotation.y = 3.14
	
	label.visible = obj.visible
	
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
	
#The size of a Label is equal to the scale / 100. BGECore Design must guarentee that all fonts have 4 vertex and medians of size 1.
class Label(Widget):
	"""
	The basic Text object of BGECore.
	
	Labels are dynamic texts that can be instantiated at runtime in any given position, used in Widgets or as a replacemnet for BGE text objects. To replace
	a text object the TextObject must have two game properties "*(String)* Font" and "*(String[Right,Center,Left])* Align". Labels need a font object to work. Font objects are created as
	old BGE dynamic text (2.49) and have some advantages over new text objects. Font objects must be placed on an inactive layer of the GUI scene and must be
	prefixed with the *Font* keyword, *e.j: Font.Hobo, Font.Title*
	
	:param string font: The font of the label.
	:param string text: The text of the label.
	:param integer size: The size of the label.
	:param align: The alignation of the text in the label.
	:type align: :ref:`align-constant`
	:param position: The label position.
	:type position: |Vector| or size-3 list
	
	.. note:: Although font objects have a lot of avantages, they also have one clear inconvenient, they must be monspaced. A non-monospaced font won't be diplayed correctly.
	"""
	_font_id = 0
	_loaded_fonts_right = {}
	_loaded_fonts_left = {}

	def __init__(self, font, text, size = 16, align = ALIGN_LEFT, position = [0,0,0]):
		self.scene = module.scene_gui
		font_name = "Font." + font
		self._font = self.scene.objectsInactive[font_name]
		
		self.obj = self.scene.addObject(self._font, self.scene.active_camera)
		self.obj.worldPosition = position
			
		if font_name not in Label._loaded_fonts_right.keys():
			mesh = logic.LibNew('Font'+str(Label._font_id), 'Mesh', [font_name])[0]
			v_array = mesh.getVertexArrayLength(0)
			if v_array != 4:
				utils.debug("Font object not valid, skipping!")
				return
			
			v0 = mesh.getVertex(0,0)
			v1 = mesh.getVertex(0,1)
			v2 = mesh.getVertex(0,2)
			v3 = mesh.getVertex(0,3)
			_swap_UV_2(v0,v1)
			_swap_UV_2(v2,v3)
			
			Label._loaded_fonts_right[font] = mesh
			Label._loaded_fonts_left[font] = self.obj.meshes[0]
			Label._font_id += 1
		
		self._location = super().ProxyPosition()
		self._scale = super().ProxyScale()
		self._rotation = super().ProxyRotation()
		self._color = super().ProxyColor()
		self.transformable = [self.obj]
		self._align = None
		self._text = text
		self.ob2 = None #Second object to use on ALIGN_CENTER
		
		self.size = size
		self.align = align #It also does set text the first time.
		
	def delete(self):
		""" """
		if self.ob2:
			self.ob2.endObject()
			self.obj2 = None
			
		self.obj.endObject()
		self.obj = None
		del self
	
	@property
	def text(self):
		""" Text that the Label displays.
		
		:type: String
		"""
		return self._text
		
	@text.setter
	def text(self, text):
		self._text = text
		if self._align == ALIGN_LEFT:
			self.obj["Text"] = text
		if self._align == ALIGN_RIGHT:
			self.obj["Text"] = reverse_text(text)
		if self._align == ALIGN_CENTER:
			first, second = "",""
			for line in text.splitlines():
				rtext = reverse_text(line)
				if len(rtext) % 2: n = 1
				else: n = 0
				first += "  " + rtext[len(rtext)//2+n:] + "\n"
				second += " " + line[len(line)//2:] + "\n"
			
			self.obj["Text"] = second
			self.ob2["Text"] = first
	
	@property
	def font(self, name=False):
		""" Font name, the same as the object name but without the "Font." prefix.
		
		:type: String
		"""
		return self._font.name[5:]
		
	@font.setter
	def font(self, font):
		text = self.obj["Text"]
		self.obj.endObject()
		self._font = self.scene.objectsInactive["Font."+font]
		
		self.obj = self.scene.addObject(self._font, self.scene.active_camera)
		self.obj.worldPosition = self._location
		self.obj.localScale = self._scale
		self.obj.worldOrientation = self._rotation.to_matrix()		
		
	@property
	def size(self):
		""" :type: Integer"""
		return self._scale.x * 100

	@size.setter
	def size(self, size):
		x = size/100
		self.scale = [x,x,x]
		
	@property
	def align(self):
		"""
		:return: Alignation
		:type: :ref:`align-constant`
		"""
		return self._align
		
	@align.setter
	def align(self, align):
		if self._align and self._align == align: return
		font_name = self._font.name
		font_name = font_name.replace("Font.", "")
		
		if self._align and (self._align == ALIGN_RIGHT or self._align == ALIGN_CENTER) and align == ALIGN_LEFT:
			self.obj.rotation.y = 0
			self.obj.replaceMesh(self._loaded_fonts_left[font_name])
			
		if align == ALIGN_RIGHT:
			self.obj.replaceMesh(self._loaded_fonts_right[font_name])
			self.rotation.y = 3.1415 
		
		if align == ALIGN_CENTER:
			self.ob2 = self.scene.addObject(self._font, self.scene.active_camera)
			self.ob2.worldPosition = self._location
			self.ob2.localScale = self._scale
			self.transformable.append(self.ob2)
			v = self.ob2.worldOrientation.to_euler()
			v.y = 3.1415
			self.ob2.localOrientation = v.to_matrix()
			self.ob2.replaceMesh(self._loaded_fonts_right[font_name])
		else:
			if self.ob2:
				self.transformable.remove(self.ob2)
				self.ob2.endObject()
				self.ob2 = None
			
		self._align = align
		self.text = self.text #The end of the world is near!
		
	@property
	def visible(self):
		""" The visibility of the Label.
		
		:type: bool
		"""
		return self.obj.visible
	
	@visible.setter
	def visible(self, bool):
		self.obj.visible = bool
		if self.ob2: self.ob2.visible = bool