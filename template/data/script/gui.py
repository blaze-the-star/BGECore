from core import interface, utils, module, behavior, media
from script import constant, control
from bge import logic
from mathutils import Vector

class GUI(behavior.Scene):
	def init(self):
		#Set the cursor, hide for the intro video.
		interface.window.setCursor("Cursor")
		interface.window.hideCursor()
	
		#Setup the menu.
		MenuButton(0, "MItem1", "MItemOver", "Hobo", "Change scene", align=interface.label.ALIGN_CENTER)
		MenuButton(1, "MItem2", "MItemOver", "Hobo", "Move", align=interface.label.ALIGN_CENTER)
		MenuButton(2, "MItem3", "MItemOver", "Hobo", "Change color", align=interface.label.ALIGN_CENTER)
		MenuButton(3, "MItem4", "MItemOver", "Hobo", "Exit", align=interface.label.ALIGN_CENTER)
		
		#Change color of the quote
		module.labels["LineOfText.003"].color = [2,0,0,1]
		
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
	def mousePressed(self):
		if self.index == 1: self.move()

	def mouseClick(self):
		gui = module.scene_gui_behavior
		if self.index == 0:
			if not module.scene_game:
				utils.setScene("Main2")
				return
				
			if module.scene_game.name == "Main": utils.setScene("Main2")
			if module.scene_game.name == "Main2": utils.setScene("Main"); interface.window.hideCursor()
			
		if self.index == 1: pass
			
		if self.index == 2:
			lab = module.labels["LineOfText.003"]
			lab.color = utils.randRGB()
			
		if self.index == 3:
			logic.endGame()
			
	def move(self):
		pos = self.position
		for i, button in MenuButton.button.items():
			#Store z position, we don't wanna change that.
			z = button.position.z
			
			#Move widgets of the menu relative the the object being clicked.
			#The vector from the object being clicked to itself is (0,0,0).
			button.position = module.window.cursor.position + utils.vectorFrom2Points(pos, button.position)
			
			#Restores the z position
			button.position.z = z