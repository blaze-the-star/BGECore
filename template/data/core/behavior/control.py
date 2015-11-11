from bge import logic
from core import key
from mathutils import Vector, Euler
import math
from core.behavior.base import *
from core.behavior.camera import *

#The movment is on the plane and local only to the z axis.
class CamPlayerControl(Object):
	def __init__(self, object):
		super().__init__(object)
		self.speedx = 0.1
		self.speedz = 0.2
		self.jumpforce = 5
		self.moving = False
		self._last_moving = False
		module.enableInputFor(self)
		
	def onKeyPressed(self, keys):
		m = [0,0,0]
		if key.W in keys: m[2] = +self.speedz
		if key.S in keys: m[2] = -self.speedz
		if key.A in keys: m[0] = +self.speedx
		if key.D in keys: m[0] = -self.speedx
		self.moving = (m != [0,0,0])
		o = self.obj.worldOrientation.to_euler()
		sz = math.sin(o.z)
		cz = math.cos(o.z)
		self.obj.applyMovement([m[2]*sz + m[0]*cz, -m[2]*cz + m[0]*sz, 0])
		
	def onKeyDown(self, keys):
		if key.SPACE in keys and self.at_ground: self.obj.applyForce([0,0,self.jumpforce*100], False)
		
		
#World coordinates movement with fixed orientation and adjustable lerp.
class FixPlayerControl(CamPlayerControl):
	def __init__(self, object):
		super().__init__(object)
		self.lerp = 0.8

	def onKeyPressed(self, keys):
		m = [0,0,0]
		pi = 3.1415
		r = 0
		if key.W in keys: m[2] = +self.speedz
		if key.S in keys:
			m[2] = -self.speedz
			r = -pi
		if key.A in keys:
			m[0] = +self.speedx
			if key.W in keys:
				r += pi/4
			elif key.S in keys:
				r -= pi/4
			else: r += pi/2
		if key.D in keys:
			m[0] = -self.speedx
			if key.W in keys:
				r -= pi/4
			elif key.S in keys:
				r += pi/4
			else: r -= pi/2
		self.moving = (m != [0,0,0])
		o = self.obj.worldOrientation.to_euler()
		o.z = r
		self.obj.applyMovement([m[0], -m[2], 0])
		self.obj.worldOrientation = o.to_matrix().lerp(self.obj.worldOrientation, self.lerp)
		
#Like CamPlayerControl but local to all the axis.
class OutPlayerControl(CamPlayerControl):
	def onKeyPressed(self, keys):
		m = [0,0,0]
		if key.W in keys: m[2] = +self.speedz
		if key.S in keys: m[2] = -self.speedz
		if key.A in keys: m[0] = +self.speedx
		if key.D in keys: m[0] = -self.speedx
		self.moving = (m != [0,0,0])
		self.obj.applyMovement([0, -m[2], 0], True)
		self.obj.applyRotation([0, 0, m[0]/5], True)
		
class ThirdPerson(MouseLook):
	def __init__(self, object):
		super().__init__(object)
		self.camera_height = 3.5
		self.camera = None
		self.camera_distance = 10
		self.camera_real_distance = 10
		self.camera_wheelfactor = 0.8
		self.camera_xdif_max = 1.1
		self.camera_xdif_offset = 0
		self.camera_max_distance = 30
		self.camera_free = False
		self.player_control = CamPlayerControl(self.obj)
		self.moving = False
		self._last_moving = False
		
	def init(self):
		self.argument(self.camera)
		
	def update(self):
		#Define
		self.at_ground = self._at_ground
		if self.player_control:
			self.moving = self.player_control.moving
			self.player_control.at_ground = self._at_ground
		height = self.camera_height
		distance = self.camera.getDistanceTo(self.obj.worldPosition+Vector((0,0,height)))
		mhf = distance / 4
		if mhf > 4: mhf = 4
		if mhf < 1: mhf = 1
	
		#Camera & Player rotation
		x, y = logic.mouse.position
		rot = self.obj.worldOrientation.to_euler()
		crot = self.camera.worldOrientation.to_euler()
		xdif = (y-0.5)*self.inverty*self.sensitivity
		zdif = (x-0.5)*self.invertx*self.sensitivity
		if abs(xdif) > self.deathzone and abs(xdif) < 0.1:
			self.camera_xdif_offset += xdif/mhf
			if abs(self.camera_xdif_offset) < self.camera_xdif_max:
				crot.x += xdif/mhf
			else:
				if self.camera_xdif_offset < 0: self.camera_xdif_offset = -self.camera_xdif_max
				else: self.camera_xdif_offset = self.camera_xdif_max
		
		if abs(zdif) > self.deathzone and abs(zdif) < 0.1:
			if self.moving == True:
				rot.z += zdif
			crot.z += zdif
		if self.camera_free == False: self.obj.localOrientation = rot.to_matrix()
		self.camera.localOrientation = crot.to_matrix()
		logic.mouse.position = (0.5, 0.5)
		
		#Parent
		c = self.camera
		o = self.obj
		v = Vector((0, 0, self.camera_distance))
		v.rotate(c.worldOrientation)
		icl = Vector(o.worldPosition + v) + Vector((0, 0, self.camera_height))
		ob, hp, hn = o.rayCast(icl, o.worldPosition + Vector((0,0,self.camera_height)))
		if ob:
			self.camera_real_distance = (o.worldPosition + Vector((0, 0, self.camera_height)) - hp).length
			cdiff = (hn/10)
			c.worldPosition = hp + cdiff
		else:
			c.worldPosition = icl
			self.camera_real_distance = self.camera_distance
		
		#Change player orientation after he stoped moving.
		if self._last_moving == False and self.moving == True and self.camera_free == False:
			oo = self.obj.worldOrientation.to_euler()
			co = c.worldOrientation.to_euler()
			if co.x > 0: zfix = 3.1416
			else: zfix = 0
			self.obj.localOrientation = Euler((oo.x, oo.y, co.z+zfix), 'XYZ').to_matrix()
		self._last_moving = self.moving
		self.player_control.moving = False
		
		#Check if touching the ground
		self._at_ground = False
		if self.player_control: self.player_control._at_ground = False
		
		#Collision hack
		self.obj.setCollisionMargin(self.player_control.speedz*4)
		if self.colliding == False:
			self.obj.applyMovement([0,0,-0.04])
		self.colliding = False

	def onKeyPressed(self, keys):
		if key.WHEELUPMOUSE in keys:
			if self.camera_distance > self.camera_wheelfactor: self.camera_distance -= self.camera_wheelfactor
			else: self.camera_distance = 0
			
		if key.WHEELDOWNMOUSE in keys:
			if self.camera_distance < self.camera_max_distance - self.camera_wheelfactor:
				self.camera_distance += self.camera_wheelfactor
		