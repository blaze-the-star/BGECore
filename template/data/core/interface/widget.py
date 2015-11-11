from bge import logic
from mathutils import Vector
from core import module

dict = module.widget_dict

#TODO: Style Mistake, all methods should be mouseOver() not mouse_over()
class Widget():
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
		dict[self.obj] = self
		
	def delete(self):
		del dict[self.obj]
		del self
		
	def mouse_in(self):
		pass
		
	def mouse_out(self):
		pass
		
	def mouse_over(self):
		pass
	
	def mouse_click(self):
		pass
		
	def getPosition(self):
		return self._location
	
	def setPosition(self, x, y, z):
		for obj in self.transformable:
			if obj.__class__.__name__ == "KX_GameObject":
				if x: obj.worldPosition.x = x
				if y: obj.worldPosition.y = y
				if z: obj.worldPosition.z = z
			else:
				obj.setPosition(x, y, z)
			
		self._location = self.obj.worldPosition
		
	def getScale(self):
		return self._scale
	
	def setScale(self, x, y, z):
		for obj in self.transformable:
			if obj.__class__.__name__ == "KX_GameObject":
				if x: obj.localScale.x = x
				if y: obj.localScale.y = y
				if z: obj.localScale.z = z
			else:
				obj.setScale(x, y, z)
			
		self._scale = self.obj.localScale
		
	def getRotation(self):
		return self._rotation
		
	def setRotation(self, x, y, z):
		for obj in self.transformable:
			if obj.__class__.__name__ == "KX_GameObject":
				v = self._rotation
				if x: v.x = x
				if y: v.y = y
				if z: v.z = z
				if obj == self.obj: obj.localOrientation = v.to_matrix()
				else: obj.localOrientation = v.to_matrix() * obj.worldOrientation
			else:
				obj.setRotation(x, y, z)
				
		self._rotation = self.obj.worldOrientation.to_euler()
	
	