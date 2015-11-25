from core import behavior, module, utils, key
from bge import logic
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
		
		pos.rotate(self.obj.worldOrientation)
		self.obj.worldPosition += pos
		self.obj.worldOrientation = rot


class SceneEditor(behavior.Scene):
	def init(self):
		#ObjBehaviors
		self.addBehavior(CameraBorder, self.scene.active_camera)
	
		#Terrain
		self.i_base = self.objectsInactive["DYN_Terrain.Base"]
		self.i_LOD1 = self.objectsInactive["DYN_Terrain.LOD1"]
		self.i_LOD2 = self.objectsInactive["DYN_Terrain.LOD2"]
		self.i_LOD3 = self.objectsInactive["DYN_Terrain.LOD3"]
		
		self.spawn(self.i_base, [0,0,0])
		self.spawnRing(self.i_LOD1, 100, 100)
		self.spawnRing(self.i_LOD2, 200, 100)
		self.spawnRing(self.i_LOD2, 300, 100)
		self.spawnRing(self.i_LOD3, 400, 100)
		self.spawnRing(self.i_LOD3, 500, 100)
		self.spawnRing(self.i_LOD3, 600, 100)
		
	def spawnRing(self, obj, radi, dim):
		d = radi*2
		
		set = [0]
		j = int(radi/dim)
		for i in range(1, j+1):
			set.append(dim*i*2)
			set.append(-dim*i*2)
			
		print(set)
		for x in set:
			for y in set:
				if abs(x) == d or abs(y) == d:
					self.spawn(obj, [x, y, 0])
				else: continue
		
	def spawn(self, obj, position):
		o = self.scene.addObject(obj, self.scene.active_camera)
		o.worldPosition = position
		o.localOrientation = obj.localOrientation
		return o
	
behavior.addScene(SceneEditor, "SceneEditor")

class Tile(behavior.Object):
	def init(self):
		pass
		
	def updtae(self):
		pass