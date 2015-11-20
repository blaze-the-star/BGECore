from core.interface.widget import Widget
from core.interface.label import Label
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
		
	def mouseIn(self):
		""" Called when the mouse just enters the button space. You must use ``super().mouse_in()`` when overriding it. """
		if self.over and self._active == True:
			try:
				self.objt = self.scene.addObject(self.over, self.obj)
				self.objt.worldPosition.z = self.obj.worldPosition.z + 0.01
				self.transformable.append(self.objt)
			except:
				print("Button type: " + self.__class__.__name__ + " Over: " + str(self.over))
				traceback.print_exc()
		
	def mouseOut(self):
		""" Called when the mouse just exits the button space. You must use ``super().mouse_out()`` when overriding it. """
		if self.over and self._active == True:
			if self.objt:
				self.transformable.remove(self.objt)
				self.objt.endObject()
				self.objt = None
	
	def mouseOver(self):
		""" Called when the mouse is over the button space.
		
		TODO
		"""
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
		
		
from mathutils import Vector
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
		font = self.label.font
		self.transformable.append(self.label)
		
		self.scale = sc
		self.rotation = rt
		
	def enable(self):
		""" It enables the button events. (Enabled by default) """
		super().enable()
		self.label.visible = True

	def disable(self):
		""" It dishables the button events. """
		super().disable()
		self.label.visible = False
	
	def delete(self):
		""" Deletes the button """
		self.label.delete()
		super().delete()

class Menu(Button):
	""" A Button with an index, so you con do ``if self.index == ...:``
	
	:var integer index: The index.
	:var dictionary button: Acces to other instances of the menu by their index. 
	"""
	
	button = {}
	def __init__(self, index, sprite, over = None):
		super().__init__(sprite, over)
		self.index = index
		self.button[index] = self
	
	
class TextMenu(TextButton):
	""" A TextButton with an index, so you con do ``if self.index == ...:``
	
	:var integer index: The index.
	:var dictionary button: Acces to other instances of the menu by their index. 
	"""
	
	button = {}

	def __init__(self, index, sprite, over, font, text, size = 16, align = 0):
		super().__init__(sprite, over, font, text, size, align)
		self.index = index
		self.button[index] = self