from core import module, utils, dynamic, behavior
from random import randint
from . import format
import os
from bge import logic

class DynamicTerrain:
	""" Creates a new terrain from a .terrain file. If the file doesn't exist creates a new terrain. """
	sizeX = 20
	sizeY = 20

	def __init__(self, focus, filepath):
		Tile.dynt = self
		self.focus = focus
		self.filepath = filepath
		
		if os.path.isfile(self.filepath) == False:
			format.newTerrainFile(self.filepath, self.sizeX, self.sizeY, 5, [2696, 825, 180, 48, 36], [50, 25, 13, 10, 10], [50, 25, 13, 10, 10])
			print("New file!")
			
		self.terrain_file = format.TerrainFile(self.filepath)
		self.tile_manager = TileManager(self.focus, self.sizeX, self.sizeY, self.terrain_file)
		
	def writeChunk(self, obj):
		""" Test method to write an entire chunk to the disk.

		:param |KX_GameObject| obj: The Tile to store.
		"""
		
		lod = int(obj.name[15:])
		
		x, y = (obj.worldPosition.x/Tile.size, obj.worldPosition.y/Tile.size)
		msx, msy = self.terrain_file._msx, self.terrain_file._msy
		chunkpos = (int(x)+int(msx/2), int(y)+int(msy/2))
		
		vlist = []
		mesh = obj.meshes[0]
		for i in range(mesh.getVertexArrayLength(0)):
			vlist.append(mesh.getVertex(0, i))
		
		self.terrain_file.setChunkArray(lod, chunkpos, vlist)
		
	def updateChunk(self, obj):
		""" Updates the hight of a lod chunk from the disk. """
	
		lod = int(obj.name[15:])
		
		x, y = (obj.worldPosition.x/Tile.size, obj.worldPosition.y/Tile.size)
		msx, msy = self.terrain_file._msx, self.terrain_file._msy
		chunkpos = (int(x)+int(msx/2), int(y)+int(msy/2))
		
		vlist = self.terrain_file.getChunkArray(lod, chunkpos)
		
		i = 0
		cn = False
		mesh = obj.meshes[0]
		for vertex in vlist:
			z, nx, ny, nz = vertex
			v = mesh.getVertex(0, i)
			v.XYZ = (v.x, v.y, z)
			
			#if nx != None: v.setNormal((nx, ny, nz))
			#else: cn = True
			i += 1
			
		if True: utils.recalculateNormals(obj)
		
	def __del__(self):
		del self.terrain_file
		del self.tile_manager

class TileManager(behavior.Object):
	def __init__(self, focus, x, y, file):
		Tile.focus = focus
		self.file = file

		path = "core/editor/LOD"
		for i in range(0, 5):
			Tile.generator.append(dynamic.ObjectGenerator(path+str(i)+".blend"))

		Tile.file = file
		self.tiles = [[]]
		self.tiles_index = (0, 0)

		self.i = 0
		self.j = 0

		x = int(x/2)
		y = int(y/2)
		self.tiles_scale = (x, y)
		for i in range(-x, x+1):
			l = []
			self.tiles.append(l)
			for j in range(-y, y+1):
				self.tiles[i+x].append(Tile(i, j))
				
		self.updateAll()

		#module.height_frequency_callbacks.append(self.update)
		super().__init__()
		self.scene = module.scene_game
		module.scene_behavior.behaviors.append(self)

	def updateAll(self):
		for tx in self.tiles:
			for x in tx: x.update()
		
	def update(self):
		self.update_lazy()

	def update_lazy(self, maxfac = 2):
		s = Tile.size
		p = Tile.focus.worldPosition
		self.tiles_index = int(p.x/s), int(p.y/s)
		sx, sy = self.tiles_scale

		fac = 0
		if self.i <= 0: self.i = abs(sx*2)
		while(self.i > 0):
			self.i -= 1
			if self.j <= 0: self.j = abs(sy*2)
			while(self.j > 0):
					self.j -= 1
					fac += self.tiles[self.i][self.j].update()
					if fac > maxfac: return

	def update_boxmethod(self, time):
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

class Tile:
	size = 200
	focus = None
	minlod = 0
	generator = []
	file = None
	dynt = None
	
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
		self._n = self.n

	def update(self):
		""" Updates a tile chink based on it's distance from the focus

		:return int factor: The inverse of the LOD level that will be applied,
		no mesh = 0, most low poly = 1, most high poly = maxium lod.
		"""

		distance = Tile.focus.getDistanceTo([self.x, self.y, 0])
		m = Tile.minlod

		if distance <= Tile.size: n = m
		elif distance <= Tile.size*2: n = m+1
		elif distance <= Tile.size*3: n = m+2
		elif distance <= Tile.size*7: n = m+3
		elif distance <= Tile.size*10: n = m+4
		elif distance > Tile.size*2: n = -1

		if n < 5:
			s = self.check(n, self.x, self.y)
		else:
			self.check(-1, self.x, self.y)
			s = 0.2
		return s

	def check(self, n, x, y):
		if self.n != n:
			filepath = "core/editor/LOD" + str(n) + ".blend"
			if n >= 0:
				Tile.generator[n].new((x, y), self.tileJustLoaded)
			else:
				if self.o and self.n >= 0:
					self.o = None
					Tile.generator[self.n].remove((self.x, self.y))
			self.n = n
			if n == -1: return 0.5
			else: return 5-n+Tile.minlod
		return 0.05

	def tileJustLoaded(self, obj, time): #Add time
		obj.worldPosition = (self.x, self.y, 0)
		obj.visible = True
		obj["DYN_Terrain.RAYDETECT"] = 0
		
		if self.o and self._n >= 0:
			self.o = None
			Tile.generator[self._n].remove((self.x, self.y))

		self.o = obj
		self._n = self.n
		#print(str(obj) + " Time: " + str(time))
		
		self.updateMesh(obj, self.n)

	def updateMesh(self, obj, lod):
		mesh = obj.meshes[0]
		Tile.dynt.updateChunk(obj)
