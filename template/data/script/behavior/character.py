from core import behavior, utils, module
from bge import logic
from core import key

#This is a behavior that controls the main character.
#It does not control movement, that's done in the ThirdPerson behavior.
#It does control animations and things related to the mesh and armature of the mc.
class CharacterBehavior(behavior.Object):
	def init(self):
		#References to objects that will be loaded dynamically.
		self.mc = None
		self.arm = None
		
		#We load dynamically the main character and the armature.
		#If not self.loadfile is provided the objects will not be loaded dynamically.
		#Instead, member initialization should be used with already loaded objects.
		#Objects loaded using libLoad won't be accesible throught KX_Scene.objects,
		#instead you should use module.scene_behavior.objects.
		if self.loadfile: utils.libLoad(self.loadfile, "Scene", self.scene.active_camera)
		
		#We need to enable input for this behavior to make onKey events aviable.
		module.enableInputFor(self)
		
		#Indicates if some other action in been played or it should be just standing there.
		self.last_at_ground = False
	
	def update(self):
		#Wait until the dynamically loaded objects are aviable.
		if self.loadfile:
			try:
				self.mc = module.scene_behavior.objects["Character"]
				self.arm = module.scene_behavior.objects["Armature"]
			except: return
		
		#Make the mesh move like our generic Player object.
		self.mc.worldPosition = self.obj.worldPosition
		self.mc.localOrientation = self.obj.worldOrientation
		
		#Reference to the camera behavior (ThirdPerson).
		b_cam = module.scene_behavior.b_camera
		
		#Change visibility of mc according to the camera distance.
		#Rememer to enable "object color" on the material settings.
		if b_cam.camera_real_distance <= 4: self.mc.color.w = b_cam.camera_real_distance/4
		else: self.mc.color.w = 1
		
		print(b_cam.at_ground)
		print(self.last_at_ground)
		
		#Stop jump animation at ground
		if b_cam.at_ground != self.last_at_ground:
			print("Here")
			if self.last_at_ground:
				self.playAction("Jump", 0, 32, layer=0, blendin=5, play_mode=logic.KX_ACTION_MODE_LOOP)
			else:
				self.playAction("Stand", 0, 32, layer=0, blendin=5, play_mode=logic.KX_ACTION_MODE_LOOP)
			
		print(b_cam.at_ground)
		print(self.last_at_ground)
		self.last_at_ground = b_cam.at_ground
		
	def onKeyDown(self, keys):
		#We check if mc is aviable before doing anything.
		#Since mc and arm are loaded at the same time we don't need to check both.
		if not self.mc: return
		
		#Notice that since we used key replacement in the scene behavior the arrow keys will also work.
		if key.W in keys:
			self.playAction("Walk", 0, 32, layer=0, blendin=5, play_mode=logic.KX_ACTION_MODE_LOOP)
			
		#if key.SPACE in keys:
			#self.arm.playAction("Jump", 0, 32, layer=0, blendin=5, play_mode=logic.KX_ACTION_MODE_LOOP)
		
	def playAction(self, name, start=0, finish=32, layer=0, blendin=5, play_mode=logic.KX_ACTION_MODE_LOOP):
		#utils.verbose("Object (" + self.arm.name + "): Playing '" + name + "' now.")
		self.arm.stopAction(layer)
		self.arm.playAction(name, start, finish, layer, blendin, play_mode)
			
	def onKeyUp(self, keys):
		if not self.mc: return
		if key.W in keys:
			self.arm.stopAction(0)
			self.arm.playAction("Stand", 0, 32, layer=0, blendin=5, play_mode=logic.KX_ACTION_MODE_LOOP)