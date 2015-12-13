from bge import logic, texture
from core import module, interface, utils, sequencer
import aud
import os.path

#=====================================
#			DEFAULT SCREEN
#=====================================
screen = None
""" Default screen """

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
	
	.. attribute:: obj
	
	The |KX_GameObject| used as screen.
	
	.. attribute:: speaker
	
	The AudioFile of the video if used, otherwise None.
	
	"""
	
	def __init__(self, obj):
		super().__init__(obj)
		self.callback = None
		self.true_start_file = None
		self.frame = 0
		self.speaker = None
	
	def replaceTexture(self, filepath):
		""" Change the texture of the object by another, external, texture.
		
		:param string filepath: The relative path (from the data folder) of the texture/image to replace.		
		"""
		path = logic.expandPath("//../data/" + filepath)
		self.texture = texture.Texture(self.obj, 0)
		self.texture.source = texture.ImageFFmpeg(path)
		self.texture.refresh(False)
		
	def play(self, video, callback=None):
		""" Plays a video on this screen, also makes the *speaker* aviable.
		
		:param string video: The relative path (from the data folder) of the video to use.
		:param function callback: Function to call once the video ends.
		"""
		#Video
		path = logic.expandPath("//../data/" + video)
		self.video = texture.Texture(self.obj, 0)
		self.video.source = texture.VideoFFmpeg(path)
		self.video.source.scale = True
		self.video.source.play()
		module.video_playback_list.append(self)
		
		#Audio
		self.true_start_file = video
		self.speaker = AudioFile()
				
		#Callback
		self.callback = callback
		
	def fadeIn(self, time):
		"""Starts to make fadein now. It actuates over the alpha chanel of the |KX_GameObject| representing this screen. In order to work it needs *object color* enabled on the material.
		
		:param float time: How long the fadein lasts.
		"""
		sequencer.LinearInterpolation(self.obj.color.w, 1, time, self._interpol)
	
	def fadeOut(self, time):
		"""Starts to make fadeout now. It actuates over the alpha chanel of the |KX_GameObject| representing this screen. In order to work it needs *object color* enabled on the material.
		
		:param float time: How long the fadein lasts.
		"""
		sequencer.LinearInterpolation(self.obj.color.w, 0, time, self._interpol)
	
	def _interpol(self, x):
		self.obj.color.w = x
		
	def updateVideo(self):
		self.video.refresh(True)
		if 	self.video.source.status == 2:
			self.frame += 1
			if self.true_start_file and self.frame >= self.video.source.preseek:
				try: self.speaker = self.speaker.play(self.true_start_file)
				except: pass
				self.true_start_file = None
			
		if self.video.source.status == 3:
			self.frame = 0
			module.video_playback_list.remove(self)
			if self.callback: self.callback()
		

device = aud.device()

class AudioFile():
	""" A object representating an audio file. Initializating this won't play the file.
	
	Recomended formats: .mp3
	Supported Formats: .mp3, .ogg, .wav
	
	:param string filepath: Relative path (from the data folder) of the audio file to use.
	:param function callback: Function to call once the playback ends.
	
	.. attribute:: handle
	
	The *aud.Handle*, be coutious while tweaking with this.
		
	.. attribute:: volume_min
	
	Minium volume of the audio.
	
	.. attribute:: time
	
	The amount of time in seconds since the file start playing.
	
	"""
	def __init__(self, filepath = "", callback = None):
		self.filepath = filepath
		self.rcall = callback
		self.time = 0
		self.handle = None
		self.volume_min = 0
		self.callback = None
		self._volume = 1

		#LinearInterpolation Objects
		self.fadein = None
		self.fadeout = None
		
		#Status
		self.playing = False
		self.waiting = False
	
	def _transition_callback(self, n):
		self.volume = 0
		self.playing = False
		self.waiting = False
		self.play()
		self.fadeIn(n)
	
	def play(self, filepath=None, loop=False, volume = None, pitch = 1, callback = None, transition = (3, 2, 3)):
		""" Method to play an audio file.
		
		:param string filepath: Relative path (from the data folder) of the audio file to use.
		:param bool loop: If true the audio will be played in loop.
		:param float volume: The volume of the audio file relative to the master device. (Default = 1.0)
		:param float pitch: The pitch.
		:param function callback: Function to call once the playback ends.
		"""
		
		self.callback = callback
		if not filepath: filepath = self.filepath
		else: self.filepath = filepath
		
		if self.waiting == True: #Replace sound that will be played.
			self.filepath = filepath
			return
			
		if self.playing == True: #FadeOut this sound and fadeIn the new one.
			x, y, z = transition
			
			dummy = self.moveInstance()
			dummy.fadeOut(x, stop=True)

			if filepath: self.filepath = filepath
			self.waiting = True
			
			sequencer.Wait(y, lambda: self._transition_callback(z))
			return
		
		path = logic.expandPath("//../data/" + filepath)
		factory = aud.Factory(path)
		
		try:
			self.factory = factory
			self.handle = device.play(self.factory)
			self.handle.pitch = pitch
			if volume == None: self.volume = self._volume
			else: self.volume = volume
			if loop: self.handle.loop_count = -1
		except:
			if os.path.isfile(path) == False: utils.debug("Audio File, Not Found: " + path)
			else: utils.debug("AudioFile Load Error: " + path)
		
		self.playing = True
		module.low_frequency_callbacks.append(self.update)
		return self
		
	def fadeOut(self, time, stop = False):
		"""Starts to make fadeout now.
		
		:param float time: How long the fadeout lasts.
		:param bool stop: If True it will automatically stop the reproduction at the end.
		"""
		if self.fadein and self.fadein.status != False:
			self.fadein.delete()
			
		if stop:
			self.fadeout = sequencer.LinearInterpolation(self.volume, self.volume_min, time, self._interpol, self.stop)
		else:
			self.fadeout = sequencer.LinearInterpolation(self.volume, self.volume_min, time, self._interpol)
		
	def fadeIn(self, time):
		"""Starts to make fadein now.
		
		:param float time: How long the fadein lasts.
		"""
		if self.fadeout and self.fadeout.status != False:
			self.fadeout.delete()
			
		self.fadein = sequencer.LinearInterpolation(self.volume, 1, time, self._interpol)
	
	def _interpol(self, x):
		self.volume = x
		
	def moveInstance(self):
		""" Returns a new instance of this class and gives it control over the audiofile, this instance returns to its original state.
		
		.. Note:: This function is used internally to replace sounds with a fadeIn/fadeOut effect were they can be mixed during the transition.
		"""
	
		dummy = AudioFile()
		dummy.__dict__ = self.__dict__.copy()
		self.handle = None
		self.factory = None
		self.time = 0
		self.playing = False
		self.waiting = False
		module.low_frequency_callbacks.remove(self.update)
		module.low_frequency_callbacks.append(dummy.update)
		return dummy
	
	def resume(self):
		self.handle.play()
		self.playing = True
	
	def pause(self):
		pass
	
	def stop(self):
		""" Stops the sound. """
		
		module.low_frequency_callbacks.remove(self.update)
		self.playing = False
		self.handle.stop()
		self.time = 0
		if self.callback: self.callback()
		elif self.rcall:  self.rcall()
	
	@property
	def volume(self):
		""" """
		try: return self.handle.volume
		except: return 0
		
	@volume.setter
	def volume(self, x):
		try:
			if x < self.volume_min: self.handle.volume = self.volume_min
			self.handle.volume = x
		except: self._volume = x
	
	def update(self, time):
		if self.handle and self.handle.status == False:
			self.stop()
		else:
			self.time += time
		
music = AudioFile("")
sui = {}

class AudioEffect:
	def __init__(self, filepath):
		path = logic.expandPath("//../data/" + filepath)
		factory = aud.Factory(path)
		self.factory = factory.buffer()
		self.handle = None
		
	def play(self, volume = 1, pitch = 1):
		self.handle = device.play(self.factory)
		self.handle.volume = volume
		self.handle.pitch = pitch
		
class RandomMusic:
	def __init__(self, directory = "sound/music", loop = True, audiofile = music, transition = (5, 2, 4)):
		self.loop = loop
		if not directory.endswith('/'): directory += '/'
		self.directory = directory
		self.transition = transition
		
		self.playing = False
		self.audiofile = audiofile
		if loop: module.low_frequency_callbacks.append(self.update)
		
	def play(self, directory = None):
		if directory: self.directory = directory
		if self.audiofile.waiting == False:
			self.next()
			self.playing = True
		
	def stop(self):
		if self.playing:
			try:
				module.low_frequency_callbacks.remove(self.update)
				self.audiofile.fadeOut(self.transition[2], True)
				self.playing = False
			except IndexError:
				pass
		
	def next(self):
		try:
			self.audiofile.play(self.directory + self.getRandomFileTrack(), transition = self.transition)
		except IndexError: utils.debug("No music found in directory " + self.directory)
		
	def getRandomFileTrack(self):
		current_song = os.path.basename(self.audiofile.filepath)
		path = logic.expandPath("//../data/" + self.directory)
		files = [x for x in os.listdir(path) if x.endswith(".mp3") and current_song != x]
		if files: return utils.choice(files)
		else: return current_song
		
	def update(self, time):
		if self.audiofile.playing == False and self.playing == True:
			self.play()