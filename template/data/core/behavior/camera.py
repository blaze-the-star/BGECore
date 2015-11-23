from bge import logic
from core import key, module
from mathutils import Vector, Euler
import math
from core.behavior.base import *
class MouseLook(Object):
	def __init__(self, object):
		super().__init__(object)
		self.deathzone = 0.002
		self.sensitivity = 0.75
		self.invertx = -1
		self.inverty = -1
		self.speedx = 0.01
		self.speedz = 0.03
		module.enableInputFor(self)
		
	def update(self):
		x, y = logic.mouse.position
		rot = self.obj.worldOrientation.to_euler()
		xdif = (y-0.5)*self.inverty*self.sensitivity
		zdif = (x-0.5)*self.invertx*self.sensitivity
		if abs(xdif) > self.deathzone and abs(xdif) < 0.1: rot.x += xdif
		if abs(zdif) > self.deathzone and abs(zdif) < 0.1: rot.z += zdif
		self.obj.localOrientation = rot.to_matrix()
		logic.mouse.position = (0.5, 0.5)
		
	def onKeyPressed(self, keys):
		m = [0,0,0]
		if key.W in keys: m[2] = -self.speedz
		if key.S in keys: m[2] = +self.speedz
		if key.A in keys: m[0] = -self.speedx
		if key.D in keys: m[0] = +self.speedx
		self.obj.applyMovement(m, True)