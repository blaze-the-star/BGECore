from core.interface.widget import Widget
from core import module, utils
from bge import logic

#BUGS:
# - Set rotation, when called at runtime doesn't work properly.

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2

def replaceBlenderText(obj):
	font = obj.get("Font")
	if not font:
		utils.debug("Impossible to replace text object " + obj.name + ". Doesn't have a Font property.")
		return
	
	sx, sy, sz = [int(n*100) for n in obj.localScale]
	if sx != sy or sy != sz:
		utils.debug("Impossible to replace text object " + obj.name + ". Size is not uniform.")
		return
	
	align = obj.get("Align", 0)
	align = ["Left", "Center", "Right"].index(align)
	
	wp = obj.worldPosition
	position = [wp.x+float(0.006*sx), wp.y+(0.002*sx), wp.z]
	label = Label(font, obj["Text"], sx/2.5, align, position)
	x, y, z = obj.worldOrientation.to_euler()
	label.setRotation(x, y, z)
	
	label.visible(obj.visible)
	
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
	a text object its name must prefixed with the *Font* keyword, e.j. "Font.TextName.000". Labels need a font object to work. Font objects are created as
	old BGE dynamic text (2.49) and have some advantages over new text objects. Font object must be placed on an inactive layer of the GUI scene and must be
	prefixed with the *Font* keyword.
	
	:param string font: The font of the label.
	:param string text: The text of the label.
	:param integer size: The size of the label.
	:param align: The alignation of the text in the label.
	:type align: :ref:`align-constant`
	:param position: The label position.
	:type position: mathutils.Vector or size-3 list
	"""
	_font_id = 0
	_loaded_fonts_right = {}
	_loaded_fonts_left = {}

	def __init__(self, font, text, size = 16, align = ALIGN_LEFT, position = [0,0,0]):
		self.scene = module.scene_gui
		font_name = "Font." + font
		self.font = self.scene.objectsInactive[font_name]
		
		self.obj = self.scene.addObject(self.font, self.scene.active_camera)
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
		
		self._location = self.obj.worldPosition
		self._scale = self.obj.localScale
		self._rotation = self.obj.worldOrientation.to_euler()
		self.transformable = [self.obj]
		self.align = None
		self.text = text
		self.ob2 = None #Second object to use on ALIGN_CENTER
		
		self.setSize(size)
		self.setAlign(align) #It also does setText() the first time.
		
	def delete(self):
		""" """
		if self.ob2:
			self.ob2.endObject()
			self.obj2 = None
			
		self.obj.endObject()
		self.obj = None
		del self
	
	def getText(self):
		""" """
		return self.text
		
	def setText(self, text):
		""" :param string text: New text. """
		self.text = text
		if self.align == ALIGN_LEFT:
			self.obj["Text"] = text
		if self.align == ALIGN_RIGHT:
			self.obj["Text"] = reverse_text(text)
		if self.align == ALIGN_CENTER:
			first, second = "",""
			for line in text.splitlines():
				rtext = reverse_text(line)
				if len(rtext) % 2: n = 1
				else: n = 0
				first += "  " + rtext[len(rtext)//2+n:] + "\n"
				second += " " + line[len(line)//2:] + "\n"
			
			self.obj["Text"] = second
			self.ob2["Text"] = first

	def getFont(self, name=False):
		"""
		:param bool name: If true returns the font name, if false the font object. 
		:return: Font object (KX_GameObject) or name (string)
		"""
		if name == False: return self.font
		else: return self.font.name[5:]
		
	def setFont(self, font):
		"""
		:param string font: The font name, the same as the KX_GameObject.name but without the *Font* prefix. 
		"""
		text = self.obj["Text"]
		self.obj.endObject()
		self.font = self.scene.objectsInactive["Font."+font]
		
		self.obj = self.scene.addObject(self.font, self.scene.active_camera)
		self.obj.worldPosition = self._location
		self.obj.localScale = self._scale
		self.obj.worldOrientation = self._rotation.to_matrix()		
		
	def getSize(self):
		""" """
		return self._scale.x * 100
		
	def setSize(self, size):
		""" """
		x = size/100
		self.setScale(x,x,x)
		
	def getAlign(self):
		""" :return: Alignation """
		return self.align
		
	def setAlign(self, align):
		""" :param align: New alignation 
			:type align: :ref:`align-constant`
		"""
		if self.align and self.align == align: return
		font_name = self.font.name
		font_name = font_name.replace("Font.", "")
		
		if self.align and (self.align == 2 or self.align == 1) and align == 0:
			self.obj.setRotation(None, 0, None)
			self.obj.replaceMesh(self._loaded_fonts_left[font_name])
			
		if align == 2:
			self.setRotation(None, 3.1415, None) 
			self.obj.replaceMesh(self._loaded_fonts_right[font_name])
		
		if align == 1:
			self.ob2 = self.scene.addObject(self.font, self.scene.active_camera)
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
			
		self.align = align
		self.setText(self.getText())
		
	def visible(self, bool = None):
		""" :param bool bool: If used, sets the visibility.
			:return: The visibility of the Label.
		"""
		if bool == None: return self.obj.visible
		self.obj.visible = bool
		if self.ob2: self.ob2.visible = bool