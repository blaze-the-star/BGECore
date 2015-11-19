from core import interface, utils, module, behavior, media
from script import constant, control
from bge import logic

class GUI(behavior.Scene):
	def init(self):
		interface.window.hideCursor()
	
		MenuButton(0, "MItem1", None, "Hobo", "Change Scene")
		MenuButton(1, "MItem2", None, "Hobo", "Exit")
		MenuButton(2, "MItem3", None, "Hobo", "Print Version")
		MenuButton(3, "MItem4", None, "Hobo", "Nothing")
		
		#Start the game with intro video
		if not constant.GAME_DEBUG:
			utils.setCamera(self.scene, "GUICamera.001")
			media.showScreen()
			media.screen.play("data/video/intro.avi", callback=lambda: utils.setScene("Main"))
			media.screen.obj.color.w = 0
			media.screen.fadeIn(10)
		
		#Start the game directly
		else: utils.setScene("Main")
		
	def update(self):
		pass
		
behavior.addScene(GUI, constant.CORE_SCENE_GUI)

class MenuButton(interface.TextMenu):
	def mouse_click(self):
		if self.index == 0:
			if not module.scene_game:
				utils.setScene("Main2")
				return
			if module.scene_game.name == "Main": utils.setScene("Main2")
			if module.scene_game.name == "Main2": utils.setScene("Main")
			
		if self.index == 1:
			logic.endGame()
			
		if self.index == 2:
			print(constant.VERSION)
			self.button[3].index = 2
			self.button[2].index = 3
			self.button[2].text["Text"] = "Nothing"
			self.button[3].text["Text"] = "Print Version"
			
		if self.index == 3:
			pass