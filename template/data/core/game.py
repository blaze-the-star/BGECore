from script import gui
from script import behavior
from bge import logic, events
from core import module, utils, media, dynamic
from core.interface import event
import time
import traceback

start = time.time()

done = time.time()
elapsed = done - start

_state = 0
_last_time = time.time()
_last_time2 = _last_time
_last_traceback = ""
def loop():
	global _state, _last_time, _last_time2

	#Set scene
	if module.change_scene_frame == True:
		if module.change_scene_dynamic == True: dynamic.loadScene(None, None)
		else: utils.setScene(None)
		return

	#Game initialization
	if _state == 0:
		_state = 1
		logic.setMaxLogicFrame(1)
		module.scene_gui_behavior.scene = module.scene_gui
		for o in module.scene_gui.objects: module.scene_gui_behavior.objects[o.name] = o
		module.scene_gui_behavior.init()
		for b in module.scene_gui_behavior.behaviors: b.init()
		media.device.volume = float(utils.loadGameProperty("volume"))
		module.cont = logic.getCurrentController()
		module._arecallbacks = False
		if utils.checkVersion() == False: utils.debug("Atention! BGE version is outdated, please install last Blender release.")

	if module._arecallbacks == True: return

	#GUI Behavior
	if module.scene_gui_behavior.paused == False: module.scene_gui_behavior.update()
	for b in module.scene_gui_behavior.behaviors:
		if b.paused == False: b.update()

	#Key events
	listen_list = [x for x in module.listen_input_list if x._immuse_keyboard == True and x.scene == module.scene_gui]
	for x in module.listen_input_list: x._immuse_keyboard = x.use_keyboard
	event._key_event_loop(listen_list)
	event.first_time_in_frame = True
	event.last_keyevents = event.last_butstillthisframe_keyevents

	#Frequency callbacks
	for v in module.video_playback_list: v.updateVideo()

	done = time.time()
	if (done - _last_time) >= module.LOW_FREQUENCY_TICK:
		dtime = done - _last_time
		_last_time = done
		for call in module.low_frequency_callbacks:
			call(dtime)

	if (done - _last_time2) >= module.HEIGHT_FREQUENCY_TICK:
		dtime = done - _last_time2
		_last_time2 = done
		for call in module.height_frequency_callbacks:
			call(dtime)

#BUG: Fix performance issues.
_fatal_error = False
def secondary_loop():
	global _last_traceback, _fatal_error

	#It takes 0.6ms when with the editor. (Without tile replacing)
	try:
		if _fatal_error: return
		if module.change_scene_frame == False:
			if module.scene_behavior.paused == False:
				module.scene_behavior.update()
				module.scene_behavior.baseUpdate()
			if not module.scene_behavior: return #When removing the scene
			for b in module.scene_behavior.behaviors:
				if b.paused == False: b.update()
				if not module.scene_behavior: return #When removing the scene
	except:
		if not module.scene_behavior: return
		module.scene_behavior.paused = True
		s = traceback.format_exc()
		if s != _last_traceback:
			utils.debug("Error during runtime. Scene behavior suspended!")
			print(s)
			_fatal_error = True
		_last_traceback = s

	#It takes about 0.3ms (As much as the main loop)
	listen_list = [x for x in module.listen_input_list if x._immuse_keyboard == True and x.scene == module.scene_game]
	for x in module.listen_input_list: x._immuse_keyboard = x.use_keyboard
	event._key_event_loop(listen_list)
	module.window.secondary_update()
