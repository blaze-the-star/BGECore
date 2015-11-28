from core import behavior, module, utils, key
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
		self.speed = 9
		
	def onKeyPressed(self, keys):
		s = self.speed
		if key.T in keys: self.obj.worldPosition.y += s
		if key.G in keys: self.obj.worldPosition.y -= s
		if key.F in keys: self.obj.worldPosition.x += s
		if key.H in keys: self.obj.worldPosition.x -= s
		

class SceneEditor(behavior.Scene):
	def init(self):
		self.addBehavior(CameraBorder, self.scene.active_camera)
		self.addBehavior(BasicControl, "Cylinder")
		self.createTiles(50, 50)
		
	def createTiles(self, x, y):
		Tile.meshref.append(self.objectsInactive["DYN_Terrain.Base"])
		Tile.meshref.append(self.objectsInactive["DYN_Terrain.LOD1"])
		Tile.meshref.append(self.objectsInactive["DYN_Terrain.LOD2"])
		Tile.meshref.append(self.objectsInactive["DYN_Terrain.LOD3"])
		Tile.meshref.append(self.objectsInactive["DYN_Terrain.LOD4"])
		Tile.focus = self.objects["Cylinder"]
		
		self.tiles = [[]]
		self.tiles_index = (0, 0)
		#self.last_focus_position = Tile.focus.worldPosition.copy()
		self.i = 0
		
		x = int(x/2)
		y = int(y/2)
		self.tiles_scale = (x, y)
		for i in range(-x, x+1):
			l = []
			self.tiles.append(l)
			for j in range(-y, y+1):
				self.tiles[i+x].append(Tile(i, j))
				
		module.height_frequency_callbacks.append(self.updateTiles)
		
	def updateTiles(self, time):
		#if self.i == -1: return
		#update coords
		s = Tile.size
		p = Tile.focus.worldPosition
		self.tiles_index = int(p.x/s), int(p.y/s)
		#lx, ly = (int(self.last_focus_position.x/s), int(self.last_focus_position.y/s))
	
		#Update tiles inside 32x32 region at 1x32 rate.
		x, y = self.tiles_index #Updated when? Not here.
		sx, sy = self.tiles_scale
		#lx, ly = abs(x-lx), abs(y-ly)
		
		y0 = y-18+sy; y1 = y+18+sy
		x0 = x-18+sx; x1 = x+18+sx
		s = len(self.tiles)-2
		
		if y0 < 0: y0 = 0 
		if y0 >= s: y0 = s-1 
		if y1 < 0: y1 = 0
		if y1 >= s: y1 = s-1
		if x0 < 0: x0 = 0 
		if x0 >= s: x0 = s-1 
		if x1 < 0: x1 = 0
		if x1 >= s: x1 = s-1
		
		self.i += 1
		if self.i < x0: self.i = x0
		if self.i > x1-1:
			self.i = x0
			#self.i = -1
			
		for i in range(y0, y1):
			self.tiles[self.i][i].update()
			
		
	
behavior.addScene(SceneEditor, "SceneEditor")

from random import randint
class Tile:
	size = 200
	meshref = []
	focus = None
	
	def __init__(self, x, y):
		self._x = x
		self._y = y
		self.x = x * Tile.size
		self.y = y * Tile.size
		self.o = None
		self.n = 0
		self.update()
		
	def update(self):
		#print("U: " + str(self.x/self.size) + ' ' + str(self.y/self.size))
		distance = Tile.focus.getDistanceTo([self.x, self.y, 0])
		
		if distance <= Tile.size: 		self.check(0, self.x, self.y)
		elif distance <= Tile.size*2:	self.check(1, self.x, self.y)
		elif distance <= Tile.size*3:	self.check(2, self.x, self.y)
		elif distance <= Tile.size*6:	self.check(3, self.x, self.y)
		elif distance <= Tile.size*10:	self.check(4, self.x, self.y)
		else:							self.check(5, self.x, self.y)
			
	def check(self, n, x, y):
		if self.o:
			if self.n == n: return
			else:
				self.o.endObject()
				self.o = None
			
		if n >= len(Tile.meshref): return
		
		obj = Tile.meshref[n]
		sc = module.scene_game
		self.o = sc.addObject(obj, sc.active_camera)
		self.o.worldPosition = [x, y, 0]
		self.o.worldOrientation = [0,0,0]
		self.n = n
		self.updateMesh(obj, n)
		
	def updateMesh(self, obj, lod):
		if lod == 1:
			#Notice that it's the same mesh, we must replace meshes.
			print(obj.name)
			mesh = logic.LibNew(obj.name+str(self.x)+'x'+str(self.y), 'Mesh', [self.o.name])
			LibLoad(blend, type, data, load_actions=False, verbose=False, load_scripts=True, async=False)
			print(mesh)
			v = mesh.getVertex(0, 15)
			v.XYZ = [v.x, v.y, utils.randint(0, 100)]
			print(v.XYZ)
			#obj.reinstancePhysicsMesh(obj, mesh)
			
			#Replace mesh doesn't work for object instances, we will have to try with a libload copy on dynamic.
			#If we are gona do that reinstancePhysicsMesh() may be a better option.
			self.o.replaceMesh(mesh, True, True)
		
		
	