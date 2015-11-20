from core import interface, utils, module, behavior, media, key
from script import constant, control
from bge import logic
from mathutils import Vector

class GUI(behavior.Scene):
	def init(self):
		#Set the cursor, hide for the intro video.
		interface.window.setCursor("Cursor")
		interface.window.hideCursor()
	
		#Setup the menu.
		MenuButton(0, "MItem1", "Change scene")
		MenuButton(1, "MItem2", "Move")
		MenuButton(2, "MItem3", "Change color")
		MenuButton(3, "MItem4", "Quote")
		MenuButton(4, "MItem5", "Exit")
		
		#Change color of the quote
		module.labels["QuoteLine"].color = [2,0,0,0]
		control.replaceQuote()
		
		#Start the game with intro video
		if not constant.GAME_DEBUG:
			utils.setCamera(self.scene, "GUICamera.001") #Makes the menu desapear.
			media.showScreen()
			media.screen.play("data/video/intro.avi", callback=self.afterVideo)
			media.screen.obj.color.w = 0 #Sets the screen alpha to 0 (invisible).
			media.screen.fadeIn(2) #Sets the screen alpha to 1 with a linear interpolation over 2 seconds.
		
		#Start the game directly
		else: self.afterVideo()
		
	def afterVideo(self):
		utils.setCamera(self.scene, "GUICamera.000")
		interface.window.showCursor()
		media.hideScreen()	
		
	def update(self):
		pass
		
behavior.addScene(GUI, constant.CORE_SCENE_GUI)

class MenuButton(interface.TextMenu):
	over = "MItemOver"
	font = "Hobo"
	align = interface.label.ALIGN_CENTER
	
	def init(self):
		self._scaling = False
	
	def onKeyPressed(self, keys):
		one = Vector((0.03,0.03,0.03))
		if self.index == 1 and self._scaling == True:
			if key.WHEELDOWNMOUSE in keys: self.resize(self.scale + one, True)
			if key.WHEELUPMOUSE in keys: self.resize(self.scale - one, True)
			if key.PERIOD in keys: self.resize(self.scale + one)
			if key.COMMA in keys: self.resize(self.scale - one)
			
	def mousePressed(self):
		if self.index == 1:
			self.moveWithCursor()
			self._scaling = True

	def mouseClick(self):
		self._scaling = False
		gui = module.scene_gui_behavior
		if self.index == 0:
			if not module.scene_game:
				utils.setScene("Main2")
				return
				
			if module.scene_game.name == "Main": utils.setScene("Main2")
			if module.scene_game.name == "Main2": utils.setScene("Main"); interface.window.hideCursor()
			
		if self.index == 1: pass
			
		if self.index == 2:
			lab = module.labels["QuoteLine"]
			lab.color = utils.randRGB(a=lab.color.w)
		
		if self.index == 3:
			if module.labels["QuoteLine"].color.w == 1: control.changeQuote()
		
		if self.index == 4:
			logic.endGame()