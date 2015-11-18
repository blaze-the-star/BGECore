from bge import logic, texture
from core import module, interface, utils
import aud

#=====================================
#			DEFAULT SCREEN
#=====================================
screen = None
""" Default screen 

.. note::
	This implementation will probably change. Now you can't acces the screen if this is not visible.
"""

def showScreen():
	""" Makes the default screen visible. """
	global screen
	ac = module.scene_gui.active_camera
	if screen == None:
		screen = Screen(module.scene_gui.addObject("GUIScreen", ac))
		screen.obj.worldPosition.z = 0
		screen.obj.visible = True
	else:
		screen.obj.visible = True
		screen.obj.worldPosition = [ac.worldPosition.x, ac.worldPosition.y, 0]
		
def hideScreen():
	""" Makes the default screen invisible. """
	global screen
	if not screen: return
	screen.obj.visible = False

#===================================
#			SREEN CLASS
#===================================
class Screen(interface.widget.Widget):
	""" The base object used in this widget will become a screen.
	
	:param object: Object to apply the changes.
	:type object: |KX_GameObject| or string
	
	Attributes:
		obj		The |KX_GameObject| used as screen.
	"""
	
	def __init__(self, obj):
		super().__init__(obj)
		self.callback = None
		self.true_start_file = None
		self.frame = 0
	
	def replaceTexture(self, filepath):
		""" Change the texture of the object by another, external, texture.
		
		:param string filepath: The relative path (to the game folder) of the texture/image to replace.		
		"""
		path = logic.expandPath("//../" + filepath)
		self.texture = texture.Texture(self.obj, 0)
		self.texture.source = texture.ImageFFmpeg(path)
		self.texture.refresh(False)
		
	def play(self, video, mute = False, callback=None):
		""" Plays a video on this screen.
		
		:param string video: The relative path (to the game folder) of the video to use.
		:param bool mute: If true no sound will be played.
		:param function callback: Function to call once the video ends.
		"""
		#Video
		path = logic.expandPath("//../" + video)
		self.video = texture.Texture(self.obj, 0)
		self.video.source = texture.VideoFFmpeg(path)
		self.video.source.scale = True
		self.video.source.play()
		module.video_playback_list.append(self)
		
		#Audio
		self.true_start_file = video
				
		#Callback
		self.callback = callback
		
	def updateVideo(self):
		self.video.refresh(True)
		if 	self.video.source.status == 2:
			self.frame += 1
			if self.true_start_file and self.frame >= self.video.source.preseek:
				try: self.speaker = AudioFile(self.true_start_file).play()
				except: pass
				self.true_start_file = None
			
		if self.video.source.status == 3:
			self.frame = 0
			module.video_playback_list.remove(self)
			if self.callback: self.callback()
		

device = aud.device()

class AudioFile():
	""" A object representating an audio file. Initializating this won't play the file.
	
	:param string filepath: Relative path (to the game folder) of the audio file to use.
	:param function callback: Function to call once the playback ends.
	"""
	def __init__(self, filepath, callback = None):
		self.filepath = filepath
		self.rcall = callback
		self.fadein = False
		self.fadeout = False
		self.time = 0
		self.handle = None
		self.target_volume = 0
		self.volume_min = 0
		self.callback = None
	
	def play(self, filepath=None, loop=False, volume = 1, pitch = 1, fadein=(0,0), fadeout=(0,0), callback = None):
		""" Method to play the an audio file.
		
		.. note:: Current implementation doesn't support fadein and fadeout overlap, make sure they don't. 
		
		:param string filepath: Relative path (to the game folder) of the audio file to use.
		:param bool loop: If true the audio will be played in loop.
		:param float volume: The volume of the audio file relative to the master device.
		:param float pitch: The pitch.
		:param 2-size-set fadein: The amount of time to wait until fadein and how long the fadein lasts (in seconds).
		:param 2-size-set fadein: The amount of time to wait until fadeout and how long the fadeout lasts (in seconds).
		:param function callback: Function to call once the playback ends.
		"""
		
		self.callback = callback
		if not filepath: filepath = self.filepath
		path = logic.expandPath("//../" + filepath)
		factory = aud.Factory(path)
		
		s, t = fadein
		self.target_volume = volume
		if s > 0 or t > 0:
			self.fadein = True
			self.fadein_start = s+self.time
			self.fadein_interval = volume / t
			self.fadein_stop = t+s+self.time
			
		s, t = fadeout
		if s > 0 or t > 0:
			self.fadeout = True
			self.fadeout_start = s+self.time
			self.fadeout_interval = volume / t
			self.fadeout_stop = t+s+self.time
		
		self.factory = factory
		self.handle = device.play(self.factory)
		if self.fadein == False: self.handle.volume = volume
		else: self.handle.volume = self.volume_min
		self.handle.pitch = pitch
		if loop: self.handle.loop_count = -1
		
		module.low_frequency_callbacks.append(self.update)
		return self
		
	def fadeOut(self, time):
		"""Starts to make fadeout now.
		
		:param float time: How long the fadeout lasts.
		"""
		self.fadeout = True
		self.fadeout_start = self.time
		self.fadeout_interval = self.handle.volume / time
		self.fadeout_stop = time+self.time
		
	def fadeIn(self, time):
		"""Starts to make fadein now.
		
		:param float time: How long the fadein lasts.
		"""
		self.fadein = True
		self.fadein_start = self.time
		self.fadein_interval = self.target_volume / time
		self.fadein_stop = time+self.time
	
	def stop(self):
		""" Stops the sound. Equivalent of calling ``audioFile.handle.stop()``"""
		self.handle.stop()
	
	def update(self):
		self.time += 0.1
		
		if self.handle.status == True:
			if self.fadeout:
				if self.time >= self.fadeout_start and self.time <= self.fadeout_stop+0.3:
					inv = self.fadeout_interval*0.1
					if self.handle.volume > inv+self.volume_min: self.handle.volume -= inv
					else: self.handle.volume = self.volume_min
				else: self.fadeout = False
				
			if self.fadein: 
				if self.time >= self.fadein_start and self.time <= self.fadein_stop+0.3:
					inv = self.fadein_interval*0.1
					if self.handle.volume < self.target_volume-inv: self.handle.volume += inv
					else: self.handle.volume = self.target_volume
				else: self.fadein = False
	
		if self.handle.status == False:
			module.low_frequency_callbacks.remove(self.update)
			if self.callback: self.callback()
			elif self.rcall:  self.rcall()
			
		
music = AudioFile("")