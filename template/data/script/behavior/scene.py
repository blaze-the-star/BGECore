from core import behavior, utils, media, module
from script.behavior import cube, character
from core import key

class ExampleScene(behavior.Scene):
	def init(self):
		#Make sure the screen is hidden
		media.hideScreen()
		utils.setCamera(module.scene_gui, "GUICamera.000")
	
		#Key Initialization, replace arrows with WSAD so both systems work.
		key.mod[key.UPARROW] = key.bl.WKEY
		key.mod[key.DOWNARROW] = key.bl.SKEY
		key.mod[key.LEFTARROW] = key.bl.AKEY
		key.mod[key.RIGHTARROW] = key.bl.DKEY
		
		#Get object references, we can't use logic.getCurrentScene(), we use self.scene instead.
		self.cube = self.scene.objects["Cube"]
		
		#Assign behaviors, they are prefixed with "b_".
		self.b_cube = self.addBehavior(cube.CubeBehavior, self.cube)
		self.b_camera = self.addBehavior(behavior.ThirdPerson, "Player")
		
		#Some behaviors may need members initialization.
		self.b_camera.camera = self.scene.active_camera
		
		#One object can have multiple behaviors
		self.b_mc = self.addBehavior(character.CharacterBehavior, "Player")
		self.b_mc.loadfile = "character/Dave.blend"
		
		#Activate filters. Make sure the 2DFilter slot "Fn" exist on the camera and it's wired.
		utils.setFilter2D("FXAA", self.scene.active_camera, 2)
		utils.setFilter2D("ChromaticAberration", self.scene.active_camera, 1)
		#utils.setFilter2D("DOF", self.scene.active_camera, 0)
		
		#You may need to setup game properties depending on the filters you use. Check the filters documentation.
		self.scene.active_camera["vignette_size"] = 0.6
		
	def update(self):
		pass

	def onExit(self):
		pass

#This tells BGECore to use the ExampleScene behavior when the scene "Main" is loaded.
behavior.addScene(ExampleScene, "Main")