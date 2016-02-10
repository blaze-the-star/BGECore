from core import module, utils

#Effects
class Wait:
	""" Waits a certain amount of time, then calls the callback function.
	
	:param float time: The amount of time to wait in seconds.
	:param function callback: The function to call once it ends.
	
	.. attribute:: x
	
		The time since the effect started, in seconds.
	
		:type: float
	"""
	def __init__(self, time, callback):
		self.x = 0
		self.time = time
		self.callback = callback
		self.status = True
		module.low_frequency_callbacks.append(self.update)
		
	def update(self, time):
		self.x += time
		if self.x >= self.time:
			self.callback()
			self.delete()
		
	def delete(self):
		""" Deletes/Stops the effect. Automatically called once x >= time. """
		module.low_frequency_callbacks.remove(self.update)
		self.status = False

class AlphaFade:
	""" Makes a object fadeIn, wait, and fadeOut.
	
	:param obj: The object at wich apply the effect.
	:param float A: On the LinearInterpolation, A->A when fadein, A->B when fadeout.
	:param float B: On the LinearInterpolation, B->B when fadein, B->A when fadeout.
	:param float xtime: The time it takes, in seconds for the fadein.
	:param float ytime: The time it takes, in seconds for the fadeout.
	:param float mtime: The time to wait in between.
	:param xcallback: The function to call when fadein ends.
	:param mcallback: The function to call when fadeout starts.
	:param ycallback: The function to call when fadeout ends.
	
	.. attribute:: x
	
		The time since the effect started, in seconds.
	
		:type: float
	"""
	
	def __init__(self, obj, A, B, xtime, ytime, mtime = 0, xcallback = None, mcallback = None, ycallback = None):
		self.obj = obj
		self.A = A
		self.B = B
		self.xtime = xtime
		self.ytime = ytime
		self.mtime = mtime
		self.xcallback = xcallback
		self.mcallback = mcallback
		self.ycallback = ycallback
		module.low_frequency_callbacks.append(self.update)
		self.state = 0
		self.x = 0
		
	def update(self, time):
		self.x += time
		if self.x >= self.xtime + self.mtime + self.ytime: self.delete()
		
		if self.state == 0:
			self.state += 1
			if self.xtime > 0: LinearInterpolation(self.A, self.B, self.xtime, self.xchange, self.next)
			else: self.next()
			
		if self.state == 2:
			if self.x > self.xtime + self.mtime:
				if self.mcallback: self.mcallback()
				self.state += 1
			
		if self.state == 3:
			self.state += 1
			if self.ytime > 0: LinearInterpolation(self.B, self.A, self.ytime, self.xchange, self.next)
			else: self.next()
			
	def xchange(self, x):
		""" The callback that changes the color of the object. If the class is extended, this method can be overwritten to modify any property. """
		self.obj.color.w = x
	
	def next(self):
		if self.state == 1 and self.xcallback: self.xcallback()
		if self.state == 4 and self.ycallback: self.ycallback()
		self.state += 1
		
	def delete(self):
		""" Deletes/Stops the effect. Automatically called once x >= xtime+mtime+ytime. """
		if self.update in module.low_frequency_callbacks: module.low_frequency_callbacks.remove(self.update)
		del self

#3D Math
class LinearInterpolation:
	""" Makes a linear interpolation over time, uses a callback to apply changes.
	
	:param float A: The start value.
	:param float B: The end value.
	:param float time: The time it takes, in seconds.
	:param callback: The function to call to apply changes, its first argument will be the value of the interpolation (A <= value <= B).
	:param final: The function to call when the interpolation ends.
	:param bool transform: If True a hight_frequecy_callback will be used.
	
	.. attribute:: x
	
		The time since the interpolation started, in seconds.
	
		:type: float
	"""
	def __init__(self, A, B, time, callback, final = None, transform = False):
		if transform == False: module.low_frequency_callbacks.append(self.update)
		else: module.height_frequency_callbacks.append(self.update)
		self.A = A
		self.B = B
		self.m = B-A
		self.x = 0
		self.y = time
		self.callback = callback
		self.final = final
		self.transform = transform
		self.status = True
		
	def func(self, x):
		return self.m*x+self.A
	
	def update(self, time):
		if self.x < 0 or self.x > self.y: self.delete()
		self.x += time
		
		self.x = float(self.x)
		self.y = float(self.y)
		self.m = float(self.m)
		
		x = self.x/self.y
		y = self.func(x)
		
		if self.m > 0:
			if y < self.A: y = self.A
			if y > self.B: y = self.B
		if self.m < 0:
			if y > self.A: y = self.A
			if y < self.B: y = self.B 
		self.callback(y)
		
	def delete(self):
		""" Deletes/Stops the interpolation. Automatically called once x >= time. """
		if self.update in module.low_frequency_callbacks:
			module.low_frequency_callbacks.remove(self.update)
			if self.final: self.final()
		if self.update in module.height_frequency_callbacks:
			module.height_frequency_callbacks.remove(self.update)
			if self.final: self.final()
			
		self.status = False
		del self
		
class QuadraticInterpolation(LinearInterpolation):
	""" Makes a quadratic interpolation over time, uses a callback to apply changes.
	
	.. warning:: The implementation sucks.
	"""
	def __init__(self, A, B, time, callback, final = None, transform = False, inverse = False):
		super().__init__(A, B, time, callback, final, transform)
		self.inverse = inverse
		
	def func(self, x):
		a = self.A
		b = self.B
		if self.inverse: return (x**2-2*x)*(a-b)+a
		return (x**2+x)*((b-a)/2)+a
		
class Typewriter:
	""" Writtes with a typewriter effect whatever you want to writte with a typeriter effect, then calls the callback function.
	
	.. note:: Today seems I'm not very good at documenting.
	
	:param interface.Label label: The Label.
	:param function callback: The function to call once it ends.
	
	.. attribute:: x
	
		The time since the effect started, in seconds.
	
		:type: float
		
	.. attribute:: status
	
		True if playing. False if paused or stoped.
		
		:type: bool
		
	.. attribute:: callback
	
		To change the callback on runtime.
	
	.. attribute:: n
	
		The index of the last letter added to the Label. Remeber to set to integer when used.
		
		:type: float
		
	.. attribute:: speed
	
		The amount to add to *n* each iteration.
		
	.. attribute:: text
	
		The new text that will be written. Modifing this will start a new animation.
		
	"""

	def __init__(self, label, callback=None):
		self.label = label
		self.status = True
		self.x = 0
		self.n = 0
		self.speed = 1.3
		self.callback = callback
		self._text = None
		self.text = self.label.text
		
		module.height_frequency_callbacks.append(self.update)
		
	def update(self, time):
		if self.status == False: return
		if self.x < 0 or self.n >= len(self.text):
			self.status = False
			if self.callback: self.callback()

		self.x += time
		self.n += self.speed
		self.label.text = self.text[:int(self.n)]
		
	@property
	def text(self):
		return self._text
		
	@text.setter
	def text(self, val):
		self._text = val
		self.n = 0
		self.x = 0
		self.label.text = ""
		self.status = True
	
	def finish(self):
		self.label.text = self.text
		self.status = False
		self.n = len(self.text)-1
		