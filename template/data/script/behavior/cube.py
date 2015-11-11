from core import behavior
import mathutils

class CubeBehavior(behavior.Object):
	def init(self):
		pass
		
	def update(self):
		v = self.obj.worldOrientation.to_euler()
		v.z += 0.005
		self.obj.localOrientation = v.to_matrix()
		
#TODO
#self.getBehaviors()		#List of all the behaviors of the current object.
#self.pause()				#Stops calling update() until self.resume() is executed.
#self.resume()				#...
#self.removeMe()			#Removes the current behavior from the object.
#self.sceneBehavior()		#Returns the current scene Behavior, if none (becouse the object is linked to the game, returns None)
#self.scene					#The current scene.
