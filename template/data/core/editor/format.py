import struct

#TODO: Textures are implemented as an UV map, no real image is stored.

def _getHeaderFin(): return b'\x43\x72e\x61\x74\x65\x64 \x77\x69\x74h\x20BG' + b'\x45\x43\x6F\x72e\x20\x62y\x20Ro\x62e\x72\x74 ' + b'\x50\x6C\x61\x6E\x61\x73\x20\x4A\x69m\x65\x6Ee\x7A'

def newTerrainFile(filepath, msx, msy,  bN, vN, bNTsx, bNTsy):
	""" Creates a new .terrain file given the arguments. See *editor.DynaimcTerrain*. The created terrain file can be opened by the *TerrainFile* class. 
	
	:param string filepath: The relative path of the new .terrain file relative to the *data* directory.
	:param int msx: The map x size in number of tiles. (Max: 65535)
	:param int msy: The map y size in number of tiles. (Max: 65535)
	:param int bN: The number of LOD bases used. (Max: 255)
	:param list vN: The number of vertex in each LOD base. (List of integers). Obtained from *KX_MeshProxy.getVertexArrayLength(0)*
	:param list bNTsx: The texture x size in each LOD base. (List of integers)
	:param list bNTsy: The texture y size in each LOD base. (List of integers)
	
	.. note:: See the the format specifications in the file: *data/core/editor/format_specs.txt*
	"""
	vsb = 16
	fend = 11+8*bN + msx*msy*4+len(_getHeaderFin())
	byt = struct.pack("<HHHBI", msx, msy, vsb, bN, fend)
	
	if len(vN) != bN: raise ValueError("vN (vertex number) should be a list of size bN (bases number). It is not. ")
	
	def pack(st, elements):
		return struct.pack("<" + st*len(elements), *elements)
	
	with open(filepath, 'wb') as f:
		f.write(byt)
		f.write(pack("I", vN))
		f.write(pack("H", bNTsx))
		f.write(pack("H", bNTsy))
		f.write(b'\0'*msx*msy*4)
		f.write(_getHeaderFin())
	
class TerrainFile:
	""" This class manages .terrain files used in the editor """
	
	def __init__(self, filepath):
		self.filepath = filepath
		self.load()
			
	def __del__(self):
		pass
		
	def load(self):
		with open(self.filepath, 'rb') as f:
			preindex = struct.unpack('<HHHBI', f.read(11))
			self._msx = preindex[0]
			self._msy = preindex[1]
			self._vsb = preindex[2]
			self._bN = preindex[3]
			self._fend = preindex[4]
		
			self._vN = struct.unpack('<' + 'I'*self._bN, f.read(self._bN*4))
			self._bNTsx = struct.unpack('<' + 'H'*self._bN, f.read(self._bN*2))
			self._bNTsy = struct.unpack('<' + 'H'*self._bN, f.read(self._bN*2))
			self._index = list(struct.unpack('<' + 'I'*self._msx*self._msy, f.read(self._msx*self._msy*4)))
			
			headref = f.read(45)
			assert headref == _getHeaderFin(), "Terrain file failed to load." 
			
			self._startindex = 11+8*self._bN
			self._endindex = self._startindex + self._msx*self._msy*4 + len(_getHeaderFin())
			self._endtable = self._endindex
			
		
		self.chunksize = []
		self.chunktotalsize = 0
		for lod in range(self._bN):
			self.chunksize.append(self._vsb * self._vN[lod] +  self._bNTsx[lod]*self._bNTsy[lod]*2)
			self.chunktotalsize += self.chunksize[lod]
		
	def info(self):
		""" Returns file information as a string """
		
		def toKB(data): return str(int(data/1024)) + ' KB'
		
		dbs = self.chunktotalsize*self._msx*self._msy
		
		info = "Chunks size: " + str(self.chunksize) + "\n"	
		info += "Chunk total size: "+ toKB(self.chunktotalsize) + "\n"
		info += "Max number of chuncks: " + str(self._msx*self._msy) + "\n"
		info += "Max datablock segment size: " + toKB(dbs) + "\n"
		info += "Max file size: " + toKB(dbs+self._endtable) + "\n"
		
		used_chunks = 0
		for i in self._index:
			if i >= self._endtable: used_chunks += 1
		
		dbs = self.chunktotalsize*used_chunks
		info += "Used chuncks: " + str(used_chunks) + "\n"
		info += "Datablock segment size: " + toKB(dbs) + "\n"
		info += "File size: " + toKB(dbs+self._endtable)
			
		return info
			
	@property
	def size(self):
		""" Returns the x and y size in tiles. """
		return (self._msx, self._msy)
		
	def getVertexIndexInRect(self, LOD, x, y, z, w):
		pass
		
	def getVertexIndexInSphere(self, LOD, point, radious):
		pass
		
	def getVertexIndexNearestTo(self, LOD, point):
		pass
	
	def getChunkPositionInIndex(self, chunkpos):
		x, y = chunkpos
		if x > self._msx or x < 0: raise ValueError("Map position greater than map size or negative. ")
		if y > self._msy or y < 0: raise ValueError("Map position greater than map size or negative. ")
		return x*y + y
	
	def _updateIndex(self, x):
		with open(self.filepath, 'r+b') as f:
			f.seek(self._startindex + x*4)
			f.write(struct.pack("<I", self._index[x]))
			
	def allocateChunkArray(self, chunkpos):
		""" Alloctes a new chunk on the data segment. Return the position in the file of the new allocated chunk. """
		ipos = self.getChunkPositionInIndex(chunkpos)
		fpos = self._index[ipos]
		
		if fpos < self._endtable:
			self._index[ipos] = self._fend
			self._fend += self.chunktotalsize
			self._updateIndex(ipos)
			fpos = self._index[ipos]
		else: raise RuntimeError("Chunk already allocated.")
			
		with open(self.filepath, 'r+b') as f:
			f.seek(fpos)
			f.write(b'\0'*self.chunktotalsize)
			
		return fpos
	
	def setChunkArray(self, LOD, chunkpos, vertexlist):
		""" Modifies a chunk in the file. Allocates a new chunk if it doesn't exist.

		:param (x, y) chunkpos: The position of the chunk. x,y >= 0. 
		:param list vertexlist: A list of |KX_VertexProxy| to allocate. 
		"""
		
		assert len(vertexlist) == self._vN[LOD], "Vertex List is not of the same size than the chunk lod"
		
		fpos = self._index[self.getChunkPositionInIndex(chunkpos)]
		if fpos < self._endtable: fpos = self.allocateChunkArray(chunkpos)
		
		byt = b''
		for v in vertexlist:
			x, y, z = v.normal
			byt += struct.pack("<ffff", v.z, x, y, z)
		
		#Seek to the correct LOD in this chunk.
		if LOD > 0: fpos += self._vN[LOD-1]
		
		with open(self.filepath, 'r+b') as f:
			f.seek(fpos)
			f.write(byt)
	
	def getChunkArray(self, LOD, chunkpos):
		""" Return the array of hights of the selected chunk with the selected LOD. Returns the default chunk if the selected chunk is not in the file. """
		if LOD > self._bN: raise ValueError("LOD base can't be greater than the maxium LOD level. ")
		
		fpos = self._index[self.getChunkPositionInIndex(chunkpos)]
		if fpos < self._endtable:
			import itertools
			return itertools.repeat((0,None,None,None), self._vN[LOD])
			
		#Seek to the correct LOD in this chunk.
		if LOD > 0: fpos += self._vN[LOD-1]
				
		vlist = []
		with open(self.filepath, 'rb') as f:
			f.seek(fpos)
			for i in range(self._vN[LOD]):
				data = struct.unpack("<ffff", f.read(self._vsb))
				vlist.append(data)
			
		return vlist
		
	def getVertex(self, LOD, chunkpos, id):
		pass
		
	def setVertex(self, LOD, chunkpos, id, z, normal):
		pass
		
	def getTexture(self, LOD, chunkpos):
		pass
		
	def setTexture(self, LOD, chunkpos, texture):
		pass