from core import sequencer, utils, module, media

class IntroCredits:
	text = [
	["Story", "Robert Planas"],
	["Music", "Iñigo Sáez"],
	["Programming", "Robert Planas"],
	["Powered by", "Blender Game Engine\n Core Framework"]
	]
	def __init__(self):
		gui = module.scene_gui_behavior
		
		#Setup the credits
		self.creditC = module.labels["CreditCategory"]
		self.creditN = module.labels["CreditName"]
		self.creditC.color.w = 0
		self.creditN.color.w = 0
		self.icredit = 0
		self.n = 0
		
		utils.setCamera(gui, "GUICamera.002")
		self.interpolCamOrth = None
		sequencer.Wait(5, self.nextCredit)
		sequencer.Wait(1, lambda: media.music.play("sound/music/Iñigo Sáenz - The Crusader.mp3"))
		
		sequencer.Wait(45, self.startTitle)
		self.background = gui.scene.objects["GUIBlackScreen"]
		self.title = gui.objects["GUITitle"]
		self.title.color.w = 0
	
	def startTitle(self):
		sequencer.LinearInterpolation(1, 0, 8, self.backgroundcolor)
		self.secTitle()
		
	def secTitle(self):
		t = 8
		m = 6
		sequencer.AlphaFade(self.title, 0, 1, t, t, m)
		sequencer.LinearInterpolation(0.875, 1.2, t+t+m, self.setTitleScale, transform=True)
	
	def setTitleScale(self, x):
		self.title.localScale.x = x 
		self.title.localScale.y = x
		
	def backgroundcolor(self, x):
		self.background.color.w = x
	
	def nextCredit(self):
		i = self.icredit
		credit = self.text
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
		return
		module.window.showCursor()
		
	def sizex(self, x):
		self.creditC.scale.x = x
		self.creditN.scale.x = x