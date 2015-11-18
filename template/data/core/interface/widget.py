from bge import logic
from mathutils import Vector, Euler
from core import module

dict = module.widget_dict

#TODO: Style Mistake, all methods should be mouseOver() not mouse_over()
class Widget():
	""" This is a widget 
	
	.. attribute:: obj
		
		The KX_GameObject used as the base of the widget.
	
	.. attribute:: transformable
		
		List of objects that will be also tranformed with the widget (Recursive).
	
	.. attribute:: position
		
		The position of the widget in world coordinates.
		
		:type: |Vector|
	
	.. attribute:: scale
		
		The scale of the widget.
		
		:type: |Vector|
	
	.. attribute:: rotation
		
		The rotation of the widget in world coordinates.
		
		:type: mathutils.Euler
	
	"""
	_active = True

	def __init__(self, obj):
		self.scene = module.window.scene_gui
		if type(obj) is str:
			self.obj = self.scene.objects[obj]
		else:
			self.obj = obj
			self.scene = obj.scene
		
		self._location = self.obj.worldPosition
		self._scale = self.obj.localScale
		self._rotation = self.obj.worldOrientation.to_euler()
		
		self.transformable = [self.obj]
		
		global dict
		dict[self.obj] = self
		
	def delete(self):
		global dict
		del dict[self.obj]
		del self
		
	def mouseIn(self):
		pass
		
	def mouseOut(self):
		pass
		
	def mouseOver(self):
		pass
	
	def mouseClick(self):
		pass
		
	@property
	def position(self):
		return self._location
	
	@position.setter
	def position(self, xyz):
		for obj in self.transformable:
			if obj.__class__.__name__ == "KX_GameObject":
				obj.worldPosition = xyz
			else:
				obj.position = xyz
		self._location = self.obj.worldPosition
		
	@property
	def scale(self):
		return self._scale
	
	@scale.setter
	def scale(self, xyz):
		for obj in self.transformable:
			if obj.__class__.__name__ == "KX_GameObject":
				obj.localScale = xyz
			else:
				obj.scale = xyz
		self._scale = self.obj.localScale
		
	@property
	def rotation(self):
		return self._rotation
		
	@rotation.setter
	def rotation(self, xyz):
		for obj in self.transformable:
			if obj.__class__.__name__ == "KX_GameObject":
				v = self._rotation
				v = xyz
				if obj == self.obj: obj.localOrientation = v.to_matrix()
				else: obj.localOrientation = v.to_matrix() * obj.worldOrientation
			else:
				obj.rotation = xyz
		self._rotation = self.obj.worldOrientation.to_euler()
	
	