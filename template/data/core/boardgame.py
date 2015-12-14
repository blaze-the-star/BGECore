from random import randint
from core import utils

class Dice:
	v = 0
	w = 0
	x = 0
	y = 0
	z = 0
	lastZ = 0
	lastY = 0
	lastX = 0
	lastW = 0
	lastV = 0
	
	def text(self):
		v = "V: " + str(self.v)
		w = "W: " + str(self.w)
		x = "X: " + str(self.x)
		y = "Y: " + str(self.y)
		z = "Z: " + str(self.z)
		return v + "  " + w + "  " + x + "  " + y + "  " + z
	
	def roll(self, op = None):
		if not op: op = "vwxyz"
		
		self.lastZ = self.z
		self.lastY = self.y
		self.lastX = self.x
		self.lastV = self.v
		self.lastW = self.w
		if 'v' in op: self.v = randint(0, 9)
		if 'w' in op: self.w = randint(0, 9)
		if 'x' in op: self.x = randint(0, 9)
		if 'y' in op: self.y = randint(0, 9)
		if 'z' in op: self.z = randint(0, 9)
		return self.text()

class Player:
	obj = None
	point = ""
	prev = ""
	dest = ""
	reroll = 0
	speed = 1
	chanceToEncounter = 10
	
	def __init__(self, obj, point):
		self.obj = obj
		self.point = point
		self.prev = point
		obj.position = obj.scene.objects[point].position
		
	def move_loop(self, dest = None):
		if not dest: dest = self.dest
		if utils.moveObjectToObject(self.obj, self.obj.scene.objects[dest], self.speed) == False:
			self.prev = self.point
			self.point = dest
			return False
		else: return True
		