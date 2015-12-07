from core import module, utils, dynamic
from random import randint

class TileManager:
	def __init__(self, focus, x, y):
		Tile.focus = focus
		
		path = "core/editor/LOD"
		for i in range(0, 5):
			Tile.generator.append(dynamic.ObjectGenerator(path+str(i)+".blend"))
		
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
				
		module.height_frequency_callbacks.append(self.update)

	def update(self, time):
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
		
		y0 = y-20+sy; y1 = y+20+sy
		x0 = x-20+sx; x1 = x+20+sx
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
		

#All of this must be reimplemented, becouse:
#https://developer.blender.org/D1146

#Basically when using LibNew with a mesh it only loads the mesh.
#After that if we do obj.replaceMesh where obj is an instance of base,
#all other instances share the same physic mesh, we don't want that.

#Using reinstancePhysicsMesh() also replaces all other intances physical mesh.

#Therefore we only have a few options. One of them is to have multiple .blend files
#each one with one LOD level base.
#This way using LibLoad with scene we can efectively create new objects that aren't instances.

#We can also try to put all these bases together in one single file and then load it as binary data.
#But it should not be nesscesary. We will wait for the "ofuscation" phase of BGECore development to
#do that.

#They may be a problem thought. Maybe even if we use LibLoad on scene mode it stills loads new objects as
#instances (all hope not). If that's the case the only aviable solution is go for the RAW method.

class Tile:
	size = 200
	focus = None
	STABLE = 0
	LOADING = 1
	LOADED = 2
	generator = []
	
	def __init__(self, x, y):
		""" Creates a new Tile
		
		A Tile is an objects that automatically loads a chunk of terrain using it's own LOD system. It load's the chunks from
		disk instead of memory, allowing to have huge terrains. It loads them as single instances, allowing for mesh modifications
		on real time.
		
		:param int x: The x position of the tile, in Map units (u/size)
		:param int y: The y position of the tile, in Map units (u/size)
		"""
		
		self._x = x
		self._y = y
		self.x = x * Tile.size
		self.y = y * Tile.size
		self.o = None
		self.n = -1
		self.state = Tile.STABLE
		
		#And finally, we initializate all tiles in the first frame.
		self.update()		
		
	def update(self):
		""" Updates a tile chink based on it's distance from the focus """
		#print("U: " + str(self.x/self.size) + ' ' + str(self.y/self.size))
		distance = Tile.focus.getDistanceTo([self.x, self.y, 0])
		
		if distance <= Tile.size: 		self.check(0, self.x, self.y)
		elif distance <= Tile.size*2:	self.check(1, self.x, self.y)
		elif distance <= Tile.size*3:	self.check(2, self.x, self.y)
		elif distance <= Tile.size*6:	self.check(3, self.x, self.y)
		elif distance <= Tile.size*10:	self.check(4, self.x, self.y)
		else:							self.check(-1, self.x, self.y)
			
	def check(self, n, x, y):
		#NOTES
		#We don't use inactive objects (for now), we load directly all of them once.
		#If we only load a mesh, a new object is not created, obj.replaceMesh won't work as it will copy meshes across all instances.
		#So we need to set LibLoad to load the scene, this is already done in dyncamic.loadScene(), so no problem.
		#However this objects should be loaded on an active layer so that we can use LibNew to duplicate them.
		
		#We need to efectively create new objects, not just new meshes. That's becouse obj.replaceMesh also replaces
		#meshes of the same instances. Therefore we need completly new objects. 
		
		if n >= 0 and self.n != n:
			filepath = "core/editor/LOD" + str(n) + ".blend"
			if self.o:
				self.o.endObject()
				self.o = None
				Tile.generator[n].remove((self.x, self.y))
			Tile.generator[n].new((x, y), self.tileJustLoaded)
			self.n = n
		
		return
			#This gives "Blend file already open". Before I hang myself I'll check if the libaries name are the same.
			#If that doesn't work we will try opening the files manually on binary mode. <-- Seems to work!
			#If that doesn't work either we'll try generating new filenames in realtime
			#If that still doesn't work we will go for the Movment algorithm.
			#You won't kill me that easy! HAHAHAHAH!
			#No we need to free objects...
		
		#They should go on a special dict, like module.lod_tile_base[], where they would be ordered by
		#(x,y) tuples. So:
		#if self.state == Tile.LOADING and (x,y) in module.lod_tile_base:
		#	self.state = Tile.LOADED
		#	self.
		
		if self.o:
			if self.n == n: return
			else:
				self.o.endObject()
				self.o = None
				self.state = Tile.NOMESH
			
		if n >= len(Tile.meshref): return
		
		#if self.state == 0:
		sc = module.scene_game
		self.o = sc.addObject(obj, sc.active_camera)
		self.o.worldPosition = [x, y, 0]
		self.o.worldOrientation = [0,0,0]
		self.n = n
		self.updateMesh(obj, n)
		
	def tileJustLoaded(self, obj):
		obj.worldPosition = (self.x, self.y, 0)
		self.o = obj
		self.updateMesh(obj, self.n)
		
	def updateMesh(self, obj, lod):
		if lod == 1:
			#Notice that it's the same mesh, we must replace meshes.
			#mesh = logic.LibNew(obj.name+str(self.x)+'x'+str(self.y), 'Mesh', [self.o.name])
			#LibLoad(blend, type, data, load_actions=False, verbose=False, load_scripts=True, async=False)
			mesh = obj.meshes[0]
			v = mesh.getVertex(0, 15)
			v.XYZ = [v.x, v.y, utils.randint(0, 100)]
			obj.reinstancePhysicsMesh(obj, mesh)
			
			#Replace mesh doesn't work for object instances, we will have to try with a libload copy on dynamic.
			#If we are gona do that reinstancePhysicsMesh() may be a better option.
			#self.o.replaceMesh(mesh, True, True)
		

