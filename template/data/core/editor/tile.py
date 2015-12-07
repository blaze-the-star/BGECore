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
		#self.update()

	def update(self):
		""" Updates a tile chink based on it's distance from the focus """
		#print("U: " + str(self.x/self.size) + ' ' + str(self.y/self.size))
		distance = Tile.focus.getDistanceTo([self.x, self.y, 0])

		if distance <= Tile.size: 		self.check(0, self.x, self.y)
		elif distance <= Tile.size*2:	self.check(1, self.x, self.y)
		#elif distance <= Tile.size*3:	self.check(2, self.x, self.y)
		#elif distance <= Tile.size*6:	self.check(3, self.x, self.y)
		#elif distance <= Tile.size*10:	self.check(4, self.x, self.y)
		else:							self.check(-1, self.x, self.y)

	def check(self, n, x, y):
		if self.n != n:
			filepath = "core/editor/LOD" + str(n) + ".blend"
			if self.o and self.n >= 0:
				self.o = None
				Tile.generator[self.n].remove((self.x, self.y))
			if n >= 0:
				Tile.generator[n].new((x, y), self.tileJustLoaded)
			self.n = n

	def tileJustLoaded(self, obj, time): #Add time
		obj.worldPosition = (self.x, self.y, 0)
		self.o = obj
		print(str(obj) + " Time: " + str(time))
		#self.updateMesh(obj, self.n)

	def updateMesh(self, obj, lod):
		if lod == 1:
			mesh = obj.meshes[0]
			v = mesh.getVertex(0, 15)
			v.XYZ = [v.x, v.y, utils.randint(0, 100)]
			obj.reinstancePhysicsMesh(obj, mesh)
