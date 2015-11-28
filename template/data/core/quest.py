from core import utils

list = []
taken = False

def playOnMove(place):
	global taken
	for q in reversed(list):
		q.onMove(place)
		if taken == True:
			taken = False
			return

def playOnNextScene(image):
	global taken
	for q in reversed(list):
		q.onNextScene(image)
		if taken == True:
			taken = False
			return

def playOnLocationEnter():
	global taken
	for q in reversed(list):
		q.onLocationEnter()
		if taken == True:
			taken = False
			return
			
def playOnLocationExit():
	global taken
	for q in reversed(list):
		q.onLocationExit()
		if taken == True:
			taken = False
			return

def add(className):
	global list
	quest = className()
	list.append(quest)
	utils.verbose("Loaded quest: " + quest.name)

def getQuestByName(name):
	for q in list:
		if q.name == name: return q 
	
class Quest:
	state = 0
	name = None
	description = None
	
	def __init__(self):
		if self.name == None: self.name = self.__class__.__name__
		
	def onLocationEnter(self):
		pass
		
	def onLocationExit(self):
		pass
	
	def onNextScene(self, image):
		pass
		
	def onMove(self, dest):
		pass
		
	def onLoad(self):
		pass