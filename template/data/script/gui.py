from core import interface, utils, module, behavior, media, dynamic, sequencer
from script import constant, control
from bge import logic

class GUI(behavior.Scene):
	def init(self):
		#Set the cursor, hide for the intro video.
		interface.window.setCursor("Cursor")
		
		#Start the game with intro video
		if not constant.GAME_DEBUG:
			interface.window.hideCursor()
			utils.setCamera(self, "GUICamera.001") #Makes the menu desapear.
			media.showScreen()
			media.screen.play("video/intro.avi", callback=self.afterVideo)
			media.screen.obj.color.w = 0 #Sets the screen alpha to 0 (invisible).
			media.screen.fadeIn(2) #Sets the screen alpha to 1 with a linear interpolation over 2 seconds.
		
		#Start the game directly
		else: self.afterVideo()
		
	def afterVideo(self):
		utils.setCamera(self, "GUICamera.000")
		interface.window.showCursor()
		media.hideScreen()
		sequencer.Wait(1, self.setupMainMenu)
		
	def setupMainMenu(self):
		MainMenu.fadeinref = sequencer.LinearInterpolation(0, 1, 2, MainMenu.xcolor)
		MainMenu(0, "MItem.000", "New Game")
		MainMenu(1, "MItem.001", "Options")
		MainMenu(2, "MItem.002", "Exit")
		
	def startGame(self):
		dynamic.loadScene("scene/intro.blend", "Intro")
		
	def update(self):
		pass
		
behavior.addScene(GUI, constant.CORE_SCENE_GUI)

class MainMenu(interface.TextMenu):
	font = "Amble"
	size = 32
	over = "MItemOver"
	align = interface.label.ALIGN_CENTER
	visible = True
	fadeinref = None

	def init(self):
		media.sui["select"] = media.AudioEffect("sound/ui/select.wav")
		media.sui["click"] = media.AudioEffect("sound/ui/click_back.wav")
		self.color = [1, 1, 1, 0]
		self.obj.visible = True
	
	def mouseIn(self):
		if self.active: media.sui["select"].play()
	
	def select(self):
		media.sui["click"].play()
		sb = module.scene_gui_behavior
		s = 1
		if self.fadeinref:
			s = self.fadeinref.x
			self.fadeinref.delete()
			
		if self.index == 0:
			sequencer.LinearInterpolation(s, 0, 2, MainMenu.xcolor, sb.startGame)
			self.xactive(False)
			
		if self.index == 1:
			print("OP1")
		
		if self.index == 2:
			sequencer.LinearInterpolation(s, 0, 0.5, MainMenu.xcolor, logic.endGame)
			self.xactive(False)
	
	@classmethod
	def xcolor(self, x):
		for n, m in MainMenu.button.items():
			m.color.w = x
			
	
	@classmethod
	def xactive(self, x):
		for n, m in MainMenu.button.items():
			m.active = x
		