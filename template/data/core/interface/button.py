from core.interface.widget import Widget
from core.interface.label import Label, ALIGN_CENTER, ALIGN_RIGHT, ALIGN_LEFT
from core import utils, module
from mathutils import Vector
import traceback

class Button(Widget):
	""" A button Widget.
	
	The sprite and the sprite over the buttonn should be planes with scale 1:1:1, you can scale them in edit-mode. Make sure both have the same
	origin. It's recomeded to use shadeless, object color and z-transparecy(alpha:0) on the materials, and Influence->Diffuse->Alpha:1 on the texture. 
	
	
	:param sprite: The sprite that will be used as the base of the widget.
	:param over: The sprite that will be used on top of the base when the button is selected. (Must be on an inactive layer, must be No Collision)
	:type sprite: string or |KX_GameObject|
	:type over: string or |KX_GameObject|
	"""
	obj = None
	
	def __init__(self, sprite, over = None):
		super().__init__(sprite)
		if type(over) is str:
			self.over = self.scene.objectsInactive[over]
			if not self.over:
				try:
					acov = self.scene.objects[over]
					if acov: utils.debug("Interface error (" + self.__class__.__name__ + "): Object '" + acov.name + " must be in an inactive layer.")
				except: pass
		else: self.over = over
		self.objt = None
		
	def delete(self):
		""" Deletes the button """
		super().delete()
		if self.objt:
			self.objt.endObject()
			self.objt = None
		
	def _mouseIn(self):
		if self.over and self._active == True:
			try:
				self.objt = self.scene.addObject(self.over, self.obj)
				self.objt.worldPosition.z = self.obj.worldPosition.z + 0.01
				self.objt.color = self.obj.color
				self.transformable.append(self.objt)
			except:
				print("Button type: " + self.__class__.__name__ + " Over: " + str(self.over))
				traceback.print_exc()
		
	def _mouseOut(self):
		if self.over and self._active == True:
			if self.objt:
				self.transformable.remove(self.objt)
				self.objt.endObject()
				self.objt = None
				
	def mouseIn(self):
		""" Called when the mouse just enters the button space. """
		pass
		
	def mouseOut(self):
		""" Called when the mouse just exits the button space."""
		pass
	
	def mouseOver(self):
		""" Called when the mouse is over the button space. """
		pass
	
	def mouseClick(self):
		""" Called when clicking the button """
		pass
		
	def disable(self):
		""" It dishables the button events. """
		self.mouse_out()
		self.obj.visible = False
		self._active = False
	
	def enable(self):
		""" It enables the button events. (Enabled by default) """
		self.obj.visible = False
		self._active = True
		
class TextButton(Button):
	""" A button Widget with a Label.
	
	:param sprite: The sprite that will be used as the base of the widget.
	:param over: The sprite that will be used on top of the base when the button is selected.
	:type sprite: string or |KX_GameObject|
	:type over: string, |KX_GameObject| or None
	
	:param string font: The font of the label.
	:param string text: The text of the label.
	:param integer size: The size of the label.
	:param align: The alignation of the text in the label.
	:type align: :ref:`align-constant`
	
	.. attribute:: label
	
		Reference to the Label of this TextButton
	
	"""

	def __init__(self, sprite, over, font, text, size = 16, align = 0):
		super().__init__(sprite, over)
		
		sc = self.scale
		self.scale = [1,1,1]
		rt = self.rotation
		self.rotation = [0,0,0]
		
		self.label = Label(font, text, size, align, self.obj.worldPosition)
		self.label.position.z += 0.05
		self.label.middle_height = True
		font = self.label.font
		self.transformable.append(self.label)
		
		self.scale = sc
		self.rotation = rt
		
	def enable(self):
		""" It enables the button events. (Enabled by default) """
		super().enable()
		self.label.visible = True

	def disable(self):
		""" It disables the button events. """
		super().disable()
		self.label.visible = False
	
	def delete(self):
		""" Deletes the button """
		self.label.delete()
		super().delete()

def menuMove(self, position):
	""" Moves a menu to a given position. 
	
	Also accesible from *Menu* and *TextMenu* with: ``self.move(position)``
	
	:param position: The position in world coordinates.
	:type position: |Vector|
	"""
	pos = self.position
	for i, button in self.button.items():
		z = button.position.z
		button.position = position + utils.vectorFrom2Points(pos, button.position)
		button.position.z = z
		
def menuScale(self, scale, point = None):
	"""Scales a menu based on the scale of *self.obj.position* from any given position. 
	
	Also accesible from *Menu* and *TextMenu* with: ``self.resize(position, point = self.obj.position)``
	
	:param scale: The scale in world coordinates of the Button.
	:type position: |Vector|
	:param point: The center point from where to scale, if *None* no center point will be used and the scale will not modify the buttons position.
	:type position: |Vector|
	"""
	xyz = Vector(scale)
	if point != None: point = Vector((point))
	pos = self.position
	sca = self.scale
	for i, button in self.button.items():
		os = button.scale
		ls = Vector((xyz.x / sca.x, xyz.y / sca.y, xyz.z / sca.z))
		sc = [os.x * ls.x, os.y * ls.y, os.z * ls.z]
		button.scale = sc
		
		if point != None:
			os = (point - button.position)
			sc = [os.x * ls.x, os.y * ls.y, os.z * ls.z]
			z = button.position.z
			button.position = Vector(sc) + pos
			button.position.z = z
			
_cursor_relative = {}
def menuMoveWithCursor(self):
	"""Moves a menu to the cursor position. 
	
	Also accesible from *Menu* and *TextMenu* with: ``self.moveWithCursor()``
	"""
	global _cursor_relative
	ccp = module.window.cursor.position
	
	if self not in _cursor_relative.keys():
		_cursor_relative[self] = utils.vectorFrom2Points(ccp, self.position)
	
	menuMove(self, ccp + _cursor_relative[self])
		
class Menu(Button):
	""" A Button with an index, so you con do ``if self.index == ...:``
	
	.. Note:: Menus have input events enabled by default in order for ``moveWithCursor`` to work.
	
	.. attribute:: index

		The index.
	
	.. attribute:: button

		A dictionary of the other instances of the menu indexed with their index. 
	"""
	
	button = {}
	over = None
	def __init__(self, index, sprite, over = None):
		if over == None: over = self.over
		
		super().__init__(sprite, over)
		self.index = index
		self.button[index] = self
		
		module.enableInputFor(self)
		
		self.init()
		
	def init(self): pass
	
	def _mouseClick(self):
		super()._mouseClick()
		global _cursor_relative
		if self in _cursor_relative.keys(): del _cursor_relative[self]
		self.select()
	
	def select(self):
		""" Called when the mouse clicks an item. """
		pass
		
	def move(self, position): menuMove(self, position)
	def moveWithCursor(self): menuMoveWithCursor(self)
	def resize(self, scale, noparent = False):
		if noparent: menuScale(self, scale)
		else: menuScale(self, scale, self.position)
	
class TextMenu(TextButton):
	""" A TextButton with an index, so you con do ``if self.index == ...:``
	
	.. Note:: Menus have input events enabled by default in order for ``moveWithCursor`` to work.
	
	.. attribute:: index

		The index.
	
	.. attribute:: button

		A dictionary of the other instances of the menu indexed with their index. 
	"""
	
	button = {}
	
	over = None
	font = None
	size = 16
	align = ALIGN_LEFT
	
	def __init__(self, index, sprite, text, over = None, font = None, size = None, align = None):
		if over == None: over = self.over
		if font == None: font = self.font
		if size == None: size = self.size
		if align == None: align = self.align
		
		super().__init__(sprite, over, font, text, size, align)
		self.index = index
		self.button[index] = self
		self.label.color = self.color
		self.color = self.ProxyColor()
		
		module.enableInputFor(self)
		
		self.init()
		
	def init(self): pass
		
	def _mouseClick(self):
		super()._mouseClick()
		global _cursor_relative
		if self in _cursor_relative.keys(): del _cursor_relative[self]
		if self._active == True: self.select()
	
	def select(self):
		""" Called when the mouse clicks an item """
		pass
		
	def move(self, position): menuMove(self, position)
	def moveWithCursor(self): menuMoveWithCursor(self)
	def resize(self, scale, noparent = False):
		if noparent: menuScale(self, scale)
		else: menuScale(self, scale, self.position)
