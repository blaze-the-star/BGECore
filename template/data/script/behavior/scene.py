from core import behavior, utils, module, key, media
from script import credits, constant

class IntroScene(behavior.Scene):
	def init(self):
		if constant.GAME_DEBUG == False: credits.IntroCredits()
		else: module.scene_gui.objects["GUIBlackScreen"].color.w = 0
		module.window.hideCursor()
		utils.setFilter2D("FXAA", self.scene.active_camera, 0)
		utils.setFilter2D("ChromaticAberration", self.scene.active_camera, 1)
		
		self.camtrack = self.objects["IntroCamera"]
		#self.camtrack.playAction("IntroCameraAction", 0, 2000)
		self.addBehavior(behavior.MouseLook, self.camtrack)
		utils.setCamera(self, "IntroCamera")
		
		#Subtitles
		self.subs = media.Subtitles(module.labels["Subtitles"], "gui/Star Trek.srt")
		
		
	def update(self):
		pass

	def onExit(self):
		pass

#This tells BGECore to use the ExampleScene behavior when the scene "Main" is loaded.
behavior.addScene(IntroScene, "Intro")