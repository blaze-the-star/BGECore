from bge import logic
from mathutils import Vector, Euler
from core import module, utils

class ProxyPosition(Vector):
	obj = None
	def __setattr__(self, name, value):
		if not hasattr(self, "obj"): super(Vector, self).__setattr__(name, value); return
		if name == 'x': self.obj.position = [value, self.y, self.z]; return
		if name == 'y': self.obj.position = [self.x, value, self.z]; return
		if name == 'z': self.obj.position = [self.x, self.y, value]; return
		super(Vector, self).__setattr__(name, value)
		
class ProxyScale(Vector):
	def __setattr__(self, name, value):
		if not hasattr(self, "obj"): super(Vector, self).__setattr__(name, value); return
		if name == 'x': self.obj.scale = [value, self.y, self.z]; return
		if name == 'y': self.obj.scale = [self.x, value, self.z]; return
		if name == 'z': self.obj.scale = [self.x, self.y, value]; return
		super(Vector, self).__setattr__(name, value)
		
class ProxyRotation(Euler):
	def __setattr__(self, name, value):
		if not hasattr(self, "obj"): super(Euler, self).__setattr__(name, value); return
		if name == 'x': self.obj.rotation = [value, self.y, self.z]; return
		if name == 'y': self.obj.rotation = [self.x, value, self.z]; return
		if name == 'z': self.obj.rotation = [self.x, self.y, value]; return
		super(Euler, self).__setattr__(name, value)
		
class ProxyColor(Vector):
	def __setattr__(self, name, value):
		if not hasattr(self, "obj"): super(Vector, self).__setattr__(name, value); return
		if name == 'x': self.obj.color = [value, self.y, self.z, self.w]; return
		if name == 'y': self.obj.color = [self.x, value, self.z, self.w]; return
		if name == 'z': self.obj.color = [self.x, self.y, value, self.w]; return
		if name == 'w': self.obj.color = [self.x, self.y, self.z, value]; return
		super(Vector, self).__setattr__(name, value)

dict = module.widget_dict

#TODO: Style Mistake, all methods should be mouseOver() not mouse_over()
class Widget():
	""" This is a widget.
	
	Widgets usually are 2D objects that represent a GUI element. To make a widget in blender you can just use a plane with an image texture. 
	
	.. attribute:: obj
		
		The KX_GameObject used as the base of the widget.
	
	.. attribute:: transformable
		
		List of objects that will be also tranformed with the widget (Recursive).
	
	"""
	_immuse_keyboard = True

	def __init__(self, obj):
		self.scene = module.window.scene_gui
		if type(obj) is str:
			self.obj = self.scene.objects[obj]
		else:
			self.obj = obj
			self.scene = obj.scene
		
		self._location = self.ProxyPosition()
		self._scale = self.ProxyScale()
		self._rotation = self.ProxyRotation()
		self._color = self.ProxyColor()
		self._active = True
		self.transformable = [self.obj]
		
		global dict
		dict[self.obj] = self
		
	def ProxyPosition(self):
		P = ProxyPosition(self.obj.worldPosition)
		P.obj = self; return P
		
	def ProxyScale(self):
		P = ProxyScale(self.obj.localScale)
		P.obj = self; return P
		
	def ProxyRotation(self):
		P = ProxyRotation(self.obj.worldOrientation.to_euler())
		P.obj = self; return P
		
	def ProxyColor(self):
		P = ProxyColor(self.obj.color)
		P.obj = self; return P
	
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
		
	def _mouseClick(self):
		pass
		
	def _mouseIn(self):
		pass
	
	def _mouseOut(self):
		pass
		
	def mousePressed(self):
		pass
		
	def onKeyUp(self, keys):
		pass

	def onKeyPressed(self, keys):
		pass

	def onKeyDown(self, keys):
		pass
		
	@property
	def position(self):
		""" The position of the widget. On read it's the sprite position, on write it applies a relative position to all inner elements of the widget. """
		return self._location
	
	@position.setter
	def position(self, xyz):
		xyz = Vector(xyz)
		pos = Vector(self.obj.worldPosition)
		for obj in self.transformable:
			if obj.__class__.__name__ == "KX_GameObject":
				if obj == self.obj: obj.worldPosition = xyz
				else: obj.worldPosition = xyz + utils.vectorFrom2Points(pos, obj.worldPosition)
			else:
				v = utils.vectorFrom2Points(pos, obj.position)
				obj.position = xyz + v
		self._location = self.ProxyPosition()
		
	@property
	def scale(self):
		""" The scale of the widget. On read it's the sprite scale, on write it applies a proportional scale to all inner elements of the widget. """
		return self._scale
	
	@scale.setter
	def scale(self, xyz):
		xyz = Vector(xyz)
		sca = Vector(self.obj.localScale)
		for obj in self.transformable:
			if obj.__class__.__name__ == "KX_GameObject":
				if obj == self.obj: obj.localScale = xyz
				else:
					os = obj.localScale
					ls = Vector((xyz.x / sca.x, xyz.y / sca.y, xyz.z / sca.z))
					sc = [os.x * ls.x, os.y * ls.y, os.z * ls.z]
					obj.localScale = sc
			else:
				os = obj.scale
				ls = Vector((xyz.x / sca.x, xyz.y / sca.y, xyz.z / sca.z))
				sc = [os.x * ls.x, os.y * ls.y, os.z * ls.z]
				obj.scale = sc 
					
		self._scale = self.ProxyScale()
		
	@property
	def rotation(self):
		""" The rotation of the widget. On read it's the sprite orientation, on write it applies a proportional rotation to all inner elements of the widget. """
		return self._rotation
		
	@rotation.setter
	def rotation(self, xyz):
		if len(xyz) != 3: utils.debug("Rotation assignment failed on " + self.obj.name + " object. xyz size != 3.")
		if isinstance(xyz, (list, tuple)) or len(xyz) == 3:
			xyz = Euler(xyz, 'XYZ')
		srt = self.obj.localOrientation.copy()
		xyz = xyz.to_matrix()
			
		for obj in self.transformable:
			if obj.__class__.__name__ == "KX_GameObject":
				if obj == self.obj: obj.localOrientation = xyz
				else:
					srr = obj.worldOrientation.copy()
					srr.rotate(xyz)
					srr = srr.to_euler()
					obj.localOrientation = srr
			else:
				srr = obj.rotation.copy()
				srr.rotate(xyz)
				obj.localOrientation = srr
				obj.rotation = srr
		self._rotation = self.ProxyRotation()
		
	@property
	def color(self):
		""" The widget color. The color is applied to all inner elemnts of the widget. 
		
		.. note:: Object color must be enabled in the material properties.
		"""
		return self._color
		
	@color.setter
	def color(self, color):
		x, y, z, w = color
		if self.color.x != x:
			for obj in self.transformable: obj.color.x = x
		if self.color.y != y:
			for obj in self.transformable: obj.color.y = y
		if self.color.z != z:
			for obj in self.transformable: obj.color.z = z
		if self.color.w != w:
			for obj in self.transformable: obj.color.w = w
		self._color = self.ProxyColor()
		
	@property
	def active(self): return self._active
	
	@active.setter
	def active(self, x): self._active = x
	
	