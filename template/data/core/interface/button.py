from core.interface.widget import Widget
from core.interface.label import Label
import traceback

class Button(Widget):
	""" A button Widget.
	
	:param sprite: The sprite that will be used as the base of the widget.
	:param over: The sprite that will be used on top of the base when the button is selected.
	:type sprite: string or KX_GameObject
	:type over: string or KX_GameObject
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
		
	def mouse_in(self):
		""" Called when the mouse just enters the button space. You must use ``super().mouse_in()`` when overriding it. """
		if self.over and self._active == True:
			try:
				self.objt = self.scene.addObject(self.over, self.obj)
				self.objt.worldPosition.z = self.obj.worldPosition.z + 0.1
				self.transformable.append(self.objt)
			except:
				print("Button type: " + self.__class__.__name__ + " Over: " + str(self.over))
				traceback.print_exc()
		
	def mouse_out(self):
		""" Called when the mouse just exits the button space. You must use ``super().mouse_out()`` when overriding it. """
		if self.over and self._active == True:
			if self.objt:
				self.transformable.remove(self.objt)
				self.objt.endObject()
				self.objt = None
	
	def mouse_over(self):
		""" Called when the mouse is over the button space. """
		pass
	
	def mouse_click(self):
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
	:type sprite: string or KX_GameObject
	:type over: string, KX_GameObject or None
	
	:param string font: The font of the label.
	:param string text: The text of the label.
	:param integer size: The size of the label.
	:param align: The alignation of the text in the label.
	:type align: :ref:`align-constant`
	"""

	def __init__(self, sprite, over, font, text, size = 16, align = 0):
		super().__init__(sprite, over)
		self.text = Label(font, text, size, align, self.obj.worldPosition)
		self.text.setPosition(None, None, 0.2)
		font = self.text.font
		self.transformable.append(self.text)
		
	def enable(self):
		""" It enables the button events. (Enabled by default) """
		super().enable()
		self.text.visible = True

	def disable(self):
		""" It dishables the button events. """
		super().disable()
		self.text.visible = False
	
	def delete(self):
		""" Deletes the button """
		self.text.delete()
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
		
class TestButton(Button):
	def mouse_click(self):
		from core.utils import rand10
		print("(TestButton) Click from object: " + str(self))
		self.set_rotation(0, 0, 2)