from core import behavior, module, utils, key
from .tile import TileManager
from bge import logic, types
from mathutils import Vector
import math

class CameraBorder(behavior.Object):
	def init(self):
		module.enableInputFor(self)
		self.speed = 0.03
		self.margin = 0.01
		self.capmargin = self.margin - 0.001 
		
	def update(self):
		x, y = logic.mouse.position
		cam = self.obj
		pos = Vector([0,0,0])
		m = self.margin
		n = self.capmargin
		l = 1
		speed = self.speed * cam.worldPosition.z
		
		if y < m: pos.y -= speed
		if y < n: y = n
		if y > 1-m: pos.y += speed
		if y > 1-n: y = 1-n
		if x < m: pos.x -= speed
		if x < n: x = n
		if x > 1-m: pos.x += speed
		if x > 1-n: x = 1-n
		logic.mouse.position = (x, y)
		
		rot = cam.worldOrientation.to_euler()
		x, y = (pos.x, pos.y)
		pos.x = x * math.cos(rot.z) + y * math.cos(rot.z-1.5)
		pos.y = x * math.sin(rot.z) + y * math.sin(rot.z-1.5)
		cam.worldPosition = pos + cam.worldPosition
		
	def onKeyPressed(self, keys):
		rot = self.obj.worldOrientation.to_euler()
		pos = Vector([0,0,0])
		if key.W in keys: rot.x += 0.01
		if key.S in keys: rot.x -= 0.01
		if key.A in keys: rot.z += 0.01
		if key.D in keys: rot.z -= 0.01
		if key.WHEELUPMOUSE in keys: pos.z = -self.obj.worldPosition.z * 0.3
		if key.WHEELDOWNMOUSE in keys: pos.z = self.obj.worldPosition.z * 0.3
		
		#Max speed is dependent of the Tile sizes, ex (200m/s = size) / 50fps = 4m/tick
		#Since we are using an extra radius we can guarante a speed of 8m/tick without glitches: 8*60fps = 480m/s = 1728 km/h
		if pos.length > 8: pos.length = 8 
		pos.rotate(self.obj.worldOrientation)
		self.obj.worldPosition += pos
		self.obj.worldOrientation = rot

class BasicControl(behavior.Object):
	def init(self):
		module.enableInputFor(self)
		self.speed = 4
		
	def onKeyPressed(self, keys):
		s = self.speed
		if key.T in keys: self.obj.worldPosition.y += s
		if key.G in keys: self.obj.worldPosition.y -= s
		if key.F in keys: self.obj.worldPosition.x += s
		if key.H in keys: self.obj.worldPosition.x -= s
	
		
class SceneEditor(behavior.Scene):
	def init(self):
		self.addBehavior(CameraBorder, self.scene.active_camera)
		focus = self.objects["Cylinder"]
		self.addBehavior(BasicControl, focus)
		self.tm = TileManager(focus, 50, 50)
		
		
#behavior.addScene(SceneEditor, "SceneEditor") #This is done on dynamic, so that we can still import dynamic here.