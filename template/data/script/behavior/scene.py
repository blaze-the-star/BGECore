from core import behavior, utils, media, module, key, sequencer
from script import text

class IntroScene(behavior.Scene):
	def init(self):
		gui = module.scene_gui_behavior
		
		#Setup the credits
		self.creditC = module.labels["CreditCategory"]
		self.creditN = module.labels["CreditName"]
		self.creditC.color.w = 0
		self.creditN.color.w = 0
		self.icredit = 0
		self.n = 0
		self.interpolCamOrth = None
		module.window.hideCursor()
		utils.setCamera(gui, "GUICamera.002")
		sequencer.Wait(5, self.nextCredit)
		sequencer.Wait(1, lambda: media.music.play("sound/music/Iñigo Sáenz - The Crusader.mp3"))
		
		sequencer.Wait(38, self.startTitle)
		self.background = gui.scene.objects["GUIBlackScreen"]
		self.title = gui.objects["GUITitle"]
		self.title.color.w = 0
		
		#Setup the scene		
		utils.setFilter2D("FXAA", self.scene.active_camera, 0)
		utils.setFilter2D("ChromaticAberration", self.scene.active_camera, 1)
		
		self.camtrack = self.objects["IntroCamera"]
		#self.camtrack.playAction("IntroCameraAction", 0, 2000)
		self.addBehavior(behavior.MouseLook, self.camtrack)
		utils.setCamera(self, "IntroCamera")
		
	def startTitle(self):
		sequencer.QuadraticInterpolation(1, 0, 18, self.backgroundcolor)
		sequencer.Wait(5, lambda: sequencer.AlphaFade(self.title, 0, 1, 6, 6, 5))
		
	def backgroundcolor(self, x):
		self.background.color.w = x
	
	def nextCredit(self):
		i = self.icredit
		credit = text.credits
		t = 3
		m = 2
		
		if i >= len(credit):
			self.afterCredit()
			return
			
		self.creditC.text = credit[i][0]
		self.creditN.text = credit[i][1]
		
		sequencer.Wait(1, lambda: sequencer.AlphaFade(self.creditC, 0, 1, t, t, m))
		sequencer.Wait(1, lambda: sequencer.AlphaFade(self.creditN, 0, 1, t, t, m, ycallback = self.nextCredit))
		if self.interpolCamOrth: self.interpolCamOrth.delete()
		#self.interpolCamOrth = sequencer.LinearInterpolation(12, 16, t+t+m+1, self.nextCreditCameraOrtho, transform = True)
		
		self.icredit += 1
		
	def nextCreditCameraOrtho(self, x):
		gui = module.scene_gui_behavior
		
		gui.scene.active_camera.ortho_scale = x
		
	def afterCredit(self):
		utils.showCursor()
		
	def sizex(self, x):
		self.creditC.scale.x = x
		self.creditN.scale.x = x
		
	def update(self):
		pass

	def onExit(self):
		pass

#This tells BGECore to use the ExampleScene behavior when the scene "Main" is loaded.
behavior.addScene(IntroScene, "Intro")