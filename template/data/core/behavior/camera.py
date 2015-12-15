from bge import logic
from core import key, module
from mathutils import Vector, Euler
import math
from core.behavior.base import *

class MouseLook(Object):
	""" Preset of a mouse look behavior. To be used with a camera.
	
	You can control the camera orientation with the mouse and move arround with WASD.

	.. attribute:: sensitivity
	
	The sensitivity of the mouse. *Default: 0.75*
	
	.. attribute:: deathzone
	
	The radious of a the zone in wich mouse movements are considered noise and therfore ignored. *Default: 0.002*
	
	.. attribute:: speedx
	
	The speed of movement on the x axis. (Left/Right) *Default: 0.1*
	
	.. attribute:: speedz
	
	The speed of movement on the z axis. (Front/Back) *Default: 0.3*
	
	.. attribute:: lock_rotation
	
	It can be used to ensure a maixum rotation on the x axis, so avoiding an inverted view. If ``None`` no limit will be applied, otherwise a float representing the angle in radiants (for one direction) will be used. *Default: 1*
	
	
	"""

	def __init__(self, object):
		super().__init__(object)
		self.deathzone = 0.002
		self.sensitivity = 0.75
		self.invertx = -1
		self.inverty = -1
		self.speedx = 0.1
		self.speedz = 0.3
		self.lock_rotation = 1
		module.enableInputFor(self)
		
	def update(self):
		x, y = logic.mouse.position
		tmp = self.obj.worldOrientation.to_euler()
		rot = tmp.copy()
		xdif = (y-0.5)*self.inverty*self.sensitivity
		zdif = (x-0.5)*self.invertx*self.sensitivity
		if abs(xdif) > self.deathzone: tmp.x += xdif
		if abs(zdif) > self.deathzone: tmp.z += zdif
		if self.lock_rotation == None: rot = tmp
		else:
			rot.z = tmp.z
			if abs(tmp.x-1.57) <= self.lock_rotation:
				rot.x = tmp.x
		
		self.obj.localOrientation = rot
		logic.mouse.position = (0.5, 0.5)
		
	def onKeyPressed(self, keys):
		m = [0,0,0]
		if key.W in keys: m[2] = -self.speedz
		if key.S in keys: m[2] = +self.speedz
		if key.A in keys: m[0] = -self.speedx
		if key.D in keys: m[0] = +self.speedx
		self.obj.applyMovement(m, True)