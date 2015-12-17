class TerrainFile:
	""" This class manages .terrain files used in the editor """
	
	def __init__(self):
		self.filepath = filepath
			
	def __del__(self):
		pass

	def new(self, filepath, msx, msy,  bN, vN, bNTsx, bNTsy):
		return self
		
	def load(self, filepath):
		return self
		
	def getVertexIndexInRect(self, LOD, x, y, z, w):
		pass
		
	def getVertexIndexInSphere(self, LOD, point, radious):
		pass
		
	def getVertexIndexNearestTo(self, LOD, point):
		pass
	
	def getChunkArray(self, LOD, chunkpos):
		pass
		
	def getVertex(self, LOD, chunkpos, id):
		pass
		
	def setVertex(self, LOD, chunkpos, id, z, normal):
		pass
		
	def getTexture(self, LOD, chunkpos):
		pass
		
	def setTexture(self, LOD, chunkpos, texture):
		pass